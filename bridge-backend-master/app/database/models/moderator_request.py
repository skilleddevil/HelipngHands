from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.database.models.application import ApplicationModel




class ModeratorRequestModel(db.Model):
    
    # Specifying table
    __tablename__ = "moderator_request"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    donor = db.relationship(
        UserModel,
        backref="moderator_request",
        primaryjoin="ModeratorRequestModel.donor_id == UserModel.id",
    )
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"))
    application = db.relationship(
        ApplicationModel,
        backref="moderator_request",
        primaryjoin="ModeratorRequestModel.application_id == ApplicationModel.id",
    )
    accepted = db.Column(db.Boolean)
    mod_email = db.Column(db.String(70))
    
    def __init__(self, donor, invitee_email, unique_code):
        self.invitee_email = invitee_email
        self.unique_code = unique_code
        self.donor = donor
    
    
    @classmethod
    def find_by_mod_email(cls, invitee_email: str) -> 'InvitesModel':
        return cls.query.filter_by(invitee_email=invitee_email).first()
    
    def save_to_db(self) -> None:
        '''Add invite details to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes invite details from the database.'''
        db.session.delete(self)
        db.session.commit()
    