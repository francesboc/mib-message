from datetime import date, datetime
from typing import MutableSequence
from mib.dao.manager import Manager
from mib.models.message import Message,msglist
from sqlalchemy import update
from mib import db

class MessageManager(Manager):

    @staticmethod
    def create_message(message: Message):
        Manager.create(message=message)

    @staticmethod
    def retrieve_by_id(id_):
        Manager.check_none(id=id_)
        return Message.query.get(id_)

    @staticmethod
    def retrieve_sent_by_id(sender_id):
       return Message.query.filter(Message.id == sender_id).filter(Message.is_draft == False).all()

    @staticmethod
    def retrieve_drafted_by_id(sender_id):
        return Message.query.filter(Message.id == sender_id).filter(Message.is_draft == True).all()
    
    @staticmethod
    def update_draft(msg_id, title, content, new_date, font):
        stmt = (
            update(Message).
            where(Message.id==int(msg_id)).
            values(title=title, content=content,date_of_delivery=new_date,font=font)
        )
        
        db.session.execute(stmt)
        db.session.commit()   
    
    @staticmethod
    def get_all_new(rec_id):
        return Message.query.filter(Message.date_of_delivery<=datetime.now()).filter(msglist.c.user_id==rec_id,msglist.c.msg_id==Message.id).all()

    @staticmethod
    def delete_message(message: Message):
        Manager.delete(message=message)

    @staticmethod
    def delete_message_by_id(id_: int):
        user = MessageManager.retrieve_by_id(id_)
        MessageManager.delete_message(user)    

    #@staticmethod
    #def retrieve_by_email(email):
    #    Manager.check_none(email=email)
    #    return User.query.filter(User.email == email).first()
    #
    #@staticmethod
    #def retrieve_by_phone(phone):
    #    Manager.check_none(phone=phone)
    #    return User.query.filter(User.phone == phone).first()
#
    #@staticmethod
    #def update_user(user: User):
    #    Manager.update(user=user)
#
#
    ##retrieve all users in the DB filtering 
    #@staticmethod
    #def retrieve_all():
    #    return User.query.all()
    
