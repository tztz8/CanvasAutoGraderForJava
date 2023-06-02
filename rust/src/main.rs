use canvasapi::canvas::CanvasInformation;
use canvasapi::prelude::{Canvas};
use config::Config;

#[tokio::main]
async fn main() {
    println!("Hello, world!");

    let secret = Config::builder()
        .add_source(config::File::with_name("secret.config"))
        .build().expect("No Secret Config File given");

    let base_url:String = secret.get("base_url")
        .expect("no base url in Secret Config");

    let canvas_token:String = secret.get("canvas_token")
        .expect("no canvas_token in Secret Config");

    let canvas = CanvasInformation::new(&base_url, &canvas_token);

    let course = Canvas::get_course(secret.get("course_id")
        .expect("No Course ID Given in Secret Config"))
        .expect("Unable to setup Course Fetch")
        .fetch(&canvas).await
        .expect("Unable to get Course")
        .inner();

    let assignment = course.get_assignment(
        secret.get("assignment_id")
            .expect("no assignment in Secret Config"))
        .expect("No Assignment in course")
        .fetch(&canvas).await.expect("unable").inner();

    let submissions = assignment.get_submissions()
        .expect("No submissions")
        .fetch(&canvas).await.expect("unable").inner();

    let users = course.get_users()
        .expect("get users")
        .fetch(&canvas).await.expect("unable").inner();

    for user in users {
        let user_name = user.name.expect("no name");
        let user_id = user.id;
        let mut s_grade = String::from("no grade");
        for submission in &submissions {
            if submission.user_id.expect("no id") == user_id {
                s_grade = submission.grade.clone().expect("no grade");
                break;
            }
        }
        println!("Found {user_name}, ID: {user_id}, Grade: {s_grade}");
    }

    let a_name = assignment.name.expect("no name");
    let a_due = assignment.due_at.expect("no due");

    println!("Assignment Name: {a_name}, Due: {a_due}");

}
