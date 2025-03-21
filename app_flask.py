
import os
import pandas as pd
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

from utils import preencher_escala_otimizado, gerar_estatisticas

load_dotenv()

app = Flask(__name__)
app.secret_key = "segredo_seguro"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Logger
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

USERS = {
    "admin": {"password": os.getenv("ADMIN_PASSWORD")},
    "user": {"password": os.getenv("USER_PASSWORD")}
}

if not USERS["admin"]["password"] or not USERS["user"]["password"]:
    raise ValueError("Erro: Senhas não carregadas corretamente do .env")

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in USERS:
        return User(username)
    return None

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
ALLOWED_EXTENSIONS = {"xlsx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("upload"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username]["password"]:
            stored_hash = USERS[username]["password"]
            logger.debug(f"Verificando login para {username}")
            if check_password_hash(stored_hash, password):
                login_user(User(username))
                return redirect(url_for("upload"))
        flash("Usuário ou senha incorretos!", "danger")

    return render_template("login.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    estatisticas = None

    if request.method == "POST":
        files = {}
        for key in ["escala", "disponibilidade", "inspetores", "preferencias"]:
            file = request.files.get(key)
            if file and allowed_file(file.filename):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                files[key] = filepath
                logger.debug(f"Arquivo {key} salvo em {filepath}")
            else:
                flash(f"Erro: Apenas arquivos .xlsx são permitidos ({key})", "error")
                return redirect(url_for("upload"))

        if len(files) < 4:
            flash("Erro: Todos os arquivos devem ser carregados!", "error")
            return redirect(url_for("upload"))

        try:
            escala_df = pd.read_excel(files["escala"])
            disponibilidade_df = pd.read_excel(files["disponibilidade"])
            inspetores_df = pd.read_excel(files["inspetores"])
            preferencia_df = pd.read_excel(files["preferencias"])

            for df in [escala_df, disponibilidade_df]:
                df["Semana"] = pd.to_datetime(df["Semana"], format="%d/%m/%Y", errors="coerce")

            preferencias = dict(zip(preferencia_df["Nome"], preferencia_df["Preferência"]))

            escala_final, estatisticas_df = preencher_escala_otimizado(
                escala_df.copy(), disponibilidade_df, inspetores_df, preferencias
            )

            escala_final["Semana"] = escala_final["Semana"].dt.strftime("%d/%m/%Y")
            estatisticas = estatisticas_df.to_dict(orient="records")

            result_path = os.path.join(STATIC_FOLDER, "Escala_Final_Otimizada.xlsx")
            escala_final.to_excel(result_path, index=False)

            flash("Escala gerada com sucesso!", "success")
            return render_template("index.html", estatisticas=estatisticas)

        except Exception as e:
            logger.error(f"Erro ao processar arquivos: {e}")
            flash(f"Erro ao processar arquivos: {e}", "error")
            return redirect(url_for("upload"))

    return render_template("index.html", estatisticas=estatisticas)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sessão com sucesso!", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
