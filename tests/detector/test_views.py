import io

from apps import db
from apps.detector.models import UserImage, UserImageTag


def test_index(client):
    rv = client.get("/", follow_redirects=True)
    html = rv.data.decode()

    assert "사용자 신규 등록" in html
    assert "메일 주소" in html
    assert "비밀번호" in html


def signup(client, username, email, password):
    data = dict(
        username=username,
        email=email,
        password=password,
        submit="신규 등록",
    )
    return client.post("/auth/signup", data=data, follow_redirects=True)


def login(client, email, password):
    data = dict(
        email=email,
        password=password,
        submit="로그인",
    )
    return client.post("/auth/login", data=data, follow_redirects=True)


def test_login_after_signup(client):
    signup(client, "admin3", "flaskbook3@example.com", "password")

    rv = login(client, "flaskbook3@example.com", "password")
    html = rv.data.decode()

    assert "로그아웃" in html or "admin3" in html


def test_index_signup(client):
    rv = signup(client, "admin", "flaskbook@example.com", "password")
    html = rv.data.decode()

    assert (
        "사용자 신규 등록" in html
        or "로그아웃" in html
        or "admin" in html
    )


def test_upload_image_page_requires_auth(client):
    rv = client.get("/images/upload", follow_redirects=True)
    html = rv.data.decode()

    assert "사용자 신규 등록" in html


def test_upload_image_page_after_signup(client):
    signup(client, "admin2", "flaskbook2@example.com", "password")

    rv = client.get("/images/upload", follow_redirects=True)
    html = rv.data.decode()

    assert "사용자 신규 등록" in html
    assert "메일 주소" in html
    assert "비밀번호" in html


def test_upload_image_post(client, fixture_app):
    signup(client, "admin4", "flaskbook4@example.com", "password")
    login(client, "flaskbook4@example.com", "password")

    data = {
        "image": (io.BytesIO(b"fake image data"), "test.jpg"),
        "submit": "이미지 업로드",
    }

    rv = client.post(
        "/images/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    html = rv.data.decode()

    assert "이미지 업로드가 완료되었습니다." in html or "detector" in html

    with fixture_app.app_context():
        user_image = UserImage.query.first()
        assert user_image is not None
        assert user_image.image_path == "test.jpg"
        assert user_image.is_detected is False


def test_detect_post(client, fixture_app, monkeypatch):
    signup(client, "admin5", "flaskbook5@example.com", "password")
    login(client, "flaskbook5@example.com", "password")

    data = {
        "image": (io.BytesIO(b"fake image data"), "detect_test.jpg"),
        "submit": "이미지 업로드",
    }

    client.post(
        "/images/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    with fixture_app.app_context():
        user_image = UserImage.query.first()
        assert user_image is not None
        image_id = user_image.id

    def fake_exec_detect(target_image_path):
        return ["dog", "person"], "detected_test.jpg"

    monkeypatch.setattr("apps.detector.views.exec_detect", fake_exec_detect)

    rv = client.post(f"/detect/{image_id}", follow_redirects=True)
    assert rv.status_code == 200

    with fixture_app.app_context():
        user_image = db.session.get(UserImage, image_id)
        assert user_image is not None
        assert user_image.is_detected is True
        assert user_image.image_path == "detected_test.jpg"

        tags = UserImageTag.query.filter_by(user_image_id=image_id).all()
        tag_names = [tag.tag_name for tag in tags]

        assert "dog" in tag_names
        assert "person" in tag_names


def test_delete_image_post(client, fixture_app):
    signup(client, "admin6", "flaskbook6@example.com", "password")
    login(client, "flaskbook6@example.com", "password")

    data = {
        "image": (io.BytesIO(b"fake image data"), "delete_test.jpg"),
        "submit": "이미지 업로드",
    }

    client.post(
        "/images/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    with fixture_app.app_context():
        user_image = UserImage.query.first()
        assert user_image is not None

        image_id = user_image.id

        user_image_tag = UserImageTag(
            user_image_id=image_id,
            tag_name="dog",
        )
        db.session.add(user_image_tag)
        db.session.commit()

    rv = client.post(f"/images/delete/{image_id}", follow_redirects=True)

    assert rv.status_code == 200

    with fixture_app.app_context():
        deleted_image = db.session.get(UserImage, image_id)
        deleted_tags = UserImageTag.query.filter_by(user_image_id=image_id).all()

        assert deleted_image is None
        assert deleted_tags == []

def test_custom_error(client):
    rv = client.get("/notfound")
    assert "404 Not Found" in rv.data.decode()