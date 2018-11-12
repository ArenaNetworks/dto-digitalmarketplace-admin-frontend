from flask import Blueprint


main = Blueprint('main', __name__)

from .views import (  # noqa
    login,
    agreements,
    case_study,
    communications,
    service_updates,
    services,
    suppliers,
    stats,
    users,
    buyers,
    applications,
    assessments,
    zendesk)
from app.main import errors  # noqa
