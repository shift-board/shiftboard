from io import BytesIO
from PIL import Image as PImage
import time
import uuid

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, tag
from django.urls import reverse

from .models import Board, Image, Post

# Create your tests here.

class BoardModelTests(TestCase):
    """
    A class with tests for testing relationships with the `Board` database model.
    """

    def test_identical_photos(self):
        """Make sure that photos with identical names and BLOBs can still be added to the image table."""
        i1 = Image(name="shari", photo=bytearray("joseph", "utf-8"))
        i2 = Image(name="shari", photo=bytearray("joseph", "utf-8"))
        i1.save()
        i2.save()

        self.assertIsNot(i1, i2)

    @tag('core')
    def test_board_post_image_connections(self):
        """Make sure that boards and posts and their connections to an image does not throw errors."""
        b1 = Board(title="board1", description="bar")
        b1.save()

        i2 = Image(name="foo", photo=bytearray("bar", "utf-8"))
        i3 = Image(name="ham", photo=bytearray("sam", "utf-8"))
        i2.save()
        i3.save()

        b2 = Board(title="board2", description="foo", bg=i2)
        b2.save()

        self.assertIs(b2.bg, i2)
        self.assertIs(i2.board, b2)

        p1 = Post(associated_board=b2, name="p1", message="m1")
        p2 = Post(associated_board=b2, name="p1", message="m1", photo=Image(name="spam", photo=bytearray("eggs", "utf-8")).save())
        p3 = Post(associated_board=b2, name="p1", message="m1", photo=i3)
        p1.save()
        p2.save()
        p3.save()

        self.assertIs(p3.photo, i3)
        self.assertIs(i3.post, p3)
        self.assertIs(p2.photo.name, "spam")

    @tag('core')
    def test_board_post_connections(self):
        """Make sure that posts to a board are properly associated and posts can be found."""
        i1 = Image(name="1", photo=bytearray("1", "utf-8"))
        i2 = Image(name="2", photo=bytearray("2", "utf-8"))
        i3 = Image(name="3", photo=bytearray("3", "utf-8"))
        i1.save()
        i2.save()
        i3.save()

        b1 = Board(title="foo", description="bar", bg=i1)
        b2 = Board(title="foo2", description="bar", bg=i2)
        b1.save()
        b2.save()

        p1 = Post(associated_board=b1, name="a", message="b")
        p2 = Post(associated_board=b1, name="a", photo=i3)
        p3 = Post(associated_board=b2, name="a", message="b")
        p4 = Post(associated_board=b1, name="a", message="b")
        p1.save()
        p2.save()
        p3.save()
        p4.save()

        self.assertQuerysetEqual(b1.post_set.all(), [p1, p2, p4], ordered=False)
        self.assertQuerysetEqual(b2.post_set.all(), [p3], ordered=False)

    @tag('core')
    def test_admin_board_connections(self):
        """Make sure that admins for a board are properly associated and vice versa."""
        i1 = Image(name="1", photo=bytearray("1", "utf-8"))
        i2 = Image(name="2", photo=bytearray("2", "utf-8"))
        i3 = Image(name="3", photo=bytearray("3", "utf-8"))
        i1.save()
        i2.save()
        i3.save()

        b1 = Board(title="foo", description="bar", bg=i1)
        b2 = Board(title="foo2", description="bar", bg=i2)
        b3 = Board(title="foo3", description="bar", bg=i3)
        b1.save()
        b2.save()
        b3.save()

        u1 = User(username="foo", password="bar")
        u2 = User(username="baz", password="qux")
        u3 = User(username="spam", password="eggsham")
        u4 = User(username="waldo", password="fred")
        u1.save()
        u2.save()
        u3.save()
        u4.save()

        b1.admin_users.add(u1)
        b1.admin_users.add(u2)
        b1.admin_users.add(u4)
        b2.admin_users.add(u3)
        b3.admin_users.add(u1)

        self.assertQuerysetEqual(b1.admin_users.all(), [u1, u2, u4], ordered=False)
        self.assertQuerysetEqual(b2.admin_users.all(), [u3], ordered=False)
        self.assertQuerysetEqual(u1.board_set.all(), [b1, b3], ordered=False)
        self.assertQuerysetEqual(u2.board_set.all(), [b1], ordered=False)
        self.assertQuerysetEqual(u3.board_set.all(), [b2], ordered=False)
        self.assertQuerysetEqual(Board.objects.filter(admin_users__id=1), [b1, b3], ordered=False)
        self.assertQuerysetEqual(Board.objects.filter(admin_users__id=3), [b2], ordered=False)

    @tag('core')
    def test_post_creation_combinations(self):
        """Make sure that creating posts in different combinations doesn't break anything."""
        i1 = Image(name="1", photo=bytearray("1", "utf-8"), uuid=uuid.uuid4())
        i2 = Image(name="2", photo=bytearray("2", "utf-8"))
        i3 = Image(name="3", photo=bytearray("3", "utf-8"))
        i4 = Image(name="2", photo=bytearray("2", "utf-8"))
        i5 = Image(name="3", photo=bytearray("3", "utf-8"))
        i1.save()
        i2.save()
        i3.save()
        i4.save()
        i5.save()

        b1 = Board(title="foo", description="bar", bg=i1)
        b2 = Board(title="green eggs", description="and ham")
        b1.save()
        b2.save()

        # just make sure that none of these throw an exception when creating
        p1 = Post(associated_board=b1, message="post1")
        p2 = Post(associated_board=b1, name="author2", photo=i2)
        p3 = Post(associated_board=b1, photo=i3)
        p4 = Post(associated_board=b1, name="author4", message="post4", photo=i4)
        p5 = Post(associated_board=b1, message="post5", photo=i5)

        p1.save()
        p2.save()
        p3.save()
        p4.save()
        p5.save()



