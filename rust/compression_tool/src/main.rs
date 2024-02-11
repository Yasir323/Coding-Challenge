use clap::{arg, command, value_parser, ArgAction, Command, Arg, ArgMatches};
use std::collections::{HashMap, BinaryHeap};
use std::cmp::{min, Ordering, Reverse};
use std::fs::File;
use std::io::{BufReader, Read};
use unicode_segmentation::UnicodeSegmentation;

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

fn build_prefix_table_recursive<'a>(node: &'a HuffmanBaseNode, code: String, prefix_table: &mut HashMap<&'a str, String>) {
    match node {
        HuffmanBaseNode::Leaf(leaf) => {
            prefix_table.insert(&leaf.element, code);
        }
        HuffmanBaseNode::Internal(internal) => {
            build_prefix_table_recursive(&*internal.left, code.clone() + "0", prefix_table);
            build_prefix_table_recursive(&*internal.right, code + "1", prefix_table);
        }
    }
}

fn generate_prefix_table(tree: &HuffmanTree) -> HashMap<&str, String> {
    let mut prefix_table = HashMap::new();
    build_prefix_table_recursive(&tree.root, String::new(), &mut prefix_table);
    prefix_table
}

fn encode_text() {
    todo!()
}

fn write_encoded_tree_to_file() {
    todo!()
}

fn main() {
    let matches = command!()
        .arg(Arg::new("file"))
        .get_matches();
    let file_contents = read_text(matches).ok().unwrap();
    let char_count = find_freq(&file_contents);
    let huffman_tree = build_binary_tree(&char_count).unwrap();
    let huffman_codes = generate_prefix_table(&huffman_tree);
    println!("{:?}", huffman_codes);
}
