from flask_restplus import fields, Model

def add_models_to_namespace(api_namespace):
    api_namespace.models[register_user_model.name] = register_user_model
    api_namespace.models[login_user_model.name] = login_user_model
    api_namespace.models[profile_body.name] = profile_body
    api_namespace.models[login_response_model.name] = login_response_model
    api_namespace.models[update_profile_body.name] = update_profile_body
    api_namespace.models[update_preferred_location_body.name] = update_preferred_location_body
    api_namespace.models[preferred_location_body.name] = preferred_location_body
    api_namespace.models[profile_image_update.name] = profile_image_update



update_profile_body = Model(
    "Get profile of a user",
    {   
        
        "name": fields.String(required=False, description="The name of the user"),
        "address": fields.String(required=False, description="The address of the user"),
        "location": fields.String(required=False, description="The location of the user"),
        "occupation": fields.String(
            required=False, description="Occupation of User"
        ),
        
    }
)
    
login_user_model = Model(
    "login User Model",
    {
        "email": fields.String(required=True, description="Email of user"),
        "password": fields.String(required=True, description="password of user")
    }
)

login_response_model = Model(
    "Login Response User Model",
    {
        "kind": fields.String(required=True, description="Kind of user"),
        "localId": fields.String(required=True, description="Firebase id"),
        "displayName": fields.String(required=True, description="Name of user"),
        "idToken": fields.String(required=True, description="Token of user"),
        "registered": fields.String(required=True, description="Bool if the user is registered"),
        "refreshToken": fields.String(required=True, description="Refresh Token"),
        "expiresIn": fields.String(required=True, description="Expiratioon duratioon of token in seconds"),
        "role": fields.Integer(required=True, description="Role of user. 0-Donor, 1-Recipient, 2-Moderator")
    }
)

register_user_model = Model(
    "Register User Model",
    {
        "name": fields.String(required=True, description="Name of user"),
        "email": fields.String(required=True, description="Email of user"),
        "password": fields.String(required=True, description="password of user"),
        "role": fields.Integer(required=True, description="Role of a user"),
        "otp": fields.String(required=True, description="Unique invitation code for moderator signup only")
    }
)

profile_body = Model(
    "Get profile of a user",
    {   
        "id": fields.String(required=True, description="id of user"),
        "firebase_id": fields.String(required=True, description="firebase_id of user"),
        
        "name": fields.String(required=True, description="The name of the user"),
        "email": fields.String(
            required=True, description="Email of user"
        ),
        "is_email_verified": fields.Boolean(required=False, description="If the user is verified or not"),
        "profile_image": fields.String(
            required=False, description="Profile Image Link"
        ),
        "occupation": fields.String(
            required=False, description="Occupation of User"
        ),
        "is_donor": fields.Boolean(required=True, description="If the owner is donor"
        ),
        "is_recipient": fields.Boolean(required=True, description="If the owner is recipient"
        ),
        "is_moderator": fields.Boolean(required=True, description="If the owner is mooderator"
        )
    }
)

update_profile_body = Model(
    "Get profile of a user",
    {   
        
        "name": fields.String(required=False, description="The name of the user"),
        "address": fields.String(required=False, description="The address of the user"),
        "location": fields.String(required=False, description="The location of the user"),
        "occupation": fields.String(
            required=False, description="Occupation of User"
        ),
        
    }
)

update_preferred_location_body = Model(
    "Update preferred location of donor",
    {   
        
        "state": fields.String(required=True, description="Selected state"),
        "district": fields.String(required=True, description="Selected district"),
        "sub_district": fields.String(required=False, description="Selected Sub District"),
        "area": fields.String(
            required=False, description="Selected area"
        ),
        
    }
)

preferred_location_body = Model(
    "Preferred location of donor",
    {   
        
        "state": fields.String(required=True, description="Selected state"),
        "district": fields.String(required=True, description="Selected district"),
        "sub_district": fields.String(required=False, description="Selected Sub District"),
        "area": fields.String(
            required=False, description="Selected area"
        ),
        
    }
)

profile_image_update = Model(
    "Update profile image of a user",
    {   
        "image_url": fields.String(required=True, description="Image of a user")
    }
)
