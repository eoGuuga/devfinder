# app.py
from flask import Flask, render_template # Importe a nova função

app = Flask(__name__)

@app.route("/")
def home():
    # A mágica acontece aqui: renderizamos nosso arquivo HTML
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)