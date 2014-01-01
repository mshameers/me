from datetime import datetime

from app.api import InvalidUsage
from app.utils import slugify
from app.models import Comment


def validate_name(name):
    if len(name) < 1:
        message = (
            'Enter a valid name.'
        )
        raise InvalidUsage(message)


