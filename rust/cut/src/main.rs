use clap::{command, Arg, ArgMatches};
use std::fs::File;
use std::io::{self, prelude::*, BufReader};

enum Stream {
    File(File),
    Stdin,
}

fn main() -> io::Result<()> {
    let matches: ArgMatches = get_args();
    let file_name: String = matches.get_one::<String>("file").map(|s| s.to_owned()).unwrap();
    let delimiter: String = matches.get_one::<String>("delimiter").map(|s| s.to_owned()).unwrap();
    // let fields: Vec<usize> = matches.get_one::<Vec<usize>>("fields").map_or(vec!(usize::MAX), |s| s.to_owned());
    let reader = get_reader(file_name.as_str());
    if let Some(fields) = matches.get_one::<String>("fields") {
        println!("{:?}", fields);
        let mut sorted_fields: Vec<usize> = fields
            .split(&[',', ' '][..])
            .filter_map(|s| s.parse().ok())
            .collect();
        sorted_fields.sort();
        for line in reader.lines() {
            let line = line?;
            let filtered_line: Vec<&str> = line
                .split(delimiter.as_str())
                .enumerate()
                .filter_map(|(col_index, value)| {
                    sorted_fields.binary_search(&col_index).ok().map(|_| value)
                })
                .collect();

            println!("{}", filtered_line.join(delimiter.as_str()));
        }
    } else {
        for line in reader.lines() {
            println!("{}", line?);
        }
    }

    Ok(())
}

fn get_args() -> ArgMatches {
    let matches = command!()
        .arg(Arg::new("file").default_value(""))
        // .arg(Arg::new("fields").short('f').long("fields").value_delimiter(',').action(ArgAction::Append))
        .arg(Arg::new("fields").short('f').long("fields"))
        .arg(Arg::new("delimiter").short('d').long("delimiter").default_value(","))
        .get_matches();
    matches
}

fn get_reader(file_name: &str) -> BufReader<Box<dyn Read>> {
    let input_stream: Stream = if !file_name.is_empty() {
        match File::open(file_name) {
            Ok(file) => Stream::File(file),
            Err(err) => {
                eprintln!("Error opening file: {}", err);
                std::process::exit(1);
            }
        }
    } else {
        Stream::Stdin
    };

    match input_stream {
        Stream::Stdin => BufReader::new(Box::new(io::stdin())),
        Stream::File(file) => BufReader::new(Box::new(file)),
    }
}
