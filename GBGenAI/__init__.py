from flask import redirect, request
from flask.app import Flask
from flask.config import Config
from flask.json import jsonify, JSONEncoder, JSONDecoder
from enum import Enum
from typing_extensions import Dict, AnyStr
from backend import Schedular, Job, Priority, jobFamily
from GBGenAI.QueryProcessor import execute_query, simplified_nlidb, convert_nl_to_sql
from uuid import UUID
from flask_uuid import FlaskUUID


#TODO: Implement All Status Code in Status Class
class Status(Enum):
    STATUS_METHOD_NOT_ALLOWED:Enum = 405
    STATUS_CODE_NOT_IMPLEMENTED:Enum = 501
    STATUS_CODE_OK:Enum = 200
    STATUS_BAD_REQUEST:Enum = 400
    STATUS_QUERY_OK:Enum = 200
    STATUS_INTERNAL_SERVER_ERROR:Enum = 503
    STATUS_JOB_NOT_FOUND:Enum = 404

app = Flask(__name__)
FlaskUUID(app)
schedular = Schedular()


@app.errorhandler(405)
def method_not_allowed(e):
    """Returns JSON Error For Error Code 405 (i.e. Method Not Allowed)"""
    return jsonify(
        {
            'status': Status.STATUS_METHOD_NOT_ALLOWED.name,
            'code': Status.STATUS_METHOD_NOT_ALLOWED.value
        }
    ), Status.STATUS_CODE_NOT_IMPLEMENTED.value

@app.route('/')
def home_url():
    return jsonify(
        {
            'status': Status.STATUS_CODE_NOT_IMPLEMENTED.name,
            'code': Status.STATUS_CODE_NOT_IMPLEMENTED.value
        }
    ), Status.STATUS_CODE_NOT_IMPLEMENTED.value

@app.route('/query', methods=['POST'])
def query():
    
    request_details:Dict = request.get_json()
    request_status:Status = Status.STATUS_CODE_OK
    request_message:AnyStr = ''
    job_id = ''
    job_type = ''

    if ('query' not in request_details):
        request_status = Status.STATUS_BAD_REQUEST
        request_message = "field `query` is missing."
    else:
        query = request_details['query']
        print(query)
        request_message = 'your request has been submitted'
        request_status = Status.STATUS_CODE_OK
        job = Job(data=query, job_function=simplified_nlidb)
        job.remarks = 'execution_job'
        job_type = job.remarks
        job_id = job.schedule_job(schedular=schedular, priority_level=Priority.PRIORITY_HIGH)
        print("Scheduled Job {}".format(job_id))

    return jsonify(
        {
            'status': request_status.name,
            'code': request_status.value,
            'message': request_message,
            'job_id': job_id,
            'job_type': job_type
        }
    ), request_status.value

@app.route('/get-status/<uuid:job_id>')
def get_status(job_id):
    status = Status.STATUS_CODE_OK
    message = 'Query Ok'
    job_status = 'Not Started'
    print(job_id)
    try:
        # job_id = UUID(job_id)
        print(jobFamily)
        if job_id not in jobFamily:
            status = Status.STATUS_JOB_NOT_FOUND
            message = 'Your job is not in Job Family maybe in Processing?'
        else:
            job:Job = jobFamily[job_id]
            job_status = 'started' if job.started else job_status
            job_status = 'running' if job.running else job_status
            job_status = 'finished' if job.finished else job_status
    
    except Exception as e:
        print(e)
        status = Status.STATUS_INTERNAL_SERVER_ERROR
        message = 'Internal Server Error'
        job_status = 'Error'


    return jsonify(
        {
            'status': status.name,
            'code': status.value,
            'message': message,
            'job_status': job_status
        }
    ), status.value


@app.route('/get-results/<uuid:job_id>')
def get_results(job_id:UUID):
    status = Status.STATUS_CODE_OK
    message = 'Query Ok'
    job_status = 'Not Started'
    results = []
    print(job_id)
    try:
        # job_id = UUID(job_id)
        print(jobFamily)
        if job_id not in jobFamily:
            status = Status.STATUS_JOB_NOT_FOUND
            message = 'Your job is not in Job Family maybe in Processing?'
        else:
            job:Job = jobFamily[job_id]
            job_status = 'started' if job.started else job_status
            job_status = 'running' if job.running else job_status
            job_status = 'finished' if job.finished else job_status
            if (job.finished and job.remarks != 'explain_job'):
                results = job.results[0]
            else:
                results = job.results[1]
    
    except Exception as e:
        print(e)
        status = Status.STATUS_INTERNAL_SERVER_ERROR
        message = 'Internal Server Error'
        job_status = 'Error'
        
    #TODO: Implement Status

    return jsonify(
        {
            'status': status.name,
            'code': status.value,
            'message': message,
            'job_status': job_status,
            'results': results
        }
    ), status.value


@app.route('/validate', methods=['POST'])
def validate():

    request_details:Dict = request.get_json()
    request_status:Status = Status.STATUS_CODE_OK
    request_message:AnyStr = ''
    job_id = ''
    job_type = ''

    if ('query' not in request_details):
        request_status = Status.STATUS_BAD_REQUEST
        request_message = "field `query` is missing."
    else:
        query = request_details['query']
        print(query)
        request_message = 'your request has been submitted'
        request_status = Status.STATUS_CODE_OK
        job = Job(data=query, job_function=convert_nl_to_sql)
        job.remarks = 'query_job'
        job_type = job.remarks
        job_id = job.schedule_job(schedular=schedular, priority_level=Priority.PRIORITY_HIGH)
        print("Scheduled Job {}".format(job_id))

    return jsonify(
        {
            'status': request_status.name,
            'code': request_status.value,
            'message': request_message,
            'job_id': job_id,
            'job_type': job_type
        }
    ), request_status.value

@app.route('/explain', methods=['POST'])
def explain():
    request_details:Dict = request.get_json()
    request_status:Status = Status.STATUS_CODE_OK
    request_message:AnyStr = ''
    job_id = ''
    job_type = ''

    if ('query' not in request_details):
        request_status = Status.STATUS_BAD_REQUEST
        request_message = "field `query` is missing."
    else:
        query = request_details['query']
        print(query)
        request_message = 'your request has been submitted'
        request_status = Status.STATUS_CODE_OK
        job = Job(data=query, job_function=convert_nl_to_sql)
        job.remarks = 'explain_job'
        job_type = job.remarks
        job_id = job.schedule_job(schedular=schedular, priority_level=Priority.PRIORITY_HIGH)
        print("Scheduled Job {}".format(job_id))

    return jsonify(
        {
            'status': request_status.name,
            'code': request_status.value,
            'message': request_message,
            'job_id': job_id,
            'job_type': job_type
        }
    ), request_status.value

