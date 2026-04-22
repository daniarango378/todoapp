from __future__ import annotations

from flask import Flask, jsonify

from app.routes.tasks import tasks_bp
from app.services.task_service import TaskNotFoundError, TaskService, ValidationError


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["TASK_SERVICE"] = TaskService()

    if config:
        app.config.update(config)

    app.register_blueprint(tasks_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(TaskNotFoundError)
    def handle_not_found(error: TaskNotFoundError):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):
        return jsonify({"error": str(error)}), 400

    @app.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        return response

    return app
