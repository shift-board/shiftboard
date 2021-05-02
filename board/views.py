from uuid import UUID

from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.views import View

from board.forms import PostForm
from board.models import Post, Board, Image

class GetMainBoard(View):
    """
    The landing page serving the React single page board app.

    This includes displaying the board, the creating post page, and the viewing post popup.

    This can be found at the path '/board-name-uuid'.
    """

    #TODO: replace board uuid with hardcoded board
    def get(self, req, board=""):
        """Get the index.html of the React app."""
        #TODO: write the board app frontend
        #TODO: generalize the board uuid

        board = '<h1>this is the board</h1>'
        return HttpResponse(board)


class GetPosts(View):
    """
    An API to get the number of posts for a board from a certain index.

    This is to ensure that the client does not try to load in all the posts at once,
    but rather request the number of posts needed as the user is scrolling down.

    For example, when the user first loads the page, they will see the first 50 posts.
    Then, as they scroll down to a certain point, the client (not the user, but the client script)
    requests for more post information and the server responds correspondingly.

    Returns an array of posts with each post looking like:
        name -> `string`: the author's name.
        message -> `string`: the message written.
        photo -> {
            uuid -> `string`: the photo's uuid.
            name -> `string`: the photo's name.
        }
    """

    def get(self, req):
        """
        Get the data from the database and send a JSON response.

        Get the `index` and `amount` from the query string params.
        Then, get the corresponding data from the database and send back a JSON response
        to the client.

        For example, if the user wished to load 30 more posts starting from the 51th post,
        the query string would be index=50&amount=30. The index is zero-based, inclusive at start
        and exclusive at the end.

        Returns:
            A JSON representation of the posts.
        """
        board_uuid = req.GET.get('board')
        index = req.GET.get('index')
        amount = req.GET.get('amount')

        #TODO: get data from DB
        posts = {}
        return JsonResponse(posts)


class CreatePost(View):
    """
    The API endpoint responsible for handling new post creations.

    The users do not need accounts to add a new post. This app is under the assumption
    that only the people with the board link can add posts to it and for simplicity reasons
    for the user, all posts are automatically approved unless the board admin removes it.

    A new post may contain photos, messages, or a mix of both. The user can also optionally
    leave their name on the post. The user cannot submit a post with only their names, and 
    of course, an empty post.
    """

    def post(self, req):
        """
        Adds the post to the database and return a response correspondingly.

        Either message/photo must exist for the POST request to be valid.
        This will be added to the database along with a created_at timestamp.
        
        The user will post form data with the following attached:
        Fields:
            name -> string: the author of the post, optional.
            message -> string: the message the user wish to convey.
            photo -> Images: the photos the user uploads.
        Returns:
            A response of either status `204` for success or `422` for invalid data.
        """
        form = PostForm(req.POST, req.FILES)

        if (form.is_valid()):
            #TODO: save form data to database

            # 204 is an empty response with no content, meaning that the operation was a success
            return HttpResponse(status=204)
        # 422 meaning the data is valid but does not match business model
        return HttpResponse(status=422)

class GetImage(View):
    """
    The API endpoint to retrieve images stored in the database.

    Since images are stored as BLOBs, they must be fetched and returned independently from posts.
    Once a GET request is sent to this view, it will respond with the image BLOB, using the 
    specified static image URI as a locator. If the image URI cannot be found in the
    database, a 404 will be returned.

    Returns `application/octet-stream`.
    """

    def get(self, req, image_uuid):
        """Gets the requested image from the specified image URI."""
        try:
            UUID(image_uuid, version=4)
        except:
            return HttpResponse(status=400)

        try:
            image = Image.objects.get(uuid=image_uuid)
        except:
            return HttpResponse(status=404)

        return HttpResponse(image.photo, content_type='application/octet-stream')


class GetBoardDetails(View):
    """
    The API endpoint to retrieve details regarding the board page.

    The details DO NOT include the posts, as they are done through a separate API.
    This returns a JSON object in the form of:

    JSON fields:
        title -> `string`: the title of the board. 
        description -> `string`: the description for the board.
        bg -> `string`: the uuid of the background image of the board. 

    """

    def get(self, req):
        """Get the board details as a JSON response."""
        
        try:
            # Ensure the query string exists.
            board_uuid = req.GET.get('board')
            # Ensure it is a valid uuid.
            UUID(board_uuid, version=4)
            # Ensure the board exists.
            board = Board.objects.get(uuid=board_uuid)
        except:
            return HttpResponse(status=404)

        board_json = {
            'title': board.title,
            'description': board.description,
            'bg': str(board.bg.uuid),
        }

        return JsonResponse(board_json)