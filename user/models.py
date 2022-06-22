from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import django
from django.utils.timezone import now
from datetime import datetime

# Create your models here.

class AppUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
      
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a Super Admin. Not to be used by any API. Only used for django-admin command.
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', email)

        user = self._create_user(email, password, **extra_fields)
        return user


from django.core.validators import RegexValidator
phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class User(AbstractUser):
    first_name = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    last_name = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    email=models.EmailField(unique=True,null=False)

    is_phone_verified=models.BooleanField(default = False)

    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True,unique=True) # Validators should be a list
    phone_otp=models.BigIntegerField(blank = True, null = True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    manager = AppUserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.username


class Devices(models.Model):
    User=models.ForeignKey(to=User,on_delete=models.CASCADE)
    iOS='iOS'
    Android='Android'
    CategoryChoices=[
        (iOS,'iOS'),
        (Android,'Android'),
    ]
    DeviceToken=models.CharField(max_length=250,blank=True,null=True)
    DeviceType=models.CharField(max_length=500,choices=CategoryChoices)
    DateAdded=models.DateTimeField(default=django.utils.timezone.now)

TOKEN_TYPE_CHOICES = (
    ("verification", "Email Verification"),
    ("pwd_reset", "Password Reset"),
)

class Token(models.Model):
    token = models.CharField(max_length=300)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token_type = models.CharField(
        max_length=20, choices=TOKEN_TYPE_CHOICES
    )
    created_on = models.DateTimeField(default=now, null=True, blank=True)
    expired_on = models.DateTimeField(default=now, null=True, blank=True)


class Profiles(models.Model):
    User=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    profile_image=models.ImageField(upload_to='profile_image',blank=True,null=True)
    Country=models.CharField(max_length=200,blank=True,null=True)
    City=models.CharField(max_length=200,blank=True,null=True)
    State=models.CharField(max_length=200,blank=True,null=True)
    latitude = models.FloatField(blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    ZipCode=models.CharField(max_length=10,blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.User)


class FriendRequests(models.Model):
    Sender=models.ForeignKey(Profiles,on_delete=models.CASCADE,related_name='Sender')
    Receiver=models.ForeignKey(Profiles,on_delete=models.CASCADE,related_name='Receiver')
    Sent='Sent'
    Accept='Accept'
    Reject='Reject'
    CategoryChoices=[
        (Sent,'Sent'),
        (Accept,'Accept'),
        (Reject,'Reject')
    ]
    Status=models.CharField(max_length=200,choices=CategoryChoices,default='Sent')
    DateAdded=models.DateTimeField(default=django.utils.timezone.now)  

    class Meta:
        unique_together = (('Sender', 'Receiver',))
        ordering = ["-DateAdded"]

    def __str__(self):
        return f"{self.Sender} follows {self.Receiver}"


from django.core.validators import FileExtensionValidator
class post(models.Model):
    
    user = models.ForeignKey(User,on_delete= models.CASCADE)
    video = models.FileField(upload_to='post',null=True,
    validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','jpg','jpeg','jfif','pjpeg','pjp','png','gif','svg'])]) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Field(models.Model):
    name=models.CharField(max_length=250,null=True,blank=True)
    type=models.CharField(max_length=250,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Form(models.Model):
    title=models.CharField(max_length=200,blank=-True,null=True)
    fields=models.ManyToManyField(Field)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class UserDetails(models.Model):
    form=models.ForeignKey(Form,on_delete=models.CASCADE,null=True,blank=True)    
    data = models.JSONField() 

    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return str(self.form.title)





















