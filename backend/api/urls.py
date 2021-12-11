import os

from django.urls import include, path
from djoser.views import TokenDestroyView
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from . import views

load_dotenv()


app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet,
                basename='recipes')
router.register('ingredients', views.IngredientsViewSet,
                basename='ingredients')
router.register('users', views.CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/token/login/',
        views.CustomTokenCreateView.as_view(), name='login'
    ),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout')
]


schema_view = get_schema_view(
    openapi.Info(
        title='Foodgram',
        default_version='v1',
        description=('Документация для сервиса Foodgram'),
        contact=openapi.Contact(email=os.getenv('CONTACT_EMAIL')),
        license=openapi.License(name=os.getenv('LICENSE')),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns += [
    path(
        'docs/swagger/json',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'docs/swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
]
