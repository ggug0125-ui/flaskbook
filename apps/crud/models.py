from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from apps import db
from apps.app import login_manager


class User(db.Model, UserMixin):
    # 사용할 테이블 이름
    __tablename__ = "users"

    # 사용자 ID
    id = db.Column(db.Integer, primary_key=True)

    # 사용자명
    username = db.Column(db.String(50), index=True)

    # 이메일
    email = db.Column(db.String(120), unique=True, index=True)

    # 비밀번호 해시값
    password_hash = db.Column(db.String(255))

    # 생성일
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 수정일
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    user_images = db.relationship(
    "UserImage", backref="user", order_by="desc(UserImage.id)"
    )

    @property
    def password(self):
        raise AttributeError("읽어 들일 수 없음")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 비밀번호 확인
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 이메일 주소 중복 확인
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)