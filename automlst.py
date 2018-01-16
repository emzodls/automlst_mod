#!/usr/bin/env python
import os, json, argparse, setlog, parsegenomes, mash
import copyseqsql, makeseqsql, glob, seqsql2fa, subprocess
import multiprocessing as mp
import makehmmsql, getgenematrix, getgenes, concatmsa

def startwf2(indir,resultdir,checkpoint=False,genus="auto",model="MFP",bs=""):
    """WORKFLOW 2: Get all query genomes and identify reference tree to add sequences to"""


##
## Workflow 1: Build query + reference phylogeny from scratch
##

def catTrees(flist,outfile):
    with open(outfile,"w") as ofil:
        for fname in flist:
            if os.path.exists(fname):
                with open(fname,"r") as ifil:
                    for line in ifil:
                        ofil.write(line)
            else:
                log.warning("Tree file not found for MLST: %s"%fname)
    return outfile

def runmafft(input,output,thread=1,maxit=0,localpair=False,options=""):
    if localpair:
        options += " --localpair"
    cmd = "mafft --quiet --thread %d --maxiterate %d %s %s"%(thread,maxit,options,input)
    cmd = cmd.split()
    with open(os.devnull,"w") as devnull, open(output,"w") as outfil:
        try:
            subprocess.call(cmd, stdout=outfil, stderr=devnull)
            log.info("Finished alignment %s"%output)
        except Exception as e:
            log.error("Failed to run mafft %s (%s)"%(input,e))

def runtrimal(input,output,method="automated1"):
    cmd = "trimal -in %s -out %s -%s"%(input,output,method)
    cmd = cmd.split()
    with open(os.devnull,"w") as devnull:
        try:
            subprocess.call(cmd, stdout=devnull, stderr=devnull)
            log.info("Finished trimming %s"%output)
        except Exception as e:
            log.error("Failed to run trimall %s (%s)"%(input,e))

def processmlst(indir,aligndir,cpu=1,parallel=True,trim=False):
    flist = glob.glob(os.path.join(indir,"*.fna"))
    if not os.path.exists(aligndir):
        os.makedirs(aligndir)

    if cpu > 1 and parallel:
        pool = mp.Pool(cpu)
        for filename in flist:
            fname = os.path.split(filename)[-1]
            if trim:
                pool.apply_async(runtrimal, args=(filename, os.path.join(aligndir,fname)))
            else:
                pool.apply_async(runmafft, args=(filename, os.path.join(aligndir,fname)))
        pool.close()
        pool.join()
    else:
        for filename in flist:
            fname = os.path.split(filename)[-1]
            if trim:
                runtrimal(filename, os.path.join(aligndir,fname))
            else:
                runmafft(filename, os.path.join(aligndir,fname),thread=cpu)

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
    usersel = os.path.join(resultdir,"userOrglist.json")
    autosel = os.path.join(resultdir,"autoOrglist.json")
    selection = False
    if os.path.exists(usersel):
        with open(usersel,"r") as fil:
            selection = json.load(fil)
    elif os.path.exists(autosel):
        with open(autosel,"r") as fil:
            selection = json.load(fil)
    elif "skip2" in skip:
        selection = {"selspecies":[x.get("id","") for x in mashresult.get("reforgs",[])][:IGlimit],
                     "seloutgroups":[x.get("id","") for x in mashresult.get("outgroups",[])][:OGlimit]}
        with open(autosel,"w") as fil:
            json.dump(selection,fil)

    return selection

def getmlstselection(resultdir,mlstpriority,maxmlst=100,skip=""):
    usersel = os.path.join(resultdir,"userMlstlist.json")
    autosel = os.path.join(resultdir,"autoMlstlist.json")
    selection = False
    delorgs = set()
    if os.path.exists(usersel):
        with open(usersel,"r") as fil:
            temp = json.load(fil)
            selection = temp["selection"]
            delorgs = temp["delorgs"]
    elif os.path.exists(autosel):
        with open(autosel,"r") as fil:
            temp = json.load(fil)
            selection = temp["selection"]
            delorgs = temp["delorgs"]
    elif "skip3" in skip:
        selection = [x["acc"] for x in mlstpriority[:maxmlst]]
        for x in mlstpriority[:maxmlst]:
            delorgs = delorgs | set(x["orgdel"])
        with open(autosel,"w") as fil:
            json.dump({"selection":selection,"delorgs":list(delorgs)},fil)

    return selection, list(delorgs)

def runIQtree(outdir,infasta,partfile="",cpu=1,model="MFP",bs="",fout="speciestree",titlesep=""):
    #If title seperator exists rename titles in file first
    if titlesep:
        tf = os.path.join(infasta,".renamed")
        with open(tf,"w") as ofil, open(infasta,"r") as ifil:
            for line in ifil:
                lineout = line.strip()
                if line.startswith(">") and titlesep in line:
                    lineout = line.strip().split(titlesep)[0]
                ofil.write(lineout+"\n")
        infasta = tf
    log.info("Building tree: model=%s, bootstrap=%s, file=%s"%(model,bs,fout))
    cmd=["iqtree-omp", "-quiet", "-nt", str(cpu), "-s", infasta, "-m", model,"-pre",os.path.join(outdir,fout)]
    if bs:
        cmd.extend(["-bb",str(bs)])
    if partfile:
        cmd.extend(["-spp", partfile])
    with open(os.devnull,"w") as devnull:
        subprocess.call(cmd,stdout=devnull,stderr=devnull)

