use unicode_segmentation::UnicodeSegmentation;

pub fn print_total_bytes(buffer: &str) {
    print!(" {} ", buffer.as_bytes().len());
}

pub fn print_total_lines(buffer: &str) {
    print!(" {} ", buffer.lines().count());
}

pub fn print_total_words(buffer: &str) {
    print!(
        " {} ",
        buffer.lines().fold(0, |acc, x| acc
            + x.replace(&['\r', '\n', '\t'][..], " ")
                .split_whitespace()
                .collect::<Vec<&str>>()
                .len())
    );
}

pub fn print_total_characters(buffer: &str) {
    print!(" {} ", buffer.graphemes(true).collect::<Vec<&str>>().len());
}
