from re import S
from sqlalchemy.orm import relationship
from mib import db


msglist = db.Table('msglist',
    db.Column('msg_id', db.Integer, db.ForeignKey('Message.id'), primary_key=True),
    db.Column('user_id', db.Integer, primary_key=True),
    db.Column('read',db.Boolean, default=False),
    db.Column('notified',db.Boolean, default=False),
    db.Column('hasReported', db.Boolean, default=False) #this is to know if a user has already reported a specific message
)

class Message(db.Model):
    """Representation of User model."""

    __tablename__ = 'Message'
    
    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'sender', 'title', 'content','date_of_delivery']

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
    receivers = relationship('Message', secondary=msglist,
        primaryjoin=id==msglist.c.msg_id,
        backref="msg_id")
    
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def set_sender(self, sender):
        self.sender = sender

    def set_content(self, txt):
        self.content = txt

    def set_title(self, title):
        self.title = title

    def set_font(self, font):
        self.font = font

    def set_delivery_date(self, date):
        self.date_of_delivery = date

    def set_draft(self, is_draft):
        self.is_draft = is_draft

    def get_id(self):
        return self.id
    
    def serialize(self):
        return dict([(k,self.__getattribute__(k)) for k in self.SERIALIZE_LIST])

class Image(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=False) # data of the image
    message = db.Column(db.Integer, db.ForeignKey('Message.id')) # msg in witch the image is
    mimetype = db.Column(db.Text, nullable=False)

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'image', 'message', 'mimetype']

    def __init__(self, *args, **kw):
        super(Image, self).__init__(*args, **kw)
    
    def set_image(self, image):
        self.image = image
    
    def set_mimetype(self, mimetype):
        self.mimetype = mimetype
    
    def set_message(self, message):
        self.message = message

    def serialize(self):
        serialized_dict = []
        for k in self.SERIALIZE_LIST:
            if k == 'image':
                serialized_dict.append((k,str(self.__getattribute__(k)).encode('base64')))
            else:
                serialized_dict.append((k,str(self.__getattribute__(k))))
        return serialized_dict