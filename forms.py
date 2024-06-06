from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import InputRequired, Length, EqualTo, Email
from config import ALLOWED_EXTENSIONS

# All forms for html


class RegistrationForm(FlaskForm):
    username = StringField("Введите имя пользователя", validators=[
        InputRequired(message="Пожалуйта, введите имя пользователя"),
        Length(min=2, max=25, message="Длина имени должна быть от 2 до 25 символов")
    ])
    password = PasswordField("Введите пароль", validators=[
        InputRequired(message="Пожалуйста, введите пароль"),
        Length(min=6, max=42, message="Длина пароля должна быть от 6 до 42 символов"),
        EqualTo("confirm", message="Пароли должны совпадать")
    ])
    confirm = PasswordField("Повторите пароль", validators=[
        InputRequired(message="Пожалуйста, введите пароль повторно")
    ])
    submit = SubmitField("Зарегистрироваться")


class AuthorizationForm(FlaskForm):
    username = StringField("Введите имя пользователя", validators=[
        InputRequired(message="Пожалуйта, введите имя пользователя"),
        Length(min=2, max=25, message="Длина имени должна быть от 2 до 25 символов")
    ])
    password = PasswordField("Введите пароль", validators=[
        InputRequired(message="Пожалуйста, введите пароль"),
        Length(min=6, max=42, message="Длина пароля должна быть от 6 до 42 символов")
    ])
    submit = SubmitField("Войти")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Текущий пароль", validators=[
        InputRequired(message="Пожалуйста, введите текущий пароль")
    ])
    new_password = PasswordField("Новый пароль", validators=[
        InputRequired(message="Пожалуйста, введите новый пароль"),
        Length(min=6, max=42, message="Длина пароля должна быть от 6 до 42 символов")
    ])
    submit = SubmitField("Изменить пароль")


class ChangeEmailForm(FlaskForm):
    new_email = StringField("Новый Email", validators=[
        InputRequired(message="Пожалуйста, введите новый Email"),
        Email(message="Пожалуйста, введите почту")
    ])
    submit = SubmitField("Изменить Email")


class ChangeUsernameForm(FlaskForm):
    new_username = StringField("Новый никнейм", validators=[
        InputRequired(message="Пожалуйста, введите новый никнейм"),
        Length(min=2, max=25, message="Длина имени должна быть от 2 до 25 символов")
    ])
    submit = SubmitField("Поменять никнейм")


class ResetPasswordForm(FlaskForm):
    email = StringField("Email", validators=[
        InputRequired(message="Пожалуйста, введите почту"),
        Email(message="Пожалуйста, введите почту")])
    submit = SubmitField("Сбросить пароль")


class UploadPhotoForm(FlaskForm):
    photo = FileField("Выберите фотографию", validators=[
        FileAllowed(["jpg", "jpeg", "png"], message="Пожалуйста, выберите другое расширнение фотографии")
    ])
    submit = SubmitField("Загрузить")


class CreateCaseForm(FlaskForm):
    name = StringField("Название кейса", validators=[
        InputRequired()
    ])
    image = FileField("Изображение кейса", validators=[
        FileRequired(message="Необходимо выбрать файл"),
        FileAllowed(ALLOWED_EXTENSIONS,
                    message="Допустимы только файлы с расширением PNG, JPG, JPEG, GIF")
    ])
    submit = SubmitField("Создать кейс")


class EditCaseForm(FlaskForm):
    name = StringField("Название кейса", validators=[
        InputRequired()
    ])
    image = FileField("Фотография кейса", validators=[
        FileAllowed(["jpg", "jpeg", "png"], message="Пожалуйста, выберите другое расширнение фотографии")
    ])
    submit = SubmitField("Сохранить изменения")


class CreateCommentForm(FlaskForm):
    text = StringField("Текст комментария", validators=[
        InputRequired()
    ])
    submit = SubmitField("Опубликовать комментарий")


class EditCommentForm(FlaskForm):
    text = StringField("Текст комментария", validators=[
        InputRequired()
    ])
    submit = SubmitField("Сохранить изменения")
