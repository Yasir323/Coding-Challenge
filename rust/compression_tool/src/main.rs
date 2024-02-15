use clap::{command, Arg, ArgMatches};
use std::collections::{HashMap, BinaryHeap};
use std::cmp::{ Ordering, Reverse};
use bitstream_io::{BitRead, BitReader, BitWrite, BitWriter};
use std::fs::File;
use std::io::{BufReader, BufWriter, Read, Write};
use unicode_segmentation::UnicodeSegmentation;
use serde_json;

fn read_text(matches: ArgMatches) -> std::io::Result<String> {
    let file_path = matches.get_one::<String>("file").unwrap();
    let file = File::open(file_path).expect("File not found!");
    let mut buf_reader = BufReader::new(file);
    let mut contents = String::new();
    buf_reader.read_to_string(&mut contents)?;
    Ok(contents)
}

fn find_freq(text: &str) -> HashMap<&str, usize>{
    let mut map: HashMap<&str, usize> = HashMap::new();
    let graphemes: Vec<&str> = text.graphemes(true).collect();
    for grapheme in graphemes {
        map.entry(grapheme).and_modify(|count| *count += 1).or_insert(1);
    }
    map
}

enum HuffmanBaseNode {
    Leaf(HuffmanLeafNode),
    Internal(HuffmanInternalNode),
}

struct HuffmanLeafNode {
    element: String,
    weight: usize,
}

struct HuffmanInternalNode {
    weight: usize,
    left: Box<HuffmanBaseNode>,
    right: Box<HuffmanBaseNode>
}

impl HuffmanLeafNode {
    fn new(element: String, weight: usize) -> Self {
        HuffmanLeafNode {
            element,
            weight
        }
    }

    fn weight(&self) -> usize {
        self.weight
    }
}

impl HuffmanInternalNode {
    fn new(weight: usize, left: Box<HuffmanBaseNode>, right: Box<HuffmanBaseNode>) -> Self {
        HuffmanInternalNode {
            weight,
            left,
            right,
        }
    }

    fn weight(&self) -> usize {
        self.weight
    }
}

struct HuffmanTree {
    root: HuffmanBaseNode,
}

impl HuffmanTree {
    fn new(node: HuffmanBaseNode) -> Self {
        HuffmanTree { root: node }
    }

    fn weight(&self) -> usize {
        match &self.root {
            HuffmanBaseNode::Leaf(leaf) => leaf.weight(),
            HuffmanBaseNode::Internal(internal) => internal.weight(),
        }
    }
}

impl Eq for HuffmanTree {}

impl PartialEq<Self> for HuffmanTree {
    fn eq(&self, other: &Self) -> bool {
        self.weight() == other.weight()
    }
}

