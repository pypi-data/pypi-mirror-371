import os

import openai
import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
    )


@app.route("/login/oauth/callback")
def callback():
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }
    token_headers = {"Accept": "application/json"}
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    token_json = token_response.json()
    session["access_token"] = token_json.get("access_token")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "access_token" in session:
        return render_template("index.html", authenticated=True)
    return redirect(url_for("home"))


@app.route("/ask", methods=["POST"])
def ask():
    if openai.api_key is None:
        print("La clé API n'est pas définie. Vérifiez vos variables d'environnement.")
    else:
        if "access_token" not in session:
            return redirect(url_for("home"))

        command = request.form["command"]
        response = openai.ChatCompletion.create(
            model="gpt-4.1", messages=[{"role": "user", "content": command}]
        )
        answer = response["choices"][0]["message"]["content"]
        return render_template("index.html", authenticated=True, answer=answer)


def launch_app():
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)  # Ensure there's a newline at the end
