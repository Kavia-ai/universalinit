import json
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from rest_framework.request import Request
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

class Command(BaseCommand):
    def handle(self, *args, **options):
        factory = RequestFactory()
        django_request = factory.get('/api/?format=openapi')

        schema_view = get_schema_view(
            openapi.Info(
                title="My API",
                default_version='v1',
                description="Test description",
            ),
            public=True,
            permission_classes=(AllowAny,),
        )

        # Call the view with the raw Django HttpRequest
        response = schema_view.without_ui(cache_timeout=0)(django_request)
        response.render()

        with open("openapi.json", "wb") as f:
            f.write(response.content)