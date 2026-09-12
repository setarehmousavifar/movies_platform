from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from main.exceptions import DomainError
from main.models import Animation, FavoriteItem, Genre, Movie, Review, Series
from main.services import (
    AlertService,
    EntitlementService,
    EnrichmentService,
    FavoriteService,
    RecommendationService,
    ReviewService,
    SearchService,
    SubscriptionService,
    ViewCountService,
    WatchlistService,
)

from .serializers import (
    AnimationDetailSerializer,
    AnimationListSerializer,
    EnrichRequestSerializer,
    FavoriteItemSerializer,
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    NotificationSerializer,
    RegisterSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
    SearchResultSerializer,
    SeriesDetailSerializer,
    SeriesListSerializer,
    SubscriptionSerializer,
    UserSerializer,
    WatchlistSerializer,
)
from .throttles import AuthBurstThrottle, WriteBurstThrottle


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstThrottle]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)


@extend_schema_view(
    list=extend_schema(tags=['catalog']),
    retrieve=extend_schema(tags=['catalog']),
)
class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().prefetch_related('genres', 'download_links')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'country', 'genres']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'overall_rating', 'view_count', 'title']
    ordering = ['-release_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ViewCountService.bump(Movie, instance.pk)
        instance.refresh_from_db(fields=['view_count'])
        return Response(self.get_serializer(instance).data)


@extend_schema_view(list=extend_schema(tags=['catalog']), retrieve=extend_schema(tags=['catalog']))
class SeriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Series.objects.all().prefetch_related('genres', 'download_links')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'country', 'genres', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'overall_rating', 'view_count', 'start_year', 'title']
    ordering = ['-release_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SeriesDetailSerializer
        return SeriesListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ViewCountService.bump(Series, instance.pk)
        instance.refresh_from_db(fields=['view_count'])
        return Response(self.get_serializer(instance).data)


@extend_schema_view(list=extend_schema(tags=['catalog']), retrieve=extend_schema(tags=['catalog']))
class AnimationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Animation.objects.all().prefetch_related('genres', 'download_links')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['language', 'country', 'genres']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'overall_rating', 'view_count', 'title']
    ordering = ['-release_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnimationDetailSerializer
        return AnimationListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ViewCountService.bump(Animation, instance.pk)
        instance.refresh_from_db(fields=['view_count'])
        return Response(self.get_serializer(instance).data)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class ReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Review.objects.select_related('user', 'movie', 'series', 'animation').filter(
        parent__isnull=True
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['movie', 'series', 'animation', 'user']
    ordering = ['-review_date']
    throttle_classes = [WriteBurstThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            review = ReviewService.create_review(
                user=request.user,
                rating=data['rating'],
                review_text=data.get('review_text', ''),
                movie=data.get('movie'),
                series=data.get('series'),
                animation=data.get('animation'),
                parent_id=data.get('parent_id'),
            )
        except DomainError as exc:
            return Response({'detail': exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class FavoriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteItemSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [WriteBurstThrottle]

    def get_queryset(self):
        return FavoriteItem.objects.filter(user=self.request.user).select_related(
            'movie', 'series', 'animation'
        )

    def create(self, request, *args, **kwargs):
        movie_id = request.data.get('movie')
        if not movie_id:
            return Response({'detail': 'movie is required.'}, status=400)
        movie = get_object_or_404(Movie, pk=movie_id)
        try:
            item, created = FavoriteService.add_movie(request.user, movie)
        except DomainError as exc:
            return Response({'detail': exc.message}, status=400)
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(FavoriteItemSerializer(item).data, status=code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.movie_id:
            FavoriteService.remove_movie(request.user, instance.movie)
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchlistViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [WriteBurstThrottle]

    def get_queryset(self):
        return WatchlistService.list_for(self.request.user)

    def create(self, request, *args, **kwargs):
        movie_id = request.data.get('movie')
        if not movie_id:
            return Response({'detail': 'movie is required.'}, status=400)
        movie = get_object_or_404(Movie, pk=movie_id)
        try:
            item, created = WatchlistService.add_movie(request.user, movie)
        except DomainError as exc:
            return Response({'detail': exc.message}, status=400)
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(WatchlistSerializer(item).data, status=code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.movie_id:
            WatchlistService.remove_movie(request.user, instance.movie)
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sub = SubscriptionService.current_for(request.user)
        return Response(
            {
                'role': request.user.role,
                'has_premium_access': request.user.has_premium_access(),
                'can_download': EntitlementService.can_download(request.user),
                'subscription': SubscriptionSerializer(sub).data if sub else None,
            }
        )


class SubscriptionRequestUpgradeView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [WriteBurstThrottle]

    def post(self, request):
        try:
            SubscriptionService.request_upgrade(
                user=request.user, note=request.data.get('note', '')
            )
        except DomainError as exc:
            return Response({'detail': exc.message}, status=400)
        return Response({'detail': 'Upgrade request recorded.'}, status=status.HTTP_202_ACCEPTED)


@extend_schema(
    parameters=[OpenApiParameter(name='q', required=True, type=str)],
    responses=SearchResultSerializer(many=True),
    tags=['search'],
)
class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = (request.query_params.get('q') or '').strip()
        if not query:
            return Response([])
        results = SearchService.search_all(query)
        return Response(SearchResultSerializer(results, many=True).data)


@extend_schema(responses=MovieListSerializer(many=True), tags=['recommendations'])
class RecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 10) or 10), 30)
        movies = RecommendationService.recommend_movies(request.user, limit=limit)
        return Response(MovieListSerializer(movies, many=True, context={'request': request}).data)


@extend_schema(request=EnrichRequestSerializer, tags=['enrichment'])
class EnrichMovieView(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [WriteBurstThrottle]

    def post(self, request, pk):
        force = bool(request.data.get('force', False))
        movie = get_object_or_404(Movie, pk=pk)
        EnrichmentService.enrich_instance(movie, force=force)
        movie.refresh_from_db()
        return Response(MovieDetailSerializer(movie, context={'request': request}).data)


@extend_schema(request=EnrichRequestSerializer, tags=['enrichment'])
class EnrichSeriesView(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [WriteBurstThrottle]

    def post(self, request, pk):
        force = bool(request.data.get('force', False))
        series = get_object_or_404(Series, pk=pk)
        EnrichmentService.enrich_instance(series, force=force)
        series.refresh_from_db()
        return Response(SeriesDetailSerializer(series, context={'request': request}).data)


@extend_schema(request=EnrichRequestSerializer, tags=['enrichment'])
class EnrichAnimationView(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [WriteBurstThrottle]

    def post(self, request, pk):
        force = bool(request.data.get('force', False))
        animation = get_object_or_404(Animation, pk=pk)
        EnrichmentService.enrich_instance(animation, force=force)
        animation.refresh_from_db()
        return Response(AnimationDetailSerializer(animation, context={'request': request}).data)


@extend_schema(responses=NotificationSerializer(many=True), tags=['alerts'])
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = AlertService.recent_for(request.user, limit=30)
        return Response(NotificationSerializer(items, many=True).data)


@extend_schema(tags=['alerts'])
class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [WriteBurstThrottle]

    def post(self, request, pk):
        ok = AlertService.mark_read(request.user, pk)
        if not ok:
            return Response({'detail': 'Not found or already read.'}, status=404)
        return Response({'detail': 'Marked as read.'})


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [AuthBurstThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [AuthBurstThrottle]
