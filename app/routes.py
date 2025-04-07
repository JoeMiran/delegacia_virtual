# app/routes.py

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
            return "Login inválido", 401
    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            Username: <input type="text" name="username" required><br>
            Senha: <input type="password" name="senha" required><br>
            <input type="submit" value="Entrar">
        </form>
    """)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# --------------------------------
# Rota de Dashboard (redireciona conforme papel do usuário)
# --------------------------------

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if user.role == "vitima":
        return render_template_string("""
            <h2>Dashboard Vítima</h2>
            <ul>
                <li><a href="{{ url_for('registrar_ocorrencia') }}">Registrar Ocorrência</a></li>
                <li><a href="{{ url_for('acompanhar_ocorrencias') }}">Acompanhar Investigações</a></li>
                <li><a href="{{ url_for('logout') }}">Logout</a></li>
            </ul>
        """)
    elif user.role == "investigador":
        return render_template_string("""
            <h2>Dashboard Investigador</h2>
            <ul>
                <li><a href="{{ url_for('listar_ocorrencias') }}">Listar Ocorrências (Status: Nova)</a></li>
                <li><a href="{{ url_for('logout') }}">Logout</a></li>
            </ul>
        """)
    elif user.role == "delegado":
        return render_template_string("""
            <h2>Dashboard Delegado</h2>
            <ul>
                <li><a href="{{ url_for('listar_investigacoes') }}">Listar Investigações para Avaliação</a></li>
                <li><a href="{{ url_for('logout') }}">Logout</a></li>
            </ul>
        """)
    else:
        return "Perfil não reconhecido", 400

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

    return render_template_string("""
        <h2>Registrar Ocorrência</h2>
        <form method="post">
            Descrição: <textarea name="descricao" required></textarea><br>
            <input type="submit" value="Registrar">
        </form>
        <a href="{{ url_for('dashboard') }}">Voltar</a>
    """)

@app.route("/vitima/ocorrencias")
def acompanhar_ocorrencias():
    user = get_current_user()
    if not user or user.role != "vitima":
        return redirect(url_for("login"))

    minhas_ocorrencias = user.acompanhar_ocorrencias()
    return render_template_string("""
        <h2>Minhas Ocorrências</h2>
        <ul>
            {% for o in ocorrencias %}
                <li>
                    Ocorrência {{ o.id }}: {{ o.descricao }} - Status: {{ o.status }}
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('dashboard') }}">Voltar</a>
    """, ocorrencias=minhas_ocorrencias)

# --------------------------------
# Rotas para Investigador
# --------------------------------

@app.route("/investigador/ocorrencias")
def listar_ocorrencias():
    user = get_current_user()
    if not user or user.role != "investigador":
        return redirect(url_for("login"))

    novas = [o for o in occurrences if o.status == "Nova"]
    return render_template_string("""
        <h2>Ocorrências para Investigar</h2>
        <ul>
            {% for o in novas %}
                <li>
                    Ocorrência {{ o.id }}: {{ o.descricao }}
                    [<a href="{{ url_for('investigar_ocorrencia', ocorrencia_id=o.id) }}">Investigar</a>]
                    [<a href="{{ url_for('solicitar_pericia', ocorrencia_id=o.id) }}">Solicitar Perícia</a>]
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('dashboard') }}">Voltar</a>
    """, novas=novas)

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

    return render_template_string("""
        <h2>Investigar Ocorrência {{ ocorrencia.id }}</h2>
        <p>{{ ocorrencia.descricao }}</p>
        <form method="post">
            Suspeito: <input type="text" name="suspeito" required><br>
            Evidências: <textarea name="evidencias" required></textarea><br>
            <input type="submit" value="Registrar Investigação">
        </form>
        <a href="{{ url_for('listar_ocorrencias') }}">Voltar</a>
    """, ocorrencia=ocorrencia)

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

    return render_template_string("""
        <h2>Solicitar Perícia para Ocorrência {{ ocorrencia.id }}</h2>
        <form method="post">
            Data da Perícia: <input type="date" name="data_pericia" required><br>
            Descrição: <textarea name="descricao" required></textarea><br>
            <input type="submit" value="Solicitar Perícia">
        </form>
        <a href="{{ url_for('listar_ocorrencias') }}">Voltar</a>
    """, ocorrencia=ocorrencia)

# --------------------------------
# Rotas para Delegado
# --------------------------------

@app.route("/delegado/investigacoes")
def listar_investigacoes():
    user = get_current_user()
    if not user or user.role != "delegado":
        return redirect(url_for("login"))

    pendentes = [inv for inv in investigations if inv.decisao is None]
    return render_template_string("""
        <h2>Investigações para Avaliação</h2>
        <ul>
            {% for inv in pendentes %}
                <li>
                    Investigação {{ inv.id }} da Ocorrência {{ inv.ocorrencia.id }} - 
                    Suspeito: {{ inv.suspeito }}
                    [<a href="{{ url_for('avaliar_investigacao', investigation_id=inv.id) }}">Avaliar</a>]
                </li>
            {% endfor %}
        </ul>
        <a href="{{ url_for('dashboard') }}">Voltar</a>
    """, pendentes=pendentes)

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

    return render_template_string("""
        <h2>Avaliar Investigação {{ investigation.id }}</h2>
        <p>Ocorrência: {{ investigation.ocorrencia.descricao }}</p>
        <p>Suspeito: {{ investigation.suspeito }}</p>
        <p>Evidências: {{ investigation.evidencias }}</p>
        <form method="post">
            Decisão: <select name="decisao" required>
                <option value="Ordenar prisão">Ordenar prisão</option>
                <option value="Provas insuficientes, continue investigando">Provas insuficientes, continue investigando</option>
                <option value="Suspeito inocente">Suspeito inocente</option>
            </select><br>
            <input type="submit" value="Avaliar">
        </form>
        <a href="{{ url_for('listar_investigacoes') }}">Voltar</a>
    """, investigation=investigation)

# --------------------------------
# Rota Inicial
# --------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))
