use std::{
    sync::{mpsc, Arc, Mutex},
    thread,
};

type Job = Box<dyn FnOnce() + Send + 'static>;

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            // The call to recv() is blocking
            let message = receiver.lock().unwrap().recv();
            match message {
                Ok(job) => {
                    // println!("Worker-{id} handling the request...");
                    job();
                }
                Err(_) => {
                    println!("Worker-{id} disconnected; shutting down.");
                    break;
                }
            }
        });
        Worker {
            id,
            thread: Some(thread),
        }
    }
}

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}

impl ThreadPool {
    /// Create a new ThreadPool.
    ///
    /// Tpool_sizehe  is the number of workers in the pool.
    ///
    /// # Panics
    ///
    /// The `new` function will panic if the pool_size is zero.
    pub fn new(pool_size: usize) -> ThreadPool {
        assert!(pool_size > 0);
        let (sender, receiver) = mpsc::channel();
        // Since mpsc should have only one comsumer, we have to use reference counting and a lock at the
        // receiving end so that multiple threads can listen to incoming requests in this channel
        let receiver = Arc::new(Mutex::new(receiver));
        let mut workers = Vec::with_capacity(pool_size);
        for id in 0..pool_size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }
        ThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        // Put the job in the channel
        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        // Dropping sender closes the channel which indicates no more requests will have to be handled
        drop(self.sender.take());
        // After dropping the sender, all calls to recv will return an error instead of blocking the threads

        for worker in &mut self.workers {
            println!("Shutting down worker-{}", worker.id);
            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}
