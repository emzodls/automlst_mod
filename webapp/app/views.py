
import os, routines, json, uuid
from flask import render_template, jsonify, request, redirect, abort, make_response, send_from_directory, flash, Response, url_for
from Bio import Phylo
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

@app.route('/results/getreport', methods=['POST'])
def getreport():
    jobid = request.form.get("jobid")
    return redirect("/results/"+jobid+"/loading")

@app.route('/results/<jobid>')
@app.route('/results/<jobid>/')
def showresults(jobid):
    #return render_template("startjob.html",jobid=jobid)
    return redirect("/results/"+jobid+"/loading")

@app.route('/results/<jobid>/<step>', methods=['GET'])
@app.route('/results/<jobid>/<step>/', methods = ['GET'])
def showstep(jobid,step):
    jobinfo = routines.getjobstatus(jobid)
    paramdict = jobinfo.get("params")
    laststep = request.args.get('laststep','NONE')
    if step == "loading":
        if jobinfo["workflow"] == "1" or jobinfo["workflow"] == 0:
            if laststep == "step2" or laststep == "step3":
                return render_template("startjob.html", jobid=jobid, laststep=laststep)
            else:
                return render_template("startjob.html", jobid=jobid)
        else:
            return render_template("startjob2.html", jobid=jobid)
    elif step == "step2":
        return render_template("step2.html",jobid=jobid)
    elif step == "step3":
        return render_template("step3.html",jobid=jobid)
    elif step == "report":
        if jobinfo["workflow"] == "1":
            return render_template("report.html",jobid=jobid)
        else:
            return render_template("report.html",jobid=jobid,workflow=2)

@app.route('/results/<jobid>/reanalyze')
def reanalyze(jobid):
    routines.reanalyzejob(jobid)
    return render_template("step2.html", jobid=jobid)

@app.route('/results/<jobid>/tree', methods=['GET'])
def getTree(jobid):
    format = request.args.get('format','newick')
    resultdir = app.config['RESULTS_FOLDER']
    resulttree = 'StrepTreePruned3'
    print os.path.join(resultdir,resulttree+'.tree')
