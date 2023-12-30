use std::collections::HashMap;

mod cli;
mod file_io;
mod text_processing;

fn main() -> std::io::Result<()> {
    let matches = cli::parse_args();

    if let Ok(buffer) = file_io::get_buffer(&matches) {
        let mut features: HashMap<&str, fn(&str)> = HashMap::new();
        features.insert("byte", text_processing::print_total_bytes);
        features.insert("line", text_processing::print_total_lines);
        features.insert("word", text_processing::print_total_words);
        features.insert("character", text_processing::print_total_characters);
        let mut flags = features.len();

        // If flags are provided
        for id in matches.ids() {
            if id.as_str() != "file" && matches.get_flag(id.as_str()) {
                (features.get(id.as_str()).unwrap())(&buffer);
                flags -= 1;
            }
        }

        // If no flags were passed
        if flags == features.len() {
            (features.get("line").unwrap())(&buffer);
            (features.get("word").unwrap())(&buffer);
            (features.get("byte").unwrap())(&buffer);
        }

        println!(
            "{}",
            matches.get_one::<String>("file").unwrap_or(&"".to_string())
        );
    }

    Ok(())
}
