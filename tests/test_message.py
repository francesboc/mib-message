from flask import json
from .view_test import ViewTest
from faker import Faker
import wget, base64

class TestMessage(ViewTest):
    faker = Faker('it_IT')

    @classmethod
    def setUpClass(cls):
        super(TestMessage, cls).setUpClass()

    def test_get_all(self):
        r = self.client.get('messages/all/1')
        assert r.status_code == 200
        print(r.data)


    def test_get_message_by_id(self):
        
        #---------------------------------------- img for message
        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        image = "/tmp/fluidicon.png"
        binary_img = (open(image, 'rb'))
        
        my_raw_img = []
        my_mimetypes = []
        
        binary_file_data = binary_img.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        my_raw_img.append(base64_message)
        my_mimetypes.append('image/png')
        #----------------------------------------
        
        #non existing msg
        r  = self.client.get('message/56')
        assert r.status_code == 404

        #create new msg
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
                'message_id': 0, #the id will be generated automatically
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': my_raw_img,
                'mimetypes': my_mimetypes}
        
        r  = self.client.post('message/send',json=data)
        assert r.status_code == 201
        print(r.data)
        
        print('o'*40)
        r = self.client.get('messages/all/1')
        print(r.data)
        
        r  = self.client.get('message/1')
        assert r.status_code == 200

       
       
    def test_receiver(self):
          
        #---------------------------------------- img for message
        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        image = "/tmp/fluidicon.png"
        binary_img = (open(image, 'rb'))
        
        my_raw_img = []
        my_mimetypes = []
        
        binary_file_data = binary_img.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        my_raw_img.append(base64_message)
        my_mimetypes.append('image/png')
        #----------------------------------------
          
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
                'message_id': 0, #id will be generated automatically
                'delete_image_ids': [],
                'delete_user_ids': [],
                'raw_images': my_raw_img,
                'mimetypes': my_mimetypes}
        
        r  = self.client.post('message/send',json=data)
        
        data = {
            "receiver": "1",
            "date": "2022-01-01 10:00",
            "filter": False}

        r = self.client.post('messages/received/', json=data)
        assert r.status_code == 200
  
        r = self.client.get('message/list/2/1')
        assert r.status_code == 200



    def test_draft(self):
          
      #---------------------------------------- img for message
      wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
      image = "/tmp/fluidicon.png"
      binary_img = (open(image, 'rb'))
      
      my_raw_img = []
      my_mimetypes = []
      
      binary_file_data = binary_img.read()
      base64_encoded_data = base64.b64encode(binary_file_data)
      base64_message = base64_encoded_data.decode('utf-8')
      my_raw_img.append(base64_message)
      my_mimetypes.append('image/png')
      #----------------------------------------
          
      data = {
            'payload': {
              'title': 'New Message to you',
              'content': '',
              'date_of_delivery': '2022-01-01',
              'time_of_delivery': '10:21',
              'font': 'Arial',
              'destinator': [
                3,
                1
              ]
            },
            'sender': 1,
            'message_id': 0, #id will be generated automatically
            'delete_image_ids': [],
            'delete_user_ids': [],
            'raw_images': my_raw_img,
            'mimetypes': my_mimetypes}
      
      r = self.client.post('message/draft',json=data)
      assert r.status_code == 201
      
      print('t'*60)
      r = self.client.get('messages/all/1')
      print(r.data)
      print('t'*60)
      
      delet_imgs = my_raw_img
      
      data = {
              'payload': {
                'title': 'New Message to delete',
                'content': '',
                'date_of_delivery': '2022-01-01',
                'time_of_delivery': '10:21',
                'font': 'Arial',
                'destinator': [
                  3,
                  1
                ]
              },
              'sender': 1,
              'message_id': 2, #id of a drafted msg
              'delete_image_ids': [],
              'delete_user_ids': [],
              'raw_images': my_raw_img,
              'mimetypes': my_mimetypes}

      
      
      #draft a already drafted msg
      data_2 = {
              'payload': {
                'title': 'New Message drafted to update cdknkcs',
                'content': '',
                'date_of_delivery': '2022-01-01',
                'time_of_delivery': '10:21',
                'font': 'Arial',
                'destinator': [
                  3,
                  1
                ]
              },
              'sender': 1,
              'message_id': 2, #id of a drafted msg
              'delete_image_ids': [1],
              'delete_user_ids': [3],
              'raw_images': my_raw_img,
              'mimetypes': my_mimetypes
              }

      r = self.client.post('message/draft',json=data)
      assert r.status_code == 200
      
      
      #send a drafted msg
      r = self.client.post('message/send',json=data_2)
      assert r.status_code == 200
          
      
    def test_delete_msg(self):
          
      #---------------------------------------- img for message
      wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
      image = "/tmp/fluidicon.png"
      binary_img = (open(image, 'rb'))
      
      my_raw_img = []
      my_mimetypes = []
      
      binary_file_data = binary_img.read()
      base64_encoded_data = base64.b64encode(binary_file_data)
      base64_message = base64_encoded_data.decode('utf-8')
      my_raw_img.append(base64_message)
      my_mimetypes.append('image/png')
      #----------------------------------------
          
      data = {
              'payload': {
                'title': 'New Message to delete',
                'content': '',
                'date_of_delivery': '2022-01-01',
                'time_of_delivery': '10:21',
                'font': 'Arial',
                'destinator': [
                  3,
                  1
                ]
              },
              'sender': 1,
              'message_id': 0, #id will be generated automatically
              'delete_image_ids': [],
              'delete_user_ids': [],
              'raw_images': my_raw_img,
              'mimetypes': my_mimetypes
              }
      
      data_2 = {
              'payload': {
                'title': 'hellooooooo',
                'content': '',
                'date_of_delivery': '2022-01-01',
                'time_of_delivery': '10:23',
                'font': 'Arial',
                'destinator': [
                  3,
                  1
                ]
              },
              'sender': 1,
              'message_id': 0, #id will be generated automatically
              'delete_image_ids': [],
              'delete_user_ids': [],
              'raw_images': my_raw_img,
              'mimetypes': my_mimetypes}
      
      r  = self.client.post('message/send',json=data)
      assert r.status_code == 201
      
      r  = self.client.post('message/send',json=data_2)
      assert r.status_code == 201
      
      print('*'*50)
      print("Gettin msg by id")
      r = self.client.get('messages/all/3')
      print(r.data)
      print('*'*50)
      
      r = self.client.delete('message/2')
      assert r.status_code == 200
      
      
      #delete a non existing msg
      r = self.client.delete('message/1456')
      assert r.status_code == 404
      
      

    def test_list_of_images(self):
        r = self.client.get('message/3/images')
        assert r.status_code == 200
        
    def test_forward_msg(self):
          data = {
            'destinators': [4,5],
            'messageid': '2'
          }
          r = self.client.post('message/forward/2', json = data)
          assert r.status_code == 200
          
          data = {
            'destinators': [],
            'messageid': '99'
          }
          r = self.client.post('message/forward/2', json = data)
          assert r.status_code == 400
          
          
          
   
    def test_send_with_images(self):
          
      wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
      image = "/tmp/fluidicon.png"
      binary_img = (open(image, 'rb'))
      
      my_raw_img = []
      my_mimetypes = []
      
      binary_file_data = binary_img.read()
      base64_encoded_data = base64.b64encode(binary_file_data)
      base64_message = base64_encoded_data.decode('utf-8')
      my_raw_img.append(base64_message)
      my_mimetypes.append('image/png')
      
      
      data_w_img = {
              'payload': {
                'title': 'New Message to you',
                'content': '',
                'date_of_delivery': '2022-01-01',
                'time_of_delivery': '10:21',
                'font': 'Arial',
                'destinator': [2,1]
              },
              'sender' : 1,
              'message_id': 0, #id will be generated automatically
              'delete_image_ids': [],
              'delete_user_ids': [],
              'raw_images': my_raw_img,
              'mimetypes': my_mimetypes}
          
      r = self.client.post('message/send',json=data_w_img)
      assert r.status_code == 201


    def test_x_no_destinators(self):
      data_no_dst = {
          'payload': {
            'title': 'New Message to you',
            'content': '',
            'date_of_delivery': '2022-01-01',
            'time_of_delivery': '10:21',
            'font': 'Arial',
            'destinator': []
          },
          'sender' : 1,
          'message_id': 0, #id will be generated automatically
          'delete_image_ids': [],
          'delete_user_ids': [],
          'raw_images': [],
          'mimetypes': []}
          
      r = self.client.post('message/send',json=data_no_dst)
      assert r.status_code != 201
      
      
    #it's impourtant to see that we use neutrino API and we only have 50 request/day
    def test_xx_msg_with_content(self):
          
      wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
      image = "/tmp/fluidicon.png"
      binary_img = (open(image, 'rb'))
      
      my_raw_img = []
      my_mimetypes = []
      
      binary_file_data = binary_img.read()
      base64_encoded_data = base64.b64encode(binary_file_data)
      base64_message = base64_encoded_data.decode('utf-8')
      my_raw_img.append(base64_message)
      my_mimetypes.append('image/png')
          
      data = {
          'payload': {
            'title': 'New Message to you',
            'content': 'fuck fuck',
            'date_of_delivery': '2022-01-01',
            'time_of_delivery': '10:21',
            'font': 'Arial',
            'destinator': [7]
          },
          'sender' : 1,
          'message_id': 0, #id will be generated automatically
          'delete_image_ids': [],
          'delete_user_ids': [],
          'raw_images': my_raw_img,
          'mimetypes': my_mimetypes}
          
      r = self.client.post('message/send',json=data)
      
      resp_conent = str(r.data, 'utf-8')
      print(resp_conent)
      
      if "Error with NeutrinoApi" in resp_conent: #request limit reached
        assert r.status_code == 400
      else:
        assert r.status_code == 201
      
