use load_balancer::start_servers;

#[tokio::main]
async fn main() {
    // Start 5 backend servers
    let ports: Vec<u16> = (8080..=8085).collect();
    tokio::spawn(start_servers(ports));

    // Start the load balancer
    // tokio::spawn(start_load_balancer);

    // Wait for 5 seconds
    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
}
