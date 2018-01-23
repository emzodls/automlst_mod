import os, tempfile, models, json, datetime, csv
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash, g
from flask_mail import Message
from redis import Redis
from redis import ConnectionError as redisConnectError
from app import app
from app import mail
from werkzeug.utils import secure_filename
from Bio import Entrez

def getdb():
    rddb = getattr(g,"_redisdb",False)
    if not rddb:
        rddb = g._redisdb = Redis.from_url('redis://localhost:6379/0')
    try:
        rddb.ping()
    except redisConnectError:
        rddb = False
    return rddb

def validatefile(fname, asfil=False):
    validgbkext = ['gbk','genbank','gbff','gb','embl']
    validfakext = ['fasta','fa','fna','faa','fas']
    ext = os.path.splitext(fname)[1]
    if not asfil and ext[1:].lower() in validgbkext+validfakext:
        return True
    elif asfil and ext[1:].lower() in validgbkext:
        return True
    return False

def getNCBIgbk(acc):
    try:
        #crude check for format
        if acc.upper().startswith("GCA_") or acc.upper().startswith("GCF_"):
            flash("Error, cannot use assembly accession number, please use Genbank or Refseq sequence accession")
            filename = False
        elif acc.replace("_","").replace(".","").isalnum() and len(acc) <= 20 and len(acc) >= 6:
            if "." in acc:
                acc = acc[:acc.index(".")]
            Entrez.email = "artsuser@ziemertlab.com"
            handle = Entrez.efetch(db="nucleotide", rettype="gbwithparts", id=acc, retmode="text")
            filename = os.path.join(tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER']), secure_filename(acc+".gbk"))
            with open(filename,"w") as outfile:
                outfile.write(handle.read())
        else:
            flash("Error with Accession number ")
            filename = False
    except Exception, e:
        flash("Error retrieving gbk from NCBI")
        filename = False
    return filename

def getinfile():
    ufile = False
    filename = ""
    # USe empty string for FALSE due to storage as string in redis
#    if 'asjobid' in request.form and request.form['asjobid']:
#        if getASstatus(request.form['asjobid']):
#            filename = getASgbk(request.form['asjobid'])
#            if not filename:
#                return False,""
#        else:
#            return False,""
    if 'ncbiacc1' in request.form and request.form['ncbiacc1'] and request.form.get("filesrc") == 'ncbi':
         filename = getNCBIgbk(request.form['ncbiacc1'])
         if not filename:
             return False
#    elif 'asseqfile' in request.files and validatefile(request.files['asseqfile'].filename,True):
#        ufile = request.files['asseqfile']
    elif 'seqfile1' in request.files and validatefile(request.files['seqfile1'].filename) and request.form.get("filesrc") == 'seqfile':
        ufile = request.files['seqfile1']
    if ufile:
        filename = os.path.join(tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER']), secure_filename(ufile.filename))
        ufile.save(filename)
    return filename

def addjob(**kwargs):
    rddb = getdb()
    automlstjob = models.automlstjob(**kwargs)
    if rddb:
        rddb.hmset("automlstjob:%s"%automlstjob.id, automlstjob.getdict())
        rddb.lpush("AMLSTSQ",automlstjob.id)
        # make a results directory?
    return automlstjob
def updatejob(jobid,newref):
    rddb = getdb()
    if rddb:
        redisid = "automlstjob:"+jobid
        rddb.hset(redisid,"reference",newref)

def getjobstatus(jobid):
    jobstatus = "Waiting in queue"
    mashstatus = ""
    checkpoint = ""
    percent = 0
    workflow = 0
    paramdict = {}
    if os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],jobid,'automlst.log')):
        with open(os.path.join(app.config['RESULTS_FOLDER'],jobid,'automlst.log'), 'r') as infile:
            for line in infile:
                if 'JOB_STATUS' in line:
                    statlist = line.strip().split('::')
                    jobstatus = statlist[1]
                elif 'JOB_PROGRESS' in line:
                    proglist = line.strip().split('::')
                    fraction = str(proglist[1]).split('/')
                    percent = 100 * (float(fraction[0]) / float(fraction[1]))
                elif 'MASH_STATUS' in line:
                    mashlist = line.strip().split('::')
                    mashstatus = mashlist[1]
                elif 'JOB_CHECKPOINT' in line:
                    checklist = line.strip().split('::')
                    checkpoint = checklist[1]
                elif 'WORKFLOW' in line:
                    workflowline = line.strip().split('::')
                    workflow= workflowline[1]
                elif 'JOB_PARAMS' in line:
                    paramlist = line.strip().split('::')
                    paramdict = json.loads(paramlist[1])
    jobstatdict = {"progress": percent,"status":jobstatus, "mash":mashstatus, "checkpoint": checkpoint, "workflow": workflow, "params":paramdict}
    return jobstatdict

def reanalyzejob(jobid):
    paramdict={}
    with open(os.path.join(app.config['RESULTS_FOLDER'],jobid,'automlst.log'),'r') as jobread:
        for line in jobread:
            if 'JOB_PARAMS' in line:
                paramlist = line.strip().split('::')
                paramdict = json.loads(paramlist[1])
    paramdict["skip"]=[]
    with open(os.path.join(app.config['RESULTS_FOLDER'],jobid,'automlst.log'),'a') as joblog:
        joblog.write('\n'+str(datetime.datetime.now())+' - INFO - JOB_REANALYZE::true \n'+str(datetime.datetime.now())+' - INFO - JOB_CHECKPOINT::W1-STEP2 \n'+str(datetime.datetime.now())+' - INFO - JOB_STATUS::Reanalyzing\n'+str(datetime.datetime.now())+' - INFO - JOB_PARAMS::'+json.dumps(paramdict)+'\n')

def jsontotsv(jsonpath,jobid):
    resultdict = {}
    with open(jsonpath, 'r') as jsondict:
        fulldict = json.load(jsondict)
        orglist = fulldict["orglist"]
        refdict = fulldict["reforgs"]
        for i in range(0,len(refdict)):
            currorg = refdict[i]
            distvals=currorg["dlist"]
            pvals=currorg["plist"]
            for j in range (0, len(orglist)):
                currquery = orglist[j]
                currd=""
                currp=""
                if not j >= len(pvals):
                    currp=pvals[j]
                if not j >= len(distvals):
                    currd=distvals[j]
                orgcomp = currorg["orgname"] + currquery
                if orgcomp not in resultdict:
                    resultdict[orgcomp] = ""
                resultdict[orgcomp] = {"orgname":currorg["orgname"], "strain":currorg["strain"], "id":currorg["id"], "queryname":currquery,"pval":currp, "dist":currd}
    with open(os.path.join(app.config['RESULTS_FOLDER'],jobid,'reftext.txt'),'wb') as csvfile:
        csvwriter = csv.writer(csvfile,delimiter="\t")
        for resultval in resultdict.values():
            csvwriter.writerow([resultval["orgname"],resultval["strain"],resultval["id"],resultval["queryname"],resultval["pval"],resultval["dist"]])

def sendnotifymail(msg="",jobid="",to=""):
    try:
        if not msg:
            msg = "Hello, your autoMLST job has been submitted! Your job id is: "
        assert to, jobid
        msgobj = Message("Your autoMLST Job (%s) has been submitted"%jobid,recipients=[to])
        msgobj.html = "%s %s <br> <a href='http://127.0.0.1:5000/results/%s'>http://127.0.0.1:5000/results/%s</a>"%(msg,jobid,jobid,jobid) #placeholder address while testing
        mail.send(msgobj)
    except Exception as e:
        print "Warning: Email not sent, check email configuration"
        print e