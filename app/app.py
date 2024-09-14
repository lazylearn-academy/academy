from flask import Flask, render_template, send_from_directory, render_template, make_response, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import EmailField, PasswordField, SubmitField, StringField, DateField, TextAreaField, SelectField, FieldList, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError, regexp
import os
from publisher import send_email_verification
from jinja2 import StrictUndefined
from config import DB_NAME, SECRET_KEY
import random
from config import DB_HOST, DB_USER, DB_PWD, DB_NAME, DB_PORT


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.jinja_env.undefined = StrictUndefined

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

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

    submit = SubmitField("Продолжить")

    @staticmethod
    def validate_username(self, email):
        existing_user_email = User.query.filter_by(
            username=email.data).first()

        if existing_user_email:
            raise ValidationError(
                'Такая почта уже существует. Пожалуйста, проверьте правильность или войдите в систему.')
        

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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_email_approved = db.Column(db.Boolean, nullable=False, default=False)
    verification_code = db.Column(db.String(4), nullable=False, unique=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    name = db.Column(db.String(30), nullable=False, unique=False)
    surname = db.Column(db.String(30), nullable=False, unique=False)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('lk'))
            
        return render_template('login.html', form=form, error="Неверный логин или пароль!", link_styles=[
                     "", "color:white;", "", "", "", "", ""
        ])

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
        user_exists = db.session.query(User.id).filter_by(login=form.email.data).first() is not None
        if user_exists:
                return render_template('register.html', form=form, error="Такой пользователь уже существует!", link_styles=[
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

        send_email_verification({"email": new_user.login, "code": code})

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('confirm', user_login=new_user.login))

    return render_template('register.html', form=form, error="", link_styles=[
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



@app.route('/')
@app.route('/home')
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
    return render_template("blog.html", link_styles=[
        "", "", "", "", "color:white;", "", ""
    ])


@app.route('/contacts')
def contacts():
    return render_template("contacts.html", link_styles=[
        "", "", "", "", "", "color:white;", ""
    ])


@app.route('/courses')
def courses():
    return render_template("courses.html", link_styles=[
        "", "", "", "color:white;", "", "", ""
    ])


@app.route('/helpproject')
def helpproject():
    return render_template("helpproject.html", link_styles=[
        "", "", "", "", "", "",  "color:white;"
    ])


@app.route('/courses/<course_name>')
def get_course(course_name):
    return render_template(f"courses/{course_name}/course_{course_name}.html", link_styles=[
        "", "", "", "color:white;", "", "", ""
    ])



@app.route('/courses/<course_name>/themes/<theme_name>')
def get_theme(course_name, theme_name):
    return render_template(f"courses/{course_name}/{theme_name}.html", link_styles=[
        "", "", "", "color:white;", "", "", ""
    ])


@app.route('/blog/articles/<article_name>')
def get_article(article_name):
    return render_template(f"blog/{article_name}.html", link_styles=[
        "", "", "", "", "color:white;", "", ""
    ])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/sitemap.xml', methods=["GET"])
def sitemap():
    course_folder = 'templates/courses'

    themes = []
    for root, dirs, files in os.walk(course_folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            for file in os.listdir(dir_path):
                file_name, file_ext = os.path.splitext(file)
                themes.append(f"courses/{dir}/themes/{file_name}")

    articles = list(map(lambda x: os.path.splitext(x)[0], os.listdir("templates/blog")))
    sm_xml = render_template("sitemap.xml", themes=themes, articles=articles)
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
    with app.app_context():
        db.create_all()
    app.run("0.0.0.0")
