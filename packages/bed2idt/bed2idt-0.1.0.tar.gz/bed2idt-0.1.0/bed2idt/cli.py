import argparse
import pathlib


def cli():
    description = "Generates IDT input files from the 7 col primer.bed"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-b",
        "--bedfile",
        help="Path the the bedfile",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The output location, please use the .xlsx extention",
        type=pathlib.Path,
        default=pathlib.Path("output.xlsx"),
    )

    subparsers = parser.add_subparsers(dest="command")
    # Add the plate arguments
    plate_parser = subparsers.add_parser("plate")
    plate_parser.add_argument(
        "-s",
        "--splitby",
        choices=["pool", "ref", "none", "nest"],
        default="pool",
        help="Should the primers be split across more than one plate",
    )
    plate_parser.add_argument(
        "-f",
        "--fillby",
        choices=["rows", "cols"],
        default="rows",
        help="How should the plate be filled",
    )
    # Add the tube arguments
    tube_parser = subparsers.add_parser("tube")
    tube_parser.add_argument(
        "-s",
        "--scale",
        help="The conc of the primers",
        required=False,
        type=str,
        default="25nm",
        choices=[
            "25nm",
            "100nm",
            "250nm",
            "1um",
            "2um",
            "5um",
            "10um",
            "4nmU",
            "20nmU",
            "PU",
            "25nmS",
        ],
    )
    tube_parser.add_argument(
        "-p",
        "--purification",
        help="Purifcation",
        required=False,
        type=str,
        default="STD",
        choices=["STD", "PAGE", "HPLC", "IEHPLC", "RNASE", "DUALHPLC", "PAGEHPLC"],
    )
    parser.add_argument(
        "--force",
        help="Override the output directory",
        action="store_true",
    )

    args = parser.parse_args()
    return args
