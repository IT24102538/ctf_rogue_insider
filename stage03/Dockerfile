FROM python:3.9-slim
RUN pip install --no-cache-dir Flask==3.0.3 Werkzeug==3.0.3
WORKDIR /app
COPY app.py .
COPY static/ ./static/
CMD ["python", "app.py"]
