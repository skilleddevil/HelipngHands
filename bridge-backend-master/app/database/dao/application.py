from flask import request, Response
from app.database.models.user import UserModel
from app.database.models.application import ApplicationModel
from app.database.models.reserved_application import ReservedApplicationModel
from app.database.models.documents import DocumentsModel
from app.database.models.invites import InvitesModel
from app.database.models.institution import InstitutionModel
import requests
import json
from app.utils import messages
from firebase_admin import auth
from app.apis.validate.application_validate import validate_application_submit_data
from typing import Dict
from os import environ
from app.database.sqlalchemy_extension import db
from app.database.models.preferred_location import PreferredLocationModel
from app.utils.email_utils import send_invite_mod_email
import random
from datetime import date, timedelta, datetime


class ApplicationDAO:
    """Data Access Object for Application"""

    @staticmethod
    def create_application(firebase_id: str, data: Dict[str, str]):
        
        user = UserModel.find_by_firebase_id(firebase_id)
        user_application = user.application
        
        if user.is_recipient == False:
            return {"message": "This user cannot submit application"}, 403
        
        # data = request.json
        ''' Personal information '''
        applicant_first_name = data["applicant_first_name"]
        applicant_last_name = data["applicant_last_name"]
        contact_number = data["contact_number"]
        aadhaar_number = data["aadhaar_number"]
        state = data["state"]
        district = data["district"]
        sub_district = data["sub_district"]
        area = data["area"]
        description = data["description"]
        
        
        ''' Institution details '''
        institute_name = data["institute_name"]
        institute_state = data["institute_state"]
        institute_district = data["institute_district"]
        institution_affiliation_code = data["institution_affiliation_code"]
        year_or_semester = data["year_or_semester"]
        course_name = data["course_name"]
        amount = data["amount"]

        ''' Documents details '''
        offer_letter = data["offer_letter"]
        fee_structure = data["fee_structure"]
        bank_statement = data["bank_statement"]
        institute_type = data["institute_type"]
        
        if user_application:
            if any(application.is_open == True for application in user_application):
                    return {"message": "Application already in progress."}, 400
            
            '''Use this is list of application'''
            # for application in user_application:
            #     end_date = application.expiration_date
            #     format_str = '%Y-%m-%d' # The format
            #     expiration_date = datetime.strptime(end_date, format_str) # Expiration date string to date object
            #     if expiration_date < date.today() and application.is_open:
            
        
        
        application = ApplicationModel(applicant_first_name, applicant_last_name, contact_number, 
                                       aadhaar_number, state, district, sub_district, 
                                       area, year_or_semester, course_name, int(amount), description)
        application.applicant = user
        
        
        documents = DocumentsModel(offer_letter, fee_structure, bank_statement)
        documents.application = application
        documents.save_to_db()
        application.insittute = InstitutionModel(institute_name,institute_type, institute_state, institute_district, institution_affiliation_code)
        application.save_to_db()
        # institute = InstitutionModel(institute_name, institute_state, institute_district, institution_affiliation_code)
        # institute.save_to_db()
        
        
        # already_exist_application = ApplicationModel.query.filter_by(name='reza')
        
        return {"message": "Success! Application submitted"}, 200
        
    @staticmethod
    def accept_application(firebase_id: str, data: Dict[str, str]):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if user.is_donor == False:
            return {"message": "This user cannot accept application"}, 403
        
        application_id = data["application_id"]
        donating_full_amount = data["donating_full_amount"]
        amount = data["amount"]
        moderator_email = data["moderator_email"]
        
        application = ApplicationModel.find_by_id(application_id)
        if application.remaining_amount == 0:
            return {"message": "No further amount needed"}, 409
        
        if application in user.donating:
            return {"message": "Already donating to this application"}, 409
        
        application.donor.append(user)
        application.no_of_donors = application.no_of_donors + 1
        
        if donating_full_amount:
            application.remaining_amount = 0
        else:
            application.remaining_amount = application.remaining_amount - amount
        
        ''' Find existing moderator '''
        moderator = UserModel.find_by_email(moderator_email.lower())
        
        if moderator:
            if moderator.is_moderator:
                application.moderator.append(moderator)
                application.moderator_email = moderator.email
                application.save_to_db()
                reserved = ReservedApplicationModel(application= application, donor=user, moderator=moderator, is_active=True, verified=False, amount=amount)
                reserved.save_to_db()
                if moderator.firebase_id == "":
                    return {"message": "Application accepted. Moderator is already invited, please ask moderator to register by code given earlier."}, 200
                else:
                    return {"message": "Application accepted"}, 200
            else:
                role = "donor" if moderator.is_donor else "recipient" if moderator.is_recipient else "moderator"
                return {"message": f"Invited Moderator is register as a {role}"}, 409
        else:
            temp_mod_user = UserModel("","",moderator_email.lower(), "",2)
            temp_mod_user.save_to_db()
            application.moderator.append(temp_mod_user)
            reserved = ReservedApplicationModel(application= application, donor=user, moderator=temp_mod_user, is_active=True, verified=False, amount=amount)
            reserved.save_to_db()
            application.save_to_db()
            ''' Send invite to moderator '''
            invite_code = random.randint(111111,999999)
            invite = InvitesModel(user, temp_mod_user, moderator_email, invite_code)
            invite.save_to_db()
            send_invite_mod_email(user.name, invite_code, moderator_email)
            
            return {"message": "Application accepted. Waiting for moderator to accept the inivite"}, 200
        return {"message": "Application accepted"}, 200
    
    
    @staticmethod
    def verify_application(firebase_id: str, reserved_application_id: int):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if user.is_recipient:
            return {"message": "Only moderator or donor can verify the application"}, 200
        
        application = ReservedApplicationModel.find_by_id(reserved_application_id)
        
        if application:
            application.verified = True
            application.verification_date = str(date.today())
            application.save_to_db()
            return {"message": "Application is now verified"}, 200
        else:
            return {"message": "Cannot find reserved application"}, 404
        
    @staticmethod
    def donate_application(firebase_id: str, reserved_application_id: int):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if not user.is_donor:
            return {"message": "This user cannot donate"}, 200
        
        application = ReservedApplicationModel.find_by_id(reserved_application_id)
        
        if not application.verified:
            return {"message": "Please verify the application first"}, 200
        
        
        if application:
            application.donation_date = str(date.today())
            application.save_to_db()
            return {"message": "Thanks for your donation"}, 200
        else:
            return {"message": "Cannot find reserved application"}, 404
        
    @staticmethod
    def close_application(firebase_id: str, reserved_application_id: int):
        try:
            user = UserModel.find_by_firebase_id(firebase_id)
        except Exception as e:
            return messages.CANNOT_FIND_USER, 400
        
        if not user.is_donor:
            return {"message": "This user cannot close the application"}, 200
        
        application = ReservedApplicationModel.find_by_id(reserved_application_id)
        
        if application and application.donor == user:
            if application.donation_date == None:
                original_applcation = ApplicationModel.find_by_id(application.application_id)
                original_applcation.remaining_amount = original_applcation.remaining_amount + application.amount
                original_applcation.donor.remove(user)
                original_applcation.save_to_db()
                # Not a good practice, if we need to check which donor is culprit and just wasting time of moderator and recipient
                application.delete_from_db()
                return {"message": "Application is removed and updated"}, 200
            else:
                application.is_active = False
                original_applcation = ApplicationModel.find_by_id(application.application_id)
                original_applcation.donor.remove(user)
                original_applcation.save_to_db()
                application.save_to_db()
                return {"message": "Application is closed"}, 200
        else:
            return {"message": "Cannot find reserved application for this user"}, 404
    
    @staticmethod
    def list_application():
        applications = ApplicationModel.query.all()
        all_applications = list()
        for application in applications:
            exp_date_string = application.expiration_date
            expiration_date = datetime.strptime(exp_date_string, "%Y-%m-%d").date()
            if application.is_open:
                if application.remaining_amount != 0:
                    if expiration_date > date.today():
                        all_applications.append(application.json())
            
        return all_applications, 200
    
    @staticmethod
    def list_application_with_args(state: str, district: str, sub_district: str, area: str):
        if district != "" and sub_district == "" and area == "":
           applications = ApplicationModel.query.filter_by(state=state, district=district)          
        elif sub_district != "" and area == "":
            applications = ApplicationModel.query.filter_by(state=state, district=district, sub_district=sub_district)
        elif area != "":
            applications = ApplicationModel.query.filter_by(state=state, district=district, sub_district=sub_district, area=area)
        else:
            applications = ApplicationModel.query.filter_by(state=state)

        all_applications = []
        for application in applications:
            exp_date_string = application.expiration_date
            expiration_date = datetime.strptime(exp_date_string, "%Y-%m-%d").date()
            if application.is_open:
                if application.remaining_amount != 0:
                    if expiration_date > date.today():
                        all_applications.append(application.json())
        return all_applications, 200

