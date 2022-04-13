from typing import Dict

def validate_user_signup_data(data: Dict[str, str]):
    if "email" not in data:
        return {'message': "Please enter valid email address"}, 400
    if "name" not in data:
        return {'message': "Please enter valid name"}, 400
    if "password" not in data:
        return {'message': "Please enter valid password"}, 400
    if "role" not in data:
        return {'message': "Please select a role"}, 400
    
    if len(data['password']) < 6:
        return {"message": "Password length is too short."}, 403

    if type(data["role"]) is not int:
        return {"message": "Type mismatch of role."}

    if "@" not in data['email']:
        return {"message": "Email is invalid."}, 403
    
    