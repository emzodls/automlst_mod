
import os, routines, json
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash, Response
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template("front.html")

@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/results')
def results():
    return render_template("results.html")

@app.route('/analyze')
def analyze():
    return render_template("analyze.html")

@app.route('/upload', methods=['POST'])
def upload():
    filename = routines.getinfile()
    #    filename = routines.getNCBIgbk(request.form["ncbiacc1"])
    return json.dumps({"filename": filename})
@app.route('/results/example/report') # why won't just example work?
def example():
    return render_template("example.html")
@app.route('/analyze/step2')
def step2():
    return render_template("step2.html")

@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html',title="",errormsg=e)

