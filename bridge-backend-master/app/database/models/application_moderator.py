from app.database.sqlalchemy_extension import db

application_moderator = db.Table('application_moderator',
    db.Column('application_id', db.Integer, db.ForeignKey('application.id')),
    db.Column('moderator_id', db.Integer, db.ForeignKey('user.id'))
    )