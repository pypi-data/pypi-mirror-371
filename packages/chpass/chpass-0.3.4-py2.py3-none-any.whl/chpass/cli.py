import argparse
import getpass

from chpass.config import (
    DEFAULT_EXPORT_DESTINATION_FOLDER,
    DEFAULT_FILE_ADAPTER
)


def create_import_parser(subparsers: argparse._SubParsersAction) -> None:
    parser_import = subparsers.add_parser("import", description="imports a file with the passwords")
    parser_import.add_argument(
        "-f",
        "--from",
        dest="from_file",
        help="credentials file to import from",
        type=str,
        required=True
    )


def create_export_parser(subparsers: argparse._SubParsersAction) -> None:
    parser_export = subparsers.add_parser("export", description="exports a chrome data files")
    parser_export.add_argument(
        "-d",
        "--destination",
        dest="destination_folder",
        type=str,
        help="destination folder to export the files",
        default=DEFAULT_EXPORT_DESTINATION_FOLDER
    )
    export_subparsers = parser_export.add_subparsers(dest="export_kind")
    export_subparsers.required = False
    export_subparsers.add_parser("passwords", description="export passwords")
    export_subparsers.add_parser("history", description="export history")
    export_subparsers.add_parser("downloads", description="export downloads")
    export_subparsers.add_parser("top_sites", description="export top sites")
    export_subparsers.add_parser("profile_pic", description="export profile picture")


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chpass",
        description="Gather information from chrome",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="mode")
    subparsers.required = True
    create_import_parser(subparsers)
    create_export_parser(subparsers)
    parser.add_argument("-u", "--user", dest="user", type=str, default=getpass.getuser())
    parser.add_argument("-i", "--file-adapter", dest="file_adapter", type=str, default=DEFAULT_FILE_ADAPTER)
    return parser


def parse_args(args: list) -> argparse.Namespace:
    arg_parser = create_arg_parser()
    return arg_parser.parse_args(args)
