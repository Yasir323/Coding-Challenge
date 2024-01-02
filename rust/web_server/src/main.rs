use std::{
    fs,
    io::{prelude::*, BufReader},
    net::{TcpListener, TcpStream},
};
use web_server::ThreadPool;

fn main() {
    let listener = TcpListener::bind("127.0.0.1:7878").unwrap();
    let pool = ThreadPool::new(16);
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        pool.execute(|| {
            handle_connection(stream);
        });
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&mut stream);
    let htp_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();
    let request_line: Vec<&str> = htp_request.get(0).unwrap().split_whitespace().collect();
    let request_path = request_line[1];
    let (status_line, file_name) = if request_path == "/" || request_path == "/index.html" {
        ("HTTP/1.1 200 OK", "index.html")
    } else {
        ("HTTP/1.1 404 NOT FOUND", "404.html")
    };
    let content = fs::read_to_string(file_name).unwrap();
    let content_length = content.len();
    let response = format!("{status_line}\r\nContent-Length: {content_length}\r\n\r\n{content}");
    stream.write_all(response.as_bytes()).unwrap();
}
