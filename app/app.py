from flask import Flask, render_template, send_from_directory, render_template, make_response, redirect, url_for, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import EmailField, PasswordField, SubmitField, StringField, DateField, TextAreaField, SelectField, FieldList, IntegerField
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms.validators import InputRequired, Length, ValidationError, regexp
import os
from jinja2 import StrictUndefined
from config import SECRET_KEY
import random
from config import DB_HOST, DB_USER, DB_PWD, DB_NAME, DB_PORT
from post import send_email_verification


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


user_course = db.Table('user_course',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

user_theme = db.Table('user_theme',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('theme_id', db.Integer, db.ForeignKey('theme.id'), primary_key=True),
)


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
    completed_themes = db.relationship('Theme', secondary=user_theme, lazy='subquery', backref=db.backref('users', lazy=True))

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    short_description = db.Column(db.String(300), nullable=True)
    long_description = db.Column(db.String(1500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    blocks = db.relationship('Block', backref='course', lazy=True)
    is_ready = db.Column(db.Boolean, nullable=False, default=False)


class Block(db.Model):
    __tablename__ = 'block'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_in_course = db.Column(db.Integer, nullable=False, unique=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    themes = db.relationship('Theme', backref='block', lazy=True)



class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_in_block = db.Column(db.Integer, nullable=False, unique=False)
    name = db.Column(db.String(120), nullable=False, unique=True)
    article_text = db.Column(db.String, nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('block.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())


class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    abstract = db.Column(db.String(500), nullable=True)
    article_text = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())


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
            link_styles=["", "color:white;", "", "", "", "", ""])

    return render_template('login.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", ""
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
                "", "color:white;", "", "", "", "", ""
            ])
        
        if form.password.data != form.password_repeat.data:
                return render_template('register.html', form=form, error="Пароли не совпадают!", link_styles=[
                    "", "color:white;", "", "", "", "", ""
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
        "", "color:white;", "", "", "", "", ""
    ])


@app.route('/recover', methods=['GET', 'POST'])
def recover():
    form = RecoverForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()
        
        if user is None:
                return render_template('recover.html', form=form, error="Такого пользователя не существует!", link_styles=[
                    "", "color:white;", "", "", "", "", ""
                ])
        
        code = random.randint(1000, 9999)
        user.verification_code = code
        db.session.commit()

        send_email_verification(user.login, code)

        return redirect(url_for('recover_confirm', user_login=user.login))

    return render_template('recover.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", ""
    ])


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    user_login = request.args.get("user_login")


    if form.validate_on_submit():
        user = User.query.filter_by(login=user_login).first()
        if user is None:
                return render_template('change_password.html', form=form, error="Такого пользователя не существует!", link_styles=[
                    "", "color:white;", "", "", "", "", ""
                ])
        if form.password.data != form.password_repeat.data:
                return render_template('change_password.html', form=form, error="Пароли не совпадают!", link_styles=[
                    "", "color:white;", "", "", "", "", ""
                ])
        hashed_password = bcrypt.generate_password_hash(form.password.data.encode("utf-8"))
        hashed_password = hashed_password.decode("utf-8")
        user.password = hashed_password
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('change_password.html', form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", ""
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
                "", "color:white;", "", "", "", "", ""
        ])


    return render_template("confirm.html", form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", ""
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
                "", "color:white;", "", "", "", "", ""
        ])


    return render_template("recover_confirm.html", form=form, error="", link_styles=[
        "", "color:white;", "", "", "", "", ""
    ])


@app.route('/')
def home():
    return render_template("index.html", link_styles=[
        "color:white;", "", "", "", "", "", ""
    ])


@app.route('/lk')
@login_required
def lk():
    return render_template("lk.html", user=current_user, link_styles=[
        "", "color:white;", "", "", "", "", ""
    ])


@app.route('/about')
def about():
    return render_template("about.html", link_styles=[
        "", "", "color:white;", "", "", "", ""
    ])


@app.route('/blog')
def blog():
    blogposts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("blog.html", blogposts=blogposts, link_styles=[
        "", "", "", "", "color:white;", "", ""
    ])


@app.route('/contacts')
def contacts():
    return render_template("contacts.html", link_styles=[
        "", "", "", "", "", "color:white;", ""
    ])


@app.route('/courses')
def courses():
    course_items = Course.query.order_by(Course.created_at).all()
    return render_template("courses.html", course_items=course_items, link_styles=[
        "", "", "", "color:white;", "", "", ""
    ])


@app.route('/helpproject')
def helpproject():
    return render_template("helpproject.html", link_styles=[
        "", "", "", "", "", "",  "color:white;"
    ])


@app.route('/courses/<course_id>')
@login_required
def get_course(course_id):
    try:
        course_item = Course.query.filter_by(id = course_id).first()
        return render_template("course.html", course_item=course_item, user=current_user, link_styles=[
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
            ordered_themes.extend([t.id for t in block.themes])

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

        return render_template("theme.html", theme_item=theme_item, block_order_in_course=block_order_in_course, 
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
        return render_template(f"blogpost.html",blogpost=blogpost, link_styles=[
            "", "", "", "", "color:white;", "", ""
        ])
    except:
        abort(404)


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
    app.run("0.0.0.0")
