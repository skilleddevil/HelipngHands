from flask_restplus import fields, Model

def add_models_to_namespace(api_namespace):
    api_namespace.models[application_submit_model.name] = application_submit_model
    api_namespace.models[application_accept_model.name] = application_accept_model
    api_namespace.models[application_filter_model.name] = application_filter_model
    
    
application_submit_model = Model(
    "Submit Application",
    {   
        "applicant_first_name": fields.String(required=True, description="first name of applicant"),
        "applicant_last_name": fields.String(required=True, description="last name of applicant"),
        
        "contact_number": fields.String(required=True, description="Contact number of the user"),
        "aadhaar_number": fields.String(
            required=True, description="Address of user"
        ),
        "state": fields.String(required=True, description="State of applicant living in"),
        "district": fields.String(
            required=True, description="District of applicant living in"
        ),
        "sub_district": fields.String(
            required=False, description="Sub District of applicant living in"
        ),
        "area": fields.String(required=False, description="Area of applicant living in"
        ),
        "institute_name": fields.String(required=True, description="Institution name"
        ),
        "institute_state": fields.String(required=True, description="Institution State"
        ),
        "institute_district": fields.String(required=True, description="Institution district"
        ),
        "institute_type": fields.Integer(required=True, description="0 means school and 1 means college/university"
        ),
        "institution_affiliation_code": fields.String(required=True, description="Institution affiliation code"
        ),
        "course_name": fields.String(required=True, description="Course name"
        ),
        "year_or_semester": fields.String(required=True, description="Year or semester"
        ),
        "amount": fields.Integer(required=True, description="Amount needed for donation"
        ),
        "description": fields.String(required=True, description="Description of why they need money"
        ),
        "offer_letter": fields.String(required=True, description="Link of offer letter"
        ),
        "fee_structure": fields.String(required=True, description="Link of fee structure"
        ),
        "bank_statement": fields.String(required=True, description="Link of bank statement"
        )
    }
)

application_accept_model = Model(
    "Accept Application",
    {   
        "application_id": fields.Integer(required=True, description="Application ID"),
        "donating_full_amount": fields.Boolean(required=True, description="Whether or not donating full amount"),
        "amount": fields.Integer(required=True, description="Amount to be donated"),
        "moderator_email": fields.String(required=True, description="Moderator email address")
    }
)

application_filter_model = Model(
    "Filter Application",
    {   
        "state": fields.String(required=True, description="State"),
        "district": fields.String(required=True, description="District"),
        "sub_district": fields.String(required=True, description="Sub District"),
        "area": fields.String(required=True, description="Area")
    }
)
