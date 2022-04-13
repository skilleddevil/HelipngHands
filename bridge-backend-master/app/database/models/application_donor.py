from app.database.sqlalchemy_extension import db

application_donor = db.Table('application_donor',
    db.Column('application_id', db.Integer, db.ForeignKey('application.id')),
    db.Column('donor_id', db.Integer, db.ForeignKey('user.id'))
    )