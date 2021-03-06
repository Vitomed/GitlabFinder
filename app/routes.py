from flask import jsonify, render_template, request, redirect, url_for
from gitlab.exceptions import GitlabAuthenticationError, GitlabSearchError

from app import app, db, gl
from app.worker import Worker


@app.route('/', methods=["GET"])
def base():
    data = request.args.get('data', '')
    return render_template('base.html', data=data), 200


@app.route('/search/', methods=['POST', 'GET'])
def search_project():
    if request.method == 'POST':
        row = request.form.get('row')
        return redirect(url_for('send_name', search=row)), 301
    return render_template('form.html'), 200


@app.route('/send/')
def send_name():
    row = request.args.get('search', '')
    if row:
        try:
            response = gl.search('projects', row)
        except GitlabSearchError as exp:
            raise GitlabSearchError("Проблемы при обращении к API Gitlab:", exp)
        except GitlabAuthenticationError:
            return "<h1>Истек период действия ключа!</h1>"
        res = Worker.send(response)
        return redirect(url_for('base', data=res)), 301
    return redirect(url_for('base', data="You send empty row!")), 301


@app.route('/projects/', methods=["GET"])
def get_porjects():
    response = Worker.view_projects()
    return jsonify(response), 200


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
