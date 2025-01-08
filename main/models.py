from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # اضافه کردن فیلدهای سفارشی
    is_premium = models.BooleanField(default=False, verbose_name="وضعیت پریمیوم")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name="عکس پروفایل")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="موجودی کیف پول")
    registration_date = models.DateField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="شماره تلفن")

    def __str__(self):
        return self.username  # نام کاربری نمایش داده شود

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    release_date = models.DateField(verbose_name="تاریخ انتشار")
    description = models.TextField(verbose_name="توضیحات")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر")
    language = models.CharField(max_length=50, verbose_name="زبان")
    age_rating = models.CharField(max_length=10, verbose_name="رده سنی")

    def __str__(self):
        return self.title


# مدل مربوط به فیلم‌ها/سریال‌ها
class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")  # عنوان فیلم یا سریال
    release_date = models.DateField(verbose_name="تاریخ انتشار")  # تاریخ انتشار
    description = models.TextField(verbose_name="توضیحات")  # توضیحات مربوط به فیلم/سریال
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")  # مدت زمان به دقیقه
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")  # تعداد بازدید
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر")  # لینک پوستر فیلم/سریال
    language = models.CharField(max_length=50, verbose_name="زبان")  # زبان فیلم/سریال
    age_rating = models.CharField(max_length=10, verbose_name="رده سنی")  # رده سنی (مثلاً PG-13)

    def __str__(self):
        return self.title  # نمایش عنوان به عنوان رشته نمایشی


# مدل مربوط به ژانرها
class Genre(models.Model):
    genre_name = models.CharField(max_length=100, verbose_name="نام ژانر")  # نام ژانر (مثلاً اکشن)
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")  # توضیحات اختیاری درباره ژانر

    def __str__(self):
        return self.genre_name  # نمایش نام ژانر


# مدل مربوط به بازیگران
class Actor(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام بازیگر")  # نام کامل بازیگر
    birth_date = models.DateField(verbose_name="تاریخ تولد")  # تاریخ تولد بازیگر
    nationality = models.CharField(max_length=50, verbose_name="ملیت")  # ملیت بازیگر

    def __str__(self):
        return self.name  # نمایش نام بازیگر


# مدل مربوط به ارتباط بین فیلم و بازیگر
class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مرتبط
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, verbose_name="بازیگر")  # بازیگر مرتبط
    role = models.CharField(max_length=100, verbose_name="نقش بازیگر")  # نقش بازیگر در فیلم

    def __str__(self):
        return f"{self.actor.name} in {self.movie.title}"  # نمایش نقش بازیگر در فیلم


# مدل مربوط به ارتباط بین فیلم و ژانر
class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مرتبط
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="ژانر")  # ژانر مرتبط

    def __str__(self):
        return f"{self.movie.title} - {self.genre.genre_name}"  # نمایش ژانر مرتبط با فیلم


