from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id, username, password) -> None:
        self.id = id
        self.username = username
        self.password = password
        

    @classmethod
    def check_password(self, hashedPass, password):
        return check_password_hash(hashedPass, password)