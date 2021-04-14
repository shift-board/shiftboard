from django.db import models

# Create your models here.


class Board(models.Model):
    """
    A database model representing a board, where posts can be created and viewed.

    This model uses a `BinaryField` as opposed to an `ImageField` to store the background image of
    the board. While this is considered poor design in many cases, Heroku's ephemeral file
    system renders the file system impossible to use for dynamic storage. The is an issue because
    `ImageField`, which is a subclass of `FileField`, defaults to storing files on the file system
    under `MEDIA_ROOT`.

    As a workaround, this model stores the image as a BLOB in the actual database. While the
    database may inflate as a result, the preservation of the images is guaranteed.

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

class Post(models.Model):
    """
    A database model representing a post, where an image and message can be displayed.

    Each post belongs to a board. Like specified in `Board`, this model uses a `BinaryField`
    instead of an `ImageField` to work around Heroku's ephemeral file system. Since images will
    be deleted if dynamically stored in the file system, they will be stored as BLOBs instead
    in the database.

    This way, the preservation and storage of the images is guaranteed. The database may inflate
    as a result, but that is an acceptable sacrifice.

    Class Attributes
    associated_board -> `ForeignKey`: The foreign key for the board that this post is on.
    author -> `CharField`: A charfield with max length 50 containing the author's name. Optional.
    description -> `CharField`: A charfield with max length 500 containing the description of the
        post. Optional, but if not included, should contain a picture. Validation will be performed 
        at the API level, as the database does not care if a post has no picture and description.
    picture -> `BinaryField`: A field containing the post's image. Optional, but if not included,
        should contain a description. Validation will be performed at the API level, as the
        database does not care if a post has no picture and description.
    """

    associated_board = models.ForeignKey(Board, on_delete=models.CASCADE)
    author = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    picture = models.BinaryField(blank=True)

    def __str__(self):
        """Returns the board id, author, and description of the post."""
        return f"{self.associated_board}: {self.author} -- {self.description}"