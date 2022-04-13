from app.database.sqlalchemy_extension import db

from werkzeug.security import generate_password_hash, check_password_hash

class UserModel(db.Model):

    # Specifying table
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    firebase_id = db.Column(db.String(100))
    name = db.Column(db.String(70))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(100))
    is_email_verified = db.Column(db.Boolean)
    profile_image = db.Column(db.Text())
    occupation = db.Column(db.Text())
    is_donor = db.Column(db.Boolean)
    is_recipient = db.Column(db.Boolean)
    is_moderator = db.Column(db.Boolean)
    address = db.Column(db.Text())
    location = db.Column(db.Text())
    
    def __init__(self, firebase_id, name, email, password, role):

        self.name = name
        self.email = email
        self.firebase_id = firebase_id
        # saving hash of password
        self.set_password(password)

        # Setting role of a user
        if role == 0:
            self.is_donor = True
            self.is_recipient = False
            self.is_moderator = False
        elif role == 1:
            self.is_donor = False
            self.is_recipient = True
            self.is_moderator = False
        elif role == 2:
            self.is_donor = False
            self.is_recipient = False
            self.is_moderator = True
            
        self.is_email_verified = False


    def json(self):
            '''UserModel object in json format.'''
            return {
                "id": self.id,
                "firebase_id": self.firebase_id,
                "name": self.name,
                "email": self.email,
                "is_email_verified": self.is_email_verified,
                "profile_image": self.profile_image,
                "address": self.address,
                "location": self.location,
                "occupation": self.occupation,
                "is_donor": self.is_donor,
                "is_recipient": self.is_recipient,
                "is_moderator": self.is_moderator,
                "profile_image": self.profile_image
            }
            
    
    @classmethod
    def find_by_email(cls, email: str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()
    
    @classmethod        
    def find_by_id(cls, _id: int) -> 'UserModel':
        '''Returns user of given id.'''
        return cls.query.filter_by(id=_id).first()
    
    @classmethod        
    def find_by_firebase_id(cls, firebase_id: str) -> 'UserModel':
        '''Returns user of given firebase_id.'''
        return cls.query.filter_by(firebase_id=firebase_id).first()
    
    def set_password(self, password_plain_text: str) -> None:
        """Sets user password"""
        self.password_hash = generate_password_hash(password_plain_text)

    def check_password(self, password_plain_text: str) -> bool:
        """Returns a boolean if password is the same as it's hash."""
        return check_password_hash(self.password_hash, password_plain_text)
    
    def save_to_db(self) -> None:
        '''Add user to database'''
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        '''Deletes user from the database.'''
        db.session.delete(self)
        db.session.commit()
        
    

