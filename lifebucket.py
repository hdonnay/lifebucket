#!/usr/bin/python
import psycopg2
import psycopg2.extras
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack, config
from flask.ext.wtf import Form, TextField, TextAreaField, Required

class submit(Form):
        key = TextField('Key', validators=[Required()])
        value = TextAreaField('Value', validators=[Required()])

# create our little application :)
app = Flask(__name__)
app.config.from_object('lifebucket.config')
app.config.from_envvar('LIFEBUCKET_CONFIG')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'psql'):
        top.psql = psycopg2.connect(app.config['DSN'])
        psycopg2.extras.register_hstore(top.psql) # This is what forces psycopg2 to interface Dicts with hstores.
    return top.psql

def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

#@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'psql'):
        top.psql.close()

@app.route('/')
def index():
    if form.validate_on_submit():
        flash("Success")
        return redirect(url_for("index"))
    return render_template('index.html', form=submit())

@app.route('/out')
def output():
    pass

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/license')
def copyright():
    return render_template('copyright.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/api/post', methods=("POST", "PUT"))
def post():
    with app.app_context():
        db = get_db()
        db.cursor().execute("INSERT INTO data (time, kv) VALUES (%s, %s);", (datetime.utcnow(), request.args.to_dict()))
        db.commit()
        return jsonify(status='success')
    return jsonify(status='failure')

if __name__ == '__main__':
    app.run()
