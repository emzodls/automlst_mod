import os, tempfile
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash
from app import app
from werkzeug.utils import secure_filename
from Bio import Entrez

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
            handle = Entrez.efetch(db="nucleotide", rettype="gb", id=acc, retmode="text")
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
    if 'ncbiacc1' in request.form and request.form['ncbiacc1']:
         filename = getNCBIgbk(request.form['ncbiacc1'])
         if not filename:
             return False,""
#    elif 'asseqfile' in request.files and validatefile(request.files['asseqfile'].filename,True):
#        ufile = request.files['asseqfile']
    elif 'seqfile1' in request.files and validatefile(request.files['seqfile1'].filename):
        ufile = request.files['seqfile1']
    if ufile:
        filename = os.path.join(tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER']), secure_filename(ufile.filename))
        ufile.save(filename)
    return filename