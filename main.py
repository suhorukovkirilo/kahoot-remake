from locals import *
from app import app, admin, database, login_manager, socket
from dbclasses import User, FullAnswerQuestion, OptionsQuestion, CheckQuestion, str_type
from datetime import datetime, timedelta
from random import shuffle, randint

current_question, answered, what_answered, checked, answered_at, score_plus = -1.0, [], {}, {}, {}, {}
logged_users, timer = [], datetime.utcnow()
with app.app_context():
    database.create_all()
    questions = [*FullAnswerQuestion.query.filter_by().all(), *OptionsQuestion.query.filter_by().all(), *CheckQuestion.query.filter_by().all()]
    shuffle(questions)

@app.route("/testing", methods=['POST', 'GET'])
@login_required
def testing():
    global current_question
    if current_user.name not in [*logged_users, admin]:
        return redirect("/logout")
    if current_question == -1:
        return render_template("waiting.html", logged_users=logged_users, current_question=current_question, admin=admin)
    if type(current_question) is float:
            return render_template("some_results.html", answered=answered, what_answered=what_answered, question=questions[int(current_question)],
                                   type=str_type(questions[int(current_question)]), checked=checked, admin=admin,
                                   range=range(len(what_answered[current_user.name].split("//")) - 1) if current_user.name in answered else [],
                                   last_question=current_question + 1 == len(questions))
    if type(current_question) is int:
        if datetime.utcnow() > timer:
            current_question = float(current_question)
            return render_template("some_results.html", answered=answered, what_answered=what_answered, question=questions[int(current_question)],
                                   type=str_type(questions[int(current_question)]), checked=checked, admin=admin,
                                   range=range(len(what_answered[current_user.name].split("//")) - 1) if current_user.name in answered else [],
                                   last_question=current_question + 1 == len(questions))
        if datetime.utcnow() + timedelta(seconds=questions[current_question].max_time) > timer:
            return render_template("quiz.html", current_question=questions[current_question], answered=answered,
                                   type=str_type(questions[int(current_question)]), time_sec=round((timer - datetime.utcnow()).total_seconds()),
                                   qq=str(current_question+1) + "/" + str(len(questions)), admin=admin)
        return render_template("question.html", question=questions[current_question].question, admin=admin)
@app.route("/next_question")
@login_required
def next_question():
    if current_user.name == admin:
        global current_question, timer, answered, what_answered, checked, answered_at, score_plus
        if type(current_question) is float:
            if current_question == -1:
                for user in User.query.order_by().all():
                    user.score = 0
                    user.correct_questions = 0
                    database.session.commit()
                socket.emit('quiz_start')
            socket.emit('next')
            current_question += 1
            current_question = int(current_question)
            timer = datetime.utcnow() + timedelta(seconds=5+questions[current_question].max_time)
            answered = []
            what_answered = {}
            checked = {}
            answered_at = {}
            score_plus = {}
    return redirect("/testing")
@app.route("/statistic")
@login_required
def statistic():
    if current_user.name == admin:
        all_users = User.query.order_by(User.score.desc()).all()
        users = []
        for user in all_users:
            if user.name in logged_users and user.name != admin:
                users.append(user)
        return render_template("statistic.html", users=users, range=range(len(users)), score_plus=score_plus, admin=admin)
    return redirect("/testing")
@app.route("/add/FullAnswerQuestion", methods=['POST', 'GET'])
@login_required
def add_full_answer_question():
    if current_user.name != admin:
        return redirect("/testing")
    if request.method == 'POST':
        question = request.form['question']
        corrects = request.form['corrects']
        time = int(request.form['time'])
        if question != "" and corrects != "":
            full_answer_question = FullAnswerQuestion(question=question, correct_answers=corrects, max_time=time)
            database.session.add(full_answer_question)
            database.session.commit()
    return render_template("FullAnswerQuestion.html")
@app.route("/add/OptionsQuestion", methods=['POST', 'GET'])
@login_required
def add_options_question():
    if current_user.name != admin:
        return redirect("/testing")
    if request.method == 'POST':
        question = request.form['question']
        answer1 = request.form['answer1']
        answer2 = request.form['answer2']
        answer3 = request.form['answer3']
        answer4 = request.form['answer4']
        answer5 = request.form['answer5']
        answer6 = request.form['answer6']
        correct = request.form['correct']
        time = int(request.form['time'])
        if question != "" and answer1 != "" and answer2 != "" and correct != "":
            options_question = OptionsQuestion(question=question, answer1=answer1, answer2=answer2, answer3=answer3,
                                               answer4=answer4, answer5=answer5, answer6=answer6, correct=correct, max_time=time)
            database.session.add(options_question)
            database.session.commit()
    return render_template("OptionsQuestion.html")
