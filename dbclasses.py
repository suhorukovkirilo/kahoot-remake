from locals import UserMixin
from app import database, login_manager

Model = database.Model
Column = database.Column
Int = database.Integer
Str = database.String

class User(UserMixin, Model):
    id = Column(Int(), primary_key=True)
    name = Column(Str(500))
    score = Column(Int(), default=0)
    correct_questions = Column(Int(), default=0)

class FullAnswerQuestion(Model):
    id = Column(Int(), primary_key=True)
    question = Column(Str(1000))
    correct_answers = Column(Str(250))
    max_time = Column(Int(), default=35)

class OptionsQuestion(Model):
    id = Column(Int(), primary_key=True)
    question = Column(Str(1000))
    answer1 = Column(Str(250))
    answer2 = Column(Str(250))
    answer3 = Column(Str(250), default="")
    answer4 = Column(Str(250), default="")
    answer5 = Column(Str(250), default="")
    answer6 = Column(Str(250), default="")
    correct = Column(Str(250))
    max_time = Column(Int(), default=20)

class CheckQuestion(Model):
    id = Column(Int(), primary_key=True)
    question = Column(Str(1000))
    max_time = Column(Int(), default=40)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def str_type(question):
    return "FullAnswerQuestion" if type(question) is FullAnswerQuestion else "OptionsQuestion" if type(question) is OptionsQuestion else \
        "CheckQuestion" if type(question) is CheckQuestion else ""