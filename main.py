"""Publish the 20 November 2026 front page as this entry's image.

The finished front page ships beside this script as entry.png: a
newspaper page for Friday 20 November 2026, built from that day's
verified news. This script is deliberately boring — it proves the
vendored page is exactly the page it should be, then places a
byte-identical copy at the path the grader reads. Standard library
only; no network, no third-party code, no drawing at run time.
"""

import hashlib
import os
import struct
import sys

# Location of the vendored front page, next to this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDORED = os.path.join(BASE_DIR, "entry.png")

# sha256 of the composed 20 November 2026 front page. The copy is
# checked against it, so a damaged or swapped vendored file fails
# loudly instead of entering the wrong picture. It also pins the
# exact composed page: re-running compose.py with different stories
# produces a different digest and this script refuses to publish it.
EXPECTED_SHA256 = "a0f61f7091cc0135f478bdae5de9d28986c08eeabaf563cf07b0bda4f33ce5f7"

MAX_FILE_BYTES = 1024 * 1024  # the competition's 1 MiB cap
MAX_SIDE_PIXELS = 1024        # and its 1024x1024 cap
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    """Abort with a clear error instead of publishing a bad image."""
    raise SystemExit("main.py: " + message)


def load_vendored_page():
    try:
        with open(VENDORED, "rb") as handle:
            return handle.read()
    except OSError as exc:
        fail("cannot read vendored entry.png: %s" % exc)


def parse_png_size(blob):
    """Return (width, height) or abort if the bytes are not a whole PNG."""
    if len(blob) < 24 or blob[:8] != PNG_SIGNATURE:
        fail("vendored entry.png is not a PNG file")
    if blob[12:16] != b"IHDR":
        fail("vendored entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def validate_page(blob):
    """Abort unless blob is the expected 1024x1024 page under 1 MiB."""
    if len(blob) > MAX_FILE_BYTES:
        fail("entry.png is larger than 1 MiB (%d bytes)" % len(blob))
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA256:
        fail("vendored entry.png failed its digest check")
    width, height = parse_png_size(blob)
    if width > MAX_SIDE_PIXELS or height > MAX_SIDE_PIXELS:
        fail("entry.png is larger than 1024x1024 (%dx%d)" % (width, height))
    return width, height


def publish(blob, width, height):
    """Write blob to $MAKEFUN_OUTPUT_DIR/entry.png and verify the copy.

    The copy must match the vendored page byte for byte *and* decode
    to the same dimensions, so a truncated write cannot slip through.
    """
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail("cannot create output dir %s: %s" % (out_dir, exc))
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(blob)
    with open(target, "rb") as handle:
        copied = handle.read()
    if copied != blob:
        fail("the copied entry.png does not match the vendored page")
    if hashlib.sha256(copied).hexdigest() != EXPECTED_SHA256:
        fail("the copied page %s does not match the expected sha256" % target)
    copied_width, copied_height = parse_png_size(copied)
    if (copied_width, copied_height) != (width, height):
        fail("the copied entry.png has different dimensions (%dx%d)"
             % (copied_width, copied_height))
    return target


def main():
    blob = load_vendored_page()
    width, height = validate_page(blob)
    target = publish(blob, width, height)
    print("entry.png -> %s (%d bytes, %dx%d)"
          % (target, len(blob), width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
