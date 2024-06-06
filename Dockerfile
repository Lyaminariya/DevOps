# FROM python:3.10
#
# COPY ./requirements.txt /app/requirements.txt
#
# WORKDIR /app
#
# RUN pip install -r requirements.txt
#
# COPY . /app
#
# ENTRYPOINT ["python"]
# CMD ["app.py"]

FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]
