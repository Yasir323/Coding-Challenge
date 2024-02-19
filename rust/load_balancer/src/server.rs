use actix_web::{get, App, HttpServer, Responder};

#[get("/")]
async fn greet() -> impl Responder {
    "Hello".to_string()
}

pub async fn start_server(port: u16) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let _server = HttpServer::new(|| {
        App::new().service(greet)
    })
    .bind(("127.0.0.1", port))
    .expect("Could not start server!")
    .run()
    .await
    .expect("Server closed!");

    Ok(())
}
