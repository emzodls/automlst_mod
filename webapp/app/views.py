
import os
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template("front.html")

@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html',title="",errormsg=e)

