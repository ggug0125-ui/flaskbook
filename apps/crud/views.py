from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from apps import db
from apps.crud.forms import UserCreateForm, UserEditForm
from apps.crud.models import User

crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@crud.route("/")
@login_required
def root():
    return redirect(url_for("crud.users"))


@crud.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("crud/index.html", users=users)


@crud.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    form = UserCreateForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("사용자 정보를 등록했습니다.")
        return redirect(url_for("crud.users"))

    return render_template("crud/create.html", form=form)


@crud.route("/users/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserEditForm()

    if not form.is_submitted():
        form.username.data = user.username
        form.email.data = user.email

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()
        flash("사용자 정보를 갱신했습니다.")
        return redirect(url_for("crud.users"))

    return render_template("crud/edit.html", user=user, form=form)


@crud.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()

    db.session.delete(user)
    db.session.commit()
    flash("사용자 정보를 삭제했습니다.")
    return redirect(url_for("crud.users"))