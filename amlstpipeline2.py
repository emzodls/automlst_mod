#!/usr/bin/env python
import os, json, argparse, setlog, parsegenomes, mash
import copyseqsql, makeseqsql, glob, seqsql2fa, subprocess
import makehmmsql, getmlstgenes, getgenematrix, getgenes

def startwf2(indir,resultdir,checkpoint=False,genus="auto"):
    """WORKFLOW 1: Get all query genomes and identify reference tree to add sequences to"""
    pass

def hmmsearch(outname,hmmdb,infile,mcpu=1,cut="tc"):
    log.info("Searching sequences against hmmdb: %s"%hmmdb)
    cmd=["hmmsearch", "--domtblout", outname, "--noali", "--notextw", hmmdb, infile]
    if mcpu>1:
        cmd[1:1] = ["--cpu", str(mcpu)]
    if cut and cut.lower() in ("ga","tc","nc"):
        cmd[1:1] = ["--cut_%s"%cut.lower()]
    with open(os.devnull,"w") as devnull:
        subprocess.call(cmd, stdout=devnull, stderr=devnull)

def buildseqdb(selorgs,queryseqs,resultdir,sourcedb):
    #Get list of all selected and outgroups
    reflist = selorgs.get("selspecies",[])
    reflist.extend(selorgs.get("seloutgroups",[]))

    #Copy from reference database to query database
    seqsdb = os.path.join(resultdir,"seqs.db")
    copyseqsql.copydb(queryseqs,sourcedb,seqsdb)

def getorgs(resultdir,mashresult,skip="",IGlimit=50,OGlimit=5):
    #Get user selection if exists
    usersel = os.path.join(resultdir,"userlist.json")
    if os.path.exists(usersel):
        with open(usersel,"r") as fil:
            usersel = json.load(fil)
    else:
        usersel = False

    if "skip2" in skip:
        selection = {"selspecies":[x.get("id","") for x in mashresult.get("reforgs",[])][:IGlimit],
                     "seloutgroups":[x.get("id","") for x in mashresult.get("outgroups",[])][:OGlimit]}
        with open(os.path.join(resultdir,"userlist.json"),"w") as fil:
            json.dump(selection,fil)
        return selection
    elif usersel:
        return usersel
    else:
        return False

