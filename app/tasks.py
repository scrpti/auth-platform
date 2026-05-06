import time 
from app.core.celery_app import celery_app

@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str, full_name: str):
    time.sleep(2) #Simulation of sending a email
    print(f"Welcome email sent to {email}")
    return {
        "status": "sent", 
        "email": email
            }

@celery_app.task(name="generate_report")
def generate_report(user_id: str):
    time.sleep(5) #Simulation of a costly report
    print(f"Report generated to user {user_id}")
    return {
        "status": "completed",
        "user_id": user_id
    }

