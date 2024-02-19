mod server;

pub async fn start_servers(ports: Vec<u16>) {
    // let tasks: Vec<Box<dyn Fn() -> _>> = ports
    //     .iter()
    //     .map(|port| {
    //         Create a boxed closure for each server start function
            // Box::new(move || server::start_server(*port))
        // })
        // .collect();
    // tokio::try_join!(tasks)
    //     .expect("ONe of the servers failed");
    let mut handles = Vec::with_capacity(ports.len());
    for port in ports {
        handles.push(tokio::spawn(server::start_server(port)));
    }
    for handle in handles {
        handle.await.unwrap().expect("TODO: panic message");
    }
}
