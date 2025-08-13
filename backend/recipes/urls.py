from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientViewSet


app_name = 'recipes'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
