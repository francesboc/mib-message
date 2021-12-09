#from mib import create_app, create_celery
#
#flask_app = create_app()
#app = create_celery(flask_app)
#
#try:
#    import mib.tasks
#except ImportError:
#    raise RuntimeError('Cannot import celery tasks')
from datetime import date, datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from smtplib import SMTPRecipientsRefused
import requests
import os
from celery.signals import worker_ready
import requests

from sqlalchemy.util.langhelpers import MemoizedSlots
from mib import create_app

REDIS_HOST = os.getenv("REDIS_HOST", None)
USERS_MS_HOST = os.getenv("USERS_MS_HOST", None)
BACKEND = BROKER = ""
if REDIS_HOST != None:
    BACKEND = BROKER = 'redis://'+ REDIS_HOST +':6379'

if USERS_MS_HOST != None: 
    USERS_MS = 'http://'+USERS_MS_HOST+':5000'

celery = Celery(__name__, backend=BACKEND, broker=BROKER)


celery.conf.timezone = 'Europe/Rome'
_APP = None

@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
   # Calls check_messages() task every 5 (300) minutes to send email for unregisred users
    sender.add_periodic_task(20.0, check_messages.s(), name='checking messages every 5 minutes')
    sender.add_periodic_task(5.0, notify.s(), name='Check notification for read messages every 5 minutes')

# task fo the lottery
@celery.task
def check_messages():
    """Background task to send an email with Flask-Mail."""
    global _APP
    # lazy init
    if not _APP:
        return
    with _APP.app_context():
        from mib import Message, Mail
        from mib.dao.image_manager import ImageManager
        from mib.dao.message_manager import MessageManager
        from mib.dao.msglist_manager import MsglistManager

        mail = Mail(_APP)
        #with app.app_context():
        #Checking all the messages not yet delivered that needs to be notified
        date = datetime.now()
        _messages = MessageManager.get_messages_by_date(date,is_draft=False)
        # Retrive the message list
        try:
            user_list = requests.get("%s/users" % (USERS_MS),timeout=5)
            json_payload = user_list.json()
            if user_list.status_code == 200:
                list_user = json_payload['users_list']
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % user_list.status_code)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return
        msglist = []
        for message in _messages:
            # Retrieving message list associated to the message
            msglist = MsglistManager.get_msglist_not_delivered(message.id, read=False, notified=False)
            #msglist.append(receivers)

            # msglist contains user that received a message not yet read or notified

            # here we need to send the mail to each receiver
            for receiver in msglist:
                for user in list_user:
                    if(receiver.receiver_id == user['id']):
                        # User data found in the list

                        # Check that sender is not in the blacklist of the receiver
                        try:
                            response = requests.get("%s/user/blacklist/%d" % (USERS_MS,user['id']), timeout=5)
                            json_payload = response.json()
                            if response.status_code == 200:
                                black_list = json_payload['black_list']
                            else:
                                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)
                        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                            print("Users MS not available")
                            break

                        black_listed_sender = False
                        for bad_user in black_list:
                            if(bad_user['id']==message.sender):
                                black_listed_sender=True
                                break

                        if black_listed_sender==False:
                            # Sender is not in the blacklist. Generating the email
                            subject = message.title
                            body = message.content
                            to_email = user['email']
                            receiver_id = receiver.receiver_id
                            msg_id = message.id
                            user_is_active = user['is_active']
                        
                            if user_is_active:
                                # we need to notify the user for a new message
                                email_data = {
                                    'subject': 'You received a new message!',
                                    'to': to_email,
                                    'body': 'Check the application for new messages'
                                }
                            else:
                                # we need to notify the unregistered user via email
                                email_data = {
                                    'subject': subject,
                                    'to': to_email,
                                    'body': body
                                }
                            
                            msg = Message(email_data['subject'], sender=_APP.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
                            msg.body = email_data['body']

                            # Take images to attach it to email
                            _images = ImageManager.get_message_images(msg_id)
                                
                            for image in _images:
                                msg.attach(str(image.id), image.mimetype, image.image)

                            try:
                                mail.send(msg)
                                MsglistManager.update_notified_user(msg_id,receiver_id)
                            except SMTPRecipientsRefused:
                                print("Error in sending E-mail")
                        break
    return []
    

@celery.task
def notify():
    """Background task to notify a user."""
    global _APP
    # lazy init
    if not _APP:
        return
    with _APP.app_context():
        from mib import Message, Mail
        from mib.dao.image_manager import ImageManager
        from mib.dao.message_manager import MessageManager
        from mib.dao.msglist_manager import MsglistManager

        mail = Mail(_APP)
        #Checking all the messages not yet delivered that needs to be notified
        date = datetime.now()
        _messages = MessageManager.get_messages_by_date(date,is_draft=False)

        for message in _messages:
            msglist = MsglistManager.get_msg_to_notify(message.id, read=True, read_notification=False)

            try:
                response = requests.get("%s/user/%d" % (USERS_MS, message.sender),timeout=5)
                if response.status_code == 200:
                    sender = response.json()['email']
                else:
                    return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                return

            for receiver in msglist:
                try:
                    response = requests.get("%s/user/%d" % (USERS_MS, receiver.receiver_id),timeout=5)
                    if response.status_code == 200:
                        receiver_mail = response.json()['email']
                    else:
                        return
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    return

                subject = "Notification"
                body = "The User "+receiver_mail+" has read the message with Title: \n"+message.title+"\n Content: \n"+message.content
                to_email = sender
    
                email_data = {
                        
                        'subject': subject,
                        'to': to_email,
                        'body': body
                    }

                msg = Message(email_data['subject'], sender=_APP.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
                msg.body = email_data['body']
            
                try:
                    mail.send(msg)
                    MsglistManager.update_read_notification(receiver.id)
                except SMTPRecipientsRefused:
                        print("Error in sending E-mail")
    return []

@worker_ready.connect
def init(sender, **k):
    with sender.app.connection() as c:
        sender.app.send_task('background.initialization', connection = c)

@celery.task
def initialization():
    global _APP
    if _APP is None:
        _APP = create_app()
    else:
        app = _APP
    return []