def runAstral(resultdir,intree,outtree,astjar=""):
    log.info("Started running Astral: %s"%(intree))
    if not astjar or not os.path.realpath(astjar):
        jar = os.path.join(os.path.dirname(__file__),"astral.5.5.9.jar")
    cmd=["java", "-Xmx3000M", "-jar", str(astjar), "-i", intree, "-o", outtree]
    with open(os.path.join(resultdir,"astral.log"),"w") as astlog:
        subprocess.call(cmd,stdout=astlog,stderr=astlog)

def colphylogeny(resultdir,trimdir,cpu=1,model="MFP",bs=""):
    treedir = os.path.join(resultdir,"trees")
    if not os.path.exists(treedir):
        os.makedirs(treedir)
    flist = glob.glob(os.path.join(trimdir,"*.fna"))
    #build all trees
    if cpu > 1:
        pool = mp.Pool(cpu)
        for filename in flist:
            pool.apply_async(runIQtree, (treedir, filename), dict(model=model,bs=bs,fout=os.path.split(filename)[-1],titlesep="|"))
        pool.close()
        pool.join()
    else:
        for filename in flist:
            runIQtree(treedir, filename, fout=os.path.split(filename)[-1], bs=bs, model=model, titlesep="|")

    #Combine all trees using ASTRAL
    flist = glob.glob(os.path.join(treedir,"*.treefile"))
    alltrees = catTrees(flist,os.path.join(treedir,"alltrees.tree"))
    coltree = os.path.join(treedir,"summaryTree.tree")
    runAstral(resultdir,alltrees,coltree)

def concatphylogeny(resultdir,concatfasta,partfile,cpu=1,model="MFP",bs=""):
    trimdir = os.path.join(resultdir,"mlst_trimmed")
    log.info("Concatenating all MLST genes")
    concatmsa.concatmsa(os.path.join(trimdir,"*.fna"),concatfasta,partfile,fsplit="|",checktype=False)
    #Build tree from concatenated fasta
    treedir = os.path.join(resultdir,"trees")
    if not os.path.exists(treedir):
        os.makedirs(treedir)
    runIQtree(treedir,concatfasta,partfile=partfile,cpu=cpu,fout="concatTree.tree",bs=bs,model=model)


