import sai

from flask import current_app, render_template, g, session, redirect, url_for
from flask import flash, request, jsonify, abort
from sai.ui import bp


@bp.route('/')
def index():
    return render_template('index.html')
