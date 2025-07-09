from flask import Blueprint, render_template

ia_bp = Blueprint('ia', __name__)

@ia_bp.route('/asignacion')
def asignacion():
    return render_template('public/ia/asignacion.html')

@ia_bp.route('/evaluacion')
def evaluacion():
    return render_template('public/ia/evaluacion.html')

@ia_bp.route('/rotacion')
def rotacion():
    return render_template('public/ia/rotacion.html')
