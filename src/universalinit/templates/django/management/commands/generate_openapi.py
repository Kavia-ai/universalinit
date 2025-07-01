from django.core.management.base import BaseCommand
from drf_yasg.openapi import Info
from drf_yasg.generators import OpenAPISchemaGenerator
import json

class Command(BaseCommand):
    help = 'Generate OpenAPI schema as openapi.json'

    def handle(self, *args, **options):
        from rest_framework.permissions import AllowAny
        from drf_yasg.views import get_schema_view

        schema_view = get_schema_view(
            Info(title="My API", default_version='v1'),
            public=True,
            permission_classes=(AllowAny,),
        )

        # Use schema generator to get schema
        generator = OpenAPISchemaGenerator(info=schema_view.info)
        schema = generator.get_schema(request=None, public=True)

        # Dump to file
        with open("openapi.json", "w") as f:
            json.dump(schema, f, indent=2)

        self.stdout.write(self.style.SUCCESS('Successfully generated openapi.json'))
