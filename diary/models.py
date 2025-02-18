from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.timezone import now

class AccessLog(models.Model):
    timestamp = models.DateTimeField(default=now)  # アクセス日時
    ip_address = models.GenericIPAddressField()  # アクセス元IPアドレス
    user_agent = models.TextField()  # ブラウザ情報
    referer = models.TextField(blank=True, null=True)  # 参照元URL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  

    def __str__(self):
        if self.user:
            return f"{self.timestamp} - {self.ip_address} - {self.user.email}"
        return f"{self.timestamp} - {self.ip_address} - ゲスト"

# カスタムユーザーマネージャー
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("メールアドレスは必須です")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# カスタムユーザーモデル
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # メールアドレスでログイン
    REQUIRED_FIELDS = []  # スーパーユーザー作成時に追加情報なし

    def __str__(self):
        return self.email

# タグモデル
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# 日記モデル
class DiaryEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default="無題")  # タイトルを追加
    date = models.DateField(blank=True, null=True)  #  任意の日付を設定できるように変更
    content = models.TextField()
    image = models.ImageField(upload_to='diary_images/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    views_count = models.PositiveIntegerField(default=0) 

    def clean(self):
        if not self.pk:  # オブジェクトがまだ保存されていない場合はスキップ
            return
        if self.tags.count() > 20:
            raise ValidationError("タグは20個までしか設定できません。")
    
    def increment_views(self):
        """ 記事のアクセス回数を増やす """
        self.views_count += 1
        self.save()
    
    def save(self, *args, **kwargs):
        self.clean()
        if not self.date:
            self.date = date.today()  # `date` が未設定なら当日にする
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.title}"  # タイトルを表示