from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.database.models.application import ApplicationModel
from app.database.models.institution import InstitutionModel
class HistoryModel(db.Model):
    
    # Specifying table
    __tablename__ = "history"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    donor = db.relationship(
        UserModel,
        backref="history",
        primaryjoin="HistoryModel.donor_id == UserModel.id",
    )
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient = db.relationship(
        UserModel,
        backref="history",
        primaryjoin="HistoryModel.recipient_id == UserModel.id",
    )
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"))
    application = db.relationship(
        ApplicationModel,
        backref="history",
        primaryjoin="HistoryModel.application_id == ApplicationModel.id",
    )
    institution_id = db.Column(db.Integer, db.ForeignKey("institution.id"))
    institution = db.relationship(
        InstitutionModel,
        backref="history",
        primaryjoin="HistoryModel.institution_id == InstitutionModel.id",
    )
    
    amount = db.Column(db.String(15))
    
    
    
    def save_to_db(self) -> None:
        '''Add history to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes history from the database.'''
        db.session.delete(self)
        db.session.commit()
    