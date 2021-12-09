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
    def add_receivers(message_id: str, list_of_receivers: list):
        for receiver_id in list_of_receivers:
            msglist = Msglist()
            msglist.set_message_id(message_id)
            msglist.set_receiver_id(receiver_id)
            Manager.create(msglist=msglist)

    @staticmethod
    def get_receivers(message_id: str):
        _receivers = Msglist.query.filter(Msglist.message_id == message_id).all()
        return [ k.receiver_id for k in _receivers ]

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
    def report_user(msg_id,user_id):
        msg = MsglistManager.get_list_by_id_and_receiver(msg_id,user_id)
        if msg is not None:
            msg.set_has_reported(True)
            db.session.commit()
            return {'message':'OK'}
        else:
            return {'message':'not found'}