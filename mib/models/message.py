from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from mib import db


class Messages(db.Model):
    """Representation of User model."""

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    #receivers = relationship('User', secondary=msglist)
    date_of_delivery = db.Column(db.DateTime)
    content = db.Column(db.Text)
    title = db.Column(db.Text)
    bad_content = db.Column(db.Boolean) #if the message contains bad words
    number_bad = db.Column(db.Integer) #number of bad words in the message
    images = relationship("Images", cascade="all,delete", backref="messages")
    font = db.Column(db.Unicode(128), default = "Times New Roman") 
    is_draft = db.Column(db.Boolean, default=False)
    
    
    def __init__(self, *args, **kw):
        super(Messages, self).__init__(*args, **kw)

    def set_sender(self, val):
        self.sender = val

    def set_content(self, txt_):
        self.content = txt_

    def set_delivery_date(self, val):
        self.date_of_delivery = val

    def get_id(self):
        return self.id

class Images(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=False) # data of the image
    message = db.Column(db.Integer, db.ForeignKey('messages.id')) # msg in witch the image is
    mimetype = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kw):
        super(Images, self).__init__(*args, **kw)
