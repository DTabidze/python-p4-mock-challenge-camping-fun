#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return ""


@app.route("/campers", methods=["GET", "POST"])
def get_campers():
    if request.method == "GET":
        all = Camper.query.all()
        campers = []
        for camper in all:
            campers.append(camper.to_dict())
        return campers, 200
    elif request.method == "POST":
        data = request.json
        camper = Camper()
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 201
        except (IntegrityError, ValueError) as ie:
            return {"error": ie.args}, 422


@app.route("/campers/<int:id>", methods=["GET", "PATCH"])
def get_camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if not camper:
        return {"error": "Camper not found"}, 404
    if request.method == "GET":
        return camper.to_dict(rules=("signups.activity",)), 200
        # return camper.to_dict(rules=("activities",)), 200
    elif request.method == "PATCH":
        data = request.json
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.commit()
            return camper.to_dict(rules=("-activities",)), 200
        except (IntegrityError, ValueError) as ie:
            return {"error": ie.args}, 422


@app.route("/activities", methods=["GET"])
def get_activities():
    all = Activity.query.all()
    if request.method == "GET":
        activities = []
        for activity in all:
            activities.append(activity.to_dict())
        return activities, 200


@app.route("/activities/<int:id>", methods=["DELETE"])
def delete_activity(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if not activity:
        return {"error": "Activity not found"}, 404
    elif request.method == "DELETE":
        db.session.delete(activity)
        db.session.commit()
        return {}, 204


@app.route("/signups", methods=["POST"])
def signup():
    signup = Signup()
    data = request.json
    try:
        for attr in data:
            setattr(signup, attr, data[attr])
        db.session.add(signup)
        db.session.commit()
        return (
            signup.to_dict(
                rules=(
                    "activity",
                    "camper",
                )
            ),
            201,
        )
    except (IntegrityError, ValueError) as ie:
        return {"errors": ["validation errors"]}, 422


if __name__ == "__main__":
    app.run(port=5555, debug=True)
