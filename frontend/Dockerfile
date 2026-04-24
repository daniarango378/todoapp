FROM python:3.12-slim

WORKDIR /app

COPY frontend /app/frontend

RUN python frontend/build_frontend.py

WORKDIR /app/frontend/dist

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "/app/frontend/serve_frontend.py"]