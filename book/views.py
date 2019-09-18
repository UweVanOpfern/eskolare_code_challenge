from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout, )
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms import ModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import (RegisterForm, LoginForm)
from .models import Book, Review
from .serializers import BookSerializer, ReviewSerializer
from .tokens import account_activation_token


class BookRegistrationForm(ModelForm):
    """
    This class is form format of book model which helps for getting is_read field
    """

    class Meta:
        model = Book
        fields = ['is_read']


class BookListView(ListView):
    """
    This class listing all books
    """
    model = Book
    context_object_name = 'books'
    template_name = 'book/home.html'

    def get_queryset(self):
        return Book.objects.order_by('-id')


class BookDetailView(DetailView):
    """
    This class listing specific book
    """
    model = Book


class BookCreateView(CreateView):
    """
    This class creating specific book
    """
    model = Book
    fields = ['title', 'category', 'author', 'cover']

    def form_valid(self, form):
        return super().form_valid(form)


class BookUpdateView(UpdateView):
    """
    This class updating specific book
    """
    model = Book
    fields = ['title', 'category', 'author', 'cover']

    def form_valid(self, form):
        return super().form_valid(form)


class BookDeleteView(DeleteView):
    """
    This class deleting specific book
    """
    model = Book
    success_url = '/'


def read_book(request, pk):
    """
    This method is for marking book as read
    """
    template = 'book/read_book.html'
    book = get_object_or_404(Book, pk=pk)
    form = BookRegistrationForm(request.POST or None, instance=book)
    if form.is_valid():
        form = form.save(commit=False)
        form.is_read = True
        form.save()
        return redirect('book-home')
    return render(request, template, {'form': form})


def get_read_book(request):
    """
    This method is for getting all books which are read(readed books)
    """
    context = {
        'books': Book.objects.all().filter(is_read=True)
    }
    return render(request, 'book/readed_book.html', context)


def get_unread_book(request):
    """
    This method is for getting all unread books
    """
    context = {
        'books': Book.objects.all().filter(is_read=False)
    }
    return render(request, 'book/unread_book.html', context)


def book_reviews(request, pk):
    """
    This method is for getting reviews of specific book
    """
    model = Review
    context_object_name = 'books'
    template_name = 'book/home.html'

    context = {
        'reviews': Review.objects.filter(book=pk).order_by('-id')
    }
    return render(request, 'book/book-review.html', context)


class ReviewDetailView(DetailView):
    """
    This class is for listing specific review
    """
    model = Review


class ReviewCreateView(CreateView):
    """
    This is for creating new review
    """
    model = Review
    fields = ['book', 'review']
    success_url = '/'

    def form_valid(self, form):
        return super().form_valid(form)


class ReviewUpdateView(UpdateView):
    """
    This is for updating specific review
    """
    model = Review
    fields = ['book', 'review']

    def form_valid(self, form):
        return super().form_valid(form)


class ReviewDeleteView(DeleteView):
    """
    This is for deleting specific review
    """
    model = Review
    success_url = '/'


def register(request):
    """
    Register a user and send email confirmation is_active to False because user is not yet activated
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activate your site account."
            message = render_to_string('book/confirm_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, message, 'infos@idatech.rw', [to_email, ], fail_silently=False)
            return render(request, 'book/confirm_email_notify.html')
    else:
        form = RegisterForm()

    return render(request, 'book/register.html', {'form': form})


User = get_user_model()


def activate(request, uidb64, token):
    """
    This method is activating user and set is_active to True
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


def login_user(request):
    """
    This method is for login a user
    """
    next = request.GET.get('next', None)
    form = LoginForm(data=request.POST or None)

    context = {
        'form': form
    }

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user is None:
                messages.error(request, "Invalid login credentials,Please try again")
                return render(request, 'book/login.html', context)
            else:
                login(request, user)
                if next:
                    return redirect(next)
                return redirect('/')

    return render(request, 'book/login.html', context)


@login_required()
def logout_user(request):
    """
    This method is for log out user
    """
    logout(request)
    return redirect('/')


# Bellow there is views logic for APIs only

class BookAPIView(APIView):
    """
    This class is API class that gets all books and create new one
    """

    def get(self, request):
        book_object = Book.objects.all().order_by('-id')
        # many=True indicates that they are many objects to return not only one
        serializer = BookSerializer(book_object, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        incoming_data = request.data
        serializer = BookSerializer(data=incoming_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class BookDetailAPIView(APIView):
    """
    This class is API class that gets, update and delete specific book
    """

    def get_object(self, id):

        try:
            return Book.objects.get(id=id)
        except Book.DoesNotExist as e:
            return Response({"error": "Given book object not found"}, status=404)

    def get(self, request, book_id):

        instance = self.get_object(book_id)
        serializer = BookSerializer(instance)
        return Response(serializer.data)

    def put(self, request, book_id=None):

        incoming_data = request.data
        instance = self.get_object(book_id)
        serializer = BookSerializer(instance, data=incoming_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, book_id=None):
        instance = self.get_object(book_id)
        instance.delete()
        return Response({"response": "Data deleted"}, status=204)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    This is CRUD operations API for reviews
    """
    serializer_class = ReviewSerializer
    queryset = Review.objects.all().order_by('-id')


def get_read_book_api(request):
    """
    This method is API method that gets all readed books
    """
    if request.method == "GET":
        readed_book = Book.objects.all().filter(is_read=True)
        serializer = BookSerializer(readed_book, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)


def get_unread_book_api(request):
    """
    This method is API method that gets all unread books
    """
    if request.method == "GET":
        readed_book = Book.objects.all().filter(is_read=False)
        serializer = BookSerializer(readed_book, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
