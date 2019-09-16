from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from .validators import UsernameValidator


class Book(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='book_covers')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    @property
    def reviews(self):
        return self.review_set.all()


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review = models.TextField(max_length=4000)

    def __str__(self):
        return self.review

    def get_absolute_url(self):
        return reverse('review-detail', kwargs={'pk': self.pk})


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("User must have a valid email address.")

        if not kwargs.get('username'):
            raise ValueError('User must have a valid username')

        user = self.model(
            username=kwargs.get('username').strip(),
            email=self.normalize_email(email),
            first_name=kwargs.get('first_name', None),
            last_name=kwargs.get('last_name', None),
        )

        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, is_staff=True, **kwargs):
        user = self.create_user(email, password, **kwargs)
        user.is_superuser = True
        user.is_admin = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model
    """
    username = models.CharField(
        max_length=255,
        unique=True,
        validators=[UsernameValidator()],
        error_messages={
            'unique': 'User with this username already exists.',
        },
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'User with this email already exists.',
        },
    )

    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=40, null=True)
    is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    class Meta:
        db_table = "users"
