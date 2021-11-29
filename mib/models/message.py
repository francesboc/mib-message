from sqlalchemy.orm import relationship
from mib import db


msglist = db.Table('msglist',
    db.Column('msg_id', db.Integer, db.ForeignKey('Message.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('Message.sender'), primary_key=True),
    db.Column('read',db.Boolean, default=False),
    db.Column('notified',db.Boolean, default=False),
    db.Column('hasReported', db.Boolean, default=False) #this is to know if a user has already reported a specific message
)

class Message(db.Model):
    """Representation of User model."""

    __tablename__ = 'Message'
    
    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'sender', 'title', 'content']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.Integer)
    date_of_delivery = db.Column(db.DateTime)
    content = db.Column(db.Text)
    title = db.Column(db.Text)
    bad_content = db.Column(db.Boolean) #if the message contains bad words
    number_bad = db.Column(db.Integer) #number of bad words in the message
    images = relationship("Image", cascade="all,delete", backref="Message")
    font = db.Column(db.Unicode(128), default = "Times New Roman") 
    is_draft = db.Column(db.Boolean, default=False)
    
    
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def set_sender(self, sender):
        self.sender = sender

    def set_content(self, txt):
        self.content = txt

    def set_title(self, title):
        self.title = title

    def set_delivery_date(self, date):
        self.date_of_delivery = date

    def get_id(self):
        return self.id
    
    def serialize(self):
        return dict([(k,self.__getattribute__(k)) for k in self.SERIALIZE_LIST])

class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=False) # data of the image
    message = db.Column(db.Integer, db.ForeignKey('Message.id')) # msg in witch the image is
    mimetype = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kw):
        super(Image, self).__init__(*args, **kw)
