from flask import request, Response
import requests
import json
from flask_restplus import Api, Resource, Namespace, fields, Model
import datetime
from firebase_admin import auth
import app.utils.messages as messages
from app.apis.models.application import add_models_to_namespace
from app.apis.models.application import *
from app.apis.validate.application_validate import validate_application_submit_data
from app.database.dao.application import ApplicationDAO
from app.utils.view_decorator import token_required

app_ns = Namespace('application', description='Functions related to application submission')
add_models_to_namespace(app_ns)

@app_ns.route('/submit')
class SubmitApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    @app_ns.expect(application_submit_model)
    def post(self):
        data = request.json
        
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        not_valid = validate_application_submit_data(data)
        
        if not_valid:
            return not_valid
        
        submit_application_response = ApplicationDAO.create_application(uid, data)
        
        return submit_application_response
    
@app_ns.route('/accept')
class AcceptApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    @app_ns.expect(application_accept_model)
    def post(self):
        data = request.json
        
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        accept_application_response = ApplicationDAO.accept_application(uid, data)
        
        return accept_application_response
    
@app_ns.route('/verify')
class VerifyApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    @app_ns.doc(params={'reserved_application_id': 'Reserved application id'})
    def post(self):
        data = request.json
        
        token = request.headers['authorization']
        args = request.args
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        reserved_application_id = args.get("reserved_application_id")
        verify_application_response = ApplicationDAO.verify_application(uid, reserved_application_id)
        
        return verify_application_response
    
@app_ns.route('/donate')
class DonateApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    @app_ns.doc(params={'reserved_application_id': 'Reserved application id'})
    def post(self):
        data = request.json
        
        token = request.headers['authorization']
        args = request.args
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        reserved_application_id = args.get("reserved_application_id")
        donate_application_response = ApplicationDAO.donate_application(uid, reserved_application_id)
        
        return donate_application_response
    
@app_ns.route('/close')
class CloseApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    @app_ns.doc(params={'reserved_application_id': 'Reserved application id'})
    def post(self):
        data = request.json
        
        token = request.headers['authorization']
        args = request.args
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        reserved_application_id = args.get("reserved_application_id")
        donate_application_response = ApplicationDAO.close_application(uid, reserved_application_id)
        
        return donate_application_response

@app_ns.route('/')
class AcceptApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    def get(self):
        
        
        list_application_response = ApplicationDAO.list_application()
        
        return list_application_response
    

@app_ns.route('/filter')
class AcceptApplication(Resource):
    
    @app_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @app_ns.expect(application_filter_model)
    @token_required
    def post(self):
        data = request.json
        
        state = data["state"]
        district = data["district"] if data["district"] else ""
        sub_district = data["sub_district"] if data["sub_district"] else ""
        area = data["area"] if data["area"] else ""
        
        list_application_response = ApplicationDAO.list_application_with_args(state, district, sub_district, area)
        
        return list_application_response