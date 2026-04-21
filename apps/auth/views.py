from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from apps import db
from apps.auth.forms import LoginForm, SignUpForm
from apps.crud.models import User


auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# 안전한 next URL인지 확인
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# 회원가입 화면
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        # 사용자 생성
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.password = form.password.data

        # 이메일 중복 확인
        if user.is_duplicate_email():
            flash("이미 사용 중인 이메일 주소입니다.")
            return redirect(url_for("auth.signup"))

        # DB 저장
        db.session.add(user)
        db.session.commit()

        # 회원가입 후 next가 있으면 그쪽으로 이동
        next_ = request.args.get("next")
        if next_ is None or not next_.startswith("/") or not is_safe_url(next_):
            next_ = url_for("detector.index")

        return redirect(next_)

    return render_template("auth/signup.html", form=form)


# 로그인 화면
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # 이메일로 사용자 조회
        user = User.query.filter_by(email=form.email.data).first()

        # 비밀번호가 맞으면 로그인
        if user is not None and user.verify_password(form.password.data):
            login_user(user)

            # 로그인 후 next가 있으면 그쪽으로 이동
            next_ = request.args.get("next")
            if next_ is None or not next_.startswith("/") or not is_safe_url(next_):
                next_ = url_for("detector.index")

            return redirect(next_)

        flash("이메일 주소 또는 비밀번호가 일치하지 않습니다.")

    return render_template("auth/login.html", form=form)


# 로그아웃
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("detector.index"))