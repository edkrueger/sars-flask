from typing import List

from flask import Flask, jsonify, url_for
from flask_cors import CORS

from . import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)


@app.route("/")
def main():
    return f"See the data at {url_for('show_records')}"


@app.route("/records/")
def show_records():
    db = SessionLocal()
    records = db.query(models.Record).all()
    db.close()
    return jsonify([record.to_dict() for record in records])


if __name__ == "__main__":
    app.run(debug=True)
