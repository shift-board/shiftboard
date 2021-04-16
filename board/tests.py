import uuid

from django.contrib.auth.models import User
from django.test import TestCase, tag

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