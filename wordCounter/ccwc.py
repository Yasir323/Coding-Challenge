import argparse
import sys


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


def parse_command_line_arguments(options):
    parser = argparse.ArgumentParser()
    parse_optional_arguments(options, parser)
    parse_positional_arguments(parser)
    args = parser.parse_args()
    return args


def parse_optional_arguments(options, parser):
    for option in options:
        parser.add_argument(
            option["short_option"],
            option["verbose_option"],
            action="store_true",
            help=option["help"]
        )


def parse_positional_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("file", nargs="?")


def print_results(arguments):
    if arguments.file:
        stream = open(arguments.file, encoding="utf-8")
    else:
        stream = sys.stdin
    try:
        if arguments.bytes:
            total_bytes = get_number_of_bytes(stream)
            print(f"{total_bytes} {arguments.file if arguments.file else ''}")
        elif arguments.chars:  # Incorrect
            total_chars = get_number_of_characters(stream)
            print(f"{total_chars} {arguments.file if arguments.file else ''}")
        elif arguments.lines:
            total_lines = get_number_of_lines(stream)
            print(f"{total_lines} {arguments.file if arguments.file else ''}")
        elif arguments.words:
            total_words = get_number_of_words(stream)
            print(f"{total_words} {arguments.file if arguments.file else ''}")
        else:
            print_all_values(stream, arguments.file)
    except FileNotFoundError:
        print("File not found: {}".format(arguments.file))
    finally:
        stream.close()


def get_number_of_bytes(stream):
    data = stream.read()
    total_bytes = len(data)
    return total_bytes


def get_number_of_characters(stream):
    data = stream.read()
    total_chars = len(data.encode(sys.getfilesystemencoding()))
    return total_chars


def get_number_of_lines(stream):
    total_lines = 0
    for _ in stream.readlines():
        total_lines += 1
    return total_lines


def get_number_of_words(stream):
    total_words = 0
    for line in stream.readlines():
        total_words += len(line.split())
    return total_words


def print_all_values(stream, filename):
    data: str = stream.read()
    lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    total_lines = len(lines) - 1
    total_words = 0
    for line in lines:
        total_words += len(line.split())
    total_bytes = len(data)
    max_len = len(str(total_bytes))
    print(f"{total_lines:>{max_len}} {total_words:>{max_len}} {total_bytes} {filename if filename else ''}")


if __name__ == "__main__":
    main()
