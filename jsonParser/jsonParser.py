from enum import Enum, auto
from typing import Union

Number = Union[int, float]
JSONDataTypes = Union[Number, str, dict, list]


class JSONObjectNode:
    def __init__(self, pairs=None):
        self.pairs = pairs or {}

    def add_pair(self, key, value):
        self.pairs[key] = value

    def __repr__(self):
        return f"{self.pairs}"


class JSONArrayNode:
    def __init__(self, items=None):
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)

    def __repr__(self):
        return f"{self.items}"


class JSONStringNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'"{self.value}"'


class JSONNumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class JSONBooleanNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}".lower()


class JSONNullNode:
    def __repr__(self):
        return "null"


# Example JSON: {"name": "John", "age": 30, "city": "New York", "is_student": false, "grades": [90, 85, 88]}
# json_object = JSONObject()
# json_object.add_pair("name", JSONString("John"))
# json_object.add_pair("age", JSONNumber(30))
# json_object.add_pair("city", JSONString("New York"))
# json_object.add_pair("is_student", JSONBoolean(False))
#
# grades_array = JSONArray([JSONNumber(90), JSONNumber(85), JSONNumber(88)])
# json_object.add_pair("grades", grades_array)
#
# print(json_object)


class TokenType(Enum):
    OBJECT_START = "{"
    OBJECT_END = "}"
    ARRAY_START = "["
    ARRAY_END = "]"
    COMMA = ","
    COLON = ":"
    HYPHEN = "-"
    DOUBLE_QUOTES = '"'
    STRING_LITERAL = auto()
    NUMBER = auto()
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    EOF = "EOF"


class JSONToken:
    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"JSONToken({self.token_type}, {self.value})"


class Lexer:

    def __init__(self, json_string):
        self.json_string = json_string
        self.position = 0
        self.current_character: Union[str, None] = self.json_string[0]
        self.length = len(json_string)

    def advance(self) -> None:
        self.position += 1
        if self.position <= self.length:
            self.current_character = self.json_string[self.position]
        else:
            self.current_character = None

    def skip_whitespace(self):
        while self.current_character and self.current_character.isspace():
            self.advance()

    def get_number(self) -> Number:
        start_position = self.position
        while self.current_character and (self.current_character.isdigit() or self.current_character == '.'):
            self.advance()
        number_str = self.json_string[start_position:self.position]
        return float(number_str) if '.' in number_str else int(number_str)

    def get_string(self):
        start_position = self.position + 1  # Skip the opening double quote
        self.current_character = self.json_string[start_position]
        while self.current_character != '"':
            self.advance()
        return self.json_string[start_position:self.position]

    def get_next_token(self):

        while self.current_character is not None:

            if self.current_character.isspace():
                self.skip_whitespace()
                continue

            elif self.current_character == TokenType.OBJECT_START.value:
                self.advance()
                return JSONToken(TokenType.OBJECT_START)

            elif self.current_character == TokenType.OBJECT_END.value:
                self.advance()
                return JSONToken(TokenType.OBJECT_END)

            elif self.current_character == TokenType.ARRAY_START.value:
                self.advance()
                return JSONToken(TokenType.ARRAY_START)

            elif self.current_character == TokenType.ARRAY_END.value:
                self.advance()
                return JSONToken(TokenType.ARRAY_END)

            elif self.current_character == TokenType.COMMA.value:
                self.advance()
                return JSONToken(TokenType.COMMA)

            elif self.current_character == TokenType.COLON.value:
                self.advance()
                return JSONToken(TokenType.COLON)

            elif self.current_character == TokenType.DOUBLE_QUOTES.value:
                return JSONToken(TokenType.STRING_LITERAL, self.get_string())

            elif self.current_character.isdigit() or self.current_character == TokenType.HYPHEN.value:
                return JSONToken(TokenType.NUMBER, self.get_number())

            elif self.current_character.isalpha():
                keyword = ""
                while self.current_character.isalpha():
                    keyword += self.current_character
                    self.advance()
                if keyword == TokenType.TRUE.value:
                    return JSONToken(TokenType.TRUE)
                elif keyword == TokenType.FALSE.value:
                    return JSONToken(TokenType.FALSE)
                elif keyword == TokenType.NULL.value:
                    return JSONToken(TokenType.NULL)
                else:
                    raise ValueError(f"Invalid keyword: {keyword}")

            raise ValueError(f"Invalid character: {self.current_character}")

        return JSONToken(TokenType.EOF)


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()




# Example usage:
json_string = '{"name": "John", "age": 30, "city": "New York", "is_student": false, "grades": [90, 85, 88]}'
lexer = Lexer(json_string)

while True:
    token = lexer.get_next_token()
    print(token)
    if token.token_type == TokenType.OBJECT_END:
        break
