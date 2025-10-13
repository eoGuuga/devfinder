# app.py

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    user_data = None
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            try:
                url = f"https://api.github.com/users/{username}"
                response = requests.get(url)
                response.raise_for_status()  # Gera um erro para respostas ruins (4xx ou 5xx)
                
                user_data = response.json()

            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 404:
                    error = f"Usuário '{username}' não encontrado."
                else:
                    error = f"Erro na API do GitHub: {http_err}"
            except Exception as err:
                error = f"Ocorreu um erro: {err}"

    return render_template("index.html", user=user_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)