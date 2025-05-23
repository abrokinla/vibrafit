from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin',   'Admin'),
        ('trainer', 'Trainer'),
        ('client',  'Client'),
    )

    email         = models.EmailField(unique=True)
    role          = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    name          = models.CharField(max_length=100, blank=True)
    country       = models.CharField(max_length=100, blank=True)
    state         = models.CharField(max_length=100, blank=True)
    is_onboarded  = models.BooleanField(default=False)
    profilePictureUrl = models.CharField(max_length=100, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.email


class TrainerProfile(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainerprofile')
    bio            = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    specialties    = models.TextField(blank=True)
    rating         = models.FloatField(default=0.0)

    def __str__(self):
        return f"TrainerProfile for {self.user.email}"

class Subscription(models.Model):
    client = models.ForeignKey('User', related_name='client_subscriptions', on_delete=models.CASCADE)
    trainer = models.ForeignKey('User', related_name='trainer_subscriptions', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20)

class Goal(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    description = models.TextField()
    target_value = models.CharField(max_length=255)
    target_date = models.DateField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

class Plan(models.Model):
    user = models.ForeignKey('User', related_name='user_plans', on_delete=models.CASCADE)
    trainer = models.ForeignKey('User', related_name='trainer_plans', on_delete=models.CASCADE)
    date = models.DateField()
    nutrition_plan = models.TextField()
    exercise_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class DailyLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)
    date = models.DateField()
    actual_nutrition = models.TextField()
    actual_exercise = models.TextField()
    completion_percentage = models.FloatField()
    notes = models.TextField(blank=True)

class Metric(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    value = models.FloatField()
    recorded_at = models.DateTimeField()
