from flask import Flask
import app
import firebase_admin
from firebase_admin import credentials, firestore
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from app.database.models.user import UserModel
from app.database.models.preferred_location import PreferredLocationModel
from dotenv import load_dotenv, find_dotenv
from os import environ
from flask_mail import Mail


def create_app() -> Flask:

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///local_data1.db"
    # app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')

    app.url_map.strict_slashes = False

    load_dotenv(find_dotenv())

    mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": environ.get('EMAIL_USER'),
    "MAIL_PASSWORD": environ.get('EMAIL_PASS')
    }

    app.config.update(mail_settings)

    from app.database.sqlalchemy_extension import db
    db.init_app(app)


    cred = credentials.Certificate('google-credentials.json')
    firebase_admin.initialize_app(cred)

    from app.apis import api
    api.init_app(app)

    from app.utils.mail_extension import mail
    mail.init_app(app)


    return app

application = create_app()


@application.before_first_request
def create_tables():
    from app.database.sqlalchemy_extension import db
    db.create_all()

if __name__ == "__main__":
    application.run(port=5000)
