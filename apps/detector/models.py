from datetime import datetime

from apps import db


# 업로드한 이미지 정보를 저장하는 모델
class UserImage(db.Model):
    __tablename__ = "user_images"

    # 이미지 PK
    id = db.Column(db.Integer, primary_key=True)

    # users 테이블의 id를 외래 키로 연결
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # 업로드한 이미지 파일명 저장
    image_path = db.Column(db.String(255))

    # 물체 감지 처리 여부 저장
    is_detected = db.Column(db.Boolean, default=False)

    # 생성일 저장
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 수정일 저장
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )


# 감지된 태그 정보를 저장하는 모델
class UserImageTag(db.Model):
    __tablename__ = "user_image_tags"

    # 태그 PK
    id = db.Column(db.Integer, primary_key=True)

    # user_images 테이블의 id를 외래 키로 연결
    user_image_id = db.Column(db.Integer, db.ForeignKey("user_images.id"))

    # 감지된 태그명 저장
    tag_name = db.Column(db.String(255))

    # 생성일 저장
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 수정일 저장
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )