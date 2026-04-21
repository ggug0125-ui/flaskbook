import os
import shutil

import pytest

from apps.app import create_app, db


@pytest.fixture
def fixture_app():
    # 테스트용 앱 생성
    app = create_app("testing")

    # Flask 앱 컨텍스트 활성화
    app.app_context().push()

    # 테스트용 DB 테이블 생성
    with app.app_context():
        db.create_all()

    # 테스트용 업로드 폴더 생성
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # 테스트 실행
    yield app

    # =========================
    # 여기부터 정리 (중요🔥)
    # =========================

    # DB 세션 정리
    db.session.remove()

    # 테이블 삭제
    db.drop_all()

    # 업로드 폴더 삭제
    shutil.rmtree(app.config["UPLOAD_FOLDER"], ignore_errors=True)


@pytest.fixture
def client(fixture_app):
    # Flask 테스트 클라이언트 반환
    return fixture_app.test_client()