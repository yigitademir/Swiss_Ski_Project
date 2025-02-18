import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
client_secret = os.getenv("CLIENT_SECRET")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Validate environment variables
if not all([client_secret, username, password]):
    raise ValueError("One or more required environment variables are missing! Check CLIENT_SECRET, USERNAME, and PASSWORD.")

# Request to obtain the token
url = "https://api.swiss-ski.ch/auth/token"
payload = {
    "grant_type": "password",
    "client_id": "rest.force8.coach",
    "client_secret": client_secret,
    "username": username,
    "password": password
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Raises an HTTPError if the request fails
    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise ValueError("Failed to retrieve access token. Response data:", data)

    print("Access Token:", access_token)

except requests.exceptions.RequestException as e:
    print("Error fetching access token:", e)
    exit(1)

# Make an API request
api_url = "https://api.swiss-ski.ch/api/rest/request/get/club_fields"
headers = {"Authorization": f"Bearer {access_token}"}

try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  

    print("API Response:", response.json())  
except requests.exceptions.RequestException as e:
    print("Error fetching API data:", e)