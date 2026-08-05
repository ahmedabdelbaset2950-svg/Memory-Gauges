from flask import request, jsonify
from flask_login import login_required

from app.search import search_bp
from app.search.services import global_search


@search_bp.route("/")
@login_required
def search():

    q = request.args.get("q", "").strip()

    if len(q) < 2:
        return jsonify([])

    return jsonify(global_search(q))