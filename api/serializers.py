from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from main.models import (
    Animation,
    DownloadLink,
    FavoriteItem,
    Genre,
    Movie,
    Review,
    Series,
    Subscription,
    Watchlist,
)
from main.services import EntitlementService

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'genre_name', 'description')


class DownloadLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadLink
        fields = ('id', 'quality', 'file_size', 'download_url')


class DownloadLinkPublicSerializer(serializers.ModelSerializer):
    """Never expose raw download_url in catalog payloads."""

    unlock_path = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()

    class Meta:
        model = DownloadLink
        fields = ('id', 'quality', 'file_size', 'locked', 'unlock_path')

    def get_locked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        return not EntitlementService.can_download(user)

    def get_unlock_path(self, obj):
        return f'/api/v1/downloads/{obj.pk}/'


class CatalogTargetCreateSerializer(serializers.Serializer):
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), required=False, allow_null=True
    )
    series = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), required=False, allow_null=True
    )
    animation = serializers.PrimaryKeyRelatedField(
        queryset=Animation.objects.all(), required=False, allow_null=True
    )

    def validate(self, attrs):
        count = sum(attrs.get(k) is not None for k in ('movie', 'series', 'animation'))
        if count != 1:
            raise serializers.ValidationError(
                'Provide exactly one of movie, series, or animation.'
            )
        return attrs


class UpgradeRequestSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class CatalogListSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'title',
            'release_date',
            'overall_rating',
            'view_count',
            'language',
            'country',
            'poster',
            'ai_summary',
            'ai_tags',
        )

    def get_poster(self, obj):
        return obj.get_poster()


class MovieListSerializer(CatalogListSerializer):
    class Meta(CatalogListSerializer.Meta):
        model = Movie


class SeriesListSerializer(CatalogListSerializer):
    class Meta(CatalogListSerializer.Meta):
        model = Series
        fields = CatalogListSerializer.Meta.fields + (
            'start_year',
            'end_year',
            'status',
            'season_count',
            'episode_count',
        )


class AnimationListSerializer(CatalogListSerializer):
    class Meta(CatalogListSerializer.Meta):
        model = Animation


class MovieDetailSerializer(MovieListSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    download_links = serializers.SerializerMethodField()
    duration_display = serializers.CharField(source='get_duration', read_only=True)

    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + (
            'description',
            'duration',
            'duration_display',
            'trailer_url',
            'genres',
            'download_links',
            'ai_enriched_at',
        )

    def get_download_links(self, obj):
        links = obj.download_links.all()
        return DownloadLinkPublicSerializer(links, many=True, context=self.context).data


class SeriesDetailSerializer(SeriesListSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    download_links = serializers.SerializerMethodField()
    duration_display = serializers.CharField(source='get_duration', read_only=True)

    class Meta(SeriesListSerializer.Meta):
        fields = SeriesListSerializer.Meta.fields + (
            'description',
            'duration',
            'duration_display',
            'trailer_url',
            'genres',
            'download_links',
            'ai_enriched_at',
        )

    def get_download_links(self, obj):
        return MovieDetailSerializer.get_download_links(self, obj)


class AnimationDetailSerializer(AnimationListSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    download_links = serializers.SerializerMethodField()
    duration_display = serializers.CharField(source='get_duration', read_only=True)

    class Meta(AnimationListSerializer.Meta):
        fields = AnimationListSerializer.Meta.fields + (
            'description',
            'duration',
            'duration_display',
            'trailer_url',
            'genres',
            'download_links',
            'ai_enriched_at',
        )

    def get_download_links(self, obj):
        return MovieDetailSerializer.get_download_links(self, obj)


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    target_title = serializers.CharField(read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'username',
            'movie',
            'series',
            'animation',
            'rating',
            'review_text',
            'parent',
            'review_date',
            'target_title',
        )
        read_only_fields = ('review_date', 'username', 'target_title')

    def validate(self, attrs):
        movie = attrs.get('movie')
        series = attrs.get('series')
        animation = attrs.get('animation')
        if self.instance:
            movie = attrs.get('movie', self.instance.movie)
            series = attrs.get('series', self.instance.series)
            animation = attrs.get('animation', self.instance.animation)
        count = sum(x is not None for x in (movie, series, animation))
        if count != 1:
            raise serializers.ValidationError(
                'Provide exactly one of movie, series, or animation.'
            )
        return attrs


class ReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=10)
    review_text = serializers.CharField(required=False, allow_blank=True)
    movie = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), required=False, allow_null=True
    )
    series = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), required=False, allow_null=True
    )
    animation = serializers.PrimaryKeyRelatedField(
        queryset=Animation.objects.all(), required=False, allow_null=True
    )
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        count = sum(attrs.get(k) is not None for k in ('movie', 'series', 'animation'))
        if count != 1:
            raise serializers.ValidationError(
                'Provide exactly one of movie, series, or animation.'
            )
        return attrs


class FavoriteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteItem
        fields = ('id', 'movie', 'series', 'animation', 'added_date')
        read_only_fields = ('added_date',)


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ('id', 'movie', 'series', 'animation', 'added_date')
        read_only_fields = ('added_date',)


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            'id',
            'subscription_type',
            'start_date',
            'end_date',
            'is_active',
        )


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    has_premium_access = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'is_premium',
            'has_premium_access',
            'role',
        )

    def get_has_premium_access(self, obj):
        return obj.has_premium_access()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
        )

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Email already registered.')
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        validate_password(attrs['password'], user=User(username=attrs.get('username'), email=attrs.get('email')))
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    overall_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    poster = serializers.CharField(allow_null=True)
    ai_summary = serializers.CharField(allow_null=True, required=False)


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    message = serializers.CharField()
    sent_date = serializers.DateTimeField()
    is_read = serializers.BooleanField()


class EnrichRequestSerializer(serializers.Serializer):
    force = serializers.BooleanField(required=False, default=False)
