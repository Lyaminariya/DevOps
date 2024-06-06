from flask import Flask, render_template, url_for, redirect, request, session, abort, jsonify, Response
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from sqlalchemy import func
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from forms import RegistrationForm, AuthorizationForm, ChangePasswordForm, ChangeEmailForm, \
    ChangeUsernameForm, ResetPasswordForm, UploadPhotoForm, CreateCaseForm, EditCaseForm, CreateCommentForm, \
    EditCommentForm
from db_models import db, User, Profile, Case, Item, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit

import os
import random
import string
import json

# Connecting .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = Flask(__name__)

socketio = SocketIO(app)

app.config.from_object("config")

# Some configs

mail = Mail(app)

db.init_app(app)

oauth = OAuth(app)

k_user = "user"

# Google authorization
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile"}
)

# GitHub authorization
oauth.register(
    name="github",
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)


@app.route("/")
def homepage():
    """Главная страница с кейсами"""
    cases = Case.query.all()
    if session.get(k_user):
        username = session[k_user].get("name")
        user = User.query.filter_by(name=username).first()
        if user:
            return render_template("homepage.html", cases=cases, user=user)

    return render_template("homepage.html", cases=cases)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """Страница регистрации"""
    error_msg = ""
    if session.get(k_user):
        username = session[k_user]["name"]
        user = User.query.filter(User.name == username).first()
        return redirect(url_for("profile", id=user.profile.id))

    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        if not User.query.filter(User.name == form.username.data).first():
            hash_password = generate_password_hash(password=form.password.data)
            user = User(name=form.username.data, password=hash_password)
            db.session.add(user)
            db.session.commit()
            profile = Profile(email=None, user_id=user.id, avatar_href="https://miro.medium.com/max"
                                                                       "/2400/1"
                                                                       "*BG6R93SDonekNLrJrkiF4g.png")
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for("login"))

        error_msg = "Пользователь с таким никнеймом уже существует"
    return render_template("registration.html", form=form, error_msg=error_msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница логина + создание сессии"""
    error_msg = ""
    if session.get(k_user):
        username = session[k_user]["name"]
        user = User.query.filter_by(name=username).first()
        return redirect(url_for("profile", id=user.profile.id))

    form = AuthorizationForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter(User.name == form.username.data).first()
        if not user:
            error_msg = "Такого пользователя не существует"
        elif check_password_hash(user.password, form.password.data):
            userinfo = {"name": user.name}
            session[k_user] = userinfo
            return redirect(url_for("profile", id=user.profile.id))
        else:
            error_msg = "Неверный пароль"
    return render_template("login.html", form=form, error_msg=error_msg)


@app.route("/login/<name>")
def login_oauth(name):
    """Скрипт для логина через oAuth"""
    client = oauth.create_client(name)
    if not client:
        abort(404)

    redirect_uri = url_for("authorize", name=name, _external=True)
    return client.authorize_redirect(redirect_uri)


@app.route("/authorize/<name>")
def authorize(name):
    """Авторизация для oAuth юзеров через гугл и гитхаб + создание сессии"""
    client = oauth.create_client(name)
    if not client:
        abort(404)

    token = client.authorize_access_token()
    if name == "google":
        userinfo = token["userinfo"]
        session[k_user] = userinfo
        session[k_user]["oauth_user"] = True

        user = User.query.filter_by(name=userinfo["name"]).first()
        if not user:
            user = User(name=userinfo["name"])
            db.session.add(user)

        profile = Profile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
        if not profile.email:
            profile.email = userinfo.get("email")
        if not profile.avatar_href:
            profile.avatar_href = userinfo.get("picture")

    elif name == "github":
        resp = client.get(k_user, token=token)
        userinfo = resp.json()
        session[k_user] = userinfo
        session[k_user]["oauth_user"] = True

        user = User.query.filter_by(name=userinfo["name"]).first()
        if not user:
            user = User(name=userinfo["name"])
            db.session.add(user)

        profile = Profile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
        if not profile.email:
            profile.email = userinfo.get("email")
        if not profile.avatar_href:
            profile.avatar_href = userinfo.get("avatar_url")

    db.session.commit()
    return redirect("/")


@app.route("/logout")
def logout():
    """Страница для удаления сессии"""
    session.pop(k_user, None)
    return redirect("/")


@app.route("/profile/<id>")
def profile(id):
    """Страница профиля"""
    if session.get(k_user):
        username = session[k_user].get("name")
        user = User.query.filter(User.name == username).first()
        if user:
            profile = Profile.query.get(id)
            if profile and profile.user_id == user.id:
                if user.profile.avatar_href.startswith("https://"):
                    return render_template("profile.html", id=user.profile.id, profile=profile, user=user,
                                           photo_filename=None)
                else:
                    return render_template("profile.html", id=user.profile.id, profile=profile, user=user,
                                           photo_filename=user.profile.avatar_href)
            elif profile:
                return render_template("other_profile.html", profile=profile)
        else:
            return redirect(url_for("homepage"))

    return redirect(url_for("login"))


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """Смена пароля с шифрованием"""
    error_msg = ""
    if not session.get(k_user):
        return redirect("login")

    username = session[k_user]["name"]
    user = User.query.filter(User.name == username).first()
    if not user.password:
        return redirect(url_for("profile", id=user.profile.id))

    form = ChangePasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if check_password_hash(user.password, form.current_password.data):
            hash_password = generate_password_hash(password=form.new_password.data)
            user.password = hash_password
            db.session.commit()
            return redirect(url_for("profile", id=user.profile.id))

        else:
            error_msg = "Текущий пароль неверен"

    return render_template("change_password.html", form=form, error_msg=error_msg)


@app.route("/change_email", methods=["GET", "POST"])
def change_email():
    """Смена email"""
    error_msg = ""
    if session.get(k_user):
        username = session[k_user]["name"]
        user = User.query.filter(User.name == username).first()

        form = ChangeEmailForm()
        if request.method == "POST" and form.validate_on_submit():
            if Profile.query.filter_by(email=form.new_email.data):
                error_msg = "Пользователь с таким аккаунтом уже существует"
            else:
                user.profile.email = form.new_email.data
                db.session.commit()
                return redirect(url_for("profile", id=user.profile.id))

        return render_template("change_email.html", form=form, error_msg=error_msg)

    return redirect(url_for("login"))


@app.route("/change_username", methods=["GET", "POST"])
def change_username():
    """Смена юзернейма"""
    error_msg = ""
    if not session.get(k_user):
        return redirect("login")

    if session[k_user].get("oauth_user", None):
        user = User.query.filter(User.name == session[k_user]["name"]).first()
        return redirect(url_for("profile", id=user.profile.id))

    form = ChangeUsernameForm()
    if request.method == "POST" and form.validate_on_submit():
        new_username = form.new_username.data
        old_username = session[k_user]["name"]

        if User.query.filter(User.name == new_username).first():
            error_msg = "Никнейм уже занят"
        else:
            user = User.query.filter(User.name == old_username).first()
            user.name = new_username
            db.session.commit()
            email = session[k_user].get("email")
            avatar_href = session[k_user].get("picture")
            oauth_user = session[k_user].get("oauth_user")
            session.pop(k_user)
            session[k_user] = {"email": email, "avatar_href": avatar_href, "name": new_username,
                               "oauth_user": oauth_user}
            user = User.query.filter(User.name == new_username).first()
            return redirect(url_for("profile", id=user.profile.id))

    return render_template("change_username.html", form=form, error_msg=error_msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Ресет пароля на новый автоматически генерируемый"""
    error_msg = ""
    if session.get(k_user):
        user = User.query.filter(User.name == session[k_user]["name"]).first()
        return redirect(url_for("profile", id=user.profile.id))

    form = ResetPasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        profile = Profile.query.filter_by(email=email).first()
        user = User.query.filter_by(id=profile.user_id).first()
        if user and user.password:
            temp_password = generate_random_password()
            user.password = generate_password_hash(temp_password)
            db.session.commit()
            send_password_reset_email(profile.email, temp_password)
            return redirect(url_for("login"))
        else:
            error_msg = "Такого email не существует"
    return render_template("reset_password.html", form=form, error_msg=error_msg)


def send_password_reset_email(email, temp_password):
    """Отправление пароля по емайл"""
    message = Message(
        "Сброс пароля",
        sender="lyamkin200603@gmail.com",
        recipients=[email]
    )
    message.body = f"Ваш временный пароль: {temp_password}"
    mail.send(message)


def generate_random_password(length=8):
    """Генерация рандомного пароля"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(length))
    return password


@app.route("/upload_photo", methods=["GET", "POST"])
def upload_photo():
    """Загрузка изображения для профиля"""
    if session.get(k_user):
        form = UploadPhotoForm()
        if request.method == "POST" and form.validate_on_submit():
            photo = form.photo.data
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = UPLOAD_FOLDER + "/" + filename
                photo.save(photo_path)
                user = User.query.filter(User.name == session[k_user]["name"]).first()
                user.profile.avatar_href = filename
                db.session.commit()
                return redirect(url_for("profile", id=user.profile.id))
    else:
        return redirect(url_for("login"))

    return render_template("upload_photo.html", form=form)


def allowed_file(filename):
    """Проверка на то, поддерживается ли разрешение картинки для загрузки"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/case/<int:case_id>")
