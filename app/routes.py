from flask import render_template
from flask import render_template_string, request, redirect, url_for, session
from app import app
from app.models import (
    Usuario, Vitima, Investigador, Delegado,
    Occurrence, Investigation, Agendamento,
    occurrences, investigations, agendamentos, users
)

# --------------------------------
# Função auxiliar para obter o usuário logado
# --------------------------------
def get_current_user():
    username = session.get("username")
    if username and username in users:
        return users[username]
    return None

# --------------------------------
# Rotas de Login / Logout
# --------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        senha = request.form.get("senha")
        user = users.get(username)
        if user and user.senha == senha:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Login inválido")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

# --------------------------------
# Rotas para Vítima
# --------------------------------

@app.route("/vitima/registrar", methods=["GET", "POST"])
def registrar_ocorrencia():
    user = get_current_user()
    if not user or user.role != "vitima":
        return redirect(url_for("login"))

    if request.method == "POST":
        descricao = request.form.get("descricao")
        user.registrar_ocorrencia(descricao)
        return redirect(url_for("acompanhar_ocorrencias"))

    return render_template("registrar_ocorrencia.html")
@app.route("/vitima/ocorrencias")

def acompanhar_ocorrencias():
    user = get_current_user()
    if not user or user.role != "vitima":
        return redirect(url_for("login"))

    minhas_ocorrencias = user.acompanhar_ocorrencias()
    return render_template("acompanhar_ocorrencias.html", ocorrencias=minhas_ocorrencias)


@app.route("/investigador/ocorrencias")
def listar_ocorrencias():
    user = get_current_user()
    if not user or user.role != "investigador":
        return redirect(url_for("login"))

    novas = [o for o in occurrences if o.status == "Nova"]
    return render_template("listar_ocorrencias.html", novas=novas)

@app.route("/investigador/investigar/<int:ocorrencia_id>", methods=["GET", "POST"])
def investigar_ocorrencia(ocorrencia_id):
    user = get_current_user()
    if not user or user.role != "investigador":
        return redirect(url_for("login"))

    ocorrencia = next((o for o in occurrences if o.id == ocorrencia_id), None)
    if not ocorrencia:
        return "Ocorrência não encontrada", 404

    if request.method == "POST":
        suspeito = request.form.get("suspeito")
        evidencias = request.form.get("evidencias")
        user.investigar(ocorrencia, suspeito, evidencias)
        return redirect(url_for("listar_ocorrencias"))

    return render_template("investigar_ocorrencia.html", ocorrencia=ocorrencia)
@app.route("/investigador/solicitar_pericia/<int:ocorrencia_id>", methods=["GET", "POST"])
def solicitar_pericia(ocorrencia_id):
    user = get_current_user()
    if not user or user.role != "investigador":
        return redirect(url_for("login"))

    ocorrencia = next((o for o in occurrences if o.id == ocorrencia_id), None)
    if not ocorrencia:
        return "Ocorrência não encontrada", 404

    if request.method == "POST":
        data_pericia = request.form.get("data_pericia")
        descricao = request.form.get("descricao")
        user.solicitar_pericia(ocorrencia, data_pericia, descricao)
        return redirect(url_for("listar_ocorrencias"))

    return render_template("solicitar_pericia.html", ocorrencia=ocorrencia)


@app.route("/delegado/investigacoes")
def listar_investigacoes():
    user = get_current_user()
    if not user or user.role != "delegado":
        return redirect(url_for("login"))

    pendentes = [inv for inv in investigations if inv.decisao is None]
    return render_template("listar_investigacoes.html", pendentes=pendentes)

@app.route("/delegado/avaliar/<int:investigation_id>", methods=["GET", "POST"])
def avaliar_investigacao(investigation_id):
    user = get_current_user()
    if not user or user.role != "delegado":
        return redirect(url_for("login"))

    investigation = next((inv for inv in investigations if inv.id == investigation_id), None)
    if not investigation:
        return "Investigação não encontrada", 404

    if request.method == "POST":
        decisao = request.form.get("decisao")
        user.avaliar_investigacao(investigation, decisao)
        return redirect(url_for("listar_investigacoes"))

    return render_template("avaliar_investigacao.html", investigation=investigation)

@app.route("/")
def index():
    return redirect(url_for("login"))
