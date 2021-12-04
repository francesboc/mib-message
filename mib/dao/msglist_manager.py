from sqlalchemy.sql.functions import user
from mib.dao.manager import Manager
from mib.models.message import msglist
from sqlalchemy import insert
from mib import db # maybe not needed

class MsglistManager(Manager):

    @staticmethod
    def add_receivers(message_id: str, list_of_receivers: list):
        for receiver_id in list_of_receivers:
            stmt = (
                insert(msglist).
                values(msg_id=message_id, user_id=receiver_id)
            )
            db.session.execute(stmt)
        db.session.commit()

    @staticmethod
    def get_receivers(message_id: str):
        receivers_list =  db.session.query(msglist.c.user_id).filter(msglist.c.msg_id==message_id).all()
        receivers_ids = []
        for i in range(0,len(receivers_list)):
            receivers_ids.append(receivers_list[i][0])
        return receivers_ids

    @staticmethod
    def update_receivers(message_id: str, user_id_to_delete: list, list_of_receivers: list):
        # delete receivers
        for id in user_id_to_delete:
            db.session.query(msglist).filter(msglist.c.msg_id == message_id).filter(msglist.c.user_id == id).delete()
        # add new receivers
        for receiver_id in list_of_receivers:
            stmt = (
                insert(msglist).
                values(msg_id=message_id, user_id=receiver_id)
            )
            db.session.execute(stmt)
        db.session.commit()
