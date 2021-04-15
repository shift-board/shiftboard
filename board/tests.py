from django.contrib.auth.models import User
from django.test import TestCase, tag

from .models import Board, Post

# Create your tests here.

class BoardModelTests(TestCase):
  """
  A class with tests for testing relationships with the `Board` database model.
  """

  @tag('core')
  def test_board_post_connections(self):
    """Make sure that posts to a board are properly associated and posts acn be found."""
    b1 = Board(title="foo", description="bar", bg=bytearray("biv", "utf-8"))
    b2 = Board(title="foo2", description="bar", bg=bytearray("biv", "utf-8"))
    b1.save()
    b2.save()

    p1 = Post(associated_board=b1, name="a", message="b")
    p2 = Post(associated_board=b1, name="a", photo=bytearray("biv", "utf-8"))
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
    b1 = Board(title="foo", description="bar", bg=bytearray("biv", "utf-8"))
    b2 = Board(title="foo2", description="bar", bg=bytearray("biv", "utf-8"))
    b3 = Board(title="foo3", description="bar", bg=bytearray("biv", "utf-8"))
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
    b1 = Board(title="foo", description="bar", bg=bytearray("biv", "utf-8"))
    b1.save()

    # just make sure that none of these throw an exception when creating
    p1 = Post(associated_board=b1, message="post1")
    p2 = Post(associated_board=b1, name="author2", photo=bytearray("post2", "utf-8"))
    p3 = Post(associated_board=b1, photo=bytearray("post3", "utf-8"))
    p4 = Post(associated_board=b1, name="author4", message="post4", photo=bytearray("pic4", "utf-8"))
    p5 = Post(associated_board=b1, message="post5", photo=bytearray("pic5", "utf-8"))

    p1.save()
    p2.save()
    p3.save()
    p4.save()
    p5.save()