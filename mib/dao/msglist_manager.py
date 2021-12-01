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
