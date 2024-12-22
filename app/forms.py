from wtforms import EmailField, PasswordField, SubmitField, StringField, DateField, TextAreaField, SelectField, FieldList, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError, regexp


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
    