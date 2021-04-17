from django.urls import path

from . import views

app_name = 'board'
urlpatterns = [
    path('', views.GetMainBoard.as_view(), name='main-board'),
    path('api/board/posts/get', views.GetPosts.as_view(), name='posts-get'),
    path('api/board/posts/create', views.CreatePost.as_view(), name='posts-create'),
    path('api/board/images/<image>', views.GetImage.as_view(), name='image-get'),
    path('<board>/', views.GetMainBoard.as_view(), name='board'),
]