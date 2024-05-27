#Script to get the spotify autorization token to use in development


import json
from flask import Flask, request, redirect
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import requests
import os
import signal
from dotenv import set_key, dotenv_values, find_dotenv

######### GPT CODE #########
def save_to_env(variables, file_path='.env'):
    # Find the .env file if it exists, or use the provided file_path
    dotenv_file = find_dotenv(file_path)
    if not dotenv_file:
        dotenv_file = file_path

    # Write each variable to the .env file
    for key, value in variables.items():
        set_key(dotenv_file, key, value)

#####################################
app = Flask(__name__)

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPE = [
    "user-read-email",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
    "playlist-read-private"
]
@app.route("/")
def teste():
    return "teste"

@app.route("/login")
def login():
    spotify = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = spotify.authorization_url(AUTH_URL)
    return redirect(authorization_url)

@app.route("/callback", methods=['GET'])
def callback():
    print('call')
    code = request.args.get('code')
    res = requests.post(TOKEN_URL,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        })
    
    variables = {"TOKEN": json.loads(res.content)['access_token']}
    save_to_env(variables)

    os.kill(os.getpid(), signal.SIGTERM)
    
    return json.dumps(res.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)