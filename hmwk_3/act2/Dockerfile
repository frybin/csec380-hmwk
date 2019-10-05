FROM python:3.7-alpine3.7

COPY act2.py simplerequest.py requirements.txt /tmp/

WORKDIR /tmp/

RUN pip install -r /tmp/requirements.txt

CMD ["python", "-u", "/tmp/act2.py"]