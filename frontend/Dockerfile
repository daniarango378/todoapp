FROM python:3.12-slim

WORKDIR /app

COPY frontend /app/frontend

RUN python frontend/build_frontend.py

WORKDIR /app/frontend/dist

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000"]
