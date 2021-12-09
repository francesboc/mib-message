from datetime import date, datetime
from typing import MutableSequence
from mib.dao.manager import Manager
from mib.models.message import Message
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
    def retrieve_by_id_until_now(id, date):
        Manager.check_none(id=id)
        return Message.query.filter(Message.id == id) \
            .filter(Message.date_of_delivery <= date) \
            .filter(Message.is_draft==False).first()

    @staticmethod
    def retrieve_sent_by_id(sender_id):
       return Message.query.filter(Message.sender == sender_id).filter(Message.is_draft == False).all()

    @staticmethod
    def retrieve_drafted_by_id(sender_id):
        return Message.query.filter(Message.sender == sender_id).filter(Message.is_draft == True).all()
    
    @staticmethod
    def update_msg(msg_id, title, content, new_date, font, isDraft, bad_content, number_bad):
        stmt = (
            update(Message).
            where(Message.id==int(msg_id)).
            values(title=title, content=content,date_of_delivery=new_date,
                font=font,is_draft=isDraft, bad_content=bad_content, number_bad=number_bad)
        )
        
        db.session.execute(stmt)
        db.session.commit()   
    
    @staticmethod
    def get_messages_by_date(date, is_draft):
        return Message.query.filter(Message.date_of_delivery<=date).filter(Message.is_draft==is_draft).all()

    @staticmethod
    def delete_message(message: Message):
        Manager.delete(message=message)
   
    @staticmethod
    def delete_message_by_id(id_: int):
        message = MessageManager.retrieve_by_id(id_)
        MessageManager.delete_message(message)    
