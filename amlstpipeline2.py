#!/usr/bin/env python
import os, argparse, setlog, parsegenomes, mash

def startwf2(indir,resultdir,checkpoint=False,genus="auto"):
    """WORKFLOW 1: Get all query genomes and identify reference tree to add sequences to"""
    pass


def startwf1(indir,resultdir,checkpoint=False,mashmxdist=0.5,cpu=1):
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

    #Read list of

def startjob(indir,resultdir,checkpoint=False,workflow=1):
    #Setup working directory
    if not os.path.exists(resultdir):
        os.makedirs(os.path.join(os.path.realpath(resultdir),"queryseqs")) #query sequence folder

    #Start log
    global log
    log = setlog.init(os.path.join(resultdir,"automlst.log"))

    #Read checkpoint from log if exists or use checkpoint parameter
    if not checkpoint:
        with open(log.handlers[0].baseFilename,"r") as fil:
            for line in fil:
                x = line.strip().split("::")
                if "JOB_CHECKPOINT::" in x[0]:
                    checkpoint = x[1]
                elif "WORKFLOW::" in x[0]:
                    workflow = x[1]

    log.debug("START / RESUME JOB")
    if workflow == 1:
        log.info("WORKFLOW::w1")
        return startwf1(indir,resultdir,checkpoint)
    elif workflow == 2:
        log.info("WORKFLOW::w1")
        return startwf2(indir,resultdir,checkpoint)

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Start from input directory of genomes, get all reference distances and build phylogeny""")
    parser.add_argument("indir", help="Directory of input genomes")
    parser.add_argument("resultdir", help="Directory to store all results")
    args = parser.parse_args()
    startjob(args.indir,args.resultdir)

