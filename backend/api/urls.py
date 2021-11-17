import os

from django.conf.urls import url
from django.urls import include, path
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet

load_dotenv()


app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet,
                basename='recipes')
router.register('ingredients', IngredientsViewSet,
                basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
#     path('auth/signup/', views.SignupView.as_view()),
#     path('auth/token/', views.ConfirmationView.as_view())
]


schema_view = get_schema_view(
    openapi.Info(
        title="Foodgram",
        default_version='v1',
        description=("Документация для сервиса Foodgram"),
        contact=openapi.Contact(email=os.getenv('CONTACT_EMAIL')),
        license=openapi.License(name=os.getenv('LICENSE')),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    url(r'^docs/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^docs/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
]
