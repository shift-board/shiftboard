from django.http import HttpResponse, JsonResponse
from django.views import View
from board.forms import PostForm

# Create your views here.

class Board(View):
    """
    The landing page serving the React single page board app.
    This includes displaying the board, the creating post page, and the viewing post popup.

    This can be found at the path 
    >>> '/board-name-hash'
    """

    def get(self):
        """
        Get the index.html of the React app.
        """
        #TODO: write the board app frontend
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
    """

    def get(self):
        """
        Get the `index` and `amount` from the query string params.
        Then, get the corresponding data from the database and send back a JSON response
        to the client.

        For example, if the user wished to load 30 more posts starting from the 51th post,
        the query string would be index=50&amount=30. The index is zero-based, inclusive at start
        and exclusive at the end.
        """
        index = self.request.GET.get('index')
        amount = self.request.GET.get('amount')
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

    def post(self):
        """
        The user will post form data with the following attached:
        - name (optional)
        - message
        - photo(s)
        Either message/photo must exist for the POST request to be valid.
        This will be added to the database along with a created_at timestamp.
        """
        form = PostForm(self.request.POST, self.request.FILES)
        if (form.is_valid()):
            #TODO: save form data to database

            # 204 is an empty response with no content, meaning that the operation was a success
            return HttpResponse(status=204)
        # 422 meaning the data is valid but does not match business model
        return HttpResponse(status=422)