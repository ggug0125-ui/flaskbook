import os
# 랜덤 색상 생성을 위한 모듈
import random

# uuid 파일명 생성을 위한 모듈
import uuid

# 경로 처리를 위한 모듈
from pathlib import Path

# 이미지 처리용 라이브러리
import cv2
import numpy as np
import torch
import torchvision

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    request,
)
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

from apps import db
from apps.crud.models import User
from apps.detector.forms import DetectorForm, UploadImageForm, DeleteForm
from apps.detector.models import UserImage, UserImageTag


# detector 블루프린트 생성
dt = Blueprint(
    "detector",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# 이미지 일람 화면
@dt.route("/")
@login_required
def index():
    # 업로드된 이미지 목록을 가져온다.
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    # 각 이미지에 연결된 태그 목록을 사전 형태로 만든다.
    user_image_tag_dict = {}

    for user_image in user_images:
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

    # 감지 버튼용 폼
    detector_form = DetectorForm()

    # 삭제 버튼용 폼
    delete_form = DeleteForm()

    return render_template(
        "detector/index.html",
        user_images=user_images,
        user_image_tag_dict=user_image_tag_dict,
        detector_form=detector_form,
        delete_form=delete_form,
    )

# 이미지 검색
@dt.route("/images/search", methods=["GET"])
@login_required
def search():
    # 업로드된 이미지 목록을 가져온다.
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    # GET 파라미터에서 검색어를 가져온다.
    search_text = request.args.get("search")

    # 검색 결과용 변수
    user_image_tag_dict = {}
    filtered_user_images = []

    # 이미지별 태그를 검사한다.
    for user_image in user_images:
        # 검색어가 비어 있으면 해당 이미지의 전체 태그를 가져온다.
        if not search_text:
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .all()
            )
        else:
            # 검색어가 있으면 해당 검색어가 포함된 태그만 먼저 찾는다.
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .filter(UserImageTag.tag_name.like("%" + search_text + "%"))
                .all()
            )

        # 검색 결과가 없으면 이 이미지는 제외한다.
        if not user_image_tags:
            continue

        # 화면에는 해당 이미지의 전체 태그를 다시 보여주기 위해 재조회한다.
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )

        # 이미지 id를 키로 태그 목록 저장
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

        # 검색 결과 이미지 목록에 추가
        filtered_user_images.append(user_image)

    # 버튼 폼 생성
    delete_form = DeleteForm()
    detector_form = DetectorForm()

    return render_template(
        "detector/index.html",
        user_images=filtered_user_images,
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
        detector_form=detector_form,
    )
    
# 업로드 폴더에 저장된 이미지를 브라우저에 표시하는 엔드포인트
@dt.route("/images/<path:filename>")
@login_required
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


