from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db_execute

login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        rows = db_execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = rows[0]
        if row:
            return User(row["id"], row["username"], row["password"])
        return None

    @staticmethod
    def get_by_username(username):
        rows = db_execute("SELECT * FROM users WHERE username = %s", (username,))
        row = rows[0]
        if row:
            return User(row["id"], row["username"], row["password"])
        return None


# Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Helpers
def register_user(username, password):
    if User.get_by_username(username):
        return False

    hashed = generate_password_hash(password)
    db_execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed),
        True
    )
    return True

def authenticate(username, password):
    user = User.get_by_username(username)
    if user and check_password_hash(user.password, password):
        return user
    return None