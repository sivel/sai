import os
import logging

from flask import Flask, abort, g

from config import config
from api_v1 import bp as api_v1_bp
from ui import bp as ui_bp

app = Flask(__name__)
app.config.from_object(config)

app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
app.register_blueprint(ui_bp, url_path='/')


@app.before_first_request
def set_root_path():
    root_path = app.config.get('root_path')
    if not root_path:
        root_path = os.path.dirname(app.root_path)
        app.config['root_path'] = root_path

    playbooks_path = app.config.get('playbooks_path')
    if not playbooks_path:
        playbooks_path = os.path.join(root_path, 'playbooks')
        app.config['playbooks_path'] = playbooks_path


@app.before_first_request
def logger():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.exception(e)
    return abort(500)
