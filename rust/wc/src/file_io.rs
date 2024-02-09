use clap::ArgMatches;
use std::fs::File;
use std::io::{BufReader, Read};

pub enum Input {
    Stdin,
    File(File),
}

pub fn get_buffer(args: &ArgMatches) -> std::io::Result<String> {
    let file_name: &str = args.get_one("file").map_or("", |s: &String| s.as_str());

    let input_stream: Input = if !file_name.is_empty() {
        // Try to open the file and handle errors
        let file = File::open(&file_name).expect("File not found");
        Input::File(file)
    } else {
        Input::Stdin
    };

    let mut buffer = String::new();
    match input_stream {
        Input::Stdin => {
            // There is a bug here, if we do not provide data from stdin via pipe, the
            // program will get stuck here indefinitely to read from this blocking stream
            let mut reader = BufReader::new(std::io::stdin());
            reader.read_to_string(&mut buffer)?;
        }
        Input::File(file) => {
            let mut reader = BufReader::new(file);
            reader.read_to_string(&mut buffer)?;
        }
    }
    Ok(buffer)
}
