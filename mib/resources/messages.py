from flask import request, jsonify
from mib.dao.message_manager import MessageManager
from mib.models import message
from mib.models.message import Message, Image
import datetime

def get_messages(sender_id):
    """Get the list of sent and drafted messages
    """

    # Need to check the presence of message with sender_id?

    _sent_messages = MessageManager.retrieve_sent_by_id(sender_id)
    _drafted_messages = MessageManager.retrieve_drafted_by_id(sender_id)

    sent_serialized = [ message.serialize() for message in _sent_messages]
    draft_serialized = [ message.serialize() for message in _drafted_messages]

    return jsonify({"_sent": sent_serialized, "_draft": draft_serialized}), 200

def get_messages_receive(receiver_id):
    return 'TODO'
def get_messages_send(sender_id):
    return 'TODO'
def get_messages_draft(sender_id):
    return 'TODO'


# Check if the message data are correct
def verif_data(data):
    if len(data["destinator"])>=1: # At least one receiver
        if data["date_of_delivery"] != "" and data["time_of_delivery"] != "": #check the oresence of delivery date and time
            new_date = data["date_of_delivery"] +" "+data["time_of_delivery"] #concat date and time
            delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
            if delivery>datetime.today(): #check that delivery date is in future
                return "OK"
        return "Date not valid"
    else:
        return "No destinator"

def send():
    get_data = request.get_json()
    r = verif_data(get_data) #check on date of delivery
    if r=="OK":
        msg = Message()
        msg.sender= get_data['sender']
        msg.title = get_data['title']
        msg.content = get_data['content']
        msg.date_of_delivery = datetime.strptime(get_data['date_of_delivery'],'%Y-%m-%d %H:%M')
        msg.font = get_data["font"]
        result = API_call(get_data['content']) # Check for bad content
        if(result['is-bad']==True):
            msg.bad_content=True
            msg.number_bad = len(result["bad-words-list"])
        else:
            msg.bad_content=False
            msg.number_bad = 0
    response_object = {
        'status': 'success',
        'message': 'Successfully registered', }
    return jsonify(response_object), 201

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