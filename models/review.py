#!/usr/bin/python3
from models.base_models import BaseModel


class Review(BaseModel):
    """ creating class Review"""

    place_id = ""
    user_id = ""
    text = ""
