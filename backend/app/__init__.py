from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .models import db
from .controllers.room_controller import room_bp
from .controllers.guest_controller import guest_bp
from .controllers.reservation_controller import reservation_bp
from .controllers.errors import register_service_errors
from .seed import seed


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    CORS(app)
    register_service_errors(app)
    db.init_app(app)

    app.register_blueprint(room_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(reservation_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Ruta no encontrada"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Método no permitido"}), 405

    with app.app_context():
        db.create_all()
        if app.config["SEED"]:
            seed()

    return app
