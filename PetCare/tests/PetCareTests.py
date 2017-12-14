import os, sys, time
import unittest, tempfile, uuid
from mock import patch, Mock, MagicMock
from StringIO import StringIO
from flask import session
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run as PC
from blueprints.Entities import Entities
from blueprints.EmailHandler import EmailHandler
from blueprints.ImageHandler import ImageHandler
from blueprints.Daos.AccountDao import AccountDao
from blueprints.Daos.PostDao import PostDao

class PetCareTests(unittest.TestCase):

    def setUp(self):
        self.databaseFile, PC.app.config['DATABASE'] = tempfile.mkstemp(dir="tests")
        PC.app.testing = True
        self.app = PC.app.test_client()
        with PC.app.app_context():
            PC.init_db()
        mockUUID = uuid
        mockUUID.uuid4 = Mock(side_effect=['id_1', 'code_1', 'id_2', 'code_2'])
        mockEmailHandler = EmailHandler
        mockEmailHandler.send_email = Mock()
        mockImageHandler = ImageHandler
        mockImageHandler.save_image = Mock(side_effect=['image1.jpg', 'image2.jpg', 'image3.jpg'])

    def tearDown(self):
        os.close(self.databaseFile)
        os.remove(PC.app.config['DATABASE'])

    def generate_account(self, k):
        return {
            'email' : 'email_' + str(k),
            'password' : 'password_' + str(k),
            'name' : 'name' + str(k),
            'gender' : 1,
            'age' : 20,
            'department' : 'CSE',
            'college' : 'UCSD'
        }

    def generate_post(self):
        return {
            'name' : 'pet',
            'species' : 'dog',
            'breed' : 'corgi',
            'gender' : 1,
            'age' : 2,
            'vaccination' : 'rabis',
            'start_date' : '2020-01-01',
            'end_date' : '2020-01-05',
            'criteria' : '0',
            'notes' : 'hahahaha',
            'image1' : (StringIO('image1'), 'image1.jpg'),
            'image2' : (StringIO('image2'), 'image2.jpg'),
            'image3' : (StringIO('image3'), 'image3.jpg')
        }

    def register_and_authenticate(self, client, k):
        client.post('/register', data=self.generate_account(k), follow_redirects=True)
        client.get('/authenticate?userId=id_{0}&code=code_{0}'.format(str(k)), follow_redirects=True)
        assert session['logged_in'] == 'id_' + str(k)

    def login(self, client, k):
        client.post('/login', data={'email':'email_'+str(k), 'password':'password_'+str(k)}, follow_redirects=True)
        assert session['logged_in'] == 'id_' + str(k)

    def logout(self, client):
        client.get('/logout', follow_redirects=True)
        assert session.get('logged_in') is None

    def create_and_view_post(self, client):
        client.post('/create_post', data=self.generate_post(), follow_redirects=True)
        response = client.get('/view_post?postId=1', follow_redirects=True)
        assert b'corgi' in response.data and b'hahahaha' in response.data

    def view_profile(self, client, k, expects):
        response = client.get('/profile?userId=id_'+str(k), follow_redirects=True)
        for expect in expects:
            assert expect in response.data

    def interest_post(self, client):
        client.post('/interest_post', data={'postId':1}, follow_redirects=True)

    def match_post(self, client, k):
        client.post('/match', data={'userId':'id_'+str(k)}, follow_redirects=True)

    def review_post(self, client, score):
        client.post('/review', data={'review':score}, follow_redirects=True)

    def test_register(self):
        with PC.app.test_client() as client:
            client.post('/register', data=self.generate_account(1), follow_redirects=True)
            account = AccountDao().get_account_info('id_1')
            assert account['email'] == 'email_1' and account['verified'] == 0

    def test_authenticate(self):
        with PC.app.test_client() as client:
            with PC.app.app_context():
                accountInfo = self.generate_account(1)
                accountInfo['id'] = 'id_1'
                accountInfo['code'] = 'code_1'
                AccountDao().add_account(accountInfo)
                client.get('/authenticate?userId=id_1&code=code_1', follow_redirects=True)
                account = AccountDao().get_account_info('id_1')
                assert account['email'] == 'email_1' and account['verified'] == 1
                assert session['logged_in'] == 'id_1'

    def test_register_and_authenticate(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)

    def test_login(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            self.logout(client)
            self.login(client, 1)

    def test_profile(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            self.view_profile(client, 1, [b'email_1'])

    def test_create_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            response = client.post('/create_post', data=self.generate_post(), follow_redirects=True)
            assert b'pet' in response.data and b'hahahaha...' in response.data

    def test_view_post(self):
        with PC.app.test_client() as client:
            with PC.app.app_context():
                self.register_and_authenticate(client, 1)
                postInfo = self.generate_post()
                postInfo['owner_id'] = 'id_1'
                postInfo['start_date'] = int(time.mktime(time.strptime(postInfo['start_date'], '%Y-%m-%d')))
                postInfo['end_date'] = int(time.mktime(time.strptime(postInfo['end_date'], '%Y-%m-%d')))
                postInfo['post_date'] = int(time.time())
                for i in ['image1', 'image2', 'image3']:
                    postInfo[i] = i + '.jpg'
                PostDao().add_post(postInfo)
                response = client.get('/view_post?postId=1', follow_redirects=True)
                assert b'corgi' in response.data and b'hahahaha' in response.data and b'Edit' in response.data and b'Delete' in response.data

    def test_create_and_view_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            self.create_and_view_post(client)

    def test_interest_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            client.post('/create_post', data=self.generate_post(), follow_redirects=True)
            self.register_and_authenticate(client, 2)
            self.interest_post(client)
            post = PostDao().get_post(1)
            assert post['interested'] == 'id_2'
            self.login(client, 1)
            self.view_profile(client, 2, [b'Approve'])

    def test_match_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            client.post('/create_post', data=self.generate_post(), follow_redirects=True)
            self.register_and_authenticate(client, 2)
            PostDao().add_interest(1, 'id_2')
            self.login(client, 1)
            self.match_post(client, 2)
            self.view_profile(client, 2, [b'Review'])

    def test_review_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            postInfo = self.generate_post()
            client.post('/create_post', data=postInfo, follow_redirects=True)
            self.register_and_authenticate(client, 2)
            PostDao().add_interest(1, 'id_2')
            self.login(client, 1)
            self.match_post(client, 2)
            self.review_post(client, 1)
            account = AccountDao().get_account_info('id_2')
            post = PostDao().get_post(1)
            assert account['reputation_sum'] == 9 and account['reputation_num'] == 3 and post['review'] == 1

    def test_interest_and_match_and_review_post(self):
        with PC.app.test_client() as client:
            self.register_and_authenticate(client, 1)
            self.create_and_view_post(client)
            self.register_and_authenticate(client, 2)
            self.interest_post(client)
            self.login(client, 1)
            self.match_post(client, 2)
            post = PostDao().get_post(1)
            postInfo = dict(post)
            postInfo['end_date'] = int(time.mktime(time.strptime('2000-01-01', '%Y-%m-%d')))
            PostDao().update_post(postInfo)
            self.review_post(client, 5)
            ownerAccount = AccountDao().get_account_info('id_1')
            account = AccountDao().get_account_info('id_2')
            assert account['reputation_sum'] == 13 and account['reputation_num'] == 3 and ownerAccount['current_post'] is None

if __name__ == '__main__':
    unittest.main()