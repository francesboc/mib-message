from os import read
from flask.json import jsonify
from mib.dao.manager import Manager
from mib.models.message import Msglist
from sqlalchemy import insert, update,delete
from mib import db # maybe not needed

class MsglistManager(Manager):

    @staticmethod
    def get_msglist_not_delivered(message_id, read, notified):
        return Msglist.query.filter(Msglist.message_id==message_id) \
                .filter(Msglist.read==read).filter(Msglist.notified==notified).all()

    @staticmethod
    def get_msg_to_notify(message_id, read, read_notification):
        return Msglist.query.filter(Msglist.message_id==message_id) \
                .filter(Msglist.read==read).filter(Msglist.read_notification==read_notification).all()

    @staticmethod
    def add_receivers(message_id: str, list_of_receivers: list):
        for receiver_id in list_of_receivers:
            msglist = Msglist()
            msglist.set_message_id(message_id)
            msglist.set_receiver_id(receiver_id)
            Manager.create(msglist=msglist)

    @staticmethod
    def get_by_id(id:int):
        return Msglist.query.filter(Msglist.id==id).first()

    @staticmethod
    def get_receivers(message_id: str):
        _receivers = Msglist.query.filter(Msglist.message_id == message_id).all()
        return [ k.receiver_id for k in _receivers ]
    
    @staticmethod
    def update_notified_user(message_id, user_id):
        # updating notified status
        stmt = (
            update(Msglist).
            where(Msglist.message_id==message_id and Msglist.notified == False and Msglist.receiver_id==user_id).
            values(notified=True)
        )
        db.session.execute(stmt)
        db.session.commit()
    
    @staticmethod
    def update_read_notification(msglist_id):
        # updating notified status
        stmt = (
            update(Msglist).
            where(Msglist.id==msglist_id).
            values(read_notification=True)
        )
        db.session.execute(stmt)
        db.session.commit()
    
    @staticmethod
    def update_read_user(message_id):
        # updating notified status
        stmt = (
            update(Msglist).
            where(Msglist.id==message_id).
            values(read=True)
        )
        db.session.execute(stmt)
        db.session.commit()

    @staticmethod
    def update_receivers(message_id: str, user_id_to_delete: list, list_of_receivers: list):
        # delete receivers
        for id in user_id_to_delete:
            Msglist.query.filter(Msglist.message_id==message_id).filter(Msglist.receiver_id==id).delete()
        # add new receivers
        for receiver_id in list_of_receivers:
            # check if the receiver is already in msglist
            check = Msglist.query.filter(Msglist.message_id==message_id).filter(Msglist.receiver_id==receiver_id).first()
            if check is None:
                msglist = Msglist()
                msglist.set_message_id(message_id)
                msglist.set_receiver_id(receiver_id)
                Manager.create(msglist=msglist)
        db.session.commit()
    
    @staticmethod
    def delete_receiver(message_id: int, user_id: int):
        Msglist.query.filter(Msglist.message_id==message_id).filter(Msglist.receiver_id==user_id).delete()
        db.session.commit()

    @staticmethod
    def get_messages_by_receiver_id(receiver_id: int):
        return Msglist.query.filter(Msglist.receiver_id==receiver_id).all()
    
    @staticmethod
    def get_list_by_id_and_receiver(msg_id, receiver_id):
        return Msglist.query.filter(Msglist.message_id==msg_id).filter(Msglist.receiver_id==receiver_id).first()
    
    @staticmethod
    def forward(user_id,destinators,msgid):
        #check if the user is already inside
        users = Msglist.query.filter(Msglist.message_id==msgid).all()
        if(users != []):
            for d in destinators:
                if(aux_contains(users,d))==False:
                    msglist = Msglist()
                    msglist.set_message_id(msgid)
                    msglist.set_receiver_id(d)
                    Manager.create(msglist=msglist)
            db.session.commit()
            return jsonify({'status':'OK'}),200
        else:
            return jsonify({'status':'KO'}),400


            
    
def aux_contains(a,element):

        for i in a:
            if element == i.get_id():
                return True
        return False


            



