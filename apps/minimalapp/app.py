import logging
import os

from email_validator import validate_email, EmailNotValidError
from flask import (
    Flask,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    make_response,
    session,
    Response,
    jsonify,
)
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = "2AZSMss3p5QpbcY2hBsJ"
app.json.ensure_ascii = False

# -------------------------------
# 로그 레벨 설정
# -------------------------------
app.logger.setLevel(logging.DEBUG)

# -------------------------------
# flask-mail 설정
# -------------------------------
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)


# -------------------------------
# 메인 페이지
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------
# 문의 입력 화면
# -------------------------------
@app.route("/contact")
def contact():
    return render_template(
        "contact.html",
        username="",
        email="",
        description=""
    )


# -------------------------------
# 문의 완료 처리
# -------------------------------
@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        is_valid = True

        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False

        if not email:
            flash("메일 주소는 필수입니다")
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요")
            is_valid = False

        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))

        # 이메일을 보낸다
        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username,
            description=description,
        )

        flash("문의 내용은 메일로 송신했습니다. 문의해 주셔서 감사합니다.")

    return render_template("contact_complete.html")


# -------------------------------
# 이메일 송신 함수
# -------------------------------
def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)


# -------------------------------
# URL 변수 사용
# -------------------------------
@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello(name):
    return f"hello, {name}!"


# -------------------------------
# 템플릿에 값 전달
# -------------------------------
@app.route("/name/<name>")
def show_name(name):
    return render_template("index.html", name=name)


# -------------------------------
# url_for() 테스트 (책 55쪽)
# -------------------------------
with app.test_request_context():
    print(url_for("index"))
    print(url_for("hello-endpoint", name="world"))
    print(url_for("show_name", name="AK", page="1"))


# -------------------------------
# Flask 컨텍스트 테스트 (책 58~59쪽)
# -------------------------------
ctx = app.app_context()
ctx.push()

print(current_app.name)

g.test = "hello"
print(g.test)

with app.test_request_context("/test?value=123"):
    print(request.args.get("value"))

with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))


# -------------------------------
# 쿠키 저장
# -------------------------------
@app.route("/set-cookie")
def set_cookie():
    response = make_response("쿠키를 설정했습니다.")
    response.set_cookie("username", "FlaskUser")
    return response


# -------------------------------
# 쿠키 읽기
# -------------------------------
@app.route("/get-cookie")
def get_cookie():
    username = request.cookies.get("username")
    return f"username={username}"


# -------------------------------
# 세션 저장
# -------------------------------
@app.route("/set-session")
def set_session():
    session["username"] = "AK"
    return "세션 저장 완료"


# -------------------------------
# 세션 읽기
# -------------------------------
@app.route("/get-session")
def get_session():
    username = session.get("username")
    return f"username={username}"


# -------------------------------
# 세션 삭제
# -------------------------------
@app.route("/delete-session")
def delete_session():
    session.pop("username", None)
    return "세션 삭제 완료"

# -------------------------------
# 응답
# -------------------------------
@app.route("/response")
def response_test():
    return Response("직접 만든 응답입니다.")

@app.route("/response-status")
def response_status():
    return Response("정상 응답입니다.", status=200)

@app.route("/response-error")
def response_error():
    return Response("에러 응답입니다.", status=500)
    
# -------------------------------
# Json 응답
# -------------------------------
@app.route("/json")
def json_test():
    return jsonify({
        "username": "AK",
        "message": "JSON 응답입니다"
    })

# -------------------------------
# 서버 실행
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)