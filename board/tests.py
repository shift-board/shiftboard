from django.contrib.auth.models import User
from django.test import TestCase, tag

from .models import Board, Post

# Create your tests here.

class BoardModelTests(TestCase):
  @tag('core')
  def test_board_post_connections(self):
    b1 = Board(title="foo", description="bar", bg=bytearray("biv", "utf-8"))
    b2 = Board(title="foo2", description="bar", bg=bytearray("biv", "utf-8"))
    b1.save()
    b2.save()

    p1 = Post(associated_board=b1, author="a", description="b")
    p2 = Post(associated_board=b1, author="a", picture=bytearray("biv", "utf-8"))
    p3 = Post(associated_board=b2, author="a", description="b")
    p4 = Post(associated_board=b1, author="a", description="b")
    p1.save()
    p2.save()
    p3.save()
    p4.save()

    self.assertQuerysetEqual(b1.post_set.all(), [p1, p2, p4], ordered=False)
    self.assertQuerysetEqual(b2.post_set.all(), [p3], ordered=False)

  @tag('core')
  def test_admin_board_connections(self):
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