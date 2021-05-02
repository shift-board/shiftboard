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

def get_post_dict(post):
    """Return a formated dictionary of a post.

    Args:
        post -> `Post`: the post.
    
    JSON fields:
        name -> `string`: the author's name.
        message -> `string`: the message written.
        photo -> {
            uuid -> `string`: the photo's uuid.
            name -> `string`: the photo's name.
        }
    """
    if (post.photo is not None):
        photo = {
            'uuid': str(post.photo.uuid),
            'name': post.photo.name,
        }
    else:
        photo = None

    return {
        'name': post.name,
        'message': post.message,
        'photo': photo,
    }

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
            photo -> Image: the photo the user uploads.
        Returns:
            Invalid form data: 400
            Board UUID not found: 404
            Success: JSON representation of the post
        """

        form = PostForm(req.POST, req.FILES)

        if (form.is_valid()):
            try:
                board_uuid = form.cleaned_data['board']
                board = Board.objects.get(uuid=board_uuid)
            except:
                return HttpResponse(status=404, headers={
                    'Content-Length': '0',
                    'Content-Type': 'application/json'
                })
            
            img_file = form.files.get('photo') 
            if (img_file is None):
                img = None
            else:
                img = Image(name=img_file.name, photo=img_file.file.read())
                img.save()
            
            post = Post(
                associated_board=board, 
                name=form.cleaned_data['name'],
                message=form.cleaned_data['message'],
                photo=img
            )
            post.save()
            return JsonResponse(get_post_dict(post))
            
        return HttpResponse(status=400, headers={
            'Content-Length': '0',
            'Content-Type': 'application/json'
        })

class GetImage(View):
    """
    The API endpoint to retrieve images stored in the database.

    Since images are stored as BLOBs, they must be fetched and returned independently from posts.
    Once a GET request is sent to this view, it will respond with the image BLOB, using the 
    specified static image URI as a locator. If the image URI cannot be found in the
    database, a 404 will be returned.
    """

    def get(self, req, image):
        """Gets the requested image from the specified image URI."""
        #TODO: return image blob and fix docstring once finished
        return HttpResponse(f'<h1>wow u got image {image}</h1>')


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
            raise Http404('Board not found')

        board_json = {
            'title': board.title,
            'description': board.description,
            'bg': str(board.bg.uuid),
        }

        return JsonResponse(board_json)