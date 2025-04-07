# app/__init__.py
from flask import Flask

app = Flask(__name__)
app.secret_key = "secretkey"  # Chave para a sessão

# Importa as rotas após criar o objeto app
from app import routes
