from django.db import models
from django.utils import timezone
import random
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('O usuário deve ter um endereço de email')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class EmailLoginCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # válido por 5 min

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))


class UserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="token_info")
    total_tokens_diarios = models.PositiveIntegerField(default=2000)
    tokens_restantes = models.PositiveIntegerField(default=2000)
    last_reset = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.tokens_restantes}/{self.total_tokens_diarios} tokens"

    class Meta:
        verbose_name = "Tokens dos Usuários"
        verbose_name_plural = "Tokens dos Usuários"


class TokenUsageLog(models.Model):
    ACTION_CHOICES = (
        ("SPEND", "Gasto"),
        ("ADD", "Adicionado"),
        ("RESET", "Resetado"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="token_logs")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantidade = models.IntegerField()  # pode ser negativo para gasto
    tokens_restantes = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Logs dos Tokens"
        verbose_name_plural = "Logs dos Tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.action} {self.quantidade} tokens em {self.created_at:%d/%m/%Y %H:%M}"
