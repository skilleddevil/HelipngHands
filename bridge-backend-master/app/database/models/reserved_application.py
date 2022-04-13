from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.database.models.application import ApplicationModel
from app.database.models.institution import InstitutionModel

from app.database.models.application_donor import application_donor
from app.database.models.application_moderator import application_moderator
from datetime import date, timedelta

class ReservedApplicationModel(db.Model):
    
    # Specifying table
    __tablename__ = "reserved_application"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"))
    application = db.relationship(
        ApplicationModel,
        backref='reserved',
        primaryjoin="ReservedApplicationModel.application_id == ApplicationModel.id",
    )
    donor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    donor = db.relationship(
        UserModel,
        backref="reserved_as_donor",
        primaryjoin="ReservedApplicationModel.donor_id == UserModel.id",
    )
    moderator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    moderator = db.relationship(
        UserModel,
        backref="reserved_as_moderator",
        primaryjoin="ReservedApplicationModel.moderator_id == UserModel.id",
    )
    
    is_active = db.Column(db.Boolean)
    verified = db.Column(db.Boolean)
    verification_date = db.Column(db.String(20))
    donation_date = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    
    
    def save_to_db(self) -> None:
        '''Add application to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes application from the database.'''
        db.session.delete(self)
        db.session.commit()
        
    
    @classmethod        
    def find_by_id(cls, id: int) -> 'ReservedApplicationModel':
        '''Returns reserved application of given id.'''
        return cls.query.filter_by(id= id).first()
    
    @classmethod        
    def find_by_application_id(cls, application_id: int) -> 'ReservedApplicationModel':
        '''Returns reserved application of given donor id.'''
        return cls.query.filter_by(application_id= application_id).first()
    
    @classmethod        
    def find_by_donor_id(cls, donor_id: int) -> 'ReservedApplicationModel':
        '''Returns reserved application of given donor id.'''
        return cls.query.filter_by(donor_id= donor_id).first()
    
    @classmethod        
    def find_by_moderator_id(cls, moderator_id: int) -> 'ReservedApplicationModel':
        '''Returns reserved application of given moderator id.'''
        return cls.query.filter_by(moderator_id= moderator_id).first()
    
    @classmethod        
    def find_reserved_application(cls, application_id: int, donor_id: int, moderator_id: int) -> 'ReservedApplicationModel':
        '''Returns reserved application of given moderator id.'''
        return cls.query.filter_by(application_id=application_id, donor_id=donor_id, moderator_id= moderator_id).first()
    