#    return '((((((((((((((((Streptomyces_sp_Root63:1.0000005E-6,Streptomyces_sp_Root1295:1.0000005E-6):0.0010404334,Streptomyces_anulatus:0.0010271309)100:1.3125094E-4,Streptomyces_sp_TSRI0395:8.425702E-4)36:1.4630829E-4,Streptomyces_europaeiscabiei:9.0665516E-4)42:0.0014606614,Streptomyces_sp_CB02115:0.004353011)100:0.0010675892,(Streptomyces_sp_W007:0.001798555,Streptomyces_sp_CB00072:0.0019330874)100:0.0045658997)94:9.0673397E-4,Streptomyces_sp_EN16:0.004080439)37:0.0013217309,Streptomyces_sp_CNB091:0.019331152)79:0.00429321,Streptomyces_sp_TSRI0261:0.004378711)62:0.003816965,(Streptomyces_sp_CS057:0.0020215332,Streptomyces_sp_MNU77:9.220031E-4)100:0.0060798563)61:0.007494472,((((Streptomyces_griseus_subsp_griseus_NBRC_13350:1.0000005E-6,Streptomyces_griseus:1.0000005E-6)41:1.0000005E-6,Streptomyces_griseus_subsp_griseus:1.0000005E-6)100:0.0014704484,Streptomyces_sp_ACT-1:9.5029053E-4)37:1.108671E-4,(Streptomyces_sp_MnatMP-M77:0.001086292,Streptomyces_sp_OspMP-M43:6.825195E-4)89:3.6729485E-4)100:0.015549392)100:0.0070974077,((Streptomyces_fimicarius:0.0011986006,Streptomyces_baarnensis:7.536904E-4)84:6.4435485E-4,Streptomyces_albus_subsp_albus:8.5986604E-4)100:0.01534833)100:0.002660125,((((((((((Streptomyces_californicus:1.0000005E-6,Streptomyces_brasiliensis:1.0000005E-6)35:1.0000005E-6,Streptomyces_purpeochromogenes:1.0000005E-6)100:7.2541845E-4,Streptomyces_sp_NRRL_F-5702:6.8800553E-4)60:2.0678385E-4,(Streptomyces_sp_NRRL_F-3218:1.0000005E-6,Streptomyces_sp_NRRL_F-3273:1.0000005E-6)100:8.900187E-4)100:4.329408E-4,Streptomyces_sp_LaPpAH-199:0.0013901303)75:2.7135492E-4,((((Streptomyces_sp_NRRL_F-2202:4.4074358E-4,Streptomyces_sp_NRRL_F-5681:5.518033E-4)100:6.8577705E-4,Streptomyces_sp_MMG1522:8.5312093E-4)70:2.840975E-4,Streptomyces_sp_NRRL_F-2295:0.001358286)36:1.4110212E-4,((Streptomyces_sp_NRRL_WC-3540:1.0000005E-6,Streptomyces_griseus_subsp_rhodochrous:1.0000005E-6)100:9.821998E-4,Streptomyces_violaceoruber:0.0011795601)62:2.3595421E-4)77:3.4878938E-4)54:1.803457E-4,(Streptomyces_floridae:0.001394433,Streptomyces_puniceus:0.0012018218)99:5.7107257E-4)90:4.94688E-4,(Streptomyces_vinaceus:0.0019849236,Streptomyces_sp_NRRL_B-1381:0.002080245)96:5.0301646E-4)100:0.015310345,Streptomyces_sp_CB02366:0.021892518)100:0.015160611,((((((((Streptomyces_roseosporus_NRRL_11379:1.0000005E-6,Streptomyces_sp_HCCB10043:1.0000005E-6)100:1.0000005E-6,Streptomyces_roseosporus_NRRL_15998:2.5405182E-4)100:0.005959932,Streptomyces_sp_Tue_6075:0.006768982)99:0.0019647044,(((Streptomyces_sp_CNS654:0.0034277556,Streptomyces_sp_Cmuel-A718b:0.0030689505)100:0.0014011568,Streptomyces_sp_PgraA7:0.0049047144)100:0.0019892184,Streptomyces_sp_Ncost-T6T-1:0.004764495)100:0.0019293395)100:0.003502295,(Streptomyces_sp_EN27:9.883776E-4,Streptomyces_sp_EN23:0.0010339423)100:0.011438335)99:0.0018742762,Streptomyces_sp_NBRC_110465:0.020332504)92:0.0011570564,Streptomyces_sp_PTY087I2:0.011000732)97:0.001828397,((((Streptomyces_tue_2401:5.1773916E-4,Streptomyces_mediolani:4.5088946E-4)99:3.3963102E-4,(Streptomyces_albovinaceus:5.398786E-4,Streptomyces_sp_TSRI0445:6.737508E-4)98:2.8017364E-4)100:0.008255567,((Streptomyces_globisporus_C-1027:3.9139084E-4,Streptomyces_sp_CB02130:5.0020445E-4)100:0.005455389,(Streptomyces_sp_JS01:0.0023294243,Streptomyces_sp_SS07:0.002592743)100:0.0049200286)100:0.0018261857)100:0.0031373154,Streptomyces_globisporus_subsp_globisporus:0.011533041)47:0.0012343931)100:0.0098615745)98:0.003334482)92:0.024976358,(((((Streptomyces_sp_NRRL_S-623:5.948444E-4,Streptomyces_sp_2R:9.268726E-4)97:4.272725E-4,Streptomyces_luridiscabiei:9.4389287E-4)100:0.004199813,(Streptomyces_alboviridis:0.0030244857,Streptomyces_fulvissimus_DSM_40593:0.001972087)100:0.0060538976)100:0.015499358,(((Streptomyces_sp_IB2014_011-1:0.0010446986,Streptomyces_cyaneofuscatus:6.7918043E-4)100:0.0052980967,Streptomyces_sp_ScaeMP-e10:0.009781817)100:0.0051066126,Streptomyces_sp_CB00316:0.014230845)98:0.003769864)75:0.003152554,Streptomyces_sp_ScaeMP-e83:0.017625038)100:0.0065441434)100:0.0074298084,(((Streptomyces_sp_CFMR_7:0.0022353106,Streptomyces_sp_DvalAA-19:0.0026482788)100:0.003941427,Streptomyces_nanshensis:0.005571169)100:0.0036120422,((Streptomyces_sp_S8:0.0022545303,Streptomyces_sp_SolWspMP-sol2th:0.0012293566)100:0.003566094,Streptomyces_sp_CcalMP-8W:0.004314778)100:0.0051145055)100:0.015895171)100:8.7407016E-4,Kitasatospora_albolonga:0.016607333);'
    if os.path.exists(os.path.join(resultdir,resulttree+'.tree')):
        if format == 'newick':
            return send_from_directory(resultdir,resulttree+'.tree',as_attachment=True)

        # elif format == 'nexml':
        #     Phylo.convert(os.path.join(resultdir,resulttree+'.tree'),'newick', os.path.join(resultdir,resulttree+'_nexml.xml'),'nexml')
        #     return send_from_directory(resultdir,resulttree+'_nexml.xml',as_attachment=True)
        # elif format == 'phyloxml':
        #     Phylo.convert(os.path.join(resultdir,resulttree +'.tree'), 'newick', os.path.join(resultdir,resulttree +'_phyloxml.xml'), 'phyloxml')
        #     return send_from_directory(resultdir, resulttree + '_phyloxml.xml', as_attachment=True)
    else:
        return "false"