@app.route("/add/CheckQuestion", methods=['POST', 'GET'])
@login_required
def add_check_question():
    if request.method == 'POST' and request.form['question'] != "":
        check_question = CheckQuestion(question=request.form['question'], time=int(request.form['time']))
        database.session.add(check_question)
        database.session.commit()
    return render_template("CheckQuestion.html")
@app.route("/answer", methods=['POST', 'GET'])
@login_required
def answer_full_question():
    global answered, what_answered, answered_at, score_plus
    if type(questions[current_question]) is FullAnswerQuestion:
        answer = request.form.get('answer')
        if current_user.name not in answered:
            answered.append(current_user.name)
            what_answered[current_user.name] = answer
            if answer in questions[current_question].correct_answers.split("//"):
                current_user.score += round((timer - datetime.utcnow()).total_seconds() * 25 + 500)
                score_plus[current_user.name] = round((timer - datetime.utcnow()).total_seconds() * 25 + 500)
                current_user.correct_questions += 1
                database.session.commit()
    if type(questions[current_question]) is CheckQuestion:
        answer = request.form.get('check-answer')
        if current_user.name not in answered:
            answered.append(current_user.name)
            what_answered[current_user.name] = answer
            answered_at[current_user.name] = (timer - datetime.utcnow()).total_seconds()
    return redirect("/testing")
@app.route("/answer/<string:answer>")
@login_required
def answer_options_question(answer):
    if type(questions[current_question]) is OptionsQuestion:
        global answered, what_answered, score_plus
        if current_user.name not in answered and answer in [questions[current_question].answer1, questions[current_question].answer2, questions[current_question].answer3,
                        questions[current_question].answer4, questions[current_question].answer5, questions[current_question].answer6]:
            answered.append(current_user.name)
            what_answered[current_user.name] = answer
            if answer == questions[current_question].correct:
                current_user.score += round((timer - datetime.utcnow()).total_seconds() * 25 + 500)
                score_plus[current_user.name] = round((timer - datetime.utcnow()).total_seconds() * 25 + 500)
                current_user.correct_questions += 1
                database.session.commit()
    return redirect("/testing")
@app.route("/check/<int:true>/<string:user>")
@login_required
def check_question(true, user):
    global checked, score_plus
    checked[user] = bool(true)
    if checked[user]:
        _user = User.query.filter_by(name=user).first()
        _user.score += round(answered_at[user] * 25 + 500)
        score_plus[_user.name] = round(answered_at[user] * 25 + 500)
        _user.correct_questions += 1
        database.session.commit()
    socket.emit('checked')
    return redirect("/testing")
@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/testing")
    if request.method == 'POST':
        nickname = request.form['nickname']
        user = User.query.filter_by(name=nickname).first()
        if not user and nickname not in ["", " "] and "kirill" not in nickname.lower() and "кирилл" not in nickname.lower():
            user = User(name=nickname)
            database.session.add(user)
            database.session.commit()
            logged_users.append(nickname)
            login_user(user)
            socket.emit('add_user', nickname)
            return redirect("/testing")
        elif nickname == admin:
            login_user(user)
            return redirect("/testing")
        else:
            flash("Введіть інше Ім'я користувача")
    return render_template("login.html", messages=get_flashed_messages())
@app.route("/clear")
def clear():
    if current_user.is_authenticated and current_user.name == admin:
        for user in User.query.order_by().all():
            database.session.delete(user)
        for question in FullAnswerQuestion.query.order_by().all():
            database.session.delete(question)
        for question in OptionsQuestion.query.order_by().all():
            database.session.delete(question)
        database.session.commit()
    return redirect("/testing")
@app.route("/reload")
def reload():
    if current_user.is_authenticated and current_user.name == admin:
        global questions
        questions = [*FullAnswerQuestion.query.filter_by().all(), *OptionsQuestion.query.filter_by().all(), *CheckQuestion.query.filter_by().all()]
    return redirect("/testing")
@app.route("/del/<string:user>")
@login_required
def delete(user):
    if current_user.name == admin:
        user = User.query.filter_by(name=user).first()
        if user:
            database.session.delete(user)
            database.session.commit()
            logged_users.remove(user.name)
    return redirect("/testing")
@app.route("/results")
@login_required
def results():
    all_users = User.query.order_by(User.score.desc()).all()
    users = []
    for user in all_users:
        if user.name in logged_users and user.name != admin:
            users.append(user)
    return render_template("results.html", users=users, range=range(len(users)), admin=admin)
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        try:
            logged_users.remove(current_user.name)
        except:
            pass
        logout_user()
    return redirect("/login")
@app.errorhandler(404)
def not_found(error):
    return redirect("/testing")


if __name__ == "__main__":
    socket.run(app=app, debug=True, host="127.0.0.1")
