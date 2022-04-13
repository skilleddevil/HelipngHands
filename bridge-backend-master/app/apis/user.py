from flask import request, Response
import requests
import json
from flask_restplus import Api, Resource, Namespace, fields, Model
import datetime
from firebase_admin import auth
import app.utils.messages as messages
from app.apis.validate.user_validate import validate_user_signup_data
from app.apis.models.user import add_models_to_namespace
from app.apis.models.user import *
from app.database.dao.user import UserDAO
from app.utils.view_decorator import token_required
import os

user_ns = Namespace('user', description='Functions related to user')
add_models_to_namespace(user_ns)

@user_ns.route('/register')
class UserRegister(Resource):
    
    @user_ns.response(201, "%s" % (
        {"message" : "User was created successfully. Please check your email to verify the account"}
    ))
    @user_ns.response(400, "%s" % (
        {"message" : "user already exists"}
    ))
    @user_ns.expect(register_user_model)
    def post(self):
        
        data = request.json
        
        not_valid = validate_user_signup_data(data)
        
        if not_valid:
            return not_valid
        
        result = UserDAO.create_user(data)
        return result
            

@user_ns.route('/login')
class UserSignIn(Resource):
    
    @user_ns.response(200, "User logged in successfully", login_response_model)
    @user_ns.response(400, "%s" % (
        {"message": "password is incorrect"}
    ))
    @user_ns.expect(login_user_model)
    def post(self):
        data = request.json
        email = data['email']
        password = data['password']
        
        login_response = UserDAO.authenticate(email, password)
        return login_response


@user_ns.route("/profile")
class UserProfile(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @user_ns.response(200, "Profile Data", profile_body)
    @user_ns.response(400, "%s\n%s\n%s\n%s" % (
        messages.TOKEN_EXPIRED,
        messages.TOKEN_INVALID,
        messages.TOKEN_REVOKED,
        {"message": "cannot find account"}
    ),
    )
    @token_required
    def get(self):
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        try:
            user = UserDAO.get_profile(uid)
        except Exception as e:
            return {"message": "cannot find account"}, 400
            
        return user, 200
    
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @user_ns.response(200, "%s" % (messages.PROFILE_UPDATE_SUCCESSFULLY))
    @user_ns.response(400, "%s\n%s\n%s\n%s" % (
        messages.TOKEN_EXPIRED,
        messages.TOKEN_INVALID,
        messages.TOKEN_REVOKED,
        {"message": "cannot find account"}
    ),
    )
    @user_ns.expect(update_profile_body)
    @token_required
    def put(self):
        data = request.json
        token = request.headers['authorization']
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']

        try:
            user_updated_response = UserDAO.update_profile(uid, data)
            
        except Exception as e:
            return {"message": str(e)}, 400
        
        return user_updated_response

@user_ns.route("/profile/image")
class UserProfile(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @user_ns.expect(200, "Profile Image Url", profile_image_update)
    @user_ns.response(400, "%s\n%s\n%s\n%s" % (
        messages.TOKEN_EXPIRED,
        messages.TOKEN_INVALID,
        messages.TOKEN_REVOKED,
        {"message": "Image updated successfully"}
    ),
    )
    @token_required
    def put(self):
        data = request.json
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        try:
            update_image_response = UserDAO.update_profile_image(uid,data["image_url"])
        except Exception as e:
            return {"message": str(e)}, 400
        
        return update_image_response
        


@user_ns.route('/preferredlocation')
class UserUpdateLocation(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @user_ns.response(200, "%s" % ({"message":"Preferred location updated successfully"}))
    @user_ns.response(400, "%s" % (
        {"message": "Cannot update preferred location"}
    ))
    @user_ns.response(401, "%s" % (
        {"message": "This user cannot set preferred location"}
    ))
    @user_ns.expect(update_preferred_location_body)
    @token_required
    def post(self):
        data = request.json
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        try:
            update_preferred_location_response = UserDAO.update_preferred_location(uid, data)
        except Exception as e:
            return {"message": str(e)}, 400
        
        return update_preferred_location_response
    
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})    
    @token_required
    @user_ns.response(400, "%s\n%s" % (
        {"message": "Cannot find preferred location"},
        {"message": "User is not a donor. Cannot set preferred location"}
    ))
    @user_ns.response(200, "Preferred Location Data", preferred_location_body)
    
    def get(self):
        token = request.headers['authorization']
        
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        try:
            preferred_location_response = UserDAO.get_preferred_location(uid)
        except Exception as e:
            return {"message": str(e)}, 400
        
        return preferred_location_response
        

@user_ns.route('/invite/moderator')
class InviteModerator(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @user_ns.response(400, "%s\n%s\n%s\n%s" % (
        {"message": "Moderator is already registered. Do you want to proceed?"},
        {"message": "User with this email is already signed up as a recipient/donor"},
        {"message": "Invitation sent"},
        {"message": "User cannot invite moderator"}
    ))
    @user_ns.doc(params={'email': 'Email of moderator'})
    @token_required
    def post(self):
        
        token = request.headers['authorization']
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        args = request.args
        
        if "email" in args:
            mod_email = args.get("email")
        else:
            return {"message": "Please add email address of moderator"}, 400
        
        try:
            send_mod_invite = UserDAO.send_invite_to_mod(uid, mod_email)
        except Exception as e:
            return {"message": str(e)}, 400
        
        return send_mod_invite

@user_ns.route('/dashboard')
class UserDashboard(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    def get(self):
        
        token = request.headers['authorization']
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        dashboard_response = UserDAO.get_dashboard(uid)
        
        return dashboard_response
        
@user_ns.route('/history')
class UserDashboard(Resource):
    
    @user_ns.doc(params={'authorization': {'in': 'header', 'description': 'An authorization token'}})
    @token_required
    def get(self):
        
        token = request.headers['authorization']
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        history_response = UserDAO.get_histroy(uid)
        
        return history_response
    
# @user_ns.route('/resetpassword')
# class ResetPassword(Resource):
    
    
#     def get(self):
#         email = request.args.get('email')
#         try:
#             link = auth.generate_password_reset_link(email, action_code_settings=None)
#             ''' Send password reset email ''' 
#             # send_reset_link(email, link)
            
#         except Exception as e:
#             return {'message': e.args[0]}, 400
        
#         return messages.RESET_LINK_SENT, 200
    