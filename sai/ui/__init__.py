from flask import Blueprint

bp = Blueprint('sai-ui', __name__, template_folder='templates',
               static_folder='static', static_url_path='/%s/static' % __name__)

from views import *