class APITests(TestCase):
    @tag('core')
    def test_get_board_details(self):
        """Get the board details of an existing board."""
        img = Image(name="shari", photo=bytearray("hi", "utf-8"))
        img.save()

        board = Board(title="hello", description="hi", bg=img)
        board.save()

        exp = {
            'title': 'hello',
            'description': 'hi',
            'bg': str(img.uuid),
        }
        
        res = self.client.get(
            reverse('board:board-details-get'), 
            {'board': str(board.uuid)},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(res.json(), exp)
    

    def test_board_details_invalid_uuid(self):
        """Returns a 404 not found if the board uuid does not exist while trying to get board details."""
        res = self.client.get(
            reverse('board:board-details-get'), 
            {'board': 'not-a-uuid'},
            HTTP_ACCEPT='application/json',
        )
        res2 = self.client.get(
            reverse('board:board-details-get'), 
            {'board': uuid.uuid4()},
            HTTP_ACCEPT='application/json',
        )
        res3 = self.client.get(
            reverse('board:board-details-get'),
        )

        self.assertEqual(res.status_code, 404)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(res3.status_code, 404)


    def test_board_details_invalid_req_method(self):
        """Returns a 405 for incorrect request method (post, delete, etc) when getting the board details."""
        res = self.client.post(reverse('board:board-details-get'))
        res2 = self.client.delete(reverse('board:board-details-get'))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res2.status_code, 405)

        

    @tag('core')
    def test_get_posts(self):
        """Make sure that it returns proper JSON responses with proper amount of posts."""


    def get_test_image(self, img_name):
        """Helper function returning a 5x5 pixel png file."""
        img = PImage.new('RGB', size=(5,5), color=(255,0,0))
        file = BytesIO()
        img.save(file, format='PNG')
        return SimpleUploadedFile(img_name, content=file.getvalue())

    @tag('core')
    def test_create_posts(self):
        """Creating a post given all fields."""
        b = Board(title='hi', description='hello')
        b.save()
        
        res = self.client.post(
            reverse('board:post-create'),
            {   
                'board': str(b.uuid),
                'name': 'bob',
                'message': 'hello world',
                'photo': self.get_test_image('test.png'),
            },
            HTTP_ACCEPT='application/json',
        )

        p = b.post_set.all()[0]
        # Ensuring it is properly saved in the database.
        self.assertEqual(p.name, 'bob')
        self.assertEqual(p.message, 'hello world')
        self.assertEqual(p.photo.name, 'test.png')
        self.assertEqual(p.photo.photo, self.get_test_image('test.png').read())

        exp = {
            'name': 'bob',
            'message': 'hello world',
            'photo': {
                'uuid': str(p.photo.uuid),
                'name': 'test.png',
            }
        }
        self.assertEqual(res.json(), exp)


    @tag('core')
    def test_create_posts_optional_fields(self):
        """Creating a post with only certain optional fields given."""

        b = Board(title='hi', description='hello')
        b.save()

        # Name + message field.
        res1 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'name': 'bob', 'message': 'hello world'},
            HTTP_ACCEPT='application/json',
        )
        exp1 = {
            'name': 'bob', 
            'message': 'hello world',
            'photo': None,
        }
        
        # Message field only.
        time.sleep(0.01) # Ensuring that there is a proper delay for the requests.
        res2 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'message': 'hello world2'},
            HTTP_ACCEPT='application/json',
        )
        exp2 = {
            'name': '', 
            'message': 'hello world2',
            'photo': None,
        }
        # Photo field only.
        time.sleep(0.01) # Ensuring that there is a proper delay for the requests.
        res3 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'photo': self.get_test_image('test.png')},
            HTTP_ACCEPT='application/json',
        )
        

        self.assertEqual(res1.json(), exp1)
        self.assertEqual(res2.json(), exp2)
          

        # Ensure that they're saved to the database properly.
        posts = b.post_set.all().order_by('created_at')
        p1, p2, p3 = posts

        self.assertEqual(p1.name, 'bob')
        self.assertEqual(p1.message, 'hello world')
        self.assertIs(p1.photo, None)

        self.assertIs(p2.name, '')
        self.assertEqual(p2.message, 'hello world2')
        self.assertIs(p2.photo, None)

        self.assertIs(p3.name, '')
        self.assertIs(p3.message, '')
        self.assertEqual(p3.photo.name, 'test.png')
        self.assertEqual(p3.photo.photo, self.get_test_image('test.png').read())
        exp3 = {
            'name': '', 
            'message': '',
            'photo': {
                'uuid': str(p3.photo.uuid), # Needed the UUID to test so it's moved here.
                'name': 'test.png',
            },
        }
        self.assertEqual(res3.json(), exp3)  


    def test_create_posts_missing_fields(self):
        """Posts should not be created if there are missing fields."""

        b = Board(title='hi', description='hello')
        b.save()

        # Name + Board field.
        res1 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'name': 'bob'},
            HTTP_ACCEPT='application/json',
        )
        
        # Board field.
        time.sleep(0.01) # Ensuring that there is a proper delay for the requests.
        res2 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid)},
            HTTP_ACCEPT='application/json',
        )

        # None
        time.sleep(0.01) # Ensuring that there is a proper delay for the requests.
        res3 = self.client.post(
            reverse('board:post-create'),
            {},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)
        self.assertQuerysetEqual(b.post_set.all(), [])


    def test_create_posts_invalid_form_data(self):
        """Invalid form data is received."""

        b = Board(title='hi', description='hello')
        b.save()

        # Photo is a string.
        res1 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'photo': 'this is a photo'},
            HTTP_ACCEPT='application/json',
        )
        
        # Photo is a file.
        img = SimpleUploadedFile('test.txt', b'data')
        time.sleep(0.01) # Ensuring that there is a proper delay for the requests.
        res2 = self.client.post(
            reverse('board:post-create'),
            {'board': str(b.uuid), 'photo': img},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res2.status_code, 400)
        self.assertQuerysetEqual(b.post_set.all(), [])

    def test_create_posts_invalid_board(self):
        """Returns a 404 not found if the board uuid does not exist while trying to create a post."""
        res = self.client.post(
            reverse('board:post-create'), 
            {'board': 'invalidId', 'message': 'hi'},
            HTTP_ACCEPT='application/json',
        )
        res2 = self.client.post(
            reverse('board:post-create'), 
            {'board': str(uuid.uuid4()), 'message': 'hi'},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res2.status_code, 404)



    @tag('core')
    def test_get_image(self):
        """Gets the blob of the image that is able to be displayed."""
