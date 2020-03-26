from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ilmiyanovwopur@192.168.0.101/db_instagram'
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class Account(db.Model):
    id = db.Column(db.Integer, unique=True)
    username = db.Column(db.String(100), unique=True, primary_key=True)
    fullname = db.Column(db.String(100), unique=True, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), unique=False, nullable=True)
    last_login = db.Column(db.Float, unique=False, nullable=True)
    is_logged_in = db.Column(db.Boolean, unique=False, nullable=True)
    cookie = db.Column(db.String(1000), unique=False, nullable=True)
    user_id = db.Column(db.String(100), unique=False, nullable=True)
    timezone = db.Column(db.String(120), unique=False, nullable=True)
    csrftoken = db.Column(db.String(100), unique=False, nullable=True)
    rur = db.Column(db.String(100), unique=False, nullable=True)
    ds_user_id = db.Column(db.String(100), unique=False, nullable=True)
    sessionid = db.Column(db.String(100), unique=False, nullable=True)
    is_from_appium = db.Column(db.Boolean, unique=False, nullable=True)
    device = db.relationship('Device', backref='account', lazy=True)

class LikeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(500), db.ForeignKey('account.username'), nullable=False)
    media_id = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.Float, unique=False, nullable=True)

class AccountStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(500), db.ForeignKey('account.username'), nullable=False)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.Float, unique=False, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(500), db.ForeignKey('account.username'), nullable=False)
    user_agent = db.Column(db.String(1000), unique=False, nullable=False)
    phone_id = db.Column(db.String(1000), unique=False, nullable=False)
    android_device_id = db.Column(db.String(1000), unique=False, nullable=False)
    uuid = db.Column(db.String(1000), unique=False, nullable=False)
    advertising_id = db.Column(db.String(1000), unique=False, nullable=True)
    waterfall_id = db.Column(db.String(1000), unique=False, nullable=True)
    x_pigeon = db.Column(db.String(1000), unique=False, nullable=False)
    attribution_id = db.Column(db.String(1000), unique=False, nullable=False)
    jazoest = db.Column(db.String(1000), unique=False, nullable=False)



    def __repr__(self):
        return '<Device %r>' % self.id

if __name__ == '__main__':
    manager.run()
