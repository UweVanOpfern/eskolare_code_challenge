from django.urls import path
from .views import (
    BookListView,
    BookCreateView,
    BookDetailView,
    BookUpdateView,
    BookDeleteView,
    ReviewCreateView,
    ReviewDetailView,
    ReviewUpdateView,
    ReviewDeleteView
)
from . import views

urlpatterns = [
    path('', BookListView.as_view(), name='book-home'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('book/new/', BookCreateView.as_view(), name='book-create'),
    path('book/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),
    path('read-book/<int:pk>', views.read_book, name='read-book'),
    path('readed-book/', views.get_read_book, name='readed-book'),
    path('unread-book/', views.get_unread_book, name='unread-book'),
    path('review/new/', ReviewCreateView.as_view(), name='review-create'),
    path('review/<int:pk>', ReviewDetailView.as_view(), name='review-detail'),
    path('review/<int:pk>/update/', ReviewUpdateView.as_view(), name='review-update'),
    path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),
    path('book_reviews/<int:pk>', views.book_reviews, name='book-review'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

]
