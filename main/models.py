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
        verbose_name = "User"
        verbose_name_plural = "Users"


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
        return self.get_name_display() 


# مدل مربوط به فیلم‌ها/سریال‌ها
class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")  
    genres = models.ManyToManyField('Genre', related_name='movies', verbose_name="ژانرها")  
    release_date = models.DateField(verbose_name="تاریخ انتشار")  
    description = models.TextField(verbose_name="توضیحات")  
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")  
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")  
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر (لینک)")  
    poster_image = models.ImageField(upload_to='posters/', null=True, blank=True, verbose_name="پوستر (تصویر)") 
    background_poster = models.ImageField(upload_to='backgrounds/', null=True, blank=True, verbose_name="پوستر پس‌زمینه")
    language = models.CharField(max_length=50, verbose_name="زبان")  
    age_rating = models.ForeignKey(AgeRating, on_delete=models.SET_NULL, null=True, verbose_name="رده‌بندی سنی")
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="امتیاز کلی")  
    country = models.CharField(max_length=100, verbose_name="کشور تولید")  
    directors = models.ManyToManyField('Director', related_name="movies", verbose_name="کارگردان‌ها")
    stars = models.ManyToManyField('Actor', related_name="movies", verbose_name="بازیگران")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="برچسب‌ها")  
    favorites = models.ManyToManyField(User, related_name="favorite_movies", blank=True, verbose_name="علاقه‌مندی‌ها")  
    trailer_url = models.URLField(null=True, blank=True, verbose_name="لینک تریلر")  
    trailer_video = models.FileField(upload_to='trailers/', null=True, blank=True, verbose_name="ویدئو تریلر")  

    def __str__(self):
        return self.title 
    
    def get_poster(self):
        # اولویت نمایش پوستر آپلود شده است. اگر موجود نبود، لینک استفاده می‌شود.
        if self.poster_image:
            return self.poster_image.url
        elif self.poster_url:
            return self.poster_url
        return None
    
    def get_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

class Series(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان سریال")
    start_year = models.PositiveIntegerField(verbose_name="سال شروع")  
    end_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="سال پایان") 
    status = models.CharField(max_length=20, choices=[('ongoing', 'در حال پخش'), ('ended', 'تمام شده')], verbose_name="وضعیت پخش")  
    seasons = models.PositiveIntegerField(verbose_name="تعداد فصل‌ها")  
    episodes = models.PositiveIntegerField(verbose_name="تعداد قسمت‌ها") 
    genres = models.ManyToManyField('Genre', related_name='series', verbose_name="ژانرها")
    release_date = models.DateField(verbose_name="تاریخ انتشار اولین قسمت")  
    description = models.TextField(verbose_name="توضیحات")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان هر قسمت (دقیقه)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر (لینک)")
    poster_image = models.ImageField(upload_to='posters/', null=True, blank=True, verbose_name="پوستر (تصویر)")
    background_poster = models.ImageField(upload_to='backgrounds/', null=True, blank=True, verbose_name="پوستر پس‌زمینه")
    language = models.CharField(max_length=50, verbose_name="زبان")
    age_rating = models.ForeignKey(AgeRating, on_delete=models.SET_NULL, null=True, verbose_name="رده‌بندی سنی")
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="امتیاز کلی")
    country = models.CharField(max_length=100, verbose_name="کشور تولید")
    directors = models.ManyToManyField('Director', related_name="series", verbose_name="کارگردان‌ها")
    stars = models.ManyToManyField('Actor', related_name="series", verbose_name="بازیگران")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="برچسب‌ها")
    favorites = models.ManyToManyField(User, related_name="favorite_series", blank=True, verbose_name="علاقه‌مندی‌ها")
    trailer_url = models.URLField(null=True, blank=True, verbose_name="لینک تریلر") 
    trailer_video = models.FileField(upload_to='trailers/', null=True, blank=True, verbose_name="ویدئو تریلر") 

    def __str__(self):
        return self.title

    def get_poster(self):
        if self.poster_image:
            return self.poster_image.url
        elif self.poster_url:
            return self.poster_url
        return None

    def get_years(self):
        # فرمت سال‌ها به صورت "2008–2013" یا "2008–"
        return f"{self.start_year}–{self.end_year if self.end_year else ''}"
    
    def get_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

