#!/usr/bin/python3

""" Creating a base model"""

import uuid
from datetime import datetime
import models


class BaseModel:
    def __init__(self, *args, **kwargs):
        """
        The class serces as the base class for other classes to
        inherit from.
        *args and **kwargs are used as constructors of the BaseModel

        """
        if key, value in kwargs.items():
            if key != "__class__":
                setattr(self, key, value)
                """ assign the attributes key and value to the
                base model instance """

            if "created_at" in kwargs:
                setattr(self, "created_at", datetime.datetime.strptime
                        (kwargs["created_at"], "%Y-%m-%dT%H:%M:%S.%f"))

            if "updated_at" in kwargs:
                setattr(self, "updated_at", datetime.datetime.strptime
                        (kwargs["updated_at"], "%Y-%m-%dT%H:%M:%S.%f"))

        else:

            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()

    def __str__(self):
        return "[{}] ({}) {}".format(type(self).__name__, self.id,
                                     self.__dict__)

    def save(self):
        self.updated_at = datetime.now()

    def to_dict(self):
        result = self.__dict__.copy()
        result['__class__'] = type(self).__name__
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result
