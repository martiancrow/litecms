import time
import base64
import struct
import bleach
from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, after_this_request
from sqlalchemy import func
from .. import db, login_manager

class res_docclass(db.Model):
    __tablename__ = 'res_docclasses'
    docclass_id = db.Column(db.Integer, primary_key=True)
    docclass_pid = db.Column(db.Integer, db.ForeignKey('res_docclasses.docclass_id'), default=0)
    docclass_name = db.Column(db.String(128))
    docclass_createtime = db.Column(db.DateTime(), default=datetime.utcnow)
    child_classes = db.relationship('res_docclasses', lazy='dynamic', cascade="all, delete-orphan")
    doc_class = db.relationship('res_docs', backref='doc_class', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(res_docclass, self).__init__(**kwargs)
        
    @property
    def doccount(self):
        if self.docclass_id:
            return db.session.query(func.count(res_doc.doc_id)).filter_by(doc_cid=self.docclass_id).first()[0]
        else:
            return None

    
    def __repr__(self):
        return '<res_docclass %r>' % self.docclass_name

class res_doc(db.Model):
    __tablename__ = 'res_docs'
    doc_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('res_docclasses.docclass_id'), default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('ua_users.ua_user_id'))
    doc_picurl = db.Column(db.String(512), default=None)
    doc_title = db.Column(db.String(64))
    doc_summary = db.Column(db.String(512))
    doc_content_html = db.Column(db.Text)
    doc_sort = db.Column(db.Integer, default=0)
    doc_isshow = db.Column(db.Boolean, default=True)
    doc_updatetime = db.Column(db.DateTime(), default=datetime.utcnow)
    doc_createtime = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(res_doc, self).__init__(**kwargs)
        self.doc_updatetime = datetime.utcnow()

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            p = res_doc(doc_title=forgery_py.lorem_ipsum.title(),
                    doc_content_html=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                    doc_updatetime=forgery_py.date.date(True),
                    doc_createtime=forgery_py.date.date(True),
                    author_id=1)
            db.session.add(p)
            db.session.commit()

    def __repr__(self):
        return '<res_doc %r>' % self.doc_title


class res_file(db.Model):
    __tablename__ = 'res_files'
    file_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('ua_users.ua_user_id'))
    file_name = db.Column(db.String(128))
    file_type = db.Column(db.String(64))
    file_data = db.Column(db.LargeBinary)
    file_uri = db.Column(db.String(512))
    file_isextern = db.Column(db.Boolean, default=False)
    file_createtime = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(res_file, self).__init__(**kwargs)

    
    def __repr__(self):
        return '<res_file %r>' % self.file_name
        



