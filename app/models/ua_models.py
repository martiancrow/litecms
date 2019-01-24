import time
import base64
import struct
from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, after_this_request, session
from flask_login import UserMixin, AnonymousUserMixin, login_user
from .. import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODERATE = 0x08
    ADMIN = 0x10

class ua_user(db.Model):
    __tablename__ = 'ua_users'
    ua_user_id = db.Column(db.Integer, primary_key=True)
    ua_user_name = db.Column(db.String(64), unique=True, index=True)
    ua_user_email = db.Column(db.String(128), unique=True, index=True)
    ua_user_nick = db.Column(db.String(64), unique=True, index=True)
    ua_pwd_hash = db.Column(db.String(128))
    ua_createtime = db.Column(db.DateTime(), default=datetime.utcnow)
    doc_author = db.relationship('res_doc', backref='doc_author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(ua_user, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.ua_pwd_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.ua_pwd_hash, password)

    def __repr__(self):
        return '<ua_user %r>' % self.ua_user_name

class User(UserMixin):

    def __init__(self, user_id, stophreat=False, **kwargs):
        self.id = user_id
        self.user_model = None

    @property
    def user(self):
        if self.user_model is None:
            self.user_model = ua_user.query.get(self.id)

        return self.user_model
    
    def data(self, key, val):
        if val is None:
            session.pop(key)
        else:
            session[key] = val

    def data(self, key):
        return session[key]        
       

@login_manager.user_loader
def load_user(key):
    sess = User(key)

    if sess.user is None:
        return None
    else:
        return sess



