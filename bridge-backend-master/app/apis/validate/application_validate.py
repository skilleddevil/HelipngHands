from typing import Dict

def validate_application_submit_data(data: Dict[str, str]):
    if "applicant_first_name" not in data:
        return {'message': "Please enter valid first name"}, 400
    if "applicant_last_name" not in data:
        return {'message': "Please enter valid last name"}, 400
    if "contact_number" not in data:
        return {'message': "Please enter contact number"}, 400
    if "aadhaar_number" not in data:
        return {'message': "Please enter aadhaar number"}, 400
    if "state" not in data:
        return {'message': "Please enter state"}, 400
    if "district" not in data:
        return {'message': "Please enter district"}, 400
    if "sub_district" not in data:
        return {'message': "Please enter sub district"}, 400
    if "area" not in data:
        return {'message': "Please enter area"}, 400
    if "institute_name" not in data:
        return {'message': "Please enter institution name"}, 400
    if "institution_affiliation_code" not in data:
        return {'message': "Please enter institution affiliation code"}, 400
    if "institute_state" not in data:
        return {'message': "Please enter institution state"}, 400
    if "institute_district" not in data:
        return {'message': "Please enter institution district"}, 400
    if "course_name" not in data:
        return {'message': "Please enter course name"}, 400
    if "year_or_semester" not in data:
        return {'message': "Please enter year or semester"}, 400
    if "amount" not in data:
        return {'message': "Please enter amount needed"}, 400
    if "offer_letter" not in data:
        return {'message': "Please add offer letter"}, 400
    if "fee_structure" not in data:
        return {'message': "Please add fee structure"}, 400
    if "bank_statement" not in data:
        return {'message': "Please add bank statement"}, 400
    if "description" not in data:
        return {'message': "Please add description"}, 400

    