use clap::{command, Arg, ArgAction, ArgMatches};
use std::{fs::File, io::Read};

struct Feature<'a, 'b> {
    flag: &'a str,
    handler: fn(&'b str),
}

enum Input {
    Stdin,
    File(File),
}

fn main() -> std::io::Result<()> {
    let args = parse_args();
    if let Ok(buffer) = get_buffer(&args) {
        let features = vec![
            Feature {
                flag: "byte",
                handler: print_total_bytes,
            },
            Feature {
                flag: "line",
                handler: print_total_lines,
            },
            Feature {
                flag: "word",
                handler: print_total_words,
            },
            Feature {
                flag: "charcter",
                handler: print_total_characters,
            },
        ];
        for feature in features {
            if args.get_flag(feature.flag) {
                (feature.handler)(&buffer);
            }
        }
    }

    Ok(())

    // todo!("no flag: -clw");
    // todo!("read from stdin");
}

fn parse_args() -> ArgMatches {
    command!()
        .arg(Arg::new("byte").short('c').action(ArgAction::SetTrue))
        .arg(Arg::new("line").short('l').action(ArgAction::SetTrue))
        .arg(Arg::new("word").short('w').action(ArgAction::SetTrue))
        .arg(Arg::new("character").short('m').action(ArgAction::SetTrue))
        .arg(Arg::new("file"))
        .get_matches()
    // let file_name: &str = args.get_one::<String>("file").unwrap();
}

fn get_buffer(args: &ArgMatches) -> std::io::Result<String> {
    let file_name: &str = args
        .get_one::<String>("file")
        .expect("File not provided, trying to read from standard input.");
    let input_stream: Input;
    if !file_name.is_empty() {
        // Try to open the file and handle errors
        let file = File::open(&file_name)?;
        input_stream = Input::File(file);
    } else {
        input_stream = Input::Stdin;
    }

    let mut buffer = String::new();

    match input_stream {
        Input::Stdin => {
            std::io::stdin().read_to_string(&mut buffer)?;
        }
        Input::File(mut file) => {
            // file.take(1024).read_to_string(&mut buffer)?;
            file.read_to_string(&mut buffer)?;
        }
    }
    Ok(buffer)
}

fn print_total_bytes(buffer: &str) {}
fn print_total_lines(buffer: &str) {}
fn print_total_words(buffer: &str) {}
fn print_total_characters(buffer: &str) {}