def open_case(case_id):
    """Страница с инфой о кейсе, его открытием и т.д."""
    if session.get(k_user):
        case = Case.query.get(case_id)
        if not case:
            return jsonify({"error": "Кейс не найден"})

        rand_item = Item.query.filter(Item.case_id == case_id).order_by(func.random()).first()
    else:
        return redirect(url_for("login"))

    username = session[k_user].get("name")
    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(name=username).first()
    comments = Comment.query.filter_by(case_id=case_id).all()

    return render_template("open_case.html", user=user, case=case, item=rand_item, comments=comments)


@app.route("/create_case", methods=["GET", "POST"])
def create_case():
    """Страница для создания кейса"""
    if session.get(k_user):
        form = CreateCaseForm()
        username = session[k_user].get("name")
        if not username:
            return redirect(url_for("login"))

        user = User.query.filter_by(name=username).first()
        if request.method == "POST" and form.validate_on_submit():
            name = form.name.data
            image = form.image.data

            if image:
                filename = secure_filename(image.filename)
                photo_path = UPLOAD_FOLDER + "/" + filename
                image.save(photo_path)

                case = Case(name=name, image_path=filename, user_id=user.id)
                db.session.add(case)
                db.session.commit()
                return redirect(url_for("homepage"))
    else:
        return redirect(url_for("login"))

    return render_template("create_case.html", form=form, user=user)


