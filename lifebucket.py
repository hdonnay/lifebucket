#!/usr/bin/python
from kyotocabinet import *
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack, config
from flask.ext.wtf import Form, TextAreaField, TextField, validators, ValidationError
import json, re

class Config():
    DB = "bucket.kct"
    LENS_STOR = "lens.kch"
    DEBUG = True
    SECRET_KEY = 'development key'
    USERNAME = 'admin'
    PASSWORD = 'default'

class Insert(Form):
    value = TextAreaField('Value', validators=[validators.Required()])

#def lensCheck(message=None):
    #if message is None or re.match(_lens_pattern, message) is None:
        #return False
    #return True

def lensCheck(form, field):
    if re.match(_lens_pattern, field.data) is None:
        raise ValidationError(u'Must Match Lens Pattern.')

class View(Form):
    lens = TextField('Lens', validators=[validators.Required(), lensCheck])

# create our little application :)
app = Flask(__name__)
app.config.from_object('lifebucket.Config')
#app.config.from_envvar('LIFEBUCKET_CONFIG')

_lens_pattern = r'^\s*from\s+(.+)\s+to\s+(.+)\s+get\s+(.+)\s*$'
OK = u'success'
NO = u'failure'

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
        if post_lens()['status'] == OK:
            flash("Success")
        else:
            flash("Something was wrong")
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

@app.route('/api/lens', methods=("POST", "PUT"))
def post_lens():
    with app.app_context():
        lens=request.args.get('lens', None)
        (time_a, time_b, ret) = re.match(_lens_pattern, lens).group(1,2,3)
        db = get_lens()
        new_key=db.count()+1
        db.set(new_key, "{0};{1};{2}".format(time_a, time_b, ret))
        db.commit()
        return jsonify(status=OK, lens=new_key)
    return jsonify(status=NO)

if __name__ == '__main__':
    app.run()
