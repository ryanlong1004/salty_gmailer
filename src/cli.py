"""CLI for wrangler"""
import argparse
import glob
import pathlib
import sys
import logging

logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(
    prog="gmailer",
    description="Configuration based automation for gmail.",
    # epilog="Example: wrangler --output-path ./temp file.yaml path",
)

parser.add_argument(
    "paths", nargs="*", type=pathlib.Path, help="path containing the rule.yaml files"
)


def get_queue(_paths: list[pathlib.Path]):
    """creates generator of files for parsing"""
    for _path in _paths:
        if _path.is_dir():
            for _file in glob.glob(f"{_path.absolute()}/*yaml", recursive=True):
                yield _file
        else:
            yield _path


def get_cli_input():
    """returns an object of user inputted data"""
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()
    # if args.output_path is None:
    #     logger.error("An output path is required using the '--output_path' flag")
    #     sys.exit(2)
    # return {"output_path": args.output_path, "queue": get_queue(args.paths)}


class RequiredInputMissing(Exception):
    """Raised when a required input is missing"""
