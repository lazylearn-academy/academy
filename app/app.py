import locale
from flask import Flask, render_template, send_from_directory, render_template, make_response, redirect, url_for, request, abort
from wtforms import EmailField, PasswordField, SubmitField, StringField, DateField, TextAreaField, SelectField, FieldList, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError, regexp
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_migrate import Migrate
import os
from jinja2 import StrictUndefined
from config import SECRET_KEY, SHOULD_CREATE_DB, ENV, DEV_HOST, PROD_HOST
import random
from config import DB_HOST, DB_USER, DB_PWD, DB_NAME, DB_PORT
from post import send_email_verification
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import base64

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True} 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.jinja_env.undefined = StrictUndefined


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class CreateForumThemeForm(FlaskForm):
    name = StringField(validators=[
        InputRequired(),
        Length(min=1, max=100)
    ], render_kw={"placeholder": "Название"})

    description = TextAreaField(validators=[
        InputRequired(),
        Length(min=1, max=1000)
    ], render_kw={"placeholder": "Описание"})

    submit = SubmitField("Создать")


class RegisterForm(FlaskForm):
    email = EmailField(validators=[
        InputRequired(),
        Length(min=5, max=120)
    ], render_kw={"placeholder": "Email"})

    name = StringField(validators=[
        InputRequired(),
        Length(min=1, max=30)
    ], render_kw={"placeholder": "Имя"})

    surname = StringField(validators=[
        InputRequired(),
        Length(min=1, max=30)
    ], render_kw={"placeholder": "Фамилия"})

    password = PasswordField(validators=[
        InputRequired(),
        Length(min=8, max=30)
    ], render_kw={"placeholder": "Пароль"})

    password_repeat = PasswordField(validators=[
        InputRequired(),
        Length(min=8, max=30)
    ], render_kw={"placeholder": "Повторите пароль"})

    submit = SubmitField("Продолжить")

    @staticmethod
    def validate_username(self, email):
        existing_user_email = User.query.filter_by(
            username=email.data).first()

        if existing_user_email:
            raise ValidationError(
                'Такая почта уже существует. Пожалуйста, проверьте правильность или войдите в систему.')
        


class ChangePasswordForm(FlaskForm):
    password = PasswordField(validators=[
        InputRequired(),
        Length(min=8, max=30)
    ], render_kw={"placeholder": "Пароль"})

    password_repeat = PasswordField(validators=[
        InputRequired(),
        Length(min=8, max=30)
    ], render_kw={"placeholder": "Повторите пароль"})

    submit = SubmitField("Продолжить")

        
class RecoverForm(FlaskForm):
    email = EmailField(validators=[
        InputRequired(),
        Length(min=5, max=120)
    ], render_kw={"placeholder": "Email"})

    submit = SubmitField("Продолжить")


class ConfirmationForm(FlaskForm):
    verification_code = StringField(validators=[
        InputRequired()
    ], render_kw={"placeholder": "Код подтверждения"})

    submit = SubmitField("Зарегистрироваться")

    @staticmethod
    def validate_username(self, email):
        existing_user_email = User.query.filter_by(
            username=email.data).first()

        if existing_user_email:
            raise ValidationError(
                'Такая почта уже существует. Пожалуйста, проверьте правильность или войдите в систему.')


class RecoverConfirmationForm(FlaskForm):
    verification_code = StringField(validators=[
        InputRequired()
    ], render_kw={"placeholder": "Код подтверждения"})

    submit = SubmitField("Зарегистрироваться")
        


class LoginForm(FlaskForm):
    email = EmailField(validators=[
        InputRequired(),
        Length(min=5, max=120)
    ], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
        InputRequired(),
        Length(min=8, max=30)
    ], render_kw={"placeholder": "Пароль"})

    submit = SubmitField("Войти в систему")
    

