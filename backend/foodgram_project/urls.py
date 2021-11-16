import os

from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

load_dotenv()

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include('api.urls')),
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
    url(r'^docs/swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
]