impl PartialOrd<Self> for HuffmanTree {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for HuffmanTree {
    fn cmp(&self, other: &Self) -> Ordering {
        self.weight().cmp(&other.weight())
    }
}

fn build_binary_tree(character_weight: &HashMap<&str, usize>) -> Option<HuffmanTree> {
    let mut min_heap: BinaryHeap<Reverse<HuffmanTree>> = BinaryHeap::from(character_weight.iter().map(|(&element, &weight)| {
        Reverse(HuffmanTree::new(HuffmanBaseNode::Leaf(HuffmanLeafNode::new(element.to_owned(), weight))))
    }).collect::<Vec<_>>());

    while min_heap.len() > 1 {
        let t1 = min_heap.pop().unwrap().0;
        let t2 = min_heap.pop().unwrap().0;
        let new_tree = HuffmanTree::new(HuffmanBaseNode::Internal(
            HuffmanInternalNode::new(t1.weight() + t2.weight(), Box::new(t1.root), Box::new(t2.root))
        ));
        min_heap.push(Reverse(new_tree));
    }

    min_heap.pop().map(|x| x.0)
}

fn build_prefix_table_recursive(node: &HuffmanBaseNode, code: String, prefix_table: &mut HashMap<String, String>) {
    match node {
        HuffmanBaseNode::Leaf(leaf) => {
            prefix_table.insert(leaf.element.to_string(), code);
        }
        HuffmanBaseNode::Internal(internal) => {
            build_prefix_table_recursive(&*internal.left, code.clone() + "0", prefix_table);
            build_prefix_table_recursive(&*internal.right, code + "1", prefix_table);
        }
    }
}

fn generate_prefix_table(tree: &HuffmanTree) -> HashMap<String, String> {
    let mut prefix_table: HashMap<String, String> = HashMap::new();
    build_prefix_table_recursive(&tree.root, String::new(), &mut prefix_table);
    prefix_table
}

fn encode_text(text: &str, code: &HashMap<String, String>) -> (Vec<u8>, usize) {
    let graphemes: Vec<&str> = text.graphemes(true).collect();
    let mut bit_writer: BitWriter<Vec<u8>, bitstream_io::LittleEndian> = BitWriter::new(Vec::new());
    let mut size = 0;
    for grapheme in graphemes {
        if let Some(code) = code.get(grapheme) {
            for bit in code.chars() {
                let bit_value = bit.to_digit(2).unwrap() != 0;
                bit_writer.write_bit(bit_value).unwrap();
                size += 1;
            }
        }
    }
    bit_writer.byte_align().unwrap();
    bit_writer.flush().unwrap();
    (bit_writer.into_writer(), size)
}

fn write_compressed_file(out_file: &str, code: &HashMap<String, String>, encoded_text_bits: &[u8]) -> std::io::Result<()> {
    let code_serialized = serde_json::to_string(code);
    let separator = b"\n---\n";
    let compressed_data: Vec<u8> = [
        code_serialized.unwrap().as_bytes(),
        separator,
        encoded_text_bits,
    ].concat();
    write_to_file(out_file, &compressed_data)
}

fn write_to_file(out_file: &str, data: &Vec<u8>) -> std::io::Result<()> {
    let file = File::create(out_file)?;
    let mut buf_writer = BufWriter::new(file);
    buf_writer.write_all(data)?;
    Ok(())
}

fn read_from_file(file_path: &str) -> std::io::Result<Vec<u8>> {
    let file = File::open(file_path)?;
    let mut buf_reader = BufReader::new(file);
    let mut content = Vec::new();
    buf_reader.read_to_end(&mut content)?;
    Ok(content)
}

fn read_compressed_file(file_path: &str) -> std::io::Result<(String, Vec<u8>)> {
    let compressed_data = read_from_file(file_path)?;
    let separator = b"\n---\n";
    if let Some(sep_index) = compressed_data.windows(separator.len()).position(|w| w == separator) {
        let huffman_codes_json = String::from_utf8_lossy(&compressed_data[..sep_index]).trim().to_string();
        let encoded_text_bits = compressed_data[sep_index + separator.len()..].to_vec();
        Ok((huffman_codes_json, encoded_text_bits))
    } else {
        Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Sepearator not found in the compressed file.",
        ))
    }
}

fn reverse_map<K, V>(original: &HashMap<K, V>) -> HashMap<V, K>
    where
        K: Clone + Eq + std::hash::Hash,
        V: Clone + Eq + std::hash::Hash,
{
    let mut reversed = HashMap::new();

    for (key, value) in original.iter() {
        reversed.insert(value.clone(), key.clone());
    }

    reversed
}

fn decode_bits_to_text(encoded_text_bits: &[u8], huffman_codes: &HashMap<String, String>, size: &usize) -> String {
    let mut decoded_text = String::new();
    let mut current_code = String::new();
    let mut bit_reader: BitReader<&[u8], bitstream_io::LittleEndian> = BitReader::new(encoded_text_bits);
    let mut bit_read = 0;
    while let Ok(bit) = bit_reader.read_bit() {
        // Since last byte is probably padded, we need to read to the exact size
        if bit_read == *size {
            break;
        }
        let bit_val = if bit == false {0} else {1};
        bit_read += 1;
        current_code.push_str(&bit_val.to_string());
        // println!("{}", current_code);
        if let Some(character) = huffman_codes.get(&current_code) {
            // print!("{}: {}", current_code, character);
            decoded_text.push_str(character);
            current_code.clear();
        }
    }

    // println!("{}", current_code);
    decoded_text
}


fn main() -> std::io::Result<()> {
    let matches = command!()
        .arg(Arg::new("file"))
        .get_matches();
    let file_contents = read_text(matches).ok().unwrap();

    // Compression
    let char_count = find_freq(&file_contents);
    let huffman_tree = build_binary_tree(&char_count).unwrap();
    let huffman_codes : HashMap<String, String>= generate_prefix_table(&huffman_tree);
    // println!("{:?}", huffman_codes);
    let (encoded_text_bits , size)= encode_text(&file_contents, &huffman_codes);
    let out_file = "compressed_file.bin";
    write_compressed_file(out_file, &huffman_codes, &encoded_text_bits)?;

    // Decompression
    let (huffman_codes_json, encoded_text_bits) = read_compressed_file(out_file)?;
    // println!("{:?}", huffman_codes);
    let huffman_codes: HashMap<String, String> = serde_json::from_str(&huffman_codes_json)?;
    let reverse_mapping = reverse_map(&huffman_codes);
    let decoded_text = decode_bits_to_text(&encoded_text_bits, &reverse_mapping, &size);
    // println!("Decoded Text: {}", decoded_text);
    assert_eq!(file_contents, decoded_text);
    Ok(())
}
