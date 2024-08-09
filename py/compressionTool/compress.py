import argparse
import json
import sys
from collections import Counter
from queue import PriorityQueue
import unittest

# Define a custom delimiter
DELIMITER = "|"


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


class TestCompression(unittest.TestCase):

    def test_compression_and_decompression(self):
        # original_text = "This is a test. Compression and decompression test."
        input_file = "test.txt"
        output_file = "test_output.bin"
        # with open(input_file, "w") as f:
        #     f.write(original_text)

        # Compress the test file
        sys.argv = ["", input_file, output_file]
        main()

        original_text = read_data_from_file(input_file)

        # Decompress the compressed file
        decompressed_text = decompress(output_file)

        # Compare the original text with the decompressed text
        self.assertEqual(original_text, decompressed_text)


def main():
    args = parse_commandline_arguments()
    data = read_data_from_file(args.input_file)
    if data:
        root = build_huffman_tree(data)
        huffman_codes = generate_huffman_codes(root)
        compressed_text, total_bits = compress_text(data, huffman_codes)
        generate_compressed_file(
            filename=args.output_file,
            header=huffman_codes,
            data=compressed_text,
            total_bits=total_bits
        )

    # Decompression
    # decompressed = decompress(args.output_file)
    # print(f"Decompressed String: {decompressed}")


def parse_commandline_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Name/path of the file to compress")
    parser.add_argument("output_file", help="Name/path of the output file")
    args = parser.parse_args()
    return args


def read_data_from_file(input_file):
    with open(input_file) as fp:
        data = fp.read()
    return data


def build_huffman_tree(text):
    char_frequency = Counter(text)
    priority_queue = PriorityQueue()

    for char, freq in char_frequency.items():
        node = HuffmanNode(char, freq)
        priority_queue.put(node)

    while priority_queue.qsize() > 1:
        left = priority_queue.get()
        right = priority_queue.get()

        parent_node = HuffmanNode(None, left.freq + right.freq)
        parent_node.left = left
        parent_node.right = right

        priority_queue.put(parent_node)

    return priority_queue.get()


def generate_huffman_codes(root, current_code="", huffman_codes=None):
    if huffman_codes is None:
        huffman_codes = {}

    if root is None:
        return huffman_codes

    if root.char:
        huffman_codes[root.char] = current_code
    generate_huffman_codes(root.left, current_code + "0", huffman_codes)
    generate_huffman_codes(root.right, current_code + "1", huffman_codes)

    return huffman_codes


def compress_text(text, huffman_codes):
    compressed_text = bytearray()
    current_byte = 0
    bits_written = 0
    total_bits = 0

    for char in text:
        code = huffman_codes[char]
        for bit in code:
            if bit == "1":
                current_byte |= (1 << (7 - bits_written))
            bits_written += 1

            if bits_written == 8:
                compressed_text.append(current_byte)
                current_byte = 0
                bits_written = 0
                total_bits += 8

    # Handle the case when there are remaining bits
    if bits_written > 0:
        compressed_text.append(current_byte)
        total_bits += bits_written

    return bytes(compressed_text), total_bits


def generate_compressed_file(filename, header, data, total_bits: int):
    with open(filename, "wb") as fp:
        header = json.dumps(header)
        fp.write(header.encode() + DELIMITER.encode() + total_bits.to_bytes(8, "big") + DELIMITER.encode())
        fp.write(data)


def decompress(file):
    with open(file, "rb") as fp:
        huffman_codes = get_huffman_codes_from_header(fp)
        root = build_huffman_tree_from_codes(huffman_codes)
        total_bits = get_total_bits(fp)
        text = extract_text(fp, root, total_bits)
    return text


def get_huffman_codes_from_header(fp):
    header = b""
    while True:
        byte = fp.read(1)
        if byte == DELIMITER.encode():
            break
        header += byte

    # Deserialize the Huffman codes from the header
    huffman_codes = json.loads(header.decode())
    print(huffman_codes)
    return huffman_codes


def build_huffman_tree_from_codes(huffman_codes):
    root = HuffmanNode(None, 0)  # Create a dummy root
    for char, code in huffman_codes.items():
        node = root
        for bit in code:
            if bit == "0":
                if node.left is None:
                    node.left = HuffmanNode(None, 0)
                node = node.left
            else:
                if node.right is None:
                    node.right = HuffmanNode(None, 0)
                node = node.right
        node.char = char
    return root


def get_total_bits(fp):
    header = fp.read(8)
    total_bits = int.from_bytes(header, 'big')
    fp.read(1)  # Delimiter
    # total_bits = int.from_bytes(header, 'big')
    print(total_bits)
    return total_bits


def extract_text(fp, root, total_bits):
    # TODO: last character is not being handled
    if not root:
        return ""

    current_node = root
    decompressed_text = ""
    bits_read = 0

    while True:
        byte = fp.read(1)
        if not byte:
            break

        for bit in byte[0].to_bytes(1, "big"):
            for i in range(8):
                if (bit & (1 << (7 - i))) > 0:
                    current_node = current_node.right
                else:
                    current_node = current_node.left

                if current_node.char:
                    decompressed_text += current_node.char
                    current_node = root
                bits_read += 1
                if bits_read >= total_bits:
                    break

    return decompressed_text


if __name__ == '__main__':
    unittest.main()
