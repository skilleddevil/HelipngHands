from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.database.models.institution import InstitutionModel

from app.database.models.application_donor import application_donor
from app.database.models.application_moderator import application_moderator
from datetime import date, timedelta


class ApplicationModel(db.Model):
    
    # Specifying table
    __tablename__ = "application"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    applicant = db.relationship(
        UserModel,
        backref='application',
        primaryjoin="ApplicationModel.applicant_id == UserModel.id",
    )
    applicant_first_name = db.Column(db.String(50)) 
    applicant_last_name = db.Column(db.String(50)) 
    contact_number = db.Column(db.String(20)) 
    aadhaar_number = db.Column(db.String(15)) 
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    sub_district = db.Column(db.String(100))
    area = db.Column(db.String(100))
    
    year_or_semester = db.Column(db.String(100))
    course_name = db.Column(db.String(100))
    
    donor = db.relationship('UserModel', secondary=application_donor, backref=db.backref('donating', lazy = 'dynamic'))
    moderator = db.relationship('UserModel', secondary=application_moderator, backref=db.backref('moderating', lazy = 'dynamic'))
    moderator_email = db.Column(db.String(70))
    institute_id = db.Column(db.Integer, db.ForeignKey("institution.id"))
    insittute = db.relationship(
        InstitutionModel,
        backref="applications",
        primaryjoin="ApplicationModel.institute_id == InstitutionModel.id",
    )
    
    description = db.Column(db.Text())
    
    is_open = db.Column(db.Boolean)
    verified = db.Column(db.Boolean)
    submission_date = db.Column(db.String(20))
    expiration_date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    remaining_amount = db.Column(db.Integer)
    no_of_donors = db.Column(db.Integer)
   
    def __init__(self, 
                 applicant_first_name, 
                 applicant_last_name, 
                 contact_number,
                 aadhaar_number,
                 state,
                 district,
                 sub_district,
                 area,
                 year_or_semester,
                 course_name,
                 amount,
                 description
                 ):
        self.applicant_first_name = applicant_first_name
        self.applicant_last_name = applicant_last_name
        self.contact_number = contact_number
        self.aadhaar_number = aadhaar_number
        self.state = state
        self.district = district
        self.sub_district = sub_district
        self.area = area
        self.year_or_semester = year_or_semester
        self.course_name = course_name
        self.amount = amount
        self.remaining_amount = amount
        self.no_of_donors = 0
        self.is_open = True
        self.verified = False
        self.submission_date = str(date.today())
        self.expiration_date = str(date.today() + timedelta(days=60))
        self.description = description
        
    def json(self):
        
        for document in self.documents:
            offer_letter = document.offer_letter
            fee_structure = document.fee_structure
            bank_statement = document.bank_statement
        return {
            "id": self.id,
            "applicant_first_name": self.applicant_first_name,
            "applicant_last_name": self.applicant_last_name,
            "state": self.state,
            "district": self.district,
            "sub_district": self.sub_district,
            "area": self.area,
            "institute": self.insittute.name,
            "remaining_amount": self.remaining_amount,
            "no_of_donors": self.no_of_donors,
            "description": self.description,
            "institute_state": self.insittute.state,
            "institute_district": self.insittute.district,
            "offer_letter": offer_letter,
            "fee_structure": fee_structure,
            "bank_statement": bank_statement
        }
    @classmethod
    def find_by_moderator_email(cls, moderator_email: str) -> 'ApplicationModel':
        return cls.query.filter_by(moderator_email=moderator_email).first()
    
    @classmethod        
    def find_by_id(cls, _id: int) -> 'ApplicationModel':
        '''Returns application of given id.'''
        return cls.query.filter_by(id=_id).first()
    
    def save_to_db(self) -> None:
        '''Add application to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes application from the database.'''
        db.session.delete(self)
        db.session.commit()
    