# 이미지 업로드 화면
@dt.route("/images/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    form = UploadImageForm()

    if form.validate_on_submit():
        image_file = form.image.data
        filename = image_file.filename

        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image_file.save(save_path)

        user_image = UserImage(
            user_id=current_user.id,
            image_path=filename,
            is_detected=False,
        )

        db.session.add(user_image)
        db.session.commit()

        flash("이미지 업로드가 완료되었습니다.")
        return redirect(url_for("detector.index"))

    return render_template("detector/upload.html", form=form)


# 이미지 삭제
@dt.route("/images/delete/<int:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        # 삭제할 이미지 조회
        user_image = (
            db.session.query(UserImage)
            .filter(UserImage.id == image_id)
            .first()
        )

        if user_image is None:
            flash("이미지를 찾을 수 없습니다.")
            return redirect(url_for("detector.index"))

        # 본인 이미지인지 확인
        if user_image.user_id != current_user.id:
            flash("삭제 권한이 없습니다.")
            return redirect(url_for("detector.index"))

        # 원본 이미지 실제 경로를 미리 보관한다
        original_image_path = Path(
            current_app.config["UPLOAD_FOLDER"],
            user_image.image_path
        )

        # 연결된 태그 먼저 삭제
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == user_image.id
        ).delete()

        # 이미지 레코드 삭제
        db.session.delete(user_image)
        db.session.commit()

        # 파일이 실제로 있으면 삭제
        if original_image_path.exists():
            original_image_path.unlink()

        flash("이미지가 삭제되었습니다.")

    except SQLAlchemyError as e:
        flash("이미지 삭제 처리에서 오류가 발생했습니다.")
        db.session.rollback()
        current_app.logger.error(e)

    except Exception as e:
        flash("이미지 파일 삭제 처리에서 오류가 발생했습니다.")
        current_app.logger.error(e)

    return redirect(url_for("detector.index"))


# 랜덤 테두리 색상을 생성한다
def make_color(labels):
    # 라벨 수만큼 랜덤 색상을 만든다
    colors = [
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        for _ in labels
    ]

    # 그 중 하나를 랜덤 선택한다
    color = random.choice(colors)
    return color


# 이미지 크기에 따라 테두리 선 두께를 계산한다
def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line


# 이미지에 사각형 테두리를 그린다
def draw_lines(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2


# 이미지에 감지된 라벨 텍스트를 그린다
def draw_texts(result_image, line, c1, cv2_module, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)

    t_size = cv2_module.getTextSize(
        display_txt,
        0,
        fontScale=line / 3,
        thickness=font
    )[0]

    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3

    cv2_module.rectangle(result_image, c1, c2, color, -1)

    cv2_module.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [225, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )

    return cv2_module


# 물체 감지를 실행하고 태그 목록, 감지 후 파일명을 반환한다
def exec_detect(target_image_path):
    print("A. exec_detect 시작")

    # config에서 라벨 목록을 읽어온다
    labels = current_app.config["LABELS"]
    print("B. LABELS 읽기 완료")

    # 대상 이미지를 RGB로 읽어온다
    image = Image.open(target_image_path).convert("RGB")
    print("C. 이미지 읽기 완료")

    # 이미지를 텐서로 변환한다
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    print("D. 텐서 변환 완료")

    # 저장된 학습 모델을 읽어온다
    model = torch.load(
        Path(current_app.root_path, "detector", "model.pt"),
        weights_only=False
    )
    print("E. 모델 로드 완료")

    # 추론 모드로 전환한다
    model = model.eval()
    print("F. eval 완료")

    # 물체 감지 추론을 수행한다
    output = model([image_tensor])[0]
    print("G. 추론 완료")

    # 감지된 태그 목록
    tags = []

    # 원본 이미지를 numpy 배열로 복사한다
    result_image = np.array(image.copy())
    print("H. 결과 이미지 배열 생성 완료")

    # 감지 결과를 순회하면서 박스와 라벨을 그린다
    for box, label, score in zip(
        output["boxes"],
        output["labels"],
        output["scores"]
    ):
        # 텐서를 파이썬 값으로 변환한다
        label = int(label)
        score = float(score)

        if score > 0.5 and labels[label] not in tags:
            # 랜덤 색상 선택
            color = make_color(labels)

            # 선 두께 계산
            line = make_line(result_image)

            # 박스 좌표를 정수로 변환
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))

            # 테두리 선을 그림
            cv2_module = draw_lines(c1, c2, result_image, line, color)

            # 라벨 텍스트를 그림
            cv2_module = draw_texts(
                result_image,
                line,
                c1,
                cv2_module,
                color,
                labels,
                label,
            )

            # 태그 목록에 추가
            tags.append(labels[label])

    print("I. 박스/라벨 처리 완료:", tags)

    # 감지 후 파일명을 새로 만든다
    detected_image_file_name = str(uuid.uuid4()) + ".jpg"

    # 감지 후 이미지 저장 경로를 만든다
    detected_image_file_path = str(
        Path(
            current_app.config["UPLOAD_FOLDER"],
            detected_image_file_name
        )
    )

    print("J. 감지 결과 저장 경로:", detected_image_file_path)

    # RGB 배열을 OpenCV 저장용 BGR로 바꿔 저장한다
    cv2.imwrite(
        detected_image_file_path,
        cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
    )

    print("K. 감지 이미지 저장 완료")

    return tags, detected_image_file_name


# 감지 결과 이미지와 태그를 DB에 저장한다
def save_detected_image_tags(user_image, tags, detected_image_file_name):
    print("L. DB 저장 시작")

    # 기존 태그가 남아 있으면 먼저 삭제한다
    db.session.query(UserImageTag).filter(
        UserImageTag.user_image_id == user_image.id
    ).delete()

    # 감지 후 이미지 파일명으로 업데이트
    user_image.image_path = detected_image_file_name

    # 감지 완료 처리
    user_image.is_detected = True

    db.session.add(user_image)

    # 감지된 태그들을 user_image_tags 테이블에 저장
    for tag in tags:
        user_image_tag = UserImageTag(
            user_image_id=user_image.id,
            tag_name=tag
        )
        db.session.add(user_image_tag)

    db.session.commit()
    print("M. DB 저장 완료")


# 물체 감지 엔드포인트
@dt.route("/detect/<int:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    print("1. detect 시작")

    # 감지 대상 이미지를 조회한다
    user_image = (
        db.session.query(UserImage)
        .filter(UserImage.id == image_id)
        .first()
    )

    print("2. user_image 조회 완료:", user_image)

    # 이미지가 없으면 메시지 출력 후 메인으로 이동
    if user_image is None:
        flash("물체 감지 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.index"))

    # 본인 이미지인지 확인한다
    if user_image.user_id != current_user.id:
        flash("물체 감지 권한이 없습니다.")
        return redirect(url_for("detector.index"))

    # 이미 감지된 이미지면 중복 처리 막기
    if user_image.is_detected:
        flash("이미 감지가 완료된 이미지입니다.")
        return redirect(url_for("detector.index"))

    # 감지 대상 이미지의 실제 경로를 만든다
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"],
        user_image.image_path
    )

    print("3. target_image_path 생성 완료:", target_image_path)

    # 실제 파일이 없으면 처리 중단
    if not target_image_path.exists():
        flash("감지 대상 이미지 파일이 존재하지 않습니다.")
        return redirect(url_for("detector.index"))

    # 물체 감지를 수행한다
    tags, detected_image_file_name = exec_detect(target_image_path)

    print("4. exec_detect 완료:", tags, detected_image_file_name)

    try:
        # 감지 결과를 DB에 저장한다
        save_detected_image_tags(
            user_image,
            tags,
            detected_image_file_name
        )
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생했습니다.")
        db.session.rollback()
        current_app.logger.error(e)
        print("DB 에러 발생:", e)
        return redirect(url_for("detector.index"))

    print("5. detect 완료")
    return redirect(url_for("detector.index"))