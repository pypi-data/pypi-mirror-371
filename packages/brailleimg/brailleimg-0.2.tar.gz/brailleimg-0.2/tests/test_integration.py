import os
import numpy as np
import sys
from pathlib import Path

import pytest

from brailleimg.cli import parse_args, run
from brailleimg.cli import DITHER_ALGORITHMS


@pytest.mark.parametrize(
    "cli_args, expected_file",
    [
        (
            ["tests/snail.png", "--width", "60", "--height", "40"],
            "tests/expected_snail_default.txt",
        ),
        (
            ["tests/snail.png", "--width", "60", "--height", "40", "--invert"],
            "tests/expected_snail_invert.txt",
        ),
        (
            ["tests/snail.png", "--width", "60", "--height", "40", "-T", "200"],
            "tests/expected_snail_t200.txt",
        ),
        (
            ["tests/snail.png", "-W", "20", "-H", "10", "-T", "median"],
            "tests/expected_snail_median.txt",
        ),
        (
            ["tests/snail.png", "-W", "20", "-H", "10", "-T", "otsu"],
            "tests/expected_snail_otsu.txt",
        ),
        (
            ["tests/snail.png", "-W", "20", "-H", "10", "-T", "otsu", "-I"],
            "tests/expected_snail_otsu_invert.txt",
        ),
        (
            ["tests/snail.png", "-W", "60", "-H", "40", "-F"],
            "tests/expected_snail_blocks.txt",
        ),
        *[
            (
                ["tests/snail.png", "-W", "60", "-H", "40", "-D", algo],
                f"tests/expected_snail_{algo}.txt",
            )
            for algo in DITHER_ALGORITHMS
            if algo != "all"
        ],
        *[
            (
                ["tests/gradient.png", "-W", "60", "-H", "40", "-D", algo],
                f"tests/expected_gradient_{algo}.txt",
            )
            for algo in DITHER_ALGORITHMS
            if algo != "all"
        ],
        *[
            (
                [
                    "tests/radial_gradient.png",
                    "-W",
                    "60",
                    "-H",
                    "40",
                    "-D",
                    algo,
                ],
                f"tests/expected_radial_gradient_{algo}.txt",
            )
            for algo in DITHER_ALGORITHMS
            if algo != "all"
        ],
    ],
)
def test_integration_snail(capsys, monkeypatch, cli_args, expected_file):
    np.random.seed(0)
    monkeypatch.setattr(sys, "argv", ["brailleimg"] + cli_args)
    args = parse_args()

    run(args)

    output = capsys.readouterr().out
    if os.getenv("BRAILLEIMG_UPDATE_TESTS"):
        Path(expected_file).write_text(output, encoding="utf-8")
    else:
        expected = Path(expected_file).read_text(encoding="utf-8")
        assert output == expected
