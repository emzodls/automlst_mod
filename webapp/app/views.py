
import os
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash
from app import app
from app import routines

@app.route('/')
@app.route('/index')
def index():
    return render_template("front.html")

@app.route('/results/<jobid>/trees/<tree>')
def gettreepng(jobid,tree,qorg=None):
    rd = os.path.join(app.config["RESULTS_FOLDER"],jobid)
    treedir = os.path.join(rd,"trees")
    fname = [x for x in os.listdir(treedir) if (tree.lower()+".tree")==x.lower()]
    if len(fname):
        fname = fname[0]
    else:
        fname = False
    qorg = routines.getqorg(rd)

    if fname and os.path.exists(os.path.join(treedir,fname)):
        if os.path.exists(os.path.join(treedir,fname+".png")):
            return send_from_directory(treedir,fname+".png",mimetype='image/png')
        elif routines.rendertree(os.path.join(treedir,fname),800,qorg):
            return send_from_directory(treedir,fname+".png",mimetype='image/png')
    return app.send_static_file("images/blank.png")

@app.route('/static/exampleinputs/<fname>')
def sendexampleinputs(fname):
    return app.send_static_file(os.path.join("exampleinputs",fname))

@app.route('/analyze/')
@app.route('/analyze')
def analyze():
    return render_template("analyze.html")

@app.route('/results/')
@app.route('/results')
def results():
    lastresult = routines.getlastresults()
    return render_template("results.html",recentresults=lastresult)

@app.route('/serverstatus')
def serverstatus():
    status = routines.getservstats()
    return jsonify(status)

@app.route('/results/<jobid>')
@app.route('/results/<jobid>/')
def gotoreport(jobid):
    return redirect("/results/%s/report"%jobid)

@app.route('/results/<jobid>/report')
def showresult(jobid):
    if jobid and routines.checkresult(jobid):
        # resp = make_response(render_template("showresult.html",resid=jobid))
        # saverun = request.form.get('saverun',False)
        # if saverun and saverun.lower() != "false":
        #     lastresult = request.cookies.get('arts.lastresult')
        #     if lastresult and jobid not in lastresult:
        #         lastresult += ";%s"%jobid
        #     elif not lastresult:
        #         lastresult = jobid
        #     resp.set_cookie('arts.lastresult',lastresult)
        # return resp
        return render_template("showresult.html",resid=jobid)
    return abort(404)

@app.route('/results/<jobid>/tables/<path:path>')
def gettables(jobid,path):
    rd = os.path.join(app.config["RESULTS_FOLDER"],jobid,"tables")
    if os.path.exists(os.path.join(rd,path)):
        return send_from_directory(rd,path)
    return abort(404)

@app.route('/results/<jobid>/xlfile')
def getxlfile(jobid):
    if jobid and routines.checkresult(jobid):
        tpath = os.path.join(app.config["RESULTS_FOLDER"],jobid,"tables")
        xlfile = routines.makexltable(tpath)
        if xlfile:
            return send_from_directory(tpath,xlfile)
        return abort(404)

@app.route('/results/<jobid>/status')
def jobstatus(jobid):
    if jobid and routines.checkresult(jobid):
        #rd = os.path.join(app.config["RESULTS_FOLDER"],jobid)
        # statuscache = os.path.join(rd,"jobstatus.json")
        # if not os.path.exists(statuscache) or os.path.getmtime(statuscache) < os.path.getmtime(os.path.join(rd,"arts-query.log")):
        status = routines.getjobstatus(jobid)
        return jsonify(status)
        # else:
        #     return send_from_directory(rd,"jobstatus.json")
    return jsonify({"data":[]})

@app.route('/results/<jobid>/antismash')
@app.route('/results/<jobid>/antismash/')
def gotoantismashfiles(jobid):
    return redirect("/results/%s/antismash/index.html"%jobid)

@app.route('/results/<jobid>/antismash/<path:path>')
def getantismash(jobid,path):
    rd = os.path.join(app.config["RESULTS_FOLDER"],jobid,"antismash")
    if os.path.exists(os.path.join(rd,path)):
        return send_from_directory(rd,path)
    return abort(404)

