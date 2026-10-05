"""Run separately with: python3 flask_api/app.py"""
import os
import sys

from flask import Flask, jsonify

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_management.settings")

import django
django.setup()

from routes.books import books_api
from routes.members import members_api
from routes.transactions import transactions_api
from routes.statistics import statistics_api


def create_app():
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.register_blueprint(books_api, url_prefix="/api/books")
    app.register_blueprint(members_api, url_prefix="/api/members")
    app.register_blueprint(transactions_api, url_prefix="/api/transactions")
    app.register_blueprint(statistics_api, url_prefix="/api/statistics")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(success=False, error="Resource not found"), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify(success=False, error="Internal server error"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
