from flask import json
from .view_test import ViewTest
from faker import Faker


class TestMessage(ViewTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestMessage, cls).setUpClass()

    def test_get_all(self):
        r = self.client.get('messages/all/1')
        assert r.status_code == 200

    def test_get_message_by_id(self):
        r  = self.client.get('message/56')
        assert r.status_code == 404

        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                    2,
                    1
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/send',json=data)
        r  = self.client.get('message/1')
        assert r.status_code == 200
        """
    def test_receiver(self):
        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                    2,
                    1
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/send',json=data)
        data = {
            "receiver": "1",
            "date": "2022-01-01 10:00",
            "filter": False}

        r = self.client.post('messages/received')
        #assert r.status_code == 200"""

    def test_send_draft(self):
        data = {
             "payload": {
               "title": "New Message to you",
               "content": "",
               "date_of_delivery": "2022-01-01",
               "time_of_delivery": "10:21",
               "font": "Arial",
               "destinator": [
                 2,
                 1
               ]
             },
             "sender": 1,
             "message_id": 0,
             "delete_image_ids": [],
             "delete_user_ids": [],
             "raw_images": [],
             "mimetypes": []}
        r = self.client.post("/message/draft",json=data)
        assert r.status_code ==201

        data = {
             "payload": {
               "title": "New Message to you",
               "content": "",
               "date_of_delivery": "2022-01-01",
               "time_of_delivery": "10:21",
               "font": "Arial",
               "destinator": [
                 2,
                 1
               ]
             },
             "sender": 1,
             "message_id": 1,
             "delete_image_ids": [],
             "delete_user_ids": [],
             "raw_images": [],
             "mimetypes": []}
        r = self.client.post("/message/draft",json=data)
        assert r.status_code ==200

        data = {
             "payload": {
               "title": "New Message to you",
               "content": "",
               "date_of_delivery": "2022-01-01",
               "time_of_delivery": "10:21",
               "font": "Arial",
               "destinator": []
             },
             "sender": 1,
             "message_id": 0,
             "delete_image_ids": [],
             "delete_user_ids": [],
             "raw_images": [],
             "mimetypes": []}
        r = self.client.post("/message/draft",json=data)
        assert r.status_code ==400

    def test_send_message(self):
        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                    2,
                    1
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/send',json=data)
        assert r.status_code == 201
        #No destinator
        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/send',json=data)
        assert r.status_code == 400
       
    
        
    def test_delete_draft(self):
        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                    2,
                    1
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/send',json=data)
        
        data = {
                'payload': {
                  'title': 'New Message to you',
                  'content': '',
                  'date_of_delivery': '2022-01-01',
                  'time_of_delivery': '10:21',
                  'font': 'Arial',
                  'destinator': [
                    2,
                    1
                  ]
                },
                'sender': 1,
                'message_id': 0,
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': [],
                'mimetypes': []}
        r  = self.client.post('message/draft',json=data)
        data={  "draftid": 12}
        r = self.client.delete('message/draft',json=data)
        assert r.status_code == 404
        data={  "draftid": 1}
        r = self.client.delete('message/draft',json=data)
        assert r.status_code == 404
        data={  "draftid": 1}
        r = self.client.delete('message/draft',json=data)
        #assert r.status_code == 200
    
    def test_delete_message_id(self):
        r = self.client.delete('message/134')
        assert r.status_code == 404
        r = self.client.delete('message/1')
        assert r.status_code == 200
