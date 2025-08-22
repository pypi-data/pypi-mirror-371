import argparse
import json
import sys

from .generator import generate_stac_items, generate_stac_items_from_template, write_ndjson


def write_ndjson_to_stdout(items: list[dict]) -> None:
    """Write list of STAC items to stdout as NDJSON."""
    for item in items:
        print(json.dumps(item, separators=(",", ":")))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="stac-sample-maker",
        description="Generate synthetic STAC Items and write as NDJSON",
    )
    parser.add_argument(
        "-n", "--num-items", type=int, default=100, help="Number of items to generate"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default=None,
        help="Output NDJSON file path (default: stdout)",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        required=False,
        help="Path to template STAC item JSON file to match structure",
    )
    parser.add_argument(
        "--start",
        type=str,
        required=False,
        help="Start of datetime range (ISO 8601, e.g., 2020-01-01T00:00:00Z)",
    )
    parser.add_argument(
        "--end",
        type=str,
        required=False,
        help="End of datetime range (ISO 8601, e.g., 2020-12-31T23:59:59Z)",
    )
    parser.add_argument(
        "--interval-percent",
        type=float,
        default=0.2,
        help="Fraction (0-1) of items that use start_datetime/end_datetime instead of datetime",
    )
    parser.add_argument(
        "--bbox",
        type=float,
        nargs=4,
        metavar=("MINX", "MINY", "MAXX", "MAXY"),
        help="Bounding box to clamp geometry and bbox [minx miny maxx maxy] in WGS84",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated STAC items against JSON schema (requires stac-validator)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = parse_args(argv)

    try:
        bbox = tuple(args.bbox) if args.bbox else None

        if args.template:
            # Generate items based on template structure
            items = generate_stac_items_from_template(
                template_path=args.template,
                num_items=args.num_items,
                start_date=args.start,
                end_date=args.end,
                bbox=bbox,
                seed=args.seed,
                validate=args.validate,
            )
        else:
            # Generate items with all extensions
            items = generate_stac_items(
                num_items=args.num_items,
                start_date=args.start,
                end_date=args.end,
                interval_percent=args.interval_percent,
                bbox=bbox,
                seed=args.seed,
                validate=args.validate,
            )

        if args.output:
            write_ndjson(args.output, items)
            print(f"Generated {len(items)} STAC items and saved to {args.output}", file=sys.stderr)
        else:
            write_ndjson_to_stdout(items)
            print(f"Generated {len(items)} STAC items", file=sys.stderr)

        return 0

    except (ValueError, SystemExit, FileNotFoundError, ImportError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
