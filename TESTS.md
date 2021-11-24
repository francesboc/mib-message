# How write tests for MessageInABottle

Due to Flask initialization issue, we have to write
a setup method for all unittest.TestCase classes.

The following example represents a very simple 
design pattern to be used when you write test cases.


```python
import unittest

class TestMyClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mib import create_app
        create_app('config.TestConfig')

        '''
            now you can import all 
            objects you need for testing,
            and set it as class properties
        '''
        from mib.models import user
        cls.user = user

    def test_restaurant(self):
        rest = self.user.User()
        # test it
``` 

In this way we fix the issue by executing the Flask initialization code in the setUpClass method, that is executed once before the execution of the tests in the class.

