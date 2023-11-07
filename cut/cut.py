import argparse
import sys


class CommandLineArgumentsParser:
    def __init__(self):
        self.options = [
            {
                "short_option": "-f",
                "verbose_option": "--fields",
                "help": "Select using a specified field, a field set, or a field range."
            },
            {
                "short_option": "-d",
                "verbose_option": "--delimiter",
                "help": "Used to specify a delimiter to use instead of the default COMMA delimiter."
            }
        ]
        self.parser = argparse.ArgumentParser()

    def parse_args(self):
        self.parse_optional_arguments()
        self.parse_positional_arguments()

    def parse_optional_arguments(self):
        for option in self.options:
            self.parser.add_argument(
                option["short_option"],
                option["verbose_option"],
                help=option["help"]
            )

    def parse_positional_arguments(self):
        self.parser.add_argument("file", nargs="?")

    def get_args(self):
        return self.parser.parse_args()


def main():
    parser = CommandLineArgumentsParser()
    parser.parse_args()
    args = parser.get_args()

    stream = get_input_stream(args.file)

    try:
        read_stream(stream, args)
    finally:
        stream.close()


def get_input_stream(file):
    if file:
        stream = open(file, encoding="utf-8")
    else:
        stream = sys.stdin
    return stream


def read_stream(stream, args):
    delimiter = "," if not args.delimiter else args.delimiter
    for line in stream.readlines():
        words = line.split(delimiter)
        cols = args.fields
        print_fields(words, cols, delimiter)


def print_fields(words, cols, delimiter):
    if cols:
        if "-" in cols:
            start, end = cols.split("-")
            start = int(start)
            if not end:
                end = -1
            else:
                end = int(end)
            words = words[start-1:end]
            print(delimiter.join(words))
        else:
            index = int(cols)
            print(words[index-1])
    else:
        print(delimiter.join(words))


if __name__ == "__main__":
    main()
