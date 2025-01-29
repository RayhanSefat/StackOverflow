FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask flask-cors pymongo bcrypt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5001
CMD ["python", "app.py"]