def startwf1(indir,resultdir,checkpoint=False,mashmxdist=0.5,cpu=1,skip="",refdb="",hmmdb="",rnadb=""):
    """WORKFLOW 2: Build phylogeny from scratch"""
    if not checkpoint:
        checkpoint = "w1-0"
    queryseqs = os.path.join(resultdir,"queryseqs")

    #Parse all inputs
    if checkpoint == "w1-0":
        if parsegenomes.parseall(indir,queryseqs):
            checkpoint = "w1-1"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            log.error("Problem parsing input genomes")
            return False

    #Run MASH distances
    mashresult = False
    if checkpoint == "w1-1":
        mashresult = mash.getdistances(queryseqs,resultdir,cpu=cpu,maxdist=mashmxdist)
        if mashresult:
            checkpoint = "w1-2"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            log.error("MASH distance failed")
            return False

    #Get set of organisms to build seq DB
    selorgs = False
    if checkpoint == "w1-2":
        log.info("Loading mash results...")
        if mashresult:
            pass
        elif not mashresult and os.path.exists(os.path.join(resultdir,"reflist.json")):
            with open(os.path.join(resultdir,"reflist.json")) as fil:
                mashresult = json.load(fil)
                log.info("Loading mash results...")
        else:
            log.error("No Mash results to process")
            return False

        selorgs = getorgs(resultdir,mashresult,skip=skip)
        if selorgs:
            checkpoint = "w1-3"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            log.info("JOB_STATUS: Waiting for selected organisms")
            return "Paused"

    #Copy reference sequence database and add query organisms
    orgdb = os.path.join(resultdir,"refquery.db")
    if checkpoint == "w1-3":
        if not selorgs:
            with open(os.path.join(resultdir,"userlist.json"),"r") as fil:
                selorgs = json.load(fil)

        #Clear old db if exists
        if os.path.exists(orgdb):
            os.remove(orgdb)

        flist = selorgs["selspecies"]
        flist.extend(selorgs["seloutgroups"])
        flist = [x for x in flist if "query" not in x.lower()]
        log.info("refdb: %s"%refdb)
        if copyseqsql.copydb(flist,refdb,orgdb):
            #get file list of query orgs and add to db
            seqlist = glob.glob(os.path.join(queryseqs,"*.fna"))
            if makeseqsql.runlist(seqlist,orgdb,True,"",True):
                checkpoint = "w1-4"
                log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            log.error("Failed at copydb")

    #Run HMM searches on query organism
    if checkpoint == "w1-4":
        if not orgdb:
            log.error("No querydb rerun at checkpoint w1-3")
            return False
        #Write newly added seqences to file
        naseqs = os.path.join(resultdir,"addedseqs.fna")
        aaseqs = os.path.join(resultdir,"addedseqs.faa")
        seqsql2fa.writefasta(orgdb,aaseqs,False,"",True)
        seqsql2fa.writefasta(orgdb,naseqs,True,"",True)

        #Run HMM searches
        if not hmmdb:
            hmmdb = os.path.join(os.path.dirname(os.path.realpath(__file__)),"reducedcore.hmm")
        if not rnadb:
            rnadb = os.path.join(os.path.dirname(os.path.realpath(__file__)),"barnap_bact_rRna.hmm")
        hmmsearch(aaseqs+".domhr",hmmdb,aaseqs,mcpu=cpu)
        hmmsearch(naseqs+".domhr",rnadb,naseqs,mcpu=cpu)

        #Add HMMresults to refdb and cleanup unused seqs
        log.info("Adding query HMM results to database")
        makehmmsql.run(aaseqs+".domhr",orgdb)
        log.info("Adding query RNA results to database")
        makehmmsql.run(naseqs+".domhr",orgdb,rna=True)
        os.remove(aaseqs)
        os.remove(naseqs)
        checkpoint = "w1-5"
        log.info("JOB_CHECKPOINT::%s"%checkpoint)

    #Calculate mlst core genes and export
    mlstdir = os.path.join(resultdir,"mlstgenes")
    genematjson = os.path.join(resultdir,"mlstmatrix.json")
    if checkpoint == "w1-5":
        #getmlstgenes.findsingles(orgdb,maxgenes=500,outdir=mlstdir)
        genemat,orgs,singles = getgenematrix.getmat(orgdb,pct=0.5,pct2=0.5,bh=True,rna=True,savefil=genematjson)


def startjob(indir,resultdir,skip="",checkpoint=False,workflow=1,refdb="",cpu=1):
    #Setup working directory
    if not os.path.exists(resultdir):
        os.makedirs(os.path.join(os.path.realpath(resultdir),"queryseqs")) #query sequence folder

    #Read checkpoint from log if exists or use checkpoint parameter
    if not checkpoint and os.path.exists(os.path.join(resultdir,"automlst.log")):
        with open(os.path.join(resultdir,"automlst.log"),"r") as fil:
            for line in fil:
                x = line.strip().split("::")
                if "JOB_CHECKPOINT" in x[0]:
                    checkpoint = x[1]
                elif "WORKFLOW" in x[0]:
                    workflow = int(x[1])
    #Start log
    global log
    log = setlog.init(os.path.join(resultdir,"automlst.log"),toconsole=True)

    log.debug("START / RESUME JOB last checkpoint: %s"%checkpoint)
    if workflow == 1:
        log.info("WORKFLOW::1")
        return startwf1(indir,resultdir,checkpoint=checkpoint,skip=skip,refdb=refdb,cpu=cpu)
    elif workflow == 2:
        log.info("WORKFLOW::2")
        return startwf2(indir,resultdir,checkpoint=checkpoint,skip=skip,refdb=refdb,cpu=cpu)

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Start from input directory of genomes, get all reference distances and build phylogeny""")
    parser.add_argument("indir", help="Directory of input genomes")
    parser.add_argument("resultdir", help="Directory to store all results")
    parser.add_argument("-skip","--skip", help="Flag to skip manual intervention of organism selection. Ex: 'skip2.skip3' skips organism and mlst selection (default for cmdline execution)",default="skip2.skip3")
    parser.add_argument("-ref","--refdb", help="Reference database of orgs",default="")
    parser.add_argument("-c","--cpu", help="Reference database of orgs",type=int, default=1)
    args = parser.parse_args()
    startjob(args.indir,args.resultdir,args.skip,refdb=args.refdb,cpu=args.cpu)

