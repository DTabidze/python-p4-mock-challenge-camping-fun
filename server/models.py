from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import re

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signup_activity = db.relationship(
        "Signup", cascade="all,delete", back_populates="activity"
    )

    # Add serialization rules
    serialize_rules = ("-signup_activity",)

    def __repr__(self):
        return f"<Activity {self.id}: {self.name}>"


class Camper(db.Model, SerializerMixin):
    __tablename__ = "campers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="camper")
    # Add association_proxy to access related activities
    # activities = association_proxy(
    #     "signups", "activity", creator=lambda activity: activity.signup_activity
    # )
    # activities = association_proxy(
    #     "signups", "activity", creator=lambda activity: Signup(activity=activity)
    # )

    # Add serialization rules
    serialize_rules = ("-signups",)

    # Add validation
    @validates("name")
    def validate_name(self, key, value):
        if type(value) != str:
            raise ValueError(f"{key} must be a string")
        return value

    @validates("age")
    def validate_age(self, key, value):
        if type(value) != int:
            raise ValueError(f"{key} must be an integer")
        elif not 8 <= value <= 18:
            raise ValueError(f"Age must be between 8-18!!!")
        return value

    def __repr__(self):
        return f"<Camper {self.id}: {self.name}>"


class Signup(db.Model, SerializerMixin):
    __tablename__ = "signups"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))

    # Add relationships
    activity = db.relationship("Activity", back_populates="signup_activity")
    camper = db.relationship("Camper", back_populates="signups")

    # Add serialization rules
    serialize_rules = ("-camper", "-activity")

    # Add validation
    @validates("time")
    def validate_time(self, key, value):
        if type(value) != int:
            raise ValueError(f"Time {key} must be integer")
        elif not 0 <= value <= 23:
            raise ValueError("Time must be between 0-23!!!")
        return value

    def __repr__(self):
        return f"<Signup {self.id}>"
