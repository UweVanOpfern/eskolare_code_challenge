from . import views
from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('reviews', views.ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('books', views.BookAPIView.as_view()),
    path('books/<int:book_id>', views.BookDetailAPIView.as_view()),
    path('readed/books', views.get_read_book_api),
    path('unread/books', views.get_unread_book_api)
]
