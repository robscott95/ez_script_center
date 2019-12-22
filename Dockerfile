FROM python:3.7
LABEL author="Robert Kuśka"

ADD requirements.txt /app/requirements.txt

WORKDIR /app

#Install Python packages
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python -u run.py"]