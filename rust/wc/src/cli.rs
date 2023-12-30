use clap::{command, Arg, ArgAction, ArgMatches};

pub fn parse_args() -> ArgMatches {
    command!()
        .arg(Arg::new("byte").short('c').action(ArgAction::SetTrue))
        .arg(Arg::new("line").short('l').action(ArgAction::SetTrue))
        .arg(Arg::new("word").short('w').action(ArgAction::SetTrue))
        .arg(Arg::new("character").short('m').action(ArgAction::SetTrue))
        .arg(Arg::new("file"))
        .get_matches()
}
