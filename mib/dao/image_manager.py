from os import stat

from sqlalchemy.sql.expression import delete
from mib.dao.manager import Manager
from mib.models.message import Image

class ImageManager(Manager):

    @staticmethod
    def add_image(image: Image):
        Manager.create(image=image)
    
    @staticmethod
    def retrieve_by_id(id_):
        Manager.check_none(id=id_)
        return Image.query.get(id_)

    @staticmethod
    def delete(image: Image):
        Manager.delete(image=image)

    @staticmethod
    def get_message_images(message_id):
        return Image.query.filter(Image.message==message_id).all()