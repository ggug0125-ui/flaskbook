FROM python:3.10.7

WORKDIR /usr/src/

COPY ./apps /usr/src/apps
COPY ./flaskbook_api/requirements.txt /usr/src/requirements.txt
COPY ./model.pt /usr/src/model.pt

RUN pip install --upgrade pip
RUN pip install torch torchvision opencv-python
RUN pip install -r requirements.txt

RUN echo "building..."

ENV FLASK_APP "apps.app:create_app('local')"
ENV IMAGE_URL "/storage/images/"

EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]