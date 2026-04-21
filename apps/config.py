from pathlib import Path

# 프로젝트 루트 경로
basedir = Path(__file__).resolve().parent.parent


class BaseConfig:
    # 공통 비밀키
    SECRET_KEY = "2AZSMss3p5QpbcY2hBsJ"

    # Flask-WTF CSRF 보호용 비밀키
    WTF_CSRF_SECRET_KEY = "AuwzyszU5sugKN7KZs6f"

    # 이미지 업로드 경로
    UPLOAD_FOLDER = str(Path(basedir, "apps", "images"))

    # 물체 감지에 사용할 라벨
    LABELS = [
        "unlabeled",
        "person",
        "bicycle",
        "car",
        "motorcycle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
        "traffic light",
        "fire hydrant",
        "N/A",
        "stop sign",
        "parking meter",
        "bench",
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
        "N/A",
        "backpack",
        "umbrella",
        "N/A",
        "N/A",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis",
        "snowboard",
        "sports ball",
        "kite",
        "baseball bat",
        "baseball glove",
        "skateboard",
        "surfboard",
        "tennis racket",
        "bottle",
        "N/A",
        "wine glass",
        "cup",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot dog",
        "pizza",
        "donut",
        "cake",
        "chair",
        "couch",
        "potted plant",
        "bed",
        "N/A",
        "dining table",
        "N/A",
        "N/A",
        "toilet",
        "N/A",
        "tv",
        "laptop",
        "mouse",
        "remote",
        "keyboard",
        "cell phone",
        "microwave",
        "oven",
        "toaster",
        "sink",
        "refrigerator",
        "N/A",
        "book",
        "clock",
        "vase",
        "scissors",
        "teddy bear",
        "hair drier",
        "toothbrush",
    ]


class LocalConfig(BaseConfig):
    # MariaDB 연결 정보
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://KKW:KKW320!!@localhost:3306/MBC320DB"

    # SQLAlchemy 이벤트 추적 비활성화
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 실행되는 SQL 로그 출력
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    # 테스트용 DB (실사용 DB 말고 별도 DB 사용)
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://KKW:KKW320!!@localhost:3306/MBC320DB_TEST"

    # SQLAlchemy 이벤트 추적 비활성화
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 테스트에서는 SQL 로그 출력 안 함
    SQLALCHEMY_ECHO = False

    # 테스트에서는 CSRF 비활성화
    WTF_CSRF_ENABLED = False

    # Flask 테스트 모드 활성화
    TESTING = True

    # 테스트용 업로드 폴더
    UPLOAD_FOLDER = str(Path(basedir, "tests", "uploads"))


config = {
    "testing": TestingConfig,
    "local": LocalConfig,
}