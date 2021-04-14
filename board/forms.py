from django import forms

class PostForm(forms.Form):
    """
    A form representing the creation of a new post.

    The post may contain a name, message, or photo(s). None of the fields are required. 
    However, at least either of the message or photo
    must exist for this to be a valid post.

    Class Attributes
        name -> string: the author's name
        message -> string: the message being written in the post
        photo -> ImageFiles: the photo(s) attached to the post    
    """
    name = forms.CharField(max_length=50, required=False)
    message = forms.CharField(max_length=500, required=False)
    photo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        required=False
    )

    def clean(self):
        """
        Cleans the form data and make sure all fields are valid.

        First clean the fields based on the parent checking functions of `django.forms.Form`.
        However, since all fields are marked as not required, but at least either one of
        'message' or 'photo' is needed, there is an additional check that is added to
        cleaning the data.

        The data is invalid if both `photo` field and `message` field do not exist.
        """
        cleaned_data = super().clean()
        if (cleaned_data.get('message') is None and self.cleaned_data('photo') is None):
            error = 'At least one photo or message must exist.'
            self.add_error('message', error)
            self.add_error('photo', error)
