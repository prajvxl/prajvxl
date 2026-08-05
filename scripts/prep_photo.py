"""
prep_photo.py — turn a normal photo into a clean, high-contrast,
background-removed grayscale image ready for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Writes:
    scripts/prepped-source.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "scripts/prepped-source.png"):
    # 1. Remove the background. rembg returns an RGBA image where the
    #    alpha channel is 0 wherever it decided "this is background".
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    result_bytes = remove(input_bytes)

    Path("scripts/_tmp_nobg.png").write_bytes(result_bytes)
    rgba = Image.open("scripts/_tmp_nobg.png").convert("RGBA")

    # 2. Composite onto pure white using the alpha mask, so the removed
    #    background becomes solid white (the "blank" end of our ASCII ramp).
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. Convert to grayscale, then apply CLAHE for local contrast.
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    Image.fromarray(contrasted).save(output_path)
    print(f"Wrote {output_path}")

    # cleanup temp file
    Path("scripts/_tmp_nobg.png").unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <path-to-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
