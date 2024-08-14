package main

import (
	"errors"
	"fmt"
)

const (
	CURLY_BRACKET_OPEN  = '{'
	CURLY_BRACKET_CLOSE = '}'
	DOUBLE_QUOTE        = '"'
	COMMA               = ','
	NEWLINE             = '\n'
	SPACE               = ' '
	COLON               = ':'
	TAB                 = '\t'
	CARRIAGE_RETURN     = '\r'
)

func main() {
	fmt.Println("Hello, World!")
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func lex(s string) []string {
	tokens := make([]string, 0)
	i := 0
	for i < len(s) {
		err, isString, jsonString := lexString(s[i:])
		check(err)
		if isString {
			tokens = append(tokens, jsonString)
			i += len(jsonString) + 2
			continue
		}

		err, isNumber, jsonNumber := lexNumber(s[i:])
		check(err)
		if isNumber {
			tokens = append(tokens, (jsonNumber))
			i += len(jsonNumber)
			continue
		}

		err, isBool, jsonBool := lexBool(s[i:])
		check(err)
		if isBool {
			tokens = append(tokens, jsonBool)
			i += len(jsonBool)
			continue
		}

		err, isNull, jsonNull := lexNull(s[i:])
		check(err)
		if isNull {
			tokens = append(tokens, jsonNull)
			i += len(jsonNull)
			continue
		}

		if s[0] == SPACE || s[0] == CARRIAGE_RETURN || s[0] == NEWLINE || s[0] == TAB {
			i++
		} else if s[0] == CURLY_BRACKET_OPEN || s[0] == CURLY_BRACKET_CLOSE || s[0] == COMMA || s[0] == COLON {
			tokens = append(tokens, string(s[i]))
			i++
		}
	}
	return tokens
}

func lexString(s string) (error, bool, string) {
	jsonString := ""
	if s[0] == DOUBLE_QUOTE {
		s = s[1:]
	} else {
		return nil, false, s
	}
	for i := 0; i < len(s); i++ {
		if s[i] == DOUBLE_QUOTE {
			return nil, true, jsonString
		} else {
			jsonString += string(s[i])
		}
	}
	return errors.New("Expected end-of-string quote"), false, jsonString
}
