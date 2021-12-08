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
import random 
from smtplib import SMTPRecipientsRefused
import requests

from sqlalchemy.util.langhelpers import MemoizedSlots
from mib import create_app

BACKEND = BROKER = 'redis://message_ms_redis:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

celery.conf.timezone = 'Europe/Rome'
_APP = None

@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):
   # Calls check_messages() task every 5 minutes to send email for unregisred users
    sender.add_periodic_task(300.0, check_messages.s(), name='checking messages every 5 minutes')

# task fo the lottery
@celery.task
def check_messages():
    global _APP
    # lazy init
    if _APP is None:
        from mib import Message, Mail
        from mib.dao.image_manager import ImageManager
        from mib.dao.message_manager import MessageManager
        from mib.dao.msglist_manager import MsglistManager

        app = create_app()
        mail = Mail(app)
        with app.app_context():
            #Checking all the messages not yet delivered that needs to be notified
            date = datetime.now()
            _messages = MessageManager.get_messages_by_date(date,is_draft=False)
            msglist = []
            for message in _messages:
                receivers = MsglistManager.get_msglist_not_delivered(message.id, read=False, notified=False)
                msglist.append(receivers)
            # msglist contains all user that received a message not yet read or notified
            try:
                user_list = requests.get("http://users_ms_worker:5000/users",timeout=5)
                json_payload = user_list.json()
                if user_list.status_code == 200:
                    list_user = json_payload['users_list']
                else:
                    raise RuntimeError('Server has sent an unrecognized status code %s' % user_list.status_code)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                return 
            
            for msglist_obj in msglist:
                for user in list_user:
                    if(msglist_obj.receiver_id == user['id']):
                        continue
            for user in list_user:
                
                if user['id'] == :
                if usr['firstname'].startswith(s) == True:
                    return  dumps({'id':usr['id'],'firstname' : usr['firstname'], 'lastname':usr['lastname'],'email':usr['email']})
            _messages = db.session.query(Messages.id, Messages.title, Messages.content, 
                    Messages.date_of_delivery, User.id, User.is_active,
                    User.email, msglist.c.notified, Messages.sender)\
                .filter(Messages.date_of_delivery<=(datetime.now()))\
                .filter(Messages.is_draft==False, msglist.c.read==False) \
                .filter(Messages.id==msglist.c.msg_id,User.id == msglist.c.user_id,msglist.c.notified==False)
            for result in _messages:
                """Background task to send an email with Flask-Mail."""
                # Generating the email
                subject = result[1]
                body = result[2]
                to_email = result[6]
                receiver_id = result[4]
                msg_id = result[0]
                message_sender = result[8]
                user_is_active = result[5]

                # Check if the sender is in the blacklist of the receiver
                _blacklist = db.session.query(blacklist.c.user_id, blacklist.c.black_id) \
                    .filter(blacklist.c.user_id == receiver_id) \
                    .filter(blacklist.c.black_id == message_sender).first()

                if _blacklist is None: # receivers doesn't block sender
                    
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
                        
                    msg = Message(email_data['subject'], sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
                    msg.body = email_data['body']

                    # Take images to attach it to email
                    _images = db.session.query(Images.id,Images.image, Images.mimetype, Images.message)\
                            .filter(Images.message == msg_id).all()
                        
                    for image in _images:
                        msg.attach(str(image.id), image.mimetype, image.image)

                    try:
                        mail.send(msg)
                    except SMTPRecipientsRefused:
                        print("Error in sending E-mail")

                

                # updating notified status
                stmt = (
                    update(msglist).
                    where(msglist.c.msg_id==msg_id, msglist.c.notified == False, msglist.c.user_id==receiver_id).
                    values(notified=True)
                )
                db.session.execute(stmt)
            db.session.commit()
    else:
        app = _APP
    return []
    

"""@worker_ready.connect
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
    return []"""