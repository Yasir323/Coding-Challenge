use clap::{command, Arg};
use std::fs::File;
use std::io::{self, prelude::*, BufReader};

fn main() -> io::Result<()>{
    let matches = command!()
        .arg(Arg::new("file"))
        .get_matches();
    let file = matches.get_one::<String>("file").unwrap();
    let file_handle = File::open(file)?;
    let reader = BufReader::new(file_handle);
    let index = 2;
    for line in reader.lines() {
        println!("{}", line.unwrap().split(",").nth(index).unwrap());
    }
    Ok(())
}
