FROM python:3.7-slim

WORKDIR /flask-test

COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY app.py model.py db.py boot.sh ./
COPY ckpt ./ckpt
ADD ckpt ./ckpt
RUN chmod +x boot.sh

ENV FLASK_APP app.py


EXPOSE 5000
CMD ["venv/bin/python", "app.py"]
# ENTRYPOINT [ "./boot.sh" ] # need to change Werkzeug==0.14.1
