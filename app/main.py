from flask import Flask, jsonify, url_for
from flask_cors import CORS

from app import models
from app.database import db, init_db

app = Flask(__name__)
CORS(app)
init_db(app)


@app.route("/")
def main():
    href = url_for("show_records")
    return f'See the data at <a href="{href}">{href}</a>'


@app.route("/records/")
def show_records():

    # records = app.db.query(models.Record).all()  # use db attribute
    # records = models.Record.query.all()  # use query_property
    records = db.query(models.Record).all()  # or use proxy
    return jsonify([record.to_dict() for record in records])
