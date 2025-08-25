from brailleimg.cli import parse_args, run


def main() -> None:
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
