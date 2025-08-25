import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from brailleimg.conversion import (
    fmt_codepoint_blocks,
    fmt_codepoint_braille,
    img_to_text,
)
from brailleimg.dither import bayer, error_diffusion, quantize, random_noise
from brailleimg.preprocess import median_threshold, otsu_threshold
from brailleimg.util import fit_inside

# The codepoint pixel coverage
CHAR_WIDTH = 2
CHAR_HEIGHT = 4


def _existing_file(path_str: str) -> Path:
    p = Path(path_str)
    if not p.exists():
        raise argparse.ArgumentTypeError(f"'{path_str}' does not exist")
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"'{path_str}' is not a file")
    return p


def try_all_algorithms(img) -> None:
    for name, func in DITHER_ALGORITHMS.items():
        if name == "all":
            continue
        dithered_img = func(img)
        print(f"{name}:")
        print(img_to_text(dithered_img))
        print()
    exit(0)


DITHER_ALGORITHMS = {
    "quantize": quantize,
    "random-noise": random_noise,
    "bayer1": lambda img: bayer(img, order=1),
    "bayer2": lambda img: bayer(img, order=2),
    "bayer3": lambda img: bayer(img, order=3),
    "floyd-steinberg": lambda img: error_diffusion(img, "floyd-steinberg"),
    "atkinson": lambda img: error_diffusion(img, "atkinson"),
    "jarvis-judice-ninke": lambda img: error_diffusion(
        img, "jarvis-judice-ninke"
    ),
    "stucki": lambda img: error_diffusion(img, "stucki"),
    "burkes": lambda img: error_diffusion(img, "burkes"),
    "sierra2": lambda img: error_diffusion(img, "sierra2"),
    "sierra3": lambda img: error_diffusion(img, "sierra3"),
    "sierra2-4a": lambda img: error_diffusion(img, "sierra-2-4a"),
    "all": try_all_algorithms,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="brailleimg",
        description="Convert image to text using Braille symbols.",
    )
    parser.add_argument(
        "path", type=_existing_file, help="image file to convert"
    )
    parser.add_argument(
        "--width",
        "-W",
        type=int,
        help="maximum output width (in terminal columns)",
        default=shutil.get_terminal_size().columns - 1,
    )
    parser.add_argument(
        "--height",
        "-H",
        type=int,
        help="maximum output height (in terminal lines)",
        default=shutil.get_terminal_size().lines - 1,
    )
    parser.add_argument(
        "--threshold",
        "-T",
        default="128",
        help="'median', 'otsu', or numeric 0..255",
        type=lambda x: (
            x
            if x in ["median", "otsu"] or (x.isdigit() and 0 <= int(x) <= 255)
            else argparse.ArgumentTypeError(
                "Must be 'median', 'otsu', or a number between 0 and 255"
            )
        ),
    )
    parser.add_argument(
        "--dither",
        "-D",
        choices=list(DITHER_ALGORITHMS.keys()),
        default=list(DITHER_ALGORITHMS.keys())[0],
        help="algorithm to quantize",
    )
    parser.add_argument(
        "--invert",
        "-I",
        action="store_true",
        help="output is meant to be viewed on a dark terminal",
    )
    parser.add_argument(
        "-F",
        "--full-blocks",
        action="store_true",
        help="use solid blocks (requires a capable font)",
    )
    parser.add_argument(
        "--font-ar", type=float, default=0.5, help="adjust font aspect ratio"
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    pil_img = Image.open(args.path).convert("L")
    width, height = fit_inside(
        pil_img.width / args.font_ar,
        pil_img.height,
        args.width,
        args.height,
    )
    width *= CHAR_WIDTH
    height *= CHAR_HEIGHT
    pil_img = pil_img.resize((width, height), resample=Image.BILINEAR)
    img = np.array(pil_img, dtype=np.float32) / 255.0

    # Compute integer threshold (0..255) via median/otsu or numeric input
    match args.threshold.strip().lower():
        case "median":
            arr_uint8 = (img * 255).astype(np.uint8)
            threshold_int = median_threshold(arr_uint8)
        case "otsu":
            arr_uint8 = (img * 255).astype(np.uint8)
            threshold_int = otsu_threshold(arr_uint8)
        case _:
            threshold_int = int(args.threshold)

    # Normalize and apply optional inversion
    threshold_float = threshold_int / 255.0
    if args.invert:
        threshold_float = 1 - threshold_float
        img = 1 - img

    # Shift image by threshold before dithering
    img = img + 0.5 - threshold_float
    img = DITHER_ALGORITHMS[args.dither](img)

    print(
        img_to_text(
            img,
            fmt_codepoint=(
                fmt_codepoint_blocks
                if args.full_blocks
                else fmt_codepoint_braille
            ),
        ),
        end="",
    )
