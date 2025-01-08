from django.db import models
from django.contrib.auth.models import AbstractUser


# مدل کاربران
class User(AbstractUser):
    is_premium = models.BooleanField(default=False, verbose_name="وضعیت پریمیوم")
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, verbose_name="عکس پروفایل")
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="موجودی کیف پول")
    registration_date = models.DateField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="شماره تلفن")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


# مدل رده‌بندی سنی فیلم‌ها
class AgeRating(models.Model):
    RATINGS = [
        ('G', 'General Audiences (همه سنین)'),
        ('PG', 'Parental Guidance (مشورت والدین)'),
        ('PG-13', 'Parents Strongly Cautioned (13+ با مشورت)'),
        ('R', 'Restricted (17+ با محدودیت)'),
        ('NC-17', 'No Children Under 17 (غیرقابل مشاهده برای زیر 17)'),
    ]

    name = models.CharField(
        max_length=50,
        choices=RATINGS,
        unique=True,
        verbose_name="رده‌بندی سنی",
        default='G'  # مقدار پیش‌فرض
    )
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")

    def __str__(self):
        return self.get_name_display()  # نمایش توضیحات به جای کد


# مدل مربوط به فیلم‌ها/سریال‌ها
class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")  # عنوان فیلم یا سریال
    release_date = models.DateField(verbose_name="تاریخ انتشار")  # تاریخ انتشار
    description = models.TextField(verbose_name="توضیحات")  # توضیحات مربوط به فیلم/سریال
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")  # مدت زمان به دقیقه
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")  # تعداد بازدید
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر")  # لینک پوستر فیلم/سریال
    language = models.CharField(max_length=50, verbose_name="زبان")  # زبان فیلم/سریال
    age_rating = models.ForeignKey(AgeRating, on_delete=models.SET_NULL, null=True, verbose_name="رده‌بندی سنی")
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="امتیاز کلی")  # امتیاز کلی فیلم/سریال (مثلاً 4.5 از 5)
    country = models.CharField(max_length=100, verbose_name="کشور تولید")  # کشور تولیدکننده فیلم/سریال
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="برچسب‌ها")  # رابطه چند به چند با تگ‌ها

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


# مدل لینک های دانلود
class DownloadLink(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مربوطه
    quality = models.CharField(max_length=20, choices=[('720p', '720p'), ('1080p', '1080p'), ('4K', '4K')], verbose_name="کیفیت")  # کیفیت فایل
    download_url = models.URLField(verbose_name="لینک دانلود")  # لینک دانلود فایل
    file_size = models.CharField(max_length=10, blank=True, verbose_name="حجم فایل")  # حجم فایل

    def __str__(self):
        return f"{self.movie.title} - {self.quality} ({self.file_size})"  # نمایش عنوان فیلم، کیفیت و حجم


# مدل زیرنویس ها
class Subtitle(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مربوطه
    language = models.CharField(max_length=50, verbose_name="زبان زیرنویس")  # زبان زیرنویس
    subtitle_file = models.URLField(verbose_name="فایل زیرنویس")  # لینک فایل زیرنویس

    def __str__(self):
        return f"{self.movie.title} - {self.language}"  # نمایش فیلم و زبان زیرنویس


#  مدل برچسب های فیلم
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")  # نام برچسب (مثل کمدی، عاشقانه)
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")  # توضیحات اختیاری

    def __str__(self):
        return self.name  # نمایش نام برچسب


class MovieTag(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مربوطه
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="برچسب")  # برچسب مربوطه

    def __str__(self):
        return f"{self.movie.title} - {self.tag.name}"  # نمایش فیلم و برچسب


class VideoQuality(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  # فیلم مربوطه
    quality = models.CharField(max_length=20, choices=[('480p', '480p'), ('720p', '720p'), ('1080p', '1080p'), ('2k', '2k'), ('4K', '4K')], verbose_name="کیفیت")  # کیفیت ویدیو
    stream_url = models.URLField(verbose_name="لینک پخش آنلاین")  # لینک پخش آنلاین
    download_url = models.URLField(verbose_name="لینک دانلود")  # لینک دانلود

    def __str__(self):
        return f"{self.movie.title} - {self.quality}"  # نمایش عنوان فیلم و کیفیت


class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True, verbose_name="نقد")  # نقد مرتبط (اختیاری)
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="پاسخ اصلی")  # پاسخ اصلی
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربری که پاسخ داده است
    reply_text = models.TextField(verbose_name="متن پاسخ")  # متن پاسخ
    reply_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پاسخ")  # تاریخ ارسال پاسخ

    def __str__(self):
        if self.parent_reply:
            return f"Reply to Reply by {self.user.username}"
        return f"Reply by {self.user.username} to {self.review.movie.title}"  # نمایش اطلاعات پاسخ


# مدل کارگردان‌ها
class Director(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام کارگردان")
    birth_date = models.DateField(verbose_name="تاریخ تولد")
    nationality = models.CharField(max_length=50, verbose_name="ملیت")

    def __str__(self):
        return self.name


# ارتباط بین فیلم‌ها و کارگردان‌ها
class MovieDirector(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")
    director = models.ForeignKey(Director, on_delete=models.CASCADE, verbose_name="کارگردان")

    def __str__(self):
        return f"{self.movie.title} - {self.director.name}"


# مدل فصل‌های سریال‌ها
class Season(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="سریال")
    season_number = models.PositiveIntegerField(verbose_name="شماره فصل")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")

    def __str__(self):
        return f"{self.movie.title} - فصل {self.season_number}"


# مدل قسمت‌های سریال‌ها
class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name="فصل")
    episode_number = models.PositiveIntegerField(verbose_name="شماره قسمت")
    title = models.CharField(max_length=200, verbose_name="عنوان قسمت")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")

    def __str__(self):
        return f"{self.season.movie.title} - فصل {self.season.season_number} - قسمت {self.episode_number}"


# مدل لایک‌ها
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")
    liked = models.BooleanField(default=True, verbose_name="لایک شده")  # True برای لایک، False برای دیسلایک

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {'Liked' if self.liked else 'Disliked'}"


# مدل لیست‌های پخش کاربران
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    name = models.CharField(max_length=100, verbose_name="نام لیست پخش")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


# آیتم‌های موجود در لیست پخش
class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, verbose_name="لیست پخش")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")
    added_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ اضافه شدن")

    def __str__(self):
        return f"{self.playlist.name} - {self.movie.title}"


# مدل پیشنهادات فیلم به کاربران
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")
    recommended_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پیشنهاد")

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

# مدل ترجیحات ژانر کاربران
class UserGenrePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="ژانر")
    preference_level = models.PositiveIntegerField(verbose_name="سطح علاقه (1 تا 5)")  # 1 کمترین، 5 بیشترین علاقه

    def __str__(self):
        return f"{self.user.username} - {self.genre.genre_name} - علاقه {self.preference_level}"
    

