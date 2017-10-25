
import os, routines, json, uuid
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash, Response, url_for
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

@app.route('/results/<jobid>')
@app.route('/results/<jobid>/')
def showresults(jobid):
    return render_template("startjob.html",jobid=jobid)

@app.route('/results/<jobid>/<step>')
@app.route('/results/<jobid>/<step>/')
def showstep(jobid,step):
    if step == "step1":
        return render_template("startjob.html",jobid=jobid)
    elif step == "step2":
        return render_template("step2.html",jobid=jobid)
    elif step == "step3":
        return render_template("step3.html",jobid=jobid)
    elif step == "report":
        return render_template("report.html",jobid=jobid)


@app.route('/analyze')
def analyze():
    return render_template("analyze.html")

@app.route('/upload', methods=['POST'])
def upload():
    filename = routines.getinfile()
    name = os.path.split(filename)[-1]
    #    filename = routines.getNCBIgbk(request.form["ncbiacc1"])
    return json.dumps({"filename": filename,"name": name})
@app.route('/startjob')
def startjob():
    jobid = unicode(uuid.uuid4())
    return redirect('/results/'+jobid)
# step 1! change rest of them...

@app.route('/results/example/report') # why won't just example work?
def example():
    return render_template("example.html")

#@app.route('/analyze/step2')
#def step2():
#    return render_template("step3.html")

@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html',title="",errormsg=e)

