test_cases = {
    "valid": [
        '{}',
        '{"key1": true, "key2": false, "key3": null, "key4": "value", "key5": 101}',
        '''{
            "key1": true,
            "key2": false,
            "key3": null,
            "key4": "value",
            "key5": 101,
            "key6": 1.1
        }'''
    ],
    "invalid": [
        '',
        '{"key1": true, "key2": false',
        '{"key1", "key2"}',
        '{"key1": true, "key2": false, []}',
        '("key1": true, "key2": false)',
        '{"key1": True, "key2": false}',
        '{"key1"- true, "key2"- false}',
        '{"key1": true, "key2": NULL}',
        '{"key1": true, "key2": None}',
        '{"key1": true, "key2": None]',
        '{"key1": true, "key2": None, "key3": ["key4": "value4", "key5": "value5"]}',
        '["key1": true, "key2": false]',
        '{"key1": true, "key2": false, "()": 5}',
        '''{"key1": true, "key2": false, 'key3': "value"}''',
        '{"key1": true, "key2": false, "key3": ("value1", "value2")}',
    ]
}

OBJECT_DELIMITER_START = "{"
OBJECT_DELIMITER_END = "}"
ARRAY_DELIMITER_START = "["
ARRAY_DELIMITER_END = "]"
SEPARATORS = [":", ","]
KEYWORDS = ["null", "true", "false"]


def main():
    return_value = parse_json(test_cases["valid"][1])
    if return_value:
        print("JSON is valid")
    else:
        print("JSON is invalid")


def parse_json(json):
    for char in json:
        if char == OBJECT_DELIMITER_START:
            pass
    return 0


if __name__ == "__main__":
    main()
