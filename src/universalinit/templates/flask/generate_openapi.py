import json
from app import app, api  # import your Flask app and Api instance

with app.app_context():
    # flask-smorest stores the spec in api.spec
    openapi_spec = api.spec.to_dict()

    # Save to openapi.json file
    with open("openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)