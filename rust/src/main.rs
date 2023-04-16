use std::task::Poll;
use canvasapi::canvas::CanvasInformation;
use canvasapi::models::course;
use canvasapi::prelude::{Canvas, Course};
use config::Config;

#[tokio::main]
async fn main() {
    println!("Hello, world!");

    let secret = Config::builder()
        .add_source(config::File::with_name("secret.config"))
        .build().expect("No Secret Config File given");
    //
    // let base_url: std::string = secret.get("base_url")
    //     .expect("No Base URL in Secret Config");
    //
    // let canvas_token = String::from(secret.get("canvas_token")
    //     .expect("No Canvas Token in Secret Config"));


    let base_url = "https://canvas.ewu.edu/";

    let canvas_token = "10~Wo5rqgrPaBV9v21Bz08jmR9cBLyUfIWUhrVDcBeJlrAspseq5b6mzBndfhdnd53C";

    let canvas = CanvasInformation::new(base_url, canvas_token);

    let course = Canvas::get_course(secret.get("course_id")
        .expect("No Course ID Given in Secret Config"))
        .expect("Unable to setup Course Fetch")
        .fetch(&canvas).await
        .expect("Unable to get Course")
        .inner();

    let assignment = course.get_assignment(
        secret.get("assignment_id")
            .expect("no assignment"))
        .expect("No Assignment")
        .fetch(&canvas).await.expect("unable").inner();

    let a_name = assignment.name.expect("no name");
    let a_due = assignment.due_at.expect("no due");

    println!("Assignment Name: {a_name}, Due: {a_due}");

}
