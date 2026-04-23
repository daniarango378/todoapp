"""Flask application factory and global application configuration."""

from __future__ import annotations

from flask import Flask, jsonify

from app.routes.tasks import tasks_bp
from app.services.task_service import TaskNotFoundError, TaskService, ValidationError


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config["TASK_SERVICE"] = TaskService()

    if config:
        app.config.update(config)

    app.register_blueprint(tasks_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        """Return a simple health response for availability checks."""
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(TaskNotFoundError)
    def handle_not_found(error: TaskNotFoundError):
        """Return a 404 response for missing task errors."""
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):
        """Return a 400 response for validation errors."""
        return jsonify({"error": str(error)}), 400

    @app.after_request
    def apply_cors(response):
        """Attach permissive CORS headers to every outgoing response."""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        return response

    return app