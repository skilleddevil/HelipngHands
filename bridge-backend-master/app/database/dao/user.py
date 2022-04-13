from flask import request, Response
from app.database.models.user import UserModel
from app.database.models.invites import InvitesModel
from app.database.models.invites import InvitesModel
from app.database.models.reserved_application import ReservedApplicationModel
from app.database.models.application import ApplicationModel
import requests
import json
from app.utils import messages
from firebase_admin import auth
from app.apis.validate.user_validate import validate_user_signup_data
from typing import Dict
from os import environ
from app.database.sqlalchemy_extension import db
from app.database.models.preferred_location import PreferredLocationModel
import random
from app.utils.email_utils import send_email_verification_message, send_invite_mod_email


class UserDAO:
    """Data Access Object for User"""

    @staticmethod
    def create_user(data: Dict[str, str]):
        """Creates a new user"""
        
        name = data['name']
        email = data['email']
        password = data['password']
        role = data['role']
        
        existing_user = UserModel.find_by_email(email.lower())
        if existing_user and existing_user.firebase_id != "":
            return {"message": "User already exists"}, 400
        
        if existing_user and existing_user.firebase_id == "" and role != 2:
            return {"message": "User is invited as a moderator. Please sign up as a moderator with unique code"}, 400
        
        if role == 2:
            if "otp" in data:
                invitation = InvitesModel.find_by_mod_email(email.lower())
                if invitation:
                    if data["otp"] != invitation.unique_code:
                        return {"message": "Code is incorrect"}, 401  
                else:
                    return {"message": "Sorry! Invite is needed to be a moderator"}, 400
            else:
                return {"message": "Please send unique code"}, 400

        print("Passed")
        
        try:    
            user = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
                display_name=name,
                disabled=False
                )
            
            link = auth.generate_email_verification_link(email, action_code_settings=None)
            ''' To implement, send verification link usingg # send_verification_link(email,link) '''
            
        except Exception as e:
            return {"message": str(e)}, 400
        
        try:    
            firebase_details = auth.get_user_by_email(email)
            uid = firebase_details.uid
            firebase_email = firebase_details.email
            
            ''' Existing user is a temporary moderator user '''
            if existing_user:
                existing_user.firebase_id = uid
                existing_user.name = name
                existing_user.email = firebase_email
                existing_user.save_to_db()
            else:
                user = UserModel(uid, name, firebase_email, password, role)
                user.save_to_db()
            
        except Exception as e:
            print(e)
            
        send_email_verification_message(link, email)

        return {"verify_link": link,
                "message" : "User was created successfully. Please check your email to verify the account"
                }, 201
        
    @staticmethod
    def authenticate(email: str, password: str):
        """ User login process"""

        try:
            user = auth.get_user_by_email(email)
            if user.email_verified != True:
                return {"message": "Email is not verified, Please verify email first"}, 400

            else:
                local_user = UserModel.find_by_email(email)
                if local_user.is_email_verified:
                    pass
                else:
                    local_user.is_email_verified = True
                    db.session.commit()
                

        except Exception as e:
            return {"message": e.args[0]}, 400
        
        
        json_string = {"email":email,"password":password,"returnSecureToken":True}
        API_KEY = environ.get('API_KEY')
        url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=' + API_KEY
        res = requests.post(url, data=json_string)
        json_res = json.loads(res.text)
        
        
        if "error" in json_res.keys():
            error_message = json_res["error"]
            if error_message["message"] == "INVALID_PASSWORD":
                return {"message": "Password is incorrect"}, 401
            else:
                return { "message": error_message["message"]}, 401    
        
        
        if "idToken" in json_res.keys():
            '''Sample response of role i.e. 0'''
            json_res["role"] = 3

            
        
        return json_res, 200
    
    @staticmethod
    def list_all_users():
        user_list = UserModel.query.all()
        list_of_users = [
            user.json()
            for user in user_list
        ]
        return list_of_users, 200
    
    @staticmethod
    def get_profile(firebase_id: str):
        user_profile = UserModel.find_by_firebase_id(firebase_id)
        return user_profile.json()
    
    @staticmethod
    def update_profile(firebase_id: str, data: Dict[str, str]):
        user_profile = UserModel.find_by_firebase_id(firebase_id)
        if "name" in data:
            user_profile.name = data["name"]
        if "address" in data:
            user_profile.address = data["address"]
        if "location" in data:
            user_profile.location = data["location"]
        if "occupation" in data:
            user_profile.occupation = data["occupation"]
        
        try:
            db.session.commit()
        except Exception as e:
            return {"message": e.args[0]}, 400
        
        
        return messages.PROFILE_UPDATE_SUCCESSFULLY, 200
    
    @staticmethod
    def update_preferred_location(firebase_id: str, data: Dict[str, str]):
        state = data['state']
        district = data['district']
        if "sub_district" in data:
            sub_district = data["sub_district"]
        else:
            sub_district = ""
        if "area" in data:
            area = data["area"]
        else:
            area = ""
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if user.is_donor:
            preferred_location = user.preferred_location
            if preferred_location:
                preferred_location.state = state
                preferred_location.district = district
                preferred_location.sub_district = sub_district
                preferred_location.area = area
                preferred_location.save_to_db()
            else:
                updated_location = PreferredLocationModel(user.id, state, district, sub_district, area)
                updated_location.save_to_db()
            return {"message": "Preferred location updated successfully"}, 200
        else:
            return {"message": "This user cannot set preferred location"}, 401
    
    @staticmethod
    def get_preferred_location(firebase_id: str):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if user.is_donor:
            preferred_location = PreferredLocationModel.find_by_user_id(user.id)
            print(preferred_location)
            if preferred_location:
                return preferred_location.json(), 200
            else:
                return {"message": "Cannot find preferred location"}, 400
        
        return {"message": "User is not a donor. Cannot set preferred location"}, 400
        
        
            
    @staticmethod
    def send_invite_to_mod(firebase_id: str, email: str):
        mod_email = email
        
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if user.is_donor:
            mod_exists = UserModel.find_by_email(mod_email)
            if mod_exists:
                if mod_exists.is_moderator:
                    return {"message": f"Moderator is already registered. Do you want to proceed?"}, 409
                else:
                    role = "donor" if mod_exists.is_donor else "recipient" if mod_exists.is_recipient else "moderator"
                    return {"message": f"User with this email is already signed up as a {role}"}, 400
            else:
                otp = random.randint(111111,999999)
                invite = InvitesModel(user, email, otp)
                invite.save_to_db()
                send_invite_mod_email(user.name, otp, email)
                return {"message": "Invitation sent"}, 200
                
        else:
            return {"message": "User cannot invite moderator"}, 401

    @staticmethod
    def dashboard(firebase_id: str):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        role = "donor" if user.is_donor else "recipient" if user.is_recipient else "moderator"
        
        return {"message": role}, 200
    
    @staticmethod
    def get_dashboard(firebase_id: str):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        role = 0 if user.is_donor else 1 if user.is_recipient else 2
        reserved_applications = list()
        if user.is_donor:
            reserved_applications = user.reserved_as_donor
        elif user.is_moderator:
            reserved_applications = user.reserved_as_moderator
        else:
            applications = user.application
            
            for app in applications:
                reserved_applications = app.reserved
        
        
        application_list = list()
        for reserved in reserved_applications:
            if reserved.is_active:
                application = ApplicationModel.find_by_id(reserved.application_id)
                application_data = application.json()
                application_data.pop("remaining_amount")
                application_data["donor_id"] = reserved.donor.firebase_id
                application_data["recipient_id"] = application.applicant.firebase_id
                application_data["donor_name"] = reserved.donor.name
                application_data["moderator_id"] = reserved.moderator.firebase_id
                application_data["moderator_name"] = reserved.moderator.name if reserved.moderator.name != "" else "Yet to accept Invite"
                status = 1 if not reserved.verified else 2
                application_data["status"] = status
                application_data["reserved_application_id"] = reserved.id
                application_data["donating_amount"] = reserved.amount
                application_list.append(application_data)
            
        
        return {"role": role, 
            "applications": application_list }, 200
        
    @staticmethod
    def get_histroy(firebase_id: str):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        role = 0 if user.is_donor else 1 if user.is_recipient else 2
        
        reserved_applications = list()
        
        if user.is_donor:
            reserved_applications = user.reserved_as_donor
        elif user.is_moderator:
            reserved_applications = user.reserved_as_moderator
        else:
            applications = user.application
            
            for app in applications:
                reserved_applications = app.reserved
                
        application_list = list()
        for reserved in reserved_applications:
            if reserved.is_active == False:
                application = ApplicationModel.find_by_id(reserved.application_id)
                application_data = application.json()
                history_application = dict()
                history_application["recipient_name"] = application_data["applicant_first_name"] + " " + application_data["applicant_last_name"]
                history_application["moderator_name"] = reserved.moderator.name
                history_application["donor_name"] = reserved.donor.name
                history_application["amount"] = reserved.amount
                history_application["donation_date"] = reserved.donation_date
                application_list.append(history_application)
                
        return {"role": role, 
            "history": application_list }, 200
        
    @staticmethod
    def update_profile_image(firebase_id: str, image_url: str):
        
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        user.profile_image = image_url
        user.save_to_db()
        
        return {"message": "Image updated successfully"}, 200
