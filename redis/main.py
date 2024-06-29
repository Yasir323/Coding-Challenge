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


class Parser:

    def parse(self, message: str):
        data_type = message[0]
        match data_type:
            case "+":  # Simple String
                data = self._parse_simple_string(message[1:])
                print(f"Simple String: {data}")
            case "-":  # Simple Error
                data = self._parse_simple_string(message[1:])
                print(f"Simple Error: {data}")
            case ":":  # Number
                data = self._parse_integer(message)
                print(f"Integer: {data}")
            case "$":  # Bulk String
                data = self._parse_bulk_string(message)
                print(f"Bulk String: {data}")
            case "*":  # Array
                data = self._parse_integer(message)
            case _:  # Nil
                data = None
        return data

    @staticmethod
    def _parse_simple_string(message: str) -> str:
        string, terminator = message[:-2], message[-2:]
        if string.find("\r") != -1 or string.find("\n") != -1 or terminator != "\r\n":
            raise RespProtocolException("Invalid String")
        return string

    @staticmethod
    def _parse_simple_error(message: str) -> str:
        error_message, terminator = message[:-2], message[-2:]
        if error_message.find("\r") != -1 or error_message.find("\n") != -1 or terminator != "\r\n":
            raise RespProtocolException("Invalid String")
        return error_message

    @staticmethod
    def _parse_integer(message: str) -> int:
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

    @staticmethod
    def _parse_bulk_string(message: str) -> str | None:
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

    def _parse_array(self, message: str) -> list | None:
        array = []
        if message.endswith("\r\n"):
            size, *elements = message.split("\r\n")
            if size == "-1":
                return None
            if len(elements) == int(size):
                for element in elements:
                    array.append(self.parse(element))
        return array


def deserialize(message: str):
    parser = Parser()
    parser.parse(message)
