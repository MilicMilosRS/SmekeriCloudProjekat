import json
import os

def handler(event, context):
    # Podaci o korisniku
    claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})

    user_id = claims.get('sub')  # jedinstveni ID korisnika
    email = claims.get('email')
    username = claims.get('cognito:username')
    first_name = claims.get('given_name')
    last_name = claims.get('family_name')
    groups = claims.get('cognito:groups', '')  # može biti string sa imenom grupe

    print("Korisnik:", username, "Email:", email, "Grupa:", groups)

    ret = {
        "id": user_id,
        "email": email,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "groups": groups
    }
    return {"statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,DELETE"
            },
            "body": json.dumps(ret)}
