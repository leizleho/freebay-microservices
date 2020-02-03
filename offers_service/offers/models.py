from sqlalchemy import func
from offers.db import db


class OfferModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    username = db.Column(db.String(50))
    description = db.Column(db.String(250))
    category = db.Column(db.String(50))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    picture_url = db.Column(db.String(150), nullable=True)
    timestamp = db.Column(db.DateTime, server_default=func.now())