#@app.route('/results2/<jobid>/<step>')
#@app.route('/results2/<jobid>/<step>/')
#def show2(jobid,step):
#    if step == "loading":
#        return render_template("startjob2.html", jobid=jobid)
#    elif step == "report":
#        return render_template("report.html",jobid=jobid,workflow=2)

@app.route('/results/<jobid>/downloadorgs', methods=['GET'])
def downloadorgs(jobid):
    format = request.args.get('format','json')
    resultdir = app.config['RESULTS_FOLDER']
    if format == 'json':
        return send_from_directory(resultdir,'reflist_full.json',as_attachment=True)
    elif format == 'txt':
        if os.path.exists(os.path.join(resultdir,'reftext.txt')):
            return send_from_directory(resultdir,'reftext.txt',as_attachment=True)
        else:
            jsonpath = os.path.join(resultdir,'reflist_full.json')
            routines.jsontotsv(jsonpath)
            return send_from_directory(resultdir,'reftext.txt',as_attachment=True)

@app.route('/results2/<jobid>/refs')
def getrefs(jobid):
    if os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],'genuslist_example2.json')):
        return send_from_directory(app.config['RESULTS_FOLDER'],'genuslist_example2.json')
@app.route('/results2/selectgenus', methods=['POST'])
def selectgenus():
    jobid = request.form.get("jobinfo")
    newref = request.form.get("genusoptions")
    routines.updatejob(jobid,newref)
    genusdict={}
    with open(os.path.join(app.config['RESULTS_FOLDER'],'genuslist_example2.json'),'r') as genusfile:
        genusdict = json.load(genusfile)
        genusdict["genuslist"] = {newref:genusdict["genuslist"][newref]}
        genusdict["maxgenus"] = newref
    with open(os.path.join(app.config['RESULTS_FOLDER'],'genuslist_example2.json'),'w') as fileout:
        json.dump(genusdict,fileout,indent=2)
    return json.dumps({"status":1,"newmax":newref})

