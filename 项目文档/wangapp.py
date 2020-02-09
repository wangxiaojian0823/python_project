#encoding: utf-8
from flask import Flask,render_template,request,redirect,url_for,session
import config
from models import User,Question,Answer
from exts import db
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)



@app.route('/')
def index():
    context = {
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

#登陆
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        if User.query.filter(User.telephone == telephone,User.password == password).first():
            session['user_id'] = User.query.filter(User.telephone == telephone,User.password == password).first().id
            #31天内不需要登陆
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号码或密码错误，请重新输入'

#注册
@app.route('/regist',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if User.query.filter(User.telephone == telephone).first():
            return u'该手机号码已被注册'
        else:
            if password1 != password2:
                return u'两次密码不相等，请重新输入'
            else:
                db.session.add(User(telephone=telephone,username=username,password=password1))
                db.session.commit()
                return redirect(url_for('login'))
#注销
@app.route('/logout')
def logout():
    #session.pop('user_id')
    session.clear()
    return redirect(url_for('login'))

#发布问答
@app.route('/question',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

#问答详情页面
@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question=question_model)

#添加评论
@app.route('/add_answer',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    user_id = session.get('user_id')
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))





@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user':user}
        else:
            pass
    else:
        return {}

if __name__ == '__main__':
    app.run()
