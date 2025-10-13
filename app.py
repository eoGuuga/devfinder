# app.py
from flask import Flask

# 1. Cria a nossa aplicação web
app = Flask(__name__)

# 2. Define a rota (URL) para a página inicial
# O decorador '@app.route("/")' diz ao Flask: "Quando alguém acessar a URL principal do site ('/')...
@app.route("/")
def home():
    # 3. ...execute esta função. E o que ela retornar será exibido no navegador."
    return "Olá, Mundo! Este é o nosso servidor DevFinder."

# O código abaixo é necessário para rodar a aplicação diretamente do terminal
# Apenas para o ambiente de desenvolvimento.
if __name__ == "__main__":
    app.run(debug=True)