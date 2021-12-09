from re import S
from sqlalchemy.orm import relationship
from mib import db
import base64


class Message(db.Model):
    """Representation of User model."""

    __tablename__ = 'Message'
    
    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'sender', 'title', 'content', 'date_of_delivery', 'font', 'is_draft','bad_content']

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
    receivers = relationship('Msglist', cascade="all,delete", backref="Message")
    
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
        serialized =  dict([(k,self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
        serialized['receivers'] = [ k.receiver_id for k in self.receivers]
        return serialized

class Msglist(db.Model):

    __tablename__ = 'Msglist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Integer, db.ForeignKey('Message.id')) # msg in witch the image is
    receiver_id = db.Column(db.Integer, nullable=False)
    read = db.Column(db.Boolean, default=False)
    read_notification = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)
    hasReported = db.Column(db.Boolean, default=False) #this is to know if a user has already reported a specific message

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'message_id', 'receiver_id', 'read', 'notified', 'hasReported']

    def get_id(self):
        return self.id
    
    def set_message_id(self, id):
        self.message_id = id 

    def set_receiver_id(self, id):
        self.receiver_id = id
    
    def set_read(self, read):
        self.read = read

    def set_notified(self, notified):
        self.notified = notified

    def set_has_reported(self, report):
        self.hasReported = report

    def serialize(self):
        return dict([(k,self.__getattribute__(k)) for k in self.SERIALIZE_LIST])

class Image(db.Model):

    __tablename__ = 'Image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=False) # data of the image
    message = db.Column(db.Integer, db.ForeignKey('Message.id')) # msg in witch the image is
    mimetype = db.Column(db.Text, nullable=False)

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'message', 'mimetype']

    def __init__(self, *args, **kw):
        super(Image, self).__init__(*args, **kw)
    
    def set_image(self, image):
        self.image = image
    
    def set_mimetype(self, mimetype):
        self.mimetype = mimetype
    
    def set_message(self, message):
        self.message = message

    def serialize(self):
        serialized =  dict([(k,self.__getattribute__(k)) for k in self.SERIALIZE_LIST])
        image = self.__getattribute__('image')
        # encoding image
        base64_encoded_data = base64.b64encode(image)
        base64_image = base64_encoded_data.decode('utf-8')
        serialized['image'] = base64_image

        return serialized