from mib.dao.manager import Manager
from mib.models.message import Message


class MessageManager(Manager):

    #@staticmethod
    #def create_user(user: User):
    #    Manager.create(user=user)

    @staticmethod
    def retrieve_by_id(id_):
        Manager.check_none(id=id_)
        return Message.query.get(id_)

    @staticmethod
    def retrieve_sent_by_id(sender_id):
        return []

    @staticmethod
    def retrieve_drafted_by_id(sender_id):
        return []
        
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
    #@staticmethod
    #def delete_user(user: User):
    #    Manager.delete(user=user)
#
    #@staticmethod
    #def delete_user_by_id(id_: int):
    #    user = UserManager.retrieve_by_id(id_)
    #    UserManager.delete_user(user)
#
    ##retrieve all users in the DB filtering 
    #@staticmethod
    #def retrieve_all():
    #    return User.query.all()
    