# 1
user_course = db.Table('user_course',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

# 2
user_coding_task = db.Table('user_coding_task',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('coding_task_id', db.Integer, db.ForeignKey('coding_task.id'), primary_key=True),
)

# 3
video_theme = db.Table('video_theme',
    db.Column('video_id', db.Integer, db.ForeignKey('video.id'), primary_key=True),
    db.Column('theme_id', db.Integer, db.ForeignKey('theme.id'), primary_key=True),
)

# 4
user_theme = db.Table('user_theme',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('theme_id', db.Integer, db.ForeignKey('theme.id'), primary_key=True),
)

# 5
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_email_approved = db.Column(db.Boolean, nullable=False, default=False)
    verification_code = db.Column(db.String(4), nullable=False, unique=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    name = db.Column(db.String(30), nullable=False, unique=False)
    surname = db.Column(db.String(30), nullable=False, unique=False)
    courses = db.relationship('Course', secondary=user_course, lazy='subquery', backref=db.backref('users', lazy=True))
    completed_coding_tasks = db.relationship('CodingTask', secondary=user_coding_task, lazy='subquery', backref=db.backref('users', lazy=True))
    viewed_themes = db.relationship('Theme', secondary=user_theme, lazy='subquery', backref=db.backref('users', lazy=True))
    forum_themes_created = db.relationship('ForumTheme', backref='user', lazy=True)
    forum_themes_created_messages = db.relationship('ForumThemeMessage', backref='user', lazy=True)
    certificates = db.relationship('Certificate', backref='user', lazy=True)
    avatars = db.relationship('Avatar', backref='user', lazy=True)
    billing_accounts = db.relationship('BillingAccount', backref='user', lazy=True)

# 6
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    short_description = db.Column(db.String(300), nullable=True)
    long_description = db.Column(db.String(1500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    blocks = db.relationship('Block', backref='course', lazy=True)
    is_ready = db.Column(db.Boolean, nullable=False, default=False)

# 7
class Block(db.Model):
    __tablename__ = 'block'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_in_course = db.Column(db.Integer, nullable=False, unique=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    themes = db.relationship('Theme', backref='block', lazy=True)

# 8
class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_in_block = db.Column(db.Integer, nullable=False, unique=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    article_text = db.Column(db.String, nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('block.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    coding_tasks = db.relationship('CodingTask', backref='theme', lazy=True)
    theme_file = db.relationship('ThemeFile', backref='theme', lazy=True)

# 9
class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    abstract = db.Column(db.String(500), nullable=True)
    article_text = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

# 10
class CodingTask(db.Model):
    __tablename__ = 'coding_task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_text = db.Column(db.String(1200), nullable=False)
    answer = db.Column(db.String(1200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

# 11
class CodingTaskSubmission(db.Model):
    __tablename__ = 'coding_task_submission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(3000), nullable=False)
    code_result = db.Column(db.String(3000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    task_id = db.Column(db.Integer, db.ForeignKey('coding_task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passed = db.Column(db.Boolean, nullable=True)


# 12
class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

# 13
class Advantages(db.Model):
    __tablename__ = 'advantages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

# 14
class Certificate(db.Model):
    __tablename__ = 'certificate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

# 15
class ForumTheme(db.Model):
    __tablename__ = 'forum_theme'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    messages = db.relationship('ForumThemeMessage', backref='forum_theme', lazy=True)


# 16
class ForumThemeMessage(db.Model):
    __tablename__ = 'forum_theme_message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('forum_theme.id'), nullable=False)
    text = db.Column(db.String(120), nullable=False, unique=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())


# 17
class ThemeFile(db.Model):
    __tablename__ = 'theme_file'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(1200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

# 18
class Avatar(db.Model):
    __tablename__ = 'avatar'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(1200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
# 19
user_viewed_forum_theme = db.Table('user_viewed_forum_theme',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('forum_theme_id', db.Integer, db.ForeignKey('forum_theme.id'), primary_key=True),
)

# 20 
class BillingAccount(db.Model):
    __tablename__ = 'billing_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(100), nullable=False)
    card_date = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("lk"))
            
        return render_template('login.html', form=form, error="Неверный логин или пароль!", 
            link_styles=["", "color:white;", "", "", "", "", "", ""])

    return render_template('login.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()

        if user is not None:
            return render_template('register.html', form=form, error="Такой пользователь уже существует!", link_styles=[
                "", "color:white;", "", "", "", "", "", ""
            ])
        
        if form.password.data != form.password_repeat.data:
                return render_template('register.html', form=form, error="Пароли не совпадают!", link_styles=[
                    "", "color:white;", "", "", "", "", "", ""
                ])

        hashed_password = bcrypt.generate_password_hash(form.password.data.encode("utf-8"))
        hashed_password = hashed_password.decode("utf-8")
        code = random.randint(1000, 9999)
        new_user = User(login=form.email.data, 
                        password=hashed_password, 
                        name=form.name.data,
                        surname=form.surname.data,
                        verification_code=code)

        send_email_verification(new_user.login, code)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('confirm', user_login=new_user.login))

    return render_template('register.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])


@app.route('/recover', methods=['GET', 'POST'])
def recover():
    form = RecoverForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()
        
        if user is None:
                return render_template('recover.html', form=form, error="Такого пользователя не существует!", link_styles=[
                    "", "color:white;", "", "", "", "", "", ""
                ])
        
        code = random.randint(1000, 9999)
        user.verification_code = code
        db.session.commit()

        send_email_verification(user.login, code)

        return redirect(url_for('recover_confirm', user_login=user.login))

    return render_template('recover.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    user_login = request.args.get("user_login")


    if form.validate_on_submit():
        user = User.query.filter_by(login=user_login).first()
        if user is None:
                return render_template('change_password.html', form=form, error="Такого пользователя не существует!", link_styles=[
                    "", "color:white;", "", "", "", "", "", ""
                ])
        if form.password.data != form.password_repeat.data:
                return render_template('change_password.html', form=form, error="Пароли не совпадают!", link_styles=[
                    "", "color:white;", "", "", "", "", "", ""
                ])
        hashed_password = bcrypt.generate_password_hash(form.password.data.encode("utf-8"))
        hashed_password = hashed_password.decode("utf-8")
        user.password = hashed_password
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('change_password.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():

    user_login = request.args.get("user_login")
    user = User.query.filter_by(login=user_login).first()
    code = user.verification_code

    form = ConfirmationForm()

    if form.validate_on_submit():

        if form.verification_code.data == code:
            user.is_email_approved = True
            db.session.commit()

            return redirect(url_for('login'))
        else:
            return render_template("confirm.html", form=form, error="Неверный код!", link_styles=[
                "", "color:white;", "", "", "", "", "", ""
        ])


    return render_template("confirm.html", form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])



@app.route('/recover_confirm', methods=['GET', 'POST'])
def recover_confirm():
    user_login = request.args.get("user_login")
    user = User.query.filter_by(login=user_login).first()
    code = user.verification_code

    form = RecoverConfirmationForm()

    if form.validate_on_submit():

        if form.verification_code.data == code:
            user.is_email_approved = True
            db.session.commit()

            return redirect(url_for('change_password', user_login=user_login))
        else:
            return render_template("recover_confirm.html", form=form, error="Неверный код!", link_styles=[
                "", "color:white;", "", "", "", "", "", ""
        ])


    return render_template("recover_confirm.html", form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])


@app.route('/')
def home():
    advantages = Advantages.query.all()
    return render_template("index.html", link_styles=[
        "color:white;", "", "", "", "", "", "", ""
    ], advantages=advantages)


@app.route('/lk')
@login_required
def lk():
    courses_stats = []
    for course in  current_user.courses:
        course_themes = Theme.query.filter(Theme.block_id.in_(Block.query.filter_by(course_id=course.id).with_entities(Block.id).all())).all()
        completed_themes = []
        for theme in course_themes:
            if len(theme.coding_tasks) == 0:
                if theme in current_user.viewed_themes:
                    completed_themes.append(theme)
                continue
            completed = True
            for task in theme.coding_tasks:
                if task not in current_user.completed_coding_tasks:
                    completed = False
                    break
            if completed:
                completed_themes.append(theme)
        courses_stats.append((course, len(completed_themes), len(course_themes)))
            
    return render_template("lk.html", user=current_user, courses_stats=courses_stats, link_styles=[
        "", "color:white;", "", "", "", "", "", ""
    ])


@app.route('/about')
def about():
    return render_template("about.html", link_styles=[
        "", "", "color:white;", "", "", "", "", ""
    ])


@app.route('/blog')
def blog():
    blogposts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("blog.html", blogposts=blogposts, link_styles=[
        "", "", "", "", "color:white;", "", "", ""
    ])


@app.route('/contacts')
def contacts():
    return render_template("contacts.html", link_styles=[
        "", "", "", "", "", "color:white;", "", ""
    ])


@app.route('/courses')
def courses():
    course_items = Course.query.order_by(Course.created_at).all()
    return render_template("courses.html", course_items=course_items, link_styles=[
        "", "", "", "color:white;", "", "", "", ""
    ])


@app.route('/helpproject')
def helpproject():
    return render_template("helpproject.html", link_styles=[
        "", "", "", "", "", "",  "color:white;", ""
    ])


@app.route('/forum')
def forum():
    themes = ForumTheme.query.order_by(ForumTheme.created_at.desc()).all()
    return render_template("forum.html", link_styles=[
        "", "", "", "", "", "",  "", "color:white;"
    ], themes=themes)


@app.route('/create_forum_theme', methods=['GET', 'POST'])
def create_forum_theme():
    form = CreateForumThemeForm()
    if form.validate_on_submit():
        forum_theme = ForumTheme(
            name = form.name.data,
            description = form.description.data,
            creator_id=current_user.id
        )
        db.session.add(forum_theme)
        db.session.commit()
        return redirect(url_for("forum"))
            
    return render_template('create_forum_theme.html', form=form, link_styles=[
        "", "", "", "", "", "", "", "", "color:white;"
    ])



@app.route('/courses/<course_id>')
@login_required
def get_course(course_id):
    try:
        course_item = Course.query.filter_by(id = course_id).first()
        course_themes = Theme.query.filter(Theme.block_id.in_(Block.query.filter_by(course_id=course_id).with_entities(Block.id).all())).all()
        completed_themes = []
        for theme in course_themes:
            if len(theme.coding_tasks) == 0:
                if theme in current_user.viewed_themes:
                    completed_themes.append(theme)
                continue
            completed = True
            for task in theme.coding_tasks:
                if task not in current_user.completed_coding_tasks:
                    completed = False
                    break

            if completed:
                completed_themes.append(theme)

        can_get_cert = len(completed_themes) == len(course_themes)

        return render_template("course.html", course_item=course_item, completed_themes=completed_themes,
                               can_get_cert=can_get_cert,
                               user=current_user, link_styles=[
            "", "", "", "color:white;", "", "", ""
        ])
    except:
        abort(404)


@app.route('/themes/<theme_id>')
@login_required
def get_theme(theme_id):
    try:
        theme_item = Theme.query.filter_by(id = theme_id).first()
        theme_block = Block.query.filter_by(id = theme_item.block_id).first()
        block_order_in_course = theme_block.order_in_course
        theme_course = Course.query.filter_by(id = theme_block.course_id).first()
        course_name = theme_course.name
        course_id = theme_course.id
        ordered_blocks = Block.query.filter_by(course_id=course_id).order_by(Block.order_in_course).all()
        ordered_themes = []
        for block in ordered_blocks:
            ordered_themes.extend([t.id for t in Theme.query.filter_by(block_id=block.id).order_by(Theme.order_in_block).all()])

        theme_id = int(theme_id)
        next_theme_id = None
        previous_theme_id = None
        if theme_id == ordered_themes[0]:
            next_theme_id = ordered_themes[1]
        elif theme_id == ordered_themes[-1]:
            previous_theme_id = ordered_themes[-2]
        else:
            theme_idx_in_order = ordered_themes.index(theme_id)
            next_theme_id = ordered_themes[theme_idx_in_order + 1]
            previous_theme_id = ordered_themes[theme_idx_in_order - 1]

        current_user.viewed_themes.append(theme_item)
        db.session.commit()

        return render_template("theme.html", user=current_user, theme_item=theme_item, block_order_in_course=block_order_in_course, 
                               course_name=course_name, course_id=course_id, previous_theme_id=previous_theme_id, next_theme_id=next_theme_id,
                               link_styles=[
            "", "", "", "color:white;", "", "", ""
        ])
    except:
        abort(404)


@app.route('/add_course', methods=["POST"])
def add_course():
    try:
        user_id = request.args.get("user_id")
        course_id = request.args.get("course_id")
        user = User.query.filter_by(id=user_id).first()
        course = Course.query.filter_by(id=course_id).first()
        user.courses.append(course)
        db.session.commit()

        return redirect(url_for('get_course', course_id=course_id))
    except:
        abort(404)


@app.route('/blog/posts/<blogpost_id>')
def get_blogpost(blogpost_id):
    try:
        blogpost = BlogPost.query.filter_by(id=blogpost_id).first()
        return render_template("blogpost.html", blogpost=blogpost, link_styles=[
            "", "", "", "", "color:white;", "", ""
        ])
    except:
        abort(404)


@app.route('/sandbox', methods=["GET", "POST"])
@login_required
def sandbox():
    task_id = request.args.get("task_id")
    task_item = CodingTask.query.filter_by(id=task_id).first()
    submission = CodingTaskSubmission.query.filter_by(task_id=task_id, user_id=current_user.id).order_by(CodingTaskSubmission.created_at.desc()).first()
    if request.method == "GET":
        return render_template("sandbox.html", task_item=task_item, submission=submission, code_result=None, user=current_user, link_styles=[
                "", "", "", "color:white;", "", "", ""
            ])
    elif request.method == "POST":
        code = request.form.get("code")
        output = ""
        error = ""
        try:
            result = subprocess.run(
                [sys.executable, '-c', code],
                capture_output=True,
                text=True,
                timeout=2  
            )
            output = result.stdout
            error = result.stderr
        except Exception as e:
           error = str(e)
        
        output = output.strip()

        passed = False
        if len(error) > 0:
            code_result = f"Код работает с ошбикой: {error}"
        elif output != task_item.answer:
            code_result = f"Неверный ответ: {output}"
        elif output == task_item.answer:
            user = current_user
            code_result = "Код работает верно"
            passed = True
            if task_item not in user.completed_coding_tasks:
                user.completed_coding_tasks.append(task_item)
                db.session.commit()

        submission = CodingTaskSubmission(
            code = code,
            code_result = code_result,
            task_id = task_id,
            user_id = current_user.id,
            passed = passed
        )

        db.session.add(submission)
        db.session.commit()

        return render_template("sandbox.html", task_item=task_item, submission=submission, code_result=code_result, user=current_user, link_styles=[
                "", "", "", "color:white;", "", "", ""
            ])


@app.get("/certificate")
@login_required
def get_certificate():
    course_id = request.args.get("course_id")
    course_item = Course.query.filter_by(id = course_id).first()
    course_themes = Theme.query.filter(Theme.block_id.in_(Block.query.filter_by(course_id=course_id).with_entities(Block.id).all())).all()
    completed_themes = []
    for theme in course_themes:
        if len(theme.coding_tasks) == 0:
            if theme in current_user.viewed_themes:
                completed_themes.append(theme)
            continue
        completed = True
        for task in theme.coding_tasks:
            if task not in current_user.completed_coding_tasks:
                completed = False
                break
        if completed:
            completed_themes.append(theme)

    can_get_cert = len(completed_themes) == len(course_themes)
    cert = None
    if can_get_cert:
        img = Image.open("static/cert-template.jpg")
        img = img.resize((900, 500))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        certificate_text = u"Сертификат о Прохождении\n\nНастоящий сертификат подтверждает, что {} {}\nуспешно прошел курс {}.\n\nДата выдачи: {}\n\nПоздравляем с прохождением! Академия LazyLearn.".format(current_user.name, current_user.surname, course_item.name, datetime.date.today().strftime('%B %d, %Y'))
        d.text((100, 100), certificate_text, font=font, fill=(0, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        cert = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template("certificate.html", course=course_item, user=current_user, cert=cert, link_styles=[
        "", "", "", "color:white;", "", "", ""
    ])


    


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/sitemap.xml', methods=["GET"])
def sitemap():
    themes = [t.id for t in Theme.query.all()]
    courses = [c.id for c in Course.query.all()]

    articles = list(map(lambda x: os.path.splitext(x)[0], os.listdir("templates/blog")))
    sm_xml = render_template("sitemap.xml", themes=themes, articles=articles, courses=courses)
    response = make_response(sm_xml)
    response.headers["Content-Type"] = "application/rss+xml"
    response.mimetype = "application/xml"
    return response


@app.route('/robots.txt', methods=["GET"])
def robots():
    rb_txt = render_template("robots.txt")
    response = make_response(rb_txt)
    response.headers["Content-Type"] = "text/plain; charset=utf-8;"
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    if SHOULD_CREATE_DB == "YES":
        with app.app_context():
            db.create_all()
    app_host = PROD_HOST if ENV == "PROD" else DEV_HOST
    print(app_host)
    app.run(host=app_host)
