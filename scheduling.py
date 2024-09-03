import os
import schedule
from connectionBD import DatabaseHandler
from datetime import datetime
from dotenv import load_dotenv
from pytz import timezone
from mqtt_publisher.publisher import publish

load_dotenv(override=True)

BD_USER = os.getenv("BD_USER")
BD_PASSWORD = os.getenv("BD_PASSWORD")
BD_HOST = os.getenv("BD_HOST")
BD_PORT = os.getenv("BD_PORT")
BD_NAME = os.getenv("BD_NAME")

dataBase = DatabaseHandler(
    user=BD_USER,
    password=BD_PASSWORD,
    host=BD_HOST,
    port=BD_PORT,
    database=BD_NAME
)

jobs = {}
dataBase.create_table()

def startConnection():
    dataBase.connect()
    schedules_data = dataBase.select_schedules_by_date("schedules")
    if schedules_data:
        for data in schedules_data:
            id, task, schedule_date, sessionName = data
            scheduleJob(id, str(schedule_date), task, sessionName)


def scheduleJob(id, date, task, sessionName):
    dateNow = datetime.now().astimezone(timezone("UTC"))
    date = datetime.fromisoformat(date)
    if date >= dateNow:
        difference = (date - dateNow).total_seconds()
        job = schedule.every(difference).seconds.do(
            executeJob, id, task, sessionName)
        jobs[id] = job


def executeJob(id, task, sessionName):
    publish(task)
    print(f"Executing task: {task} for session: {sessionName}")
    schedule.cancel_job(jobs[id])
    del jobs[id]


def createJob(text: str, schedule_date: datetime, sessionName: str):
    id = dataBase.insert_row("schedules", (text, schedule_date, sessionName))
    scheduleJob(id, str(schedule_date), text, sessionName)
    return id

def updatejob(schedule_id: int):
    schedule = dataBase.select_schedule_by_id(schedule_id, "schedules")
    if schedule:
        id, task, schedule_date, sessionName = schedule
        if id in jobs:
            schedule.cancel_job(jobs[id])
            del jobs[id]
        scheduleJob(id, str(schedule_date), task, sessionName)