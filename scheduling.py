import os
import schedule
from connectionBD import DatabaseHandler
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pytz import timezone
import time

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


def startConnection():
    print("Starting connection")
    dataBase.connect()
    schedules_data = dataBase.select_all_from_table("schedules")
    if schedules_data:
        for data in schedules_data:
            id, task, schedule_date, phone = data
            scheduleJob(id, schedule_date, task, phone)


def scheduleJob(id, date, task, phone):
    dateNow = datetime.now().astimezone(timezone("UTC"))
    date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f%z")
    print(date >= dateNow)
    if date >= dateNow:
        difference = (date - dateNow).total_seconds()
        job = schedule.every(difference).seconds.do(
            executeJob, id, task, phone)
        jobs[id] = job
        print("agendado", task, phone)


def executeJob(id, task, phone):
    print("Job executed", task,  phone)
    schedule.cancel_job(jobs[id])
    del jobs[id]


def createJob(text: str, schedule_date: datetime, phone: str):
    id = dataBase.insert_row("schedules", (text, schedule_date, phone))
    scheduleJob(id, schedule_date, text, phone)
