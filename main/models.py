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
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="امتیاز کلی")  # امتیاز کلی فیلم/سریال (مثلاً 4.5 از 5)
    country = models.CharField(max_length=100, verbose_name="کشور تولید")  # کشور تولیدکننده فیلم/سریال

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


# مدل تراکنش‌های کیف پول
class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر مربوط به تراکنش
    transaction_type = models.CharField(max_length=50, choices=[('credit', 'شارژ'), ('debit', 'برداشت')], verbose_name="نوع تراکنش")  # نوع تراکنش (شارژ یا برداشت)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ تراکنش")  # مبلغ تراکنش
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تراکنش")  # تاریخ تراکنش

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"  # نمایش جزئیات تراکنش


# مدل اشتراک‌ها
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر مربوط به اشتراک
    subscription_type = models.CharField(max_length=50, choices=[('basic', 'عادی'), ('premium', 'پریمیوم')], verbose_name="نوع اشتراک")  # نوع اشتراک
    start_date = models.DateField(verbose_name="تاریخ شروع")  # تاریخ شروع اشتراک
    end_date = models.DateField(verbose_name="تاریخ پایان")  # تاریخ پایان اشتراک

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"  # نمایش نوع اشتراک


# مدل نقدها و امتیازات
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر نویسنده نقد
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مرتبط با نقد
    rating = models.PositiveIntegerField(verbose_name="امتیاز")  # امتیاز داده شده (مثلاً از 1 تا 5)
    review_text = models.TextField(null=True, blank=True, verbose_name="متن نقد")  # متن نقد
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ نقد")  # تاریخ ثبت نقد

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.rating}"  # نمایش امتیاز و فیلم نقد شده


# مدل تاریخچه تماشا
class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر تماشا کننده
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم تماشا شده
    watch_datetime = models.DateTimeField(auto_now_add=True, verbose_name="زمان تماشا")  # زمان تماشا

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.watch_datetime}"  # نمایش تاریخچه تماشا


# مدل فیلم‌های محبوب
class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم محبوب

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"  # نمایش فیلم محبوب


# مدل اعلان‌ها
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر دریافت کننده اعلان
    message = models.TextField(verbose_name="پیام اعلان")  # متن پیام اعلان
    sent_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")  # تاریخ ارسال پیام
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")  # وضعیت خواندن اعلان

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}..."  # نمایش خلاصه پیام
