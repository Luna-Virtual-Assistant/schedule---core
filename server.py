import threading
import pytz
import datetime
import os
import time
from flask import Flask, jsonify, request, Blueprint, make_response
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from dotenv import load_dotenv
from connectionBD import DatabaseHandler
from scheduling import startConnection, createJob, schedule

load_dotenv(override=True)
app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
CORS(app)

api = Api(blueprint, title='API schedule', version='1.0', description='API schedule')
app.register_blueprint(blueprint)

BD_USER = os.getenv("BD_USER")
BD_PASSWORD = os.getenv("BD_PASSWORD")
BD_HOST = os.getenv("BD_HOST")
BD_PORT = os.getenv("BD_PORT")
BD_NAME = os.getenv("BD_NAME")
TOKEN = os.getenv("TOKEN")

dataBase = DatabaseHandler(
    user=BD_USER,
    password=BD_PASSWORD,
    host=BD_HOST,
    port=BD_PORT,
    database=BD_NAME
)

dataBase.connect()
startConnection()

schedule_model = api.model('Schedule', {
    'text': fields.String(required=True, description='The schedule text'),
    'schedule_date': fields.String(required=True, description='The schedule date'),
    'sessionName': fields.String(required=True, description='The session name')
})

schedule_update_model = api.model('ScheduleUpdate', {
    'text': fields.String(required=True, description='The schedule text'),
    'schedule_date': fields.String(required=True, description='The schedule date'),
    'sessionName': fields.String(required=True, description='The session name')
})

def schedule_pending_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_thread = threading.Thread(target=schedule_pending_jobs)
schedule_thread.start()

def get_token():
    token = request.args.get('token')
    if not token:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)
    if token != TOKEN:
        return make_response(jsonify({'error': 'Forbidden'}), 403)

@app.before_request
def before_request_handler():
    if request.path.startswith('/api-docs') or request.path.startswith('/swaggerui') or request.path == '/api/swagger.json':
        return
    response = get_token()
    if response is not None:
        return response

@api.route('/schedules')
class ScheduleListCreate(Resource):
    @api.doc(params={'token': 'Token for authentication'})
    def get(self):
        try:
            records = dataBase.select_all_from_table("schedules")
            formatted_records = [{'id': record[0], 'text': record[1],
                                  'schedule_date': record[2], 'sessionName': record[3]} for record in records]
            if len(formatted_records) <= 0:
                return make_response(jsonify({"message": "No schedules found"}), 404)
            return make_response(jsonify({"count": len(formatted_records), "schedules": formatted_records}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Internal server error {e}"}), 500)
        
    @api.expect(schedule_model, validate=True)
    @api.doc(params={'token': 'Token for authentication'})
    def post(self):
        data = request.json
        current_date = datetime.datetime.strptime(data['schedule_date'], '%Y-%m-%d %H:%M:%S.%f%z')
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if current_date < now_utc:
            return make_response(jsonify({"error": "Invalid date"}), 400)    
        try:
            new_id = createJob(data['text'], data['schedule_date'], data['sessionName'])
            return make_response(jsonify({"id": new_id}), 201)
        except Exception as e:
            print(e)
            return make_response(jsonify({"error": str(e)}), 500)
@api.route('/schedules/valid')
class ValidScheduleList(Resource):
    @api.doc(params={'token': 'Token for authentication'})
    def get(self):
        try:
            records = dataBase.select_schedules_by_date("schedules")
            formatted_records = [{'id': record[0], 'text': record[1],
                                  'schedule_date': record[2], 'sessionName': record[3]} for record in records]
            if len(formatted_records) <= 0:
                return make_response(jsonify({"message": "No schedules found"}), 404)
            return make_response(jsonify({"count": len(formatted_records), "schedules": formatted_records}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Internal server error {e}"}), 500)

@api.route('/schedules/<int:schedule_id>')
@api.param('schedule_id', 'The schedule identifier')
class ScheduleUpdateDelete(Resource):
    @api.expect(schedule_update_model, validate=True)
    @api.doc(params={'token': 'Token for authentication'})
    def put(self, schedule_id):
        data = request.json
        try:
            dataBase.update_row("schedules", "text", data['text'], "id", schedule_id)
            dataBase.update_row("schedules", "schedule_date", data['schedule_date'], "id", schedule_id)
            dataBase.update_row("schedules", "sessionName", data['sessionName'], "id", schedule_id)
            return make_response(jsonify({"message": "Schedule updated successfully"}), 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

    @api.doc(params={'token': 'Token for authentication'})
    def delete(self, schedule_id):
        try:
            dataBase.delete_row("schedules", "id", schedule_id)
            return make_response(jsonify({"message": "Schedule deleted successfully"}), 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=False)