def main():
    from .args import parse_args

    args = parse_args()

    import logging

    if args.debug:
        logging.getLogger("zundler").setLevel("DEBUG")
    else:
        logging.getLogger("zundler").setLevel("INFO")

    from .embed import embed_assets, extract_assets

    if args.extract:
        extract_assets(
            args.input_path,
            output_path=args.output_path,
        )
    else:
        embed_assets(
            args.input_path,
            output_path=args.output_path,
            append_pre=args.append_pre,
            append_post=args.append_post,
            debug=args.debug,
        )


if __name__ == "__main__":
    main()
