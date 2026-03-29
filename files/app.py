import os
from flask import Flask, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret"  # Change this to anything random

# --- Paste your GitHub OAuth app credentials here ---
GITHUB_CLIENT_ID = "Ov23lihF4b4gmTJBJLtU"
GITHUB_CLIENT_SECRET = "4df96b14c8adfd4628c4a5689909508de68ae635"
# ----------------------------------------------------

GITHUB_AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API = "https://api.github.com/user"
CALLBACK_URL = "http://localhost:3000/auth/github/callback"


@app.route("/")
def index():
    return open("github-login.html").read()


@app.route("/auth/github")
def github_login():
    github = OAuth2Session(GITHUB_CLIENT_ID, redirect_uri=CALLBACK_URL, scope=["user:email"])
    authorization_url, state = github.authorization_url(GITHUB_AUTHORIZATION_URL)
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/auth/github/callback")
def github_callback():
    github = OAuth2Session(GITHUB_CLIENT_ID, state=session["oauth_state"], redirect_uri=CALLBACK_URL)
    token = github.fetch_token(
        GITHUB_TOKEN_URL,
        client_secret=GITHUB_CLIENT_SECRET,
        authorization_response=request.url
    )
    session["oauth_token"] = token

    # Get the user's GitHub profile
    user_data = github.get(GITHUB_USER_API).json()
    name = user_data.get("name") or user_data.get("login")
    avatar = user_data.get("avatar_url")
    username = user_data.get("login")

    # Show a simple success page
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Signed in!</title>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
      <style>
        body {{
          background: #0d0d0d;
          color: #f0ede8;
          font-family: 'DM Sans', sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          margin: 0;
        }}
        .card {{
          background: #161616;
          border: 1px solid #2a2a2a;
          border-radius: 20px;
          padding: 48px;
          text-align: center;
          max-width: 360px;
          width: 90%;
        }}
        img {{ border-radius: 50%; margin-bottom: 20px; border: 3px solid #2a2a2a; }}
        h1 {{ font-size: 22px; margin-bottom: 8px; }}
        p {{ color: #6b6862; font-size: 14px; }}
        a {{
          display: inline-block;
          margin-top: 24px;
          background: #1c1c1c;
          border: 1px solid #2a2a2a;
          color: #f0ede8;
          padding: 10px 24px;
          border-radius: 10px;
          text-decoration: none;
          font-size: 14px;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <img src="{avatar}" width="80" height="80" />
        <h1>Hey, {name}! 👋</h1>
        <p>You're signed in as <strong>@{username}</strong> via GitHub.</p>
        <a href="/">← Back to login</a>
      </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allows HTTP on localhost
    app.run(port=3000, debug=True)
