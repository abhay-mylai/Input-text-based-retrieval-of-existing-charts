import requests
import jwt
from config import SUPERSET_URL, USERNAME, PASSWORD, SECRET_KEY

def get_superset_token():
    auth_url = f"{SUPERSET_URL}/api/v1/security/login"
    response = requests.post(auth_url, json={"username": USERNAME, "password": PASSWORD, "provider": "db"})  

    if response.status_code == 200:
        token = response.json()["access_token"]
        
        # Decode token for debugging
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Convert 'sub' to string if necessary
        if "sub" in decoded_token and not isinstance(decoded_token["sub"], str):
            decoded_token["sub"] = str(decoded_token["sub"])  # Convert it to a string
            token = jwt.encode(decoded_token, key=SECRET_KEY, algorithm="HS256")  # Re-encode token (only for debugging)

        
        return token  
    
    else:
        raise Exception(f"❌ Authentication Failed: {response.status_code} - {response.text}")


# Fetch all charts from Superset
def get_charts(token):
    charts_url = f"http://127.0.0.1:5000/api/v1/chart"
    headers = {"Authorization": f"Bearer {token}"}
    
    
    
    response = requests.get(charts_url, headers=headers)
    
    if response.status_code != 200:
        
        return []  # Return an empty list in case of failure
    else:
        try:
            data = response.json()
            return data.get("result", [])
        except ValueError as e:
            print(f"Failed to parse response: {e}")
            return []  # Return an empty list if parsing fails