@app.route("/create_comment/<int:case_id>", methods=["GET", "POST"])
def create_comment(case_id):
    """Страница для создания коммента"""
    form = CreateCommentForm()
    if session.get(k_user):
        username = session[k_user].get("name")
        if not username:
            return redirect(url_for("login"))

        if request.method == "POST" and form.validate_on_submit():
            user = User.query.filter_by(name=username).first()
            text = form.text.data
            comment = Comment(text=text, user_id=user.id, case_id=case_id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for("open_case", case_id=case_id))

    return render_template("create_comment.html", case=Case.query.get(case_id), form=form)


@app.route("/edit_case/<int:case_id>", methods=["GET", "POST"])
def edit_case(case_id):
    """Редактирование кейса"""
    case = Case.query.get(case_id)
    if not case:
        return jsonify({"error": "Кейс не найден"})

    form = EditCaseForm()
    username = session[k_user].get("name")
    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(name=username).first()
    if user.id != case.user_id:
        return redirect(url_for("homepage"))

    if request.method == "POST" and form.validate_on_submit():
        case.name = form.name.data

        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            case.image_path = filename

        db.session.commit()
        return redirect(url_for("homepage"))

    return render_template("edit_case.html", form=form, case=case, user=user)


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    """Страница для редактирования коммента"""
    form = EditCommentForm()

    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Коммент не найден"})

    if session.get(k_user):
        username = session[k_user].get("name")
        if not username:
            return redirect(url_for("login"))

        user = User.query.filter_by(name=username).first()
        if user.id != comment.user_id:
            return redirect(url_for("homepage"))

        if request.method == "POST" and form.validate_on_submit():
            comment.text = form.text.data
            db.session.commit()
            return redirect(url_for("open_case", case_id=comment.case.id))
    return render_template("edit_comment.html", form=form)


@app.route("/delete_case/<int:case_id>", methods=["GET", "POST"])
def delete_case(case_id):
    """Удаление кейса"""
    case = Case.query.get(case_id)
    if not case:
        return jsonify({"error": "Кейс не найден"})

    username = session[k_user].get("name")
    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(name=username).first()
    if user.id != case.user_id:
        return redirect(url_for("homepage"))

    if request.method == "POST":
        db.session.delete(case)
        db.session.commit()
        return redirect(url_for("homepage"))

    return render_template("delete_case.html", case=case, user=user)


@app.route("/delete_comment/<int:comment_id>", methods=["GET", "POST"])
def delete_comment(comment_id):
    """Удаление коммента"""
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Коммент не найден"})

    username = session[k_user].get("name")
    if not username:
        return redirect(url_for("login"))

    user = User.query.filter_by(name=username).first()
    if user.id != comment.user_id:
        return redirect(url_for("homepage"))

    if request.method == "POST":
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for("homepage"))

    return render_template("delete_comment.html", comment=comment)


@app.route("/todo/api/v1.0/user/<user_id>", methods=["GET"])
def get_user(user_id):
    """API для получения информации о пользователе"""
    if session.get(k_user, None):
        user = User.query.filter_by(id=user_id).first()
        if user:
            return jsonify({"username": user.name, "email": user.profile.email})
        else:
            return jsonify({"error": "user doesn't exist"})

    return jsonify({"error": "authorize pls"})


@app.route("/todo/api/v1.0/case/<int:case_id>", methods=["GET"])
def get_case(case_id):
    """API для получения информации о кейсе"""
    if session.get(k_user, None):
        case = Case.query.filter_by(id=case_id).first()
        items = Item.query.filter_by(case_id=case_id).all()
        if case and items:
            case_data = {
                "casename": case.name,
                "case items": [item.name for item in items],
            }

            response_data = json.dumps(case_data, ensure_ascii=False).encode("utf-8")

            response = Response(response_data, content_type="application/json; charset=utf-8")

            return response
        else:
            return jsonify({"error": "case or items doesn't exist"})

    return jsonify({"error": "authorize pls"})


@socketio.on("message")
def handle_message(message):
    emit("message", message, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True, allow_unsafe_werkzeug=True)
