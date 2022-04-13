from app.database.sqlalchemy_extension import db
from app.database.models.application import ApplicationModel


class DocumentsModel(db.Model):
    
    # Specifying table
    __tablename__ = "documents"
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"))
    application = db.relationship(
        ApplicationModel,
        backref="documents",
        primaryjoin="DocumentsModel.application_id == ApplicationModel.id",
    )
    
    offer_letter = db.Column(db.Text())
    fee_structure = db.Column(db.Text())
    bank_statement = db.Column(db.Text())
    affiliation_letter = db.Column(db.Text())
    scholarship_letter = db.Column(db.Text())
    additional_doc1 = db.Column(db.Text())
    additional_doc2 = db.Column(db.Text())
    additional_doc3 = db.Column(db.Text())
    
    
    def __init__(self, offer_letter, fee_structure, bank_statement):
        self.offer_letter = offer_letter
        self.fee_structure = fee_structure
        self.bank_statement = bank_statement
    
    
    def save_to_db(self) -> None:
        '''Add document details to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes document details from the database.'''
        db.session.delete(self)
        db.session.commit()