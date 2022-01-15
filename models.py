from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):

    def __init__(self, id, name, password, is_admin=True):
        self.id = id
        self.name = name
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)

users = []

def get_user(name):
    for user in users:
        if user.name == name:
            return user
    return None

admin = User(len(users)+1,"admin","admin")
users.append(admin)