def startwf1(indir,resultdir,checkpoint=False,concat=False,mashmxdist=0.5,cpu=1,skip="",refdb="",hmmdb="",rnadb="",maxmlst=100,model="MFP",bs=""):
    """WORKFLOW 2: Build phylogeny from scratch"""
    if not checkpoint:
        checkpoint = "w1-0"
    queryseqs = os.path.join(resultdir,"queryseqs")

    #Parse all inputs
    if checkpoint == "w1-0":
        if parsegenomes.parseall(indir,queryseqs):
            checkpoint = "w1-1"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
            log.info("JOB_PROGRESS::5/100")
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
            log.info("JOB_PROGRESS::15/100")
        else:
            log.error("MASH distance failed")
            return False

    #Get set of organisms to build seq DB
    selorgs = False
    if checkpoint == "w1-2":
        log.info("JOB_STATUS::Loading mash results...")
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
            log.info("JOB_PROGRESS::25/100")
        else:
            checkpoint = "w1-STEP2"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)

    if checkpoint == "w1-STEP2":
        log.info("JOB_STATUS:: Waiting for selected organisms")
        return "waiting"

    #Copy reference sequence database and add query organisms
    orgdb = os.path.join(resultdir,"refquery.db")
    if checkpoint == "w1-3":
        if not selorgs and os.path.exists(os.path.join(resultdir,"userOrglist.json")):
            with open(os.path.join(resultdir,"userOrglist.json"),"r") as fil:
                selorgs = json.load(fil)
        elif not selorgs and os.path.exists(os.path.join(resultdir,"autoOrglist.json")):
            with open(os.path.join(resultdir,"autoOrglist.json"),"r") as fil:
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
        log.info("JOB_STATUS:: Searching for MLST genes in query sequences...")
        log.info("JOB_PROGRESS::35/100")
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
    mlstpriority = os.path.join(resultdir,"mlstpriority.json")
    genematjson = os.path.join(resultdir,"mlstmatrix.json")
    dndsfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"dnds.json")
    if checkpoint == "w1-5":
        #getmlstgenes.findsingles(orgdb,maxgenes=500,outdir=mlstdir)
        if os.path.exists(mlstpriority) and os.path.exists(genematjson):
            with open(genematjson,"r") as mfil, open(mlstpriority,"r") as pfil:
                mlstpriority = json.load(pfil)
                temp = json.load(mfil)
                genemat = temp["counts"]
                orgs = temp["orgs"]
                del temp
        else:
            genemat,orgs,mlstpriority = getgenematrix.getmat(orgdb,pct=0.5,pct2=0.5,bh=True,rna=True,savefil=genematjson,prifile=mlstpriority,dndsfile=dndsfile)

        mlstselection, delorgs = getmlstselection(resultdir,mlstpriority,maxmlst,skip=skip)
        if mlstselection:
            #Export selected genes to mlst folder
            getgenes.writeallgenes(orgdb,mlstselection,delorgs,outdir=mlstdir)
            checkpoint = "w1-6"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            checkpoint = "w1-STEP3"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)

    if checkpoint == "w1-STEP3":
        log.info("JOB_STATUS:: Waiting for selected organisms")
        return "waiting"

    ## Align and trim all MLST genes
    aligndir = os.path.join(resultdir,"mlst_aligned")
    trimdir = os.path.join(resultdir,"mlst_trimmed")

    if checkpoint == "w1-6":
        log.info("JOB_STATUS:: Aligning MLST genes")
        log.info("JOB_PROGRESS::45/100")
        #align all
        processmlst(mlstdir,aligndir,cpu=cpu)
        #trim all
        log.info("JOB_STATUS:: Trimming alignments")
        log.info("JOB_PROGRESS::55/100")
        processmlst(aligndir,trimdir,cpu=cpu,trim=True)

        checkpoint = "w1-7"
        log.info("JOB_CHECKPOINT::%s"%checkpoint)

    #Build trees
    if checkpoint == "w1-7":
        log.info("JOB_PROGRESS::70/100")
        if concat:
            log.info("JOB_STATUS:: Running concatenated supermatrix phylogeny")
            concatfasta = os.path.join(resultdir,"concatMLST.fasta")
            partfile = os.path.join(resultdir,"nucpartition.txt")
            concatphylogeny(resultdir, concatfasta, partfile,cpu=cpu,model=model,bs=bs)
            checkpoint = "w1-F"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)
        else:
            log.info("JOB_STATUS:: Running coalescent tree phylogeny")
            colphylogeny(resultdir,trimdir,cpu=cpu,model=model,bs=bs)
            checkpoint = "w1-F"
            log.info("JOB_CHECKPOINT::%s"%checkpoint)

    if checkpoint == "w1-F":
        #Job finished? do some cleanup
        if os.path.exists(orgdb):
            os.remove(orgdb)

def startjob(indir,resultdir,skip="",checkpoint=False,workflow=1,refdb="",cpu=1,concat=False,model="GTR",bs=""):
    #Setup working directory
    if not os.path.exists(os.path.join(os.path.realpath(resultdir),"queryseqs")):
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

    #ensure bootsrtap value is valid and no more than 1000
    try:
        bs = int(bs)
        if bs > 1000:
            bs = 1000
        elif bs < 0:
            bs = 0
    except ValueError:
        log.warning("Invalid bootsrap value found, setting to 0")
        bs = 0

    log.debug("START / RESUME JOB last checkpoint: %s"%checkpoint)
    log.info('JOB_PARAMS::{"resultdir":"%s","skip":"%s","workflow":%s,"concat":"%s","model":"%s"}'%(resultdir,skip,workflow,concat,model))
    if workflow == 1:
        log.info("WORKFLOW::1")
        return startwf1(indir,resultdir,checkpoint=checkpoint,skip=skip,refdb=refdb,cpu=cpu,concat=concat,model=model,bs=bs)
    elif workflow == 2:
        log.info("WORKFLOW::2")
        return startwf2(indir,resultdir,checkpoint=checkpoint,model=model,bs=bs)
    else:
        log.error("Improper workflow specified: %s"%workflow)
        return False

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Start from input directory of genomes, get all reference distances and build phylogeny""")
    parser.add_argument("indir", help="Directory of input genomes or list of files")
    parser.add_argument("resultdir", help="Directory to store all results")
    parser.add_argument("-skip","--skip", help="Flag to skip manual intervention of organism selection. Ex: 'skip2.skip3' skips organism and mlst selection (default for cmdline execution)",default="skip2.skip3")
    parser.add_argument("-ref","--refdb", help="Reference database of orgs",default="")
    parser.add_argument("-bs","--bootstrap", help="Bootstrap replicates (default: None)",default="")
    parser.add_argument("-cat","--concat", help="Use concatenated supermatrix to build tree",action="store_true",default=False)
    parser.add_argument("-m","--model", help="Use specific model for iqtree parameter (default: Use model finder)",default="MFP")
    parser.add_argument("-ch","--checkpoint", help="Explicitly start at checkpoint",default=False)
    parser.add_argument("-c","--cpu", help="Number of cpu cores to use",type=int, default=1)
    args = parser.parse_args()
    startjob(args.indir,args.resultdir,args.skip,refdb=args.refdb,cpu=args.cpu,concat=args.concat,model=args.model,checkpoint=args.checkpoint,bs=args.bootstrap)