class Animation(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان انیمیشن")
    genres = models.ManyToManyField('Genre', related_name='animations', verbose_name="ژانرها")
    release_date = models.DateField(verbose_name="تاریخ انتشار")
    description = models.TextField(verbose_name="توضیحات")
    duration = models.PositiveIntegerField(verbose_name="مدت زمان (دقیقه)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    poster_url = models.URLField(null=True, blank=True, verbose_name="پوستر (لینک)")
    poster_image = models.ImageField(upload_to='posters/', null=True, blank=True, verbose_name="پوستر (تصویر)")
    background_poster = models.ImageField(upload_to='backgrounds/', null=True, blank=True, verbose_name="پوستر پس‌زمینه")
    language = models.CharField(max_length=50, verbose_name="زبان")
    age_rating = models.ForeignKey(AgeRating, on_delete=models.SET_NULL, null=True, verbose_name="رده‌بندی سنی")
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name="امتیاز کلی")
    country = models.CharField(max_length=100, verbose_name="کشور تولید")
    tags = models.ManyToManyField('Tag', blank=True, verbose_name="برچسب‌ها")
    favorites = models.ManyToManyField(User, related_name="favorite_animations", blank=True, verbose_name="علاقه‌مندی‌ها")
    trailer_url = models.URLField(null=True, blank=True, verbose_name="لینک تریلر")  
    trailer_video = models.FileField(upload_to='trailers/', null=True, blank=True, verbose_name="ویدئو تریلر") 

    def __str__(self):
        return self.title

    def get_poster(self):
        if self.poster_image:
            return self.poster_image.url
        elif self.poster_url:
            return self.poster_url
        return None

    def get_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

# مدل مربوط به ژانرها
class Genre(models.Model):
    genre_name = models.CharField(max_length=100, verbose_name="نام ژانر")  
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات") 

    def __str__(self):
        return self.genre_name 


# مدل مربوط به بازیگران
class Actor(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام بازیگر")  
    birth_date = models.DateField(verbose_name="تاریخ تولد")  
    nationality = models.CharField(max_length=50, verbose_name="ملیت")  

    def __str__(self):
        return self.name  


# مدل مربوط به ارتباط بین فیلم و بازیگر
class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, verbose_name="بازیگر")  
    role = models.CharField(max_length=100, verbose_name="نقش بازیگر") 

    def __str__(self):
        return f"{self.actor.name} in {self.movie.title}" 


# مدل مربوط به ارتباط بین فیلم و ژانر
class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="ژانر") 

    def __str__(self):
        return f"{self.movie.title} - {self.genre.genre_name}"  


# مدل تراکنش‌های کیف پول
class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر مربوط به تراکنش
    transaction_type = models.CharField(max_length=50, choices=[('credit', 'شارژ'), ('debit', 'برداشت')], verbose_name="نوع تراکنش")  # نوع تراکنش (شارژ یا برداشت)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ تراکنش")
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تراکنش")  

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"  # نمایش جزئیات تراکنش


# مدل اشتراک‌ها
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  # کاربر مربوط به اشتراک
    subscription_type = models.CharField(max_length=50, choices=[('basic', 'Basic'), ('premium', 'Premium')], default='basic')  # نوع اشتراک
    start_date = models.DateField(verbose_name="تاریخ شروع")  # تاریخ شروع اشتراک
    end_date = models.DateField(verbose_name="تاریخ پایان")  # تاریخ پایان اشتراک
    is_active = models.BooleanField(default=True)  # وضعیت اشتراک (فعال یا غیرفعال)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"  # نمایش نوع اشتراک


# مدل نقدها و امتیازات
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE, null=True, blank=True)  
    rating = models.PositiveIntegerField(verbose_name="امتیاز")  
    review_text = models.TextField(null=True, blank=True, verbose_name="متن نقد")  
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ نقد")  

    def __str__(self):
        return f"{self.user.username} - {self.movie.title if self.movie else self.animation.title} - {self.rating}"  


class Reply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True, verbose_name="نقد")  
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="پاسخ اصلی")  
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  
    reply_text = models.TextField(verbose_name="متن پاسخ")  
    reply_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پاسخ")  

    def __str__(self):
        if self.parent_reply:
            return f"Reply to Reply by {self.user.username}"
        return f"Reply by {self.user.username} to {self.review.movie.title}"  


# مدل تاریخچه تماشا
class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  
    watch_datetime = models.DateTimeField(auto_now_add=True, verbose_name="زمان تماشا")  

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {self.watch_datetime}"  


# مدل فیلم‌های محبوب
class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")  
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"  


# مدل اعلان‌ها
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر") 
    message = models.TextField(verbose_name="پیام اعلان")  
    sent_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")  
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")  

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}..."  


# مدل لینک های دانلود
class DownloadLink(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='download_links')  
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE, null=True, blank=True) 
    quality = models.CharField(max_length=20, choices=[('720p', '720p'), ('1080p', '1080p'), ('4K', '4K')])  
    download_url = models.URLField()  
    file_size = models.CharField(max_length=50)  

    def __str__(self):
        return f"{self.movie.title} - {self.quality} ({self.file_size})"  


# مدل زیرنویس ها
class Subtitle(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم") 
    language = models.CharField(max_length=50, verbose_name="زبان زیرنویس") 
    subtitle_file = models.URLField(verbose_name="فایل زیرنویس")  

    def __str__(self):
        return f"{self.movie.title} - {self.language}"  


#  مدل برچسب های فیلم
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")  
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")  

    def __str__(self):
        return self.name  


class MovieTag(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم") 
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="برچسب") 

    def __str__(self):
        return f"{self.movie.title} - {self.tag.name}"  


class VideoQuality(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="فیلم")  
    quality = models.CharField(max_length=20, choices=[('480p', '480p'), ('720p', '720p'), ('1080p', '1080p'), ('2k', '2k'), ('4K', '4K')], verbose_name="کیفیت")  
    stream_url = models.URLField(verbose_name="لینک پخش آنلاین")  
    download_url = models.URLField(verbose_name="لینک دانلود")  

    def __str__(self):
        return f"{self.movie.title} - {self.quality}"  


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
    preference_level = models.PositiveIntegerField(verbose_name="سطح علاقه (1 تا 5)")  

    def __str__(self):
        return f"{self.user.username} - {self.genre.genre_name} - interest {self.preference_level}"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)  
    birth_date = models.DateField(blank=True, null=True)  
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")  
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Movie")  
    added_date = models.DateTimeField(auto_now_add=True, verbose_name="Date Added") 

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

    class Meta:
        unique_together = ('user', 'movie')  # یک فیلم نمی‌تواند بیش از یک بار در واچ‌لیست کاربر باشد
        verbose_name = "Watchlist Item"
        verbose_name_plural = "Watchlist Items"
