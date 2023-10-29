import argparse
import sys


def parse_optional_arguments(options, parser):
    for option in options:
        parser.add_argument(
            option["short_option"],
            option["verbose_option"],
            action="store_true",
            help=option["help"]
        )


def parse_positional_arguments(parser):
    parser.add_argument("file")


def parse_command_line_arguments(options):
    parser = argparse.ArgumentParser()
    parse_optional_arguments(options, parser)
    parse_positional_arguments(parser)
    args = parser.parse_args()
    return args


def get_number_of_bytes(fp):
    fp.seek(0, 2)
    total_bytes = fp.tell()
    return total_bytes


def get_number_of_lines(fp):
    total_lines = 0
    for _ in fp.readlines():
        total_lines += 1
    return total_lines


def get_number_of_words(fp):
    total_words = 0
    for line in fp.readlines():
        total_words += len(line.split())
    return total_words


def get_number_of_characters(fp):
    data = fp.read()
    total_chars = len(data.encode(sys.getfilesystemencoding()))
    return total_chars


def print_all_values(fp, filename):
    total_lines = get_number_of_lines(fp)
    fp.seek(0)
    total_words = get_number_of_words(fp)
    total_bytes = get_number_of_bytes(fp)
    max_len = len(str(total_bytes))
    print(f"{total_lines:>{max_len}} {total_words:>{max_len}} {total_bytes} {filename}")


def print_results(arguments):
    try:
        with open(arguments.file, encoding="utf-8") as fp:
            if arguments.bytes:
                total_bytes = get_number_of_bytes(fp)
                print(f"{total_bytes} {arguments.file}")
            elif arguments.chars:  # Incorrect
                total_chars = get_number_of_characters(fp)
                print(f"{total_chars} {arguments.file}")
            elif arguments.lines:
                total_lines = get_number_of_lines(fp)
                print(f"{total_lines} {arguments.file}")
            elif arguments.words:
                total_words = get_number_of_words(fp)
                print(f"{total_words} {arguments.file}")
            else:
                print_all_values(fp, arguments.file)
    except FileNotFoundError:
        print("File not found: {}".format(arguments.file))


def main():
    options = [
        {
            "short_option": "-c",
            "verbose_option": "--bytes",
            "help": "print the byte counts"
        },
        {
            "short_option": "-m",
            "verbose_option": "--chars",
            "help": "print the character counts"
        },
        {
            "short_option": "-l",
            "verbose_option": "--lines",
            "help": "print the newline counts"
        },
        {
            "short_option": "-w",
            "verbose_option": "--words",
            "help": "print the word counts"
        }
    ]
    arguments = parse_command_line_arguments(options)

    print_results(arguments)


if __name__ == "__main__":
    main()
