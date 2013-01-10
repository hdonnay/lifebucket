#!/usr/bin/python
from kyotocabinet import *
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack, config
from flask.ext.wtf import Form, TextAreaField, TextField, validators, ValidationError
import json, re

app = Flask(__name__)
app.config.from_object('lifebucket.Config')
#app.config.from_envvar('LIFEBUCKET_CONFIG')

# "Constants"
_lens_pattern = r'^\s*from\s+(.+)\s+to\s+(.+)\s+get\s+(.+)\s*$'
OK = u'success'
NO = u'failure'

class Config():
    DB = "bucket.kct"
    LENS_STOR = "lens.kch"
    DEBUG = True
    SECRET_KEY = 'development key'
    USERNAME = 'admin'
    PASSWORD = 'default'

class Insert(Form):
    value = TextAreaField('Value', validators=[validators.Required()])

def lensCheck(form, field):
    if re.match(_lens_pattern, field.data) is None:
        raise ValidationError(u'Must Match Lens Pattern.')

def from_human_fmt(lens):
    comp = re.match(_lens_pattern, lens)
    (time_a, time_b, ret) = comp.group(1,2,3)
    return "{0};{1};{2}".format(time_a, time_b, ret)

def to_human_fmt(lens):
    (time_a, time_b, ret) = re.split(';', lens)
    return "from {0} to {1} get {3}".format(time_a, time_b, ret)

class View(Form):
    lens = TextField('Lens', validators=[validators.Required(), lensCheck])

class Lens(MethodView):
    def get(self, lens_id):
        with app.app_context():
            db = get_lens()
            if lens_id is None:
                return jsonify([ [ lens_id, to_human_fmt(db[lens_id]) ] for lens_id in db ])
            else:
                return jsonify([ lens_id, to_human_fmt(db[lens_id]) ])

    def post(self):
        with app.app_context():
            comp = re.match(_lens_pattern, request.args.get('lens', ''))
            if comp is not None:
                db = get_lens()
                new_key=db.count()+1
                db.set(new_key, from_human_fmt(request.args.get('lens', '')))
                db.commit()
                return jsonify(status=OK, lens=new_key)
            else:
                return jsonify(status=NO)

    def delete(self, lens_id):
        with app.app_context():
            db = get_lens()
            if db.remove(lens_id):
                return jsonify(status=OK)
            else:
                return jsonify(status=NO, error="No such lens_id")

    def put(self, lens_id):
        with app.app_context():
            db = get_lens()
            if db.replace(lens_id, from_human_fmt(request.args.get('lens', '')):
                return jsonify(status=OK)
            else:
                return jsonify(status=NO, error="No such lens_id")

# steal some flask docs code
lens_view = Lens.as_view('lens_api')
app.add_url_rule('/lens/', defaults={'lend_id': None}, view_func=lens_view, methods=['GET',])
app.add_url_rule('/lens/', view_func=lens_view, methods=['POST',])
app.add_url_rule('/lens/<int:lens_id>', view_func=lens_view, methods=['GET', 'PUT', 'DELETE'])


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = DB()
        top.db.open(app.config['DB'], DB.OWRITER | DB.OCREATE)
    return top.db

def get_lens():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'lens'):
        top.lens = DB()
        top.lens.open(app.config['LENS_STOR'], DB.OWRITER | DB.OCREATE)
    return top.lens

@app.route('/')
def index():
    form = Insert()
    if form.validate_on_submit():
        flash("Success")
        return redirect(url_for("index"))
    return render_template('index.html', form=form)

@app.route('/out')
def output():
    form = View()
    if form.validate_on_submit():
        flash("Success")
        return redirect(url_for("output"))
    return render_template('out.html', form=form)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/license')
def copyright():
    return render_template('copyright.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/api/value', methods=("POST", "PUT"))
def post_value():
    with app.app_context():
        db = get_db()
        db.set(datetime.utcnow(), json.dumps(request.args.to_dict()['value']))
        db.commit()
        return jsonify(status=OK)
    return jsonify(status=NO)

if __name__ == '__main__':
    app.run()
