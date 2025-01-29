FROM python:3.10-slim
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir flask flask-cors pymongo
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5003
CMD ["python", "app.py"]
