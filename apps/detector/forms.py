from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField


# 이미지 업로드 폼
class UploadImageForm(FlaskForm):
    image = FileField(
        "이미지",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "jpeg", "png"], "이미지 파일만 업로드할 수 있습니다."),
        ],
    )
    submit = SubmitField("이미지 업로드")


# 물체 감지 폼
class DetectorForm(FlaskForm):
    submit = SubmitField("감지")


# 이미지 삭제 폼
class DeleteForm(FlaskForm):
    submit = SubmitField("삭제")