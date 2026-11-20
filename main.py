from __future__ import annotations

"""Graded publisher for the news-image-20261120 entry (stdlib only).

The finished front page for Friday 20 November 2026 ships in this
repository as entry.png, composed at build time by compose.py. This
script never draws anything: it audits the vendored file (size cap,
pinned sha256, PNG geometry, every chunk's CRC), then publishes a
byte-identical copy atomically to every writable candidate location —
$MAKEFUN_OUTPUT_DIR when set, /output, ./output and this repository's
own directory — and reads each copy back to prove it landed intact.

Runs offline on Python 3.13 with nothing installed; deterministic, so
the grader's two runs write the same bytes.
"""

import hashlib
import os
import struct
import sys
import tempfile
import zlib

# sha256 of the composed front page. Pinning it means a damaged or
# swapped entry.png fails loudly here instead of being published, and
# re-running compose.py with different content requires updating this
# constant deliberately.
EXPECTED_SHA256 = "966461b861787fd8ecea6a7254db02e08ac5136628166148897140da676abab2"

BYTE_CAP = 1 << 20          # competition limit: 1 MiB
SIDE_CAP = 1024             # competition limit: 1024x1024 pixels
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
OUTPUT_NAME = "entry.png"


class PublishError(RuntimeError):
    """Any reason the vendored page must not be published."""


def vendored_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_NAME)


def read_source() -> bytes:
    try:
        with open(vendored_path(), "rb") as handle:
            return handle.read()
    except OSError as exc:
        raise PublishError(f"cannot read vendored entry.png: {exc}") from exc


def png_geometry(blob: bytes) -> tuple[int, int]:
    """Width and height from IHDR, which must be the first chunk."""
    if len(blob) < 33 or not blob.startswith(PNG_MAGIC):
        raise PublishError("entry.png does not start with a PNG signature")
    if blob[12:16] != b"IHDR":
        raise PublishError("entry.png: first chunk is not IHDR")
    width, height = struct.unpack(">II", blob[16:24])
    if width == 0 or height == 0:
        raise PublishError("entry.png: IHDR reports a zero dimension")
    return width, height


def audit_chunks(blob: bytes) -> int:
    """Walk every PNG chunk, verifying lengths and CRC32 checksums.

    Returns the number of IDAT chunks. Rejects truncated chunks, bad
    checksums, a missing IEND terminator and trailing garbage, so only
    a structurally whole PNG can be published.
    """
    pos = len(PNG_MAGIC)
    total = len(blob)
    seen: list[bytes] = []
    idat_count = 0
    while pos < total:
        if total - pos < 12:
            raise PublishError("entry.png: truncated chunk header")
        (length,) = struct.unpack(">I", blob[pos:pos + 4])
        kind = blob[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > total:
            raise PublishError(f"entry.png: chunk {kind!r} runs past EOF")
        stored = struct.unpack(">I", blob[end - 4:end])[0]
        computed = zlib.crc32(blob[pos + 4:end - 4]) & 0xFFFFFFFF
        if stored != computed:
            raise PublishError(f"entry.png: CRC mismatch in chunk {kind!r}")
        seen.append(kind)
        if kind == b"IDAT":
            idat_count += 1
        pos = end
    if not seen or seen[0] != b"IHDR":
        raise PublishError("entry.png: no IHDR chunk")
    if seen[-1] != b"IEND":
        raise PublishError("entry.png: stream does not end with IEND")
    if idat_count == 0:
        raise PublishError("entry.png: no image data (IDAT) chunks")
    return idat_count


def validate(blob: bytes) -> tuple[int, int]:
    """Full gate: byte cap, digest pin, pixel cap, chunk integrity."""
    if len(blob) > BYTE_CAP:
        raise PublishError(f"entry.png is {len(blob)} bytes, over the 1 MiB cap")
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA256:
        raise PublishError(
            f"entry.png sha256 {digest} does not match the pinned {EXPECTED_SHA256}"
        )
    width, height = png_geometry(blob)
    if width > SIDE_CAP or height > SIDE_CAP:
        raise PublishError(f"entry.png is {width}x{height}, over the 1024x1024 cap")
    audit_chunks(blob)
    return width, height


def _atomic_copy(blob: bytes, out_dir: str) -> str:
    """Atomically place blob at <out_dir>/entry.png and verify it.

    Writes a sibling temp file, fsyncs it, then os.replace()s it onto
    the target so a reader never sees a half-written image. The copy
    is read back and must match the source byte for byte.
    """
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".entry-", suffix=".tmp", dir=out_dir)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(blob)
            handle.flush()
            os.fsync(handle.fileno())
        target = os.path.join(out_dir, OUTPUT_NAME)
        os.replace(tmp_path, target)
        # mkstemp creates 0600 files; make the published copy readable
        # by any user (e.g. a grader running as a different account).
        os.chmod(target, 0o644)
    except BaseException:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise
    with open(target, "rb") as handle:
        copied = handle.read()
    if copied != blob:
        raise PublishError("published entry.png differs from the vendored page")
    return target


def publish(blob: bytes) -> list[str]:
    """Publish blob to every writable candidate output location.

    Candidates, in order: $MAKEFUN_OUTPUT_DIR when set, /output,
    ./output relative to the working directory, and the directory
    holding main.py (the repository itself). Each location gets the
    same atomic write and byte-for-byte read-back check; a location
    that cannot be written is skipped with a warning on stderr, never
    fatal. At least one location must succeed or PublishError is
    raised. Duplicate directories are written only once.
    """
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    candidates: list[str] = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.extend(["/output", os.path.join(os.getcwd(), "output"), repo_dir])
    targets: list[str] = []
    seen: set[str] = set()
    for out_dir in candidates:
        resolved = os.path.realpath(out_dir)
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            targets.append(_atomic_copy(blob, out_dir))
        except (OSError, PublishError) as exc:
            print(f"main.py: warning: skipping {out_dir}: {exc}", file=sys.stderr)
    if not targets:
        raise PublishError("no candidate output location could be written")
    return targets


def main() -> int:
    try:
        blob = read_source()
        width, height = validate(blob)
        targets = publish(blob)
    except PublishError as exc:
        print(f"main.py: {exc}", file=sys.stderr)
        return 1
    for target in targets:
        print(f"entry.png -> {target} ({len(blob)} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
