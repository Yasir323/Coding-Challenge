"""
RESP specification: https://redis.io/docs/latest/develop/reference/protocol-spec/

_CHARACTER_DATATYPE_MAPPING = {
    "+": "SIMPLE_STRING",
    "-": "ERROR",
    ":": "INTEGER",
    "$": "BULK_STRING",
    "*": "ARRAY",
    "_": "NULL",
    "#": "BOOLEAN",
    ",": "DOUBLE",
    "(": "BIG_NUMBER",
    "!": "BULK_ERROR",
    "=": "VERBATIM_STRING",
    "%": "MAP",
    "~": "SET",
    ">": "PUSH"
}
"""


class RespProtocolException(Exception):
    pass


def parse_simple_string(message: str):
    string, terminator = message[:-2], message[-2:]
    if string.find("\r") != -1 or string.find("\n") != -1 or terminator != "\r\n":
        raise RespProtocolException("Invalid String")
    return string


def parse_simple_error(message: str):
    error_message, terminator = message[:-2], message[-2:]
    if error_message.find("\r") != -1 or error_message.find("\n") != -1 or terminator != "\r\n":
        raise RespProtocolException("Invalid String")
    return error_message


def parse_integer(message: str):
    signed_number, terminator = message[:-2], message[-2:]
    try:
        if message[0] == "+":
            number = int(signed_number[1:])
        elif message[0] == "-":
            number = -int(signed_number[1:])
        else:
            number = int(signed_number)
    except IndexError:
        raise RespProtocolException("Invalid String")
    except ValueError:
        raise RespProtocolException("Invalid String")
    except TypeError:
        raise RespProtocolException("Invalid String")
    return number


def parse_bulk_string(message: str):
    parts = message.split("\r\n")
    if len(parts) == 2:
        length, _ = parts
        if length == "-1":
            return None
    elif len(parts) == 3:
        length, data, _ = parts
        length = int(length)
        if len(data) == length:
            return data
    raise RespProtocolException("Invalid String")


def deserialize(message: str):
    data_type = message[0]
    if data_type == "+":
        string = parse_simple_string(message[1:])
        print(f"Simple String: {string}")
    elif data_type == "-":
        error_message = parse_simple_string(message[1:])
        print(f"Simple Error: {error_message}")
    elif data_type == ":":
        number = parse_integer(message)
        print(f"Integer: {number}")
    elif data_type == "$":
        string = parse_bulk_string(message)
        print(f"Bulk String: {string}")
