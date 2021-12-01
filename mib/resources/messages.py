from flask import request, jsonify
from mib.dao.message_manager import MessageManager
from mib.dao.image_manager import ImageManager
from mib.dao.msglist_manager import MsglistManager
from mib.models.message import Message, Image
from datetime import datetime

def get_all_messages(sender_id):
    """Get the list of sent and drafted messages
    """

    # Need to check the presence of message with sender_id?

    _sent_messages = MessageManager.retrieve_sent_by_id(sender_id)
    _drafted_messages = MessageManager.retrieve_drafted_by_id(sender_id)

    sent_serialized = [ message.serialize() for message in _sent_messages]
    draft_serialized = [ message.serialize() for message in _drafted_messages]

    return jsonify({"_sent": sent_serialized, "_draft": draft_serialized}), 200

def get_messages_received():
    return 

def get_messages_sent():
    return

def get_messages_drafted(sender_id):
    return 

def send_message():
    return

def draft_message():
    """This method allows the creation of a new drafted message.
    """
    post_data = request.get_json()
    list_of_images = request.files
    sender = post_data.get('sender')

    try: 
        # Get images previously uploaded that needs to be deleted
        image_id_to_delete = post_data.get('delete_image_ids')
    except KeyError:
        image_id_to_delete = []
    try:
        # Get users previously uploaded that needs to be deleted
        user_id_to_delete = post_data.get('delete_user_ids')
    except KeyError:
        user_id_to_delete = []

    list_of_receiver = set(post_data.get('destinator'))
    # allowing draft with at least one destinator specified
    if len(list_of_receiver) == 0:
        return jsonify({
            'message': 'Draft with no recipients'
        }), 400

    date_of_delivery = post_data.get('date_of_delivery')
    time_of_delivery = post_data.get('time_of_delivery')
    content = post_data.get('content')
    title = post_data.get('title')
    font = post_data.get('font')

    if font == "":
        font = "Times New Roman"
    try: 
        msg_id = post_data.get('message_id')
    except KeyError:
        msg_id = 0
    
    if msg_id != 0:
        # this message was already drafted, need to update it
        _message = MessageManager.retrieve_by_id(msg_id)

        MsglistManager.update_receivers(msg_id, user_id_to_delete, list_of_receiver)
        
        new_date = date_of_delivery +" "+time_of_delivery
        try:
            new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
        except ValueError:
            new_date = datetime.now().strftime('%Y-%m-%d') + " " + datetime.now().strftime('%H:%M')
            new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
        
        for image_id in image_id_to_delete:
            image = ImageManager.retrieve_by_id(image_id)
            ImageManager.delete(image)

        for image in list_of_images:
            # adding new images
            img = Image()
            img.set_image(list_of_images[image].read())
            img.set_mimetype(list_of_images[image].mimetype)
            img.set_message(msg_id)
            ImageManager.add_image(image)

        MessageManager.update_draft(msg_id, title, content, new_date, font)

        response_object = {
            'message': _message.serialize(),
            'status': 'success',
            'message': 'Successfully draft creation'
        }
        return jsonify(response_object), 200
    
    #Creating new Message
    message = Message()
    message.set_title(title)
    message.set_content(content)
    message.set_font(font)
    message.set_sender(sender)
    new_date = date_of_delivery +" "+time_of_delivery
    try:
        message.set_delivery_date(datetime.strptime(new_date,'%Y-%m-%d %H:%M'))
    except ValueError:
        new_date = datetime.now().strftime('%Y-%m-%d') + " " + datetime.now().strftime('%H:%M')
        message.set_delivery_date(datetime.strptime(new_date,'%Y-%m-%d %H:%M'))
    message.set_draft(True)

    MessageManager.create_message(message)
    MsglistManager.add_receivers(message.get_id(), list_of_receiver)

    for image in list_of_images:
        img = Image()
        img.set_image(list_of_images[image].read())
        img.set_mimetype(list_of_images[image].mimetype)
        img.set_message(message.get_id())
        ImageManager.add_image(image)

    response_object = {
        'message': message.serialize(),
        'status': 'success',
        'message': 'Successfully draft creation'
    }

    return jsonify(response_object), 201