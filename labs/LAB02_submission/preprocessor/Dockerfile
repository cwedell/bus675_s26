FROM python:3.11-slim

WORKDIR /watcher

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY watcher.py .

RUN mkdir /incoming

CMD ["python", "-u", "watcher.py"]