from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel



class InvitesModel(db.Model):
    
    # Specifying table
    __tablename__ = "invites"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    donor = db.relationship(
        UserModel,
        backref="invites",
        primaryjoin="InvitesModel.donor_id == UserModel.id",
    )
    moderator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    moderator = db.relationship(
        UserModel,
        backref="getModInvite",
        primaryjoin="InvitesModel.moderator_id == UserModel.id",
    )
    invitee_email = db.Column(db.String(100))
    unique_code = db.Column(db.String(10))
    
    def __init__(self, donor, moderator, invitee_email, unique_code):
        self.invitee_email = invitee_email
        self.unique_code = unique_code
        self.donor = donor
        self.moderator = moderator
    
    
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
    