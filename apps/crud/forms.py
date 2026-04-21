from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class UserCreateForm(FlaskForm):
    username = StringField(
        "사용자명",
        validators=[DataRequired(message="사용자명은 필수입니다.")]
    )
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired(message="메일 주소는 필수입니다."),
            Email(message="메일 주소 형식이 올바르지 않습니다.")
        ]
    )
    password = PasswordField(
        "비밀번호",
        validators=[DataRequired(message="비밀번호는 필수입니다.")]
    )
    submit = SubmitField("신규 등록")


class UserEditForm(FlaskForm):
    username = StringField(
        "사용자명",
        validators=[DataRequired(message="사용자명은 필수입니다.")]
    )
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired(message="메일 주소는 필수입니다."),
            Email(message="메일 주소 형식이 올바르지 않습니다.")
        ]
    )
    password = PasswordField(
        "비밀번호",
        validators=[DataRequired(message="비밀번호는 필수입니다.")]
    )
    submit = SubmitField("갱신")