from main import app
import json

# Get the OpenAPI schema
openapi_schema = app.openapi()

# Write to file
with open("openapi.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)