@app.route('/results2/refgenus')
def refgenus():
    if os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],'acceleratedrefs.json')):
        return send_from_directory(app.config['RESULTS_FOLDER'],'acceleratedrefs.json')
    else:
        return jsonify([])

@app.route('/analyze')
def analyze():
    return render_template("analyze.html")

@app.route('/upload', methods=['POST'])
def upload():
    filename = routines.getinfile()
    name = os.path.split(filename)[-1]
    #    filename = routines.getNCBIgbk(request.form["ncbiacc1"])
    return json.dumps({"filename": filename,"name": name})
@app.route('/startjob', methods=['POST'])
def startjob():
    jobid = unicode(uuid.uuid4())
    jobdict = {"jobid": jobid, "workflow": request.form.get("workflow"), "genomes": request.form.getlist('upfiles'),
              "reference": request.form.get('genusselect','NA')}
    os.mkdir(os.path.join(app.config['RESULTS_FOLDER'],jobid))
    if request.form.get("workflow") == "1":
        print jobid
        automlstjob = routines.addjob(id=jobid,workflow=request.form.get("workflow"),genomes=request.form.getlist('upfiles'),reference=request.form.get('genusselect','NA'),skip=request.form.get('skip2',"")+","+request.form.get('skip3',""),bootstr=request.form.get('boots',0))
        #with open(os.path.join(app.config['RESULTS_FOLDER'],'examplein.json'),'w') as uploadfile:
        #    json.dump(jobdict,uploadfile)
        return redirect('/results/'+jobid)
    elif request.form.get("workflow") == "2":
        print jobid
        automlstjob = routines.addjob(id=jobid, workflow=request.form.get("workflow"),
                                      genomes=request.form.getlist('upfiles'),
                                      reference=request.form.get('genusselect', 'NA'),skip=request.form.get('skip2',"")+","+request.form.get('skip3',""),bootstr=request.form.get('boots',0))
        return redirect('/results/' + jobid + '/loading')
    else:
        flash('Invalid workflow')
        return redirect('/analyze')

@app.route('/results/<jobid>/step2/orgs', methods=['GET'])
def getOrgs(jobid):
    orgstart = int(request.args.get('start',0))
    if os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],'userlist.json')):
        with open(os.path.join(app.config['RESULTS_FOLDER'],'reflist_full.json'),'r') as reffile, open(os.path.join(app.config['RESULTS_FOLDER'],'userlist.json'),'r') as userfile:
            refdict = json.load(reffile)
            userdict = json.load(userfile)
            tempdict = [ref for ref in refdict["reforgs"] if ref["id"] in userdict["selspecies"] and not ref in refdict["reforgs"][0:(orgstart+500)]]
            refdict["reforgs"] = refdict["reforgs"][orgstart:(orgstart + 500)]
            refdict["outgroups"] = [rec for rec in refdict["outgroups"] if
                                    str(rec["phylid"]) != "N/A" and str(rec["familyid"]) != "N/A" and str(
                                        rec["orderid"]) != "N/A" and str(rec["genusid"]) != "N/A"]

            refdict["reforgs"].extend(tempdict)
            refdict.update(userdict)
            return jsonify(refdict)
    elif os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],'reflist_full.json')):
        with open(os.path.join(app.config['RESULTS_FOLDER'],'reflist_full.json'),'r') as firstref:
            refdict = json.load(firstref)
            refdict["reforgs"] = refdict["reforgs"][orgstart:(orgstart+500)]
            refdict["outgroups"] = [rec for rec in refdict["outgroups"] if str(rec["phylid"]) != "N/A" and str(rec["familyid"]) != "N/A" and str(rec["orderid"]) != "N/A" and str(rec["genusid"]) != "N/A"]
            return jsonify(refdict)


