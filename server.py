import threading
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from connectionBD import DatabaseHandler
from scheduling import startConnection, createJob, schedule

load_dotenv(override=True)
app = Flask(__name__)
CORS(app)

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

dataBase.connect()
startConnection()


def schedule_pending_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule_thread = threading.Thread(target=schedule_pending_jobs)
schedule_thread.start()


@app.route('/', methods=['GET'])
def get_all_schedules():
    try:
        records = dataBase.select_all_from_table("schedules")
        formatted_records = [{'id': record[0], 'text': record[1],
                              'schedule_date': record[2], 'phone': record[3]} for record in records]
        if len(formatted_records) <= 0:
            return jsonify({"message": "No schedules found"}), 404
        return jsonify({"count": len(formatted_records), "schedules": formatted_records})
    except Exception as e:
        return jsonify({"error": f"Internal server error {e}"}), 500


@app.route('/all-schedules-valid', methods=['GET'])
def get_schedules_valid():
    try:
        records = dataBase.select_schedules_by_date("schedules")
        formatted_records = [{'id': record[0], 'text': record[1],
                              'schedule_date': record[2], 'phone': record[3]} for record in records]
        if len(formatted_records) <= 0:
            return jsonify({"message": "No schedules found"}), 404
        return jsonify({"count": len(formatted_records), "schedules": formatted_records})
    except Exception as e:
        return jsonify({"error": f"Internal server error {e}"}), 500


@app.route('/create-schedule', methods=['POST'])
def create_schedule():
    data = request.json
    try:
        new_id = dataBase.insert_row(
            "schedules", (data['text'], data['schedule_date'], data['phone']))
        createJob(data['text'], data['schedule_date'], data['phone'])
        return jsonify({"id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/update-schedule/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    try:
        dataBase.update_row("schedules", "text",
                            data['text'], "id", schedule_id)
        dataBase.update_row("schedules", "schedule_date",
                            data['schedule_date'], "id", schedule_id)
        dataBase.update_row("schedules", "phone",
                            data['phone'], "id", schedule_id)
        return jsonify({"message": "Schedule updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete-schedule/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        dataBase.delete_row("schedules", "id", schedule_id)
        return jsonify({"message": "Schedule deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
