import argparse
import os

from text_utils import dictionary
from text_utils.api.utils import cpu_cores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-files",
        nargs="+",
        help="One or more path to text files",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Path to output file",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--max-size",
        type=int,
        default=100_000,
        help="Max words in the dictionary",
    )
    parser.add_argument(
        "-m",
        "--max-sequences",
        type=int,
        default=None,
        help="Max number of sequences to consider while building the dictionary",
    )
    parser.add_argument(
        "-n",
        "--num-threads",
        type=int,
        default=None,
        help="Number of threads to use",
    )
    parser.add_argument(
        "--char-grams",
        type=int,
        default=1,
        choices=[1, 3],
        help="For key type char, this is the number of consecutive chars we use to build the dictionary",
    )
    parser.add_argument(
        "--key",
        choices=["word", "char"],
        default="word",
        help="Key type",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar",
    )
    return parser.parse_args()


def create_dictionary(args: argparse.Namespace) -> None:
    if args.num_threads is None:
        args.num_threads = min(cpu_cores(), 4)

    d = dictionary.Dictionary.create(
        args.input_files,
        args.max_size,
        args.max_sequences,
        args.num_threads,
        args.key == "char",
        args.char_grams,
        args.progress,
    )

    output_dir = os.path.dirname(args.output_file)
    if output_dir != "":
        os.makedirs(output_dir, exist_ok=True)
    d.save(args.output_file)


def main():
    create_dictionary(parse_args())
