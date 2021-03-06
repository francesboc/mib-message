from operator import pos
import re
from flask import request, jsonify
from mib.dao.message_manager import MessageManager
from mib.dao.image_manager import ImageManager
from mib.dao.msglist_manager import MsglistManager
from mib.models.message import Message, Image, Msglist
from datetime import datetime
from dateutil.parser import parse
import base64
from background import notify
import json

def get_all_messages(sender_id):
    """Get the list of sent and drafted messages
    """


    _sent_messages = MessageManager.retrieve_sent_by_id(sender_id)
    _drafted_messages = MessageManager.retrieve_drafted_by_id(sender_id)

    sent_serialized = [ message.serialize() for message in _sent_messages]
    draft_serialized = [ message.serialize() for message in _drafted_messages]

    return jsonify({"_sent": sent_serialized, "_draft": draft_serialized}), 200

# Check if the message data are correct
def verif_data(data):
    if len(data["destinator"])>=1: # At least one receiver
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
            'user-id': 'flaskapp11',
            'api-key': 'OqwP2B4TN0t7Iuj5r3rsxq3xOXLD2bG90vdPVv4EOxkc5Cq6',
            'content': content
    }
    postdata = urllib.parse.urlencode(params).encode()
    if url.lower().startswith('http'):
        req = urllib.request.Request(url, data=postdata)
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode("utf-8"))
    
def send():
    post_data = request.get_json()
    payload = post_data['payload']
    r = verif_data(payload) #check on date of delivery
    result = {}
    if r=="OK":
        #get the values from form fields
        list_of_receiver = payload["destinator"]
        date_of_delivery = payload["date_of_delivery"]
        time_of_delivery = payload["time_of_delivery"]
        content = payload["content"]
        # Check if fields are valid before send the message
        title = payload["title"]
        if title == "":
            return jsonify({
                'message': 'Message with empty title'
            }), 400
        
        list_of_images = post_data.get('raw_images')
        list_of_mimetypes = post_data.get('mimetypes')
        sender = post_data.get('sender')
        font = payload["font"]
        if font == "":
            font = "Times New Roman"
        if content != "":
            try:
                result = API_call(content)
            except Exception:
                return jsonify({
                    'message': 'Error with NeutrinoApi'
                }), 400
        else:
            result= {'is-bad': False}

        # Check if message was drafted and then sended
        
        msg_id =  post_data.get('message_id')

        if msg_id != 0:
            # message was drafted and then sent
            image_id_to_delete = post_data.get('delete_image_ids')
            user_id_to_delete = post_data.get('delete_user_ids')

            _message = MessageManager.retrieve_by_id(msg_id)
            MsglistManager.update_receivers(msg_id, user_id_to_delete, list_of_receiver)
            
            new_date = date_of_delivery +" "+time_of_delivery
            
            new_date = parse(new_date)
            
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

            #Setting the message (bad content filter) in database
          
            if(result['is-bad']==True):
                bad_content=True
                number_bad = len(result["bad-words-list"])
            else:
                bad_content=False
                number_bad = 0

            MessageManager.update_msg(msg_id, title, content, new_date, 
                font, isDraft=False, bad_content=bad_content, number_bad=number_bad)

            response_object = {
                'message_obj': _message.serialize(),
                'status': 'success',
                'message': 'Successfully message send'
            }
            return jsonify(response_object), 200

        #Creating new Message
        message = Message()
        message.set_title(title)
        message.set_content(content)
        message.set_font(font)
        message.set_sender(sender)
        new_date = date_of_delivery +" "+time_of_delivery

        new_date = parse(new_date)
        message.set_delivery_date(new_date)
        
        message.set_draft(False)
        
        #Setting the message (bad content filter) in database
        if(result['is-bad']==True):
            message.bad_content=True
            message.number_bad = len(result["bad-words-list"])
        else:
            message.bad_content=False
            message.number_bad = 0
        
        #add message
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
    else:
        return jsonify({
                'message': 'Invalid message: '+r
            }), 400


def get_messages_received():
    post_data = request.get_json()
    
    receiver_id = post_data['receiver']
    date = parse(post_data['date'])
    filter = post_data['filter']
    msglist = MsglistManager.get_messages_by_receiver_id(receiver_id)
    messages = []
    for elem in msglist:
        message = MessageManager.retrieve_by_id_until_now(elem.message_id,date)
        if message != None:
            if filter:
                #only message with bad_content == false
                if message.bad_content == False:
                    messages.append(message)
            else:
                #retrieve all messages
                messages.append(message)

    result = [msg.serialize() for msg in messages]

    return jsonify(result), 200



def get_message_by_id(message_id):
    message = MessageManager.retrieve_by_id(message_id)
    if message is not None:
        return jsonify(message.serialize()), 200

    return jsonify({
            'message': 'Message not found'
        }), 404

def delete_message_by_id(message_id):
    try:
        MessageManager.delete_message_by_id(message_id)
    except :
        response = {
        'status': 'Failed',
        'message': 'Message not found',}
        return jsonify(response), 404
    response = {
        'status': 'Succes',
        'message': 'Message delete',}
    return jsonify(response), 200

def draft_message():
    """This method allows the creation of a new drafted message.
    """
    post_data = request.get_json()
    payload = post_data['payload']

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

        MessageManager.update_msg(msg_id, title, content, new_date, 
            font, isDraft=True, bad_content=False, number_bad=0)

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
    message.bad_content = False
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
    i=0
    for image in _images:
        response_object[str(i)] = image.serialize()
        i=i+1
    return jsonify(response_object),200

def get_msglist_by_id(msg_id, receiver_id):
    msglist = MsglistManager.get_list_by_id_and_receiver(msg_id,receiver_id)
    return jsonify(msglist.serialize()),200


def delete_receiver(msg_id, receiver_id):
    MsglistManager.delete_receiver(msg_id,receiver_id)
    return jsonify({'message': 'success'}),200

def report(message_id,receiver_id):
    msg = MessageManager.retrieve_by_id(message_id)
    if not msg:
        return jsonify({'message':'This message does not exist'}),404
    if msg.bad_content == True:
        mesg = MsglistManager.report_user(message_id,receiver_id)
        if mesg['message'] == 'OK':
            return jsonify({'message':'This message has been correctly reported','id':msg.id}),200
        else:
            #this should never happen
            return jsonify({'message':'This message does not exist'}),404
    else:
        return jsonify({'message':'No bad wards detected'}), 201

def forward(user_id):
    post_data = request.get_json()
    destinators = post_data['destinators']
    msgid =post_data['messageid']
    ms = int(msgid)
    return MsglistManager.forward(user_id,destinators,ms)
    
def notify_read(msg_list_id):
    MsglistManager.update_read_user(msg_list_id)
    return jsonify({'message': 'success'}),200