@app.route('/results/<jobid>/step2/orgin', methods=['POST'])
def orgin(jobid):
    species = request.form.getlist('specieslist')
    outgroups = request.form.getlist('outgrlist')
    jobid = request.form.get('jobinfo')
    with open(os.path.join(app.config['RESULTS_FOLDER'],'userlist.json'),'w') as userfile:
        json.dump({"selspecies":species, "seloutgroups":outgroups},userfile)
    return redirect('/results/'+jobid+'/loading?laststep=step2') # when is checkpoint set? Might get user stuck in a loop of submitting/getting redirected

@app.route('/results/<jobid>/step2/outgroups', methods=['GET'])
def outgrs(jobid):
    ingroups=[]
    commongr = request.args.get('group', False)
    multigroups = request.args.get('multiple', False)
    print multigroups
    if multigroups:
        commonid = (request.args.get('id',False)).split(',')
        ingroups = commonid
        print ingroups
    else:
        commonid = request.args.get('id', False)
        ingroups.append(str(commonid))
    outgrlimit = request.args.get('limit',1000)
    startindex = request.args.get('start',0)
    if commongr and commonid:
        with open(os.path.join(app.config['RESULTS_FOLDER'],'reflist_full.json'),'r') as outrefs:
            outdict = json.load(outrefs)
            refrec = outdict['reforgs']
            newlist = [rec for rec in refrec if str(rec[commongr+"id"]) not in ingroups and str(rec[commongr+"id"]) != "N/A" and not rec in refrec[0:(startindex+500)]]
            return jsonify(newlist[0:500])
    return send_from_directory(app.config['RESULTS_FOLDER'],'outgroups.json')

@app.route('/results/<jobid>/step3/genes')
def getgenes(jobid):
    if os.path.exists(os.path.join(app.config['RESULTS_FOLDER'],'mlstpriority.json')):
        return send_from_directory(app.config['RESULTS_FOLDER'], 'mlstpriority.json')

@app.route('/results/<jobid>/step3/genein', methods=['POST'])
def genein(jobid):
    jobid = request.form.get('jobinfo')
    genes = request.form.getlist('mlstlist')
    radioval = request.form.get('optradio')
    rmorgs = request.form.get('removeorgs')
    with open(os.path.join(app.config['RESULTS_FOLDER'],'usergenes.json'),'w') as usergenes:
        json.dump({"genes":genes,"mode":radioval,"remove":rmorgs.split(",")},usergenes)
    return redirect('/results/'+jobid+'/loading?laststep=step3')

@app.route('/jobstatus/<jobid>')
@app.route('/jobstatus/<jobid>/')
def status(jobid):
    jobstat = routines.getjobstatus(jobid)
    workflow = jobstat["workflow"]
    paramdict = jobstat.get("params")
    skips = paramdict.get("skip",[])
    if jobstat["checkpoint"].upper() == "W1-2" and "skip2" not in skips and workflow == "1":
        #redirdict = {"redirect":"step2"}
        #return jsonify(redirdict)
        jobstat["redirect"] = "step2"
        return jsonify(jobstat)
    elif jobstat["checkpoint"].upper() == "W1-2" and "skip2" in skips and workflow == "1":
        jobstat["skip"] = "c1"
        return jsonify(jobstat)
    elif jobstat["checkpoint"].upper() == "W1-3" and "skip3" not in skips and workflow == "1":
        #redirdict = {"redirect":"step3"}
        #return jsonify(redirdict)
        jobstat["redirect"] = "step3"
        return jsonify(jobstat)
    elif jobstat["checkpoint"].upper() == "W1-3" and "skip3" in skips and workflow == "1":
        jobstat["skip"] = "c2"
        return jsonify(jobstat)
    elif jobstat["checkpoint"].upper() == "W1-R" and workflow == "1":
        #redirdict = {"redirect":"report"}
        #return jsonify(redirdict)
        jobstat["redirect"] = "report"
        return jsonify(jobstat)
    else:
        return jsonify(jobstat)


@app.route('/results/example/report')
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

