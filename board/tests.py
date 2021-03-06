import uuid

from django.contrib.auth.models import User
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

from board.models import Board, Image, Post
from board.views import get_post_dict



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


class GetPostsTests(TestCase):
    """Tests the `posts-get` API endpoint."""

    def add_posts(self, board, amount):
        """Return a list of posts that are added to a board."""
        posts = []
        for i in range(amount):
            p = Post(
                associated_board=board, 
                message='hi', 
                name=str(i), 
                photo=Image(name=f'photo{i}', photo=bytearray('hi', 'utf-8')).save(),
                created_at=timezone.now()+timezone.timedelta(seconds=i)
            )
            p.save()
            posts.append(p)
        return posts

    @tag('core')
    def test_get_posts(self):
        """Make sure that it returns proper JSON responses with proper amount of posts."""
        
        b = Board(title='hi', description='hello', bg=Image(name='i', photo=bytearray('hi', 'utf-8')).save())
        b.save()
        posts = self.add_posts(b, 30)
        
        # First 10 posts
        res1 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b.uuid),
                'index': '0',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        exp1 = []
        for i in range(10):
            p = posts[-i-1]
            exp1.append(get_post_dict(p))
        self.assertEqual(res1.json(), exp1)


        # Second 10 posts
        res2 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b.uuid),
                'index': '10',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        exp2 = []
        for i in range(10):
            p = posts[-i-11]
            exp2.append(get_post_dict(p))
        
        self.assertEqual(res2.json(), exp2)
    
    @tag('core')
    def test_get_posts_optional_fields(self):
        """Get posts that does have every field"""
        b = Board(title='hi', description='hello')
        b.save()

        posts = [
            Post(associated_board=b, message='hi', created_at=timezone.now()),
            Post(
                associated_board=b, 
                name='shari', 
                message='cool', 
                created_at=timezone.now()-timezone.timedelta(1)
            ),
            Post(
                associated_board=b, 
                name='joseph', 
                photo=Image(name='i', photo=bytearray('b', 'utf-8')).save(),
                created_at=timezone.now()-timezone.timedelta(2),
            ),
        ]
        exp = []
        for p in posts:
            exp.append(get_post_dict(p))
            p.save()
        
        res = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b.uuid),
                'index': '0',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        self.assertEqual(res.json(), exp)


    @tag('core')
    def test_get_posts_fully_loaded(self):
        """ Test for when the client requests more posts than what the database have available. 
        
        Ex. If the database only have 10 more posts but the client is requesting 20 posts.
        
        It should return back whatever is available.
        """

        b1 = Board(title='hi', description='hello', bg=Image(name='i', photo=bytearray('hi', 'utf-8')).save())
        b2 = Board(title='hi2', description='hello2', bg=Image(name='i2', photo=bytearray('hi', 'utf-8')).save())

        b1.save()
        b2.save()
        posts1 = self.add_posts(b1, 5)

        # board 1 has only 5 posts but the client requested 10
        res1 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b1.uuid),
                'index': '0',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        exp1 = []
        for i in range(5):
            exp1.append(get_post_dict(posts1[-i-1]))
        self.assertEqual(res1.json(), exp1)

        # board 2 has no posts but the client requested 10
        res2 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b2.uuid),
                'index': '5',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        exp2 = []
        self.assertEqual(res2.json(), exp2)


    def test_get_posts_invalid_query(self):
        """ Test for missing or invalid query string.

        Invalid query strings include:
        - negative numbers 
        - non-existent board uuid
        - etc
        """

        b1 = Board(title='hi', description='hello', bg=Image(name='i', photo=bytearray('hi', 'utf-8')).save())
        b1.save()

        # Non-existent board uuid
        res1 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(uuid.uuid4()),
                'index': '0',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        # Bad board uuid format
        res2 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': 'invalid uuid format',
                'index': '0',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )
        # Missing query parameters
        res3 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b1.uuid),
                'index': '12',
            },
            HTTP_ACCEPT='application/json',
        )
        # Bad parameter values
        res4 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b1.uuid),
                'index': '12',
                'amount': 'mango',
            },
            HTTP_ACCEPT='application/json',
        )
        res5 = self.client.get(
            reverse('board:posts-get'),
            {
                'board': str(b1.uuid),
                'index': '-12',
                'amount': '10',
            },
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(res1.status_code, 404)
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res3.status_code, 400)
        self.assertEqual(res4.status_code, 400)
        self.assertEqual(res5.status_code, 400)


class GetBoardDetailsTest(TestCase):
    """Tests the `board-details-get` API endpoint."""

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
        # Malformed
        res = self.client.get(
            reverse('board:board-details-get'), 
            {'board': 'not-a-uuid'},
            HTTP_ACCEPT='application/json',
        )
        # UUID doesn't exist
        res2 = self.client.get(
            reverse('board:board-details-get'), 
            {'board': uuid.uuid4()},
            HTTP_ACCEPT='application/json',
        )
        # Missing parameter
        res3 = self.client.get(
            reverse('board:board-details-get'),
        )

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res2.status_code, 404)
        self.assertEqual(res3.status_code, 400)


    def test_board_details_invalid_req_method(self):
        """Returns a 405 for incorrect request method (post, delete, etc) when getting the board details."""
        res = self.client.post(reverse('board:board-details-get'))
        res2 = self.client.delete(reverse('board:board-details-get'))

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res2.status_code, 405)

