from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

# Auth routes
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    dbbucher=db_read("SELECT * FROM bucher")
    return render_template("bucher.html", bucher=dbbucher )
    # gibt an bucher.html alle infos gespeicher unter bucher, bucher.html kann dann bucher verwenden.


@app.route('/add_book', methods=['POST'])
def add_book():
    titel = request.form['buchtitel']
    autor = request.form['autor']
    verlag = request.form['verlag']
    sprache = request.form['sprache']
    preis = request.form['originalpreis']
    # holt sich den wert aus "form" (liste) und speichert ihn in jeweiliger variable
    
    sql = "INSERT INTO bucher (buchtitel, autor, verlag, sprache, originalpreis) VALUES (%s, %s, %s, %s, %s)"
    db_write(sql, (titel, autor, verlag, sprache, preis)) # führt dbwrite mit sql string und werten in klammenr aus

    return redirect('/') # zurück zur startseite

@app.route('/delete', methods=["GET", "POST"])
def delete():
    id =  request.args.get('book_id') 
    sql = "DELETE FROM bucher WHERE id=%s"
    db_write(sql, (id,)) # , damit id nicht nur als string gelesen wird sondern als tupple (wie list)

    return redirect('/')

@app.get("/search")
@login_required
def search():
    query = request.args.get('suche', '').strip() # strip entfernt alle unnötigen leerzeichen etc

    if query:
        # Suche über Buchtitel/Autor
        sql = "SELECT * FROM bucher WHERE buchtitel LIKE %s OR autor LIKE %s"
        search_param = f"%{query}%"
        
        # speichert suche in results
        results = db_read(sql, (search_param, search_param))
    else:
        # falls suchfeld leer ist
        return redirect(url_for("index"))

    # zeigt nur gesuchte bücher an
    return render_template(
        "bucher.html", 
        bucher=results, 
        current_search=query
    )

@app.get("/add_angebot", methods=["GET", "POST"])
@login_required
def add_angebot():
    book_id = request.form['book_id']
    sql= "insert into bucher (user_id, buch_id, verkauft) VALUES (%s, %s, false)"
    db_write(sql, (current_user.id, book_id)) # führt dbwrite mit sql string und werten in klammenr aus

    return redirect('/') # zurück zur startseite


@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()

