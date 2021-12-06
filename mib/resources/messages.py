from flask import request, jsonify
from mib.dao.message_manager import MessageManager
from mib.dao.image_manager import ImageManager
from mib.dao.msglist_manager import MsglistManager
from mib.models.message import Message, Image, Msglist
from datetime import datetime
from dateutil.parser import parse
import base64
import json

def get_all_messages(sender_id):
    """Get the list of sent and drafted messages
    """

    # Need to check the presence of message with sender_id?

    _sent_messages = MessageManager.retrieve_sent_by_id(sender_id)
    _drafted_messages = MessageManager.retrieve_drafted_by_id(sender_id)

    sent_serialized = [ message.serialize() for message in _sent_messages]
    draft_serialized = [ message.serialize() for message in _drafted_messages]

    return jsonify({"_sent": sent_serialized, "_draft": draft_serialized}), 200

# Check if the message data are correct
def verif_data(data):
    if len(data["receivers"])>=1: # At least one receiver
        if data["date_of_delivery"] != "" and data["time_of_delivery"] != "": #check the oresence of delivery date and time
            delivery=merge_date_time(data['date_of_delivery'],data['time_of_delivery'])
            if delivery>datetime.today(): #check that delivery date is in future
                return "OK"
        return "Date not valid"
    else:
        return "No destinator"
        
def merge_date_time(date,time):
    new_date = date +" "+time
    new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
    return new_date

def API_call(content):
    import urllib.request,urllib.parse, urllib.error
    url = 'https://neutrinoapi.net/bad-word-filter'
    params = {
            'user-id': 'flaskapp10',
            'api-key': '6OEjKKMDzj3mwfwLJfRbmiOAXamekju4dQloU95eCAjPYjO1',
            'content': content
    }
    postdata = urllib.parse.urlencode(params).encode()
    if url.lower().startswith('http'):
        req = urllib.request.Request(url, data=postdata)
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode("utf-8"))
    
def send():
    get_data = request.get_json()
    r = verif_data(get_data) #check on date of delivery
    if r=="OK":
        message = Message()
        message.set_title(get_data["title"])
        message.set_content(get_data["content"])
        message.set_font(get_data["font"])
        message.set_sender(get_data["sender"])
        message.set_delivery_date( merge_date_time(get_data['date_of_delivery'],get_data['time_of_delivery']) )
        message.set_draft(False)

        result = API_call(get_data['content']) # Check for bad content
        if(result['is-bad']==True):
            message.bad_content=True
            message.number_bad = len(result["bad-words-list"])
        else:
            message.bad_content=False
            message.number_bad = 0
        MessageManager.create_message(message)
        MsglistManager.add_receivers(message.get_id(), get_data['receivers'])
        list_of_images = request.files
        for image in list_of_images:
            img = Image()
            img.set_image(list_of_images[image].read())
            img.set_mimetype(list_of_images[image].mimetype)
            img.set_message(message.get_id())
            ImageManager.add_image(image)
        
        
    response_object = {
        'status': r,
        'message': r, }
    return jsonify(response_object), 201


def get_messages_received(receiver_id):
    list_messages = Msglist.get_messages_by_receiver_id(receiver_id)
    result = [msg.serialize() for msg in list_messages]

    return jsonify({ "msg_list": result}), 200

def get_messages_sent():
    return

def get_messages_drafted(sender_id):
    return 

def get_message_by_id(message_id):
    message = MessageManager.retrieve_by_id(message_id)
    if message is not None:
        return jsonify(message.serialize()), 200

    return jsonify({
            'message': 'Message not found'
        }), 404

def delete_message_by_id(message_id):
    return MessageManager.delete_message_by_id(message_id)

def draft_message():
    """This method allows the creation of a new drafted message.
    """
    #post_data = json.loads(request.form["payload"])
    post_data = request.get_json()
    payload = post_data['payload']
   # 
    list_of_images = post_data.get('raw_images')
    list_of_mimetypes = post_data.get('mimetypes')

    sender = post_data.get('sender')
    image_id_to_delete = post_data.get('delete_image_ids')
    user_id_to_delete = post_data.get('delete_user_ids')

    list_of_receiver = payload["destinator"]
    # allowing draft with at least one destinator specified
    if len(list_of_receiver) == 0:
        return jsonify({
            'message': 'Draft with no recipients'
        }), 400

    date_of_delivery = payload["date_of_delivery"]
    time_of_delivery = payload["time_of_delivery"]
    content = payload["content"]
    title = payload["title"]
    font = payload["font"]

    if font == "":
        font = "Times New Roman"
        
    msg_id =  post_data.get('message_id')
    
    if msg_id != 0:
        # this message was already drafted, need to update it
        _message = MessageManager.retrieve_by_id(msg_id)

        MsglistManager.update_receivers(msg_id, user_id_to_delete, list_of_receiver)
        
        new_date = date_of_delivery +" "+time_of_delivery
        try:
            new_date = parse(new_date)
        except ValueError:
            new_date = datetime.now().strftime('%Y-%m-%d') + " " + datetime.now().strftime('%H:%M')
            new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
        
        for image_id in image_id_to_delete:
            image = ImageManager.retrieve_by_id(image_id)
            if image is not None:
                ImageManager.delete(image)

        for image, mimetype in zip(list_of_images,list_of_mimetypes):
            # adding new images
            base64_img_bytes = image.encode('utf-8')
            decoded_image_data = base64.decodebytes(base64_img_bytes)
            img = Image()
            img.set_image(decoded_image_data)
            img.set_mimetype(mimetype)
            img.set_message(msg_id)
            ImageManager.add_image(img)

        MessageManager.update_draft(msg_id, title, content, new_date, font)

        response_object = {
            'message_obj': _message.serialize(),
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
        new_date = parse(new_date)
        message.set_delivery_date(new_date)
    except ValueError:
        new_date = datetime.now().strftime('%Y-%m-%d') + " " + datetime.now().strftime('%H:%M')
        message.set_delivery_date(datetime.strptime(new_date,'%Y-%m-%d %H:%M'))
    message.set_draft(True)

    MessageManager.create_message(message)
    MsglistManager.add_receivers(message.get_id(), list_of_receiver)

    for image, mimetype in zip(list_of_images,list_of_mimetypes):
        base64_img_bytes = image.encode('utf-8')
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        img = Image()
        img.set_image(decoded_image_data)
        img.set_mimetype(mimetype)
        img.set_message(message.get_id())
        ImageManager.add_image(img)

    response_object = {
        'status': 'success',
        'message': message.serialize()
    }
    return jsonify(response_object), 201

def retrieve_message_images(message_id):
    """
    This method allows the retrival of images
    associated to a message
    """
    _images = ImageManager.get_message_images(message_id)
    response_object = {}
    for image in _images:
        response_object[image.id] = image.serialize()
    return jsonify(response_object),200


def delete_draft():
         #just delete the draft
        delete_data = request.get_json()
        id = delete_data['draftid']

        msg = MessageManager.retrieve_by_id(id)
        print(msg)
        if msg is not None:
            if msg.is_draft==True:
                MessageManager.delete_message_by_id(id)
                return jsonify({'content': "Message Deleted"}),200
            else:
                return jsonify({'content': "Message is not a draft"}),404
        else:
            return jsonify({'content': "Draft not present"}),404


#  elif msg_exist.is_draft == True:
#             #just delete the draft
#             delete_ = db.session.query(Messages).filter(Messages.id == msg_id).first()
#             db.session.delete(delete_)
#             db.session.commit()
#             return render_template('get_msg_send_draft.html', draft=_draft, send=_send)
#         else:
#             return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Something went wrong...")
