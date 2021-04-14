from django.db import models

# Create your models here.


class Board(models.Model):
    """
    A database model representing a board, where posts can be created and viewed.

    This model uses a `BinaryField` as opposed to an `ImageField` to store the background image of
    the board. While this is considered poor design in many cases, Heroku's empherical file
    system renders the file system impossible to use for dynamic storage. The is an issue becuase
    `ImageField`, which is a subclass of `FileField`, defaults to storing files on the file system
    under `MEDIA_ROOT`.

    Class Attributes
        title -> `CharField`: A charfield with max length 100 containing the title of the board.
        description -> `CharField`: A charfield with max length 500 containing the title of the board.
        bg -> `BinaryField`: A field with the background image BLOB.
    """
    # TODO: look into changing the image storage

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    bg = models.BinaryField()

    def __str__(self):
        """Returns the title, which is the string representation of this model."""
        return self.title