@app.route('/results/<jobid>/log')
def joblog(jobid):
    rd = os.path.join(app.config["RESULTS_FOLDER"],jobid)
    if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,"arts-query.log")):
        return send_from_directory(rd,"arts-query.log",mimetype="text/plain")
    return "No log found"

@app.route('/results/<jobid>/export/<expfil>')
def exportfile(jobid,expfil):
    rd = os.path.join(app.config["RESULTS_FOLDER"],jobid)
    if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,expfil)):
        return send_from_directory(rd,expfil)
    return abort(404)

# @app.route('/results/<jobid>/<action>')
# def api_action(jobid,action):
#     return redirect("/api/job/%s/%s"%(jobid,action))

# @app.route('/results/<jobid>/krtab')
# def krtab(jobid):
#     rd = os.path.join(app.config['RESULTS_FOLDER'],jobid)
#     if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,"knownhits.json")):
#         return send_from_directory(rd,"knownhits.json")
#     else:
#         return jsonify({"data":[]})
#
# @app.route('/results/<jobid>/dupmatrix')
# def dupmatrix(jobid):
#     rd = os.path.join(app.config['RESULTS_FOLDER'],jobid)
#     if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,"resultsummary.json")):
#         return jsonify(routines.getdupmatrix(rd))
#     else:
#         return jsonify({"data":[]})
#
# @app.route('/results/<jobid>/bgctable')
# def bgctable(jobid):
#     rd = os.path.join(app.config['RESULTS_FOLDER'],jobid)
#     if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,"resultsummary.json")):
#         return jsonify(routines.getbgctable(rd))
#     else:
#         return jsonify({"data":[]})
#
# @app.route('/results/<jobid>/summarytab')
# def summarytab(jobid):
#     rd = os.path.join(app.config["RESULTS_FOLDER"],jobid)
#     if jobid and routines.checkresult(jobid) and os.path.exists(os.path.join(rd,"arts-query.log")):
#         st = routines.formatsumtab(jobid)
#         return jsonify(st)
#     return jsonify({"data":[]})

@app.route('/download')
def download():
    return render_template("download.html")

@app.route('/example')
def example():
    return redirect("/results/example/report")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/startjob', methods=['GET', 'POST'])
def startjob():
    if request.method == 'POST':
        filename,asrun = routines.getinfile()
        custmdl = routines.getcustmdl("custhmm")
        custcoremdl = routines.getcustmdl("custcorehmm")
        options = routines.getoptions()
        searchmode = request.form.get("searchmode","")
        if filename:
            if custmdl and custmdl=="Failed":
                redirect("/analyze")
            if custcoremdl and custcoremdl=="Failed":
                redirect("/analyze")
            artsjob = routines.addjob(infile=filename,ref=request.form.get("refset","auto"),asrun=asrun,custmdl=custmdl,custcoremdl=custcoremdl,options=options,cut=searchmode)

            resp = make_response(redirect("/results/%s/report"%artsjob.id))
            saverun = request.form.get('saverun',False)
            if saverun and saverun.lower() != "false":
                lastresult = request.cookies.get('arts.lastresult')
                if lastresult and artsjob.id not in lastresult:
                    lastresult += ";%s"%artsjob.id
                else:
                    lastresult = artsjob.id
                resp.set_cookie('arts.lastresult',lastresult)
            email = request.form.get('email',False)
            if email:
                routines.sendnotifymail(to=email,jobid=artsjob.id)

            return resp

            # return redirect("/results/%s"%artsjob.id)
        elif asrun == "invalid":
            flash("No such Antismash job found, please check Antismash id and try again")
            return redirect("/analyze")
        elif asrun == "pending":
            flash("Antismash run: %s is pending, please try again when results are available"%request.form.get("asjobid",""))
            return redirect("/analyze")
        else:
            flash("Error getting sequence file, please ensure file is in correct format and try again")
            return redirect("/analyze")
    else:
        flash("Please fill in required fields to start a job")
    return redirect("/analyze")

@app.errorhandler(404)
@app.errorhandler(401)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html',title="",errormsg=e)

