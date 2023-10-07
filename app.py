from locals import Flask, SQLAlchemy, LoginManager, SocketIO
from random import shuffle, randint

app = Flask(__name__)

symbols = list("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
shuffle(symbols)
app.secret_key = ''
for i in range(1, 21):
    app.secret_key += symbols[randint(0, 50)]
    if i % 4 == 0 and i != 20:
        app.secret_key += '-'
admin = app.secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///question.db'
app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_SITE_KEY'] = '6Len5DAmAAAAAN92u_a_vj7P4d6dw90BkSqYSG-O'
app.config['RECAPTCHA_SECRET_KEY'] = '6Len5DAmAAAAAGzuMI5PSdYSTv276kfNdpiRwWtL'

database = SQLAlchemy(app)
login_manager = LoginManager(app)
socket = SocketIO(app, ping_timeout=5, ping_interval=5)
login_manager.login_view = 'login'

with open("admin.key", "w", encoding="utf-8") as file:
    file.write(admin)