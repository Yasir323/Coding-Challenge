package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"unicode/utf8"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func main() {
	args := os.Args[1:]
	stream, isFile := getStream(args)
	defer stream.Close()

	scanner := bufio.NewScanner(stream)
	var totalBytes int
	var totalLines int
	var totalWords int
	var totalChars int

	for scanner.Scan() {
		line := scanner.Text()
		totalBytes += len(line) + 1
		totalLines++
		totalWords += len(strings.Fields(line))
		totalChars += utf8.RuneCountInString(line) + 1
	}

	result := parseArgs(args, totalBytes, totalLines, totalWords, totalChars, isFile)

	fmt.Print(result)
}

func getStream(args []string) (*os.File, bool) {
	var stream *os.File
	isFile := false
	if len(args) == 0 {
		stream = os.Stdin
	} else {
		fp, err := os.Open(args[len(args)-1])
		if err != nil {
			stream = os.Stdin
		} else {
			stream = fp
			isFile = true
		}
	}

	return stream, isFile
}

func parseArgs(args []string, totalBytes int, totalLines int,
	totalWords int, totalChars int, isFile bool) string {
	result := "  "
	hasFlags := false
	for _, flag := range args {
		if flag == "-c" {
			result += fmt.Sprintf("%d ", totalBytes)
			hasFlags = true
		} else if flag == "-l" {
			result += fmt.Sprintf("%d ", totalLines)
			hasFlags = true
		} else if flag == "-w" {
			result += fmt.Sprintf("%d ", totalWords)
			hasFlags = true
		} else if flag == "-m" {
			result += fmt.Sprintf("%d ", totalChars)
			hasFlags = true
		}
	}
	if !hasFlags {
		result += fmt.Sprintf("%d %d %d ", totalLines, totalWords, totalBytes)
	}
	if isFile {
		result += fmt.Sprintf("%s", args[len(args)-1])
	}
	result += "\n"
	return result
}
