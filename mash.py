#!/usr/bin/env python
import argparse, subprocess, glob, os, tempfile, json, setlog, pickle, base64
from numpy import median,mean,floor,round
from multiprocessing import cpu_count

log = setlog.init(toconsole=True)

def mashdist(listfile,reffile,outputfile,cpu=1):
    cmd = ["mash","dist",reffile,"-l", listfile]
    if(cpu > 1):
        cmd = cmd[:2] + ["-p",str(cpu)] + cmd[2:]
    with open(outputfile,"w") as ofil:
        try:
            log.info("MASH dist: Running all input genomes")
            subprocess.call(cmd, stdout=ofil)
            log.debug("MASH dist: finished %s"%outputfile)
            return True
        except subprocess.CalledProcessError as e:
            log.error("MASH dist: error, could not process %s - %s"%(listfile,e))
            return False

def writefilelist(indir,outdir):
    try:
        flist = glob.glob(os.path.join(os.path.realpath(indir),"*.fa"))
        if len(flist):
            tf = tempfile.NamedTemporaryFile(prefix="queryflist_",suffix=".txt",dir=os.path.realpath(outdir),delete=False)
            tf.write("\n".join(flist))
            tf.close()
            log.info("List of files generated %s"%tf.name)
            return tf.name
    except IOError:
        log.error("Failed to generate file list")
    return False

def parse(mashresult,taxdb="",maxdist=0.5,TStol=0.05):
    if not taxdb or not os.path.exists(taxdb):
        taxdb = os.path.join(os.path.dirname(os.path.realpath(__file__)),"taxonomy.pkl")
    with open(taxdb,"r") as fil:
        taxonomy = pickle.load(fil)
    with open(mashresult,"r") as fil:
        recs = {}
        for line in fil:
            tabs = line.strip().split("\t")
            dist = float(tabs[2])
            pval = float(tabs[3])
            if dist <= maxdist:
                qorg = os.path.split(tabs[1])[1]
                if qorg not in recs:
                    recs[qorg] = []
                refid = tabs[0].split(".")[0]
                lookup = taxonomy[refid]
                refseq = True if lookup["refseq_category"] else False
                typestrain = True if lookup["ts_category"] else False
                recs[qorg].append([refid,lookup["organism_name"],dist,pval,lookup["genus_taxid"],lookup["genus_name"],
                                lookup["family_id"],lookup["family_name"],lookup["order_id"],lookup["order_name"],
                                lookup["phylum_id"],lookup["phylum_name"],lookup["taxid"],lookup.get("strain","N/A"),refseq,typestrain])
        for qorg in recs:
            # Typestrain genome distances are allowed to be +(tolerance) larger for prioritization
            recs[qorg] = sorted(recs[qorg], key=lambda row: row[2]-TStol if row[-1] else row[2])
    return recs

lastid = 0
def makeid(txt,prfx="query_"):
    global lastid
    lastid += 1
    return "%s%03d"%(prfx,lastid)

def getlineage(recs):
    #Returns lineage of nearest mash hit as lineage estimate
    return {org:{"orgname":org,"id":makeid(org),"genusname":rows[0][5],"genusid":rows[0][4], "familyid":rows[0][6],
                 "familyname":rows[0][7],"orderid":rows[0][8],"ordername":rows[0][9],"phylid":rows[0][10],"phylname":rows[0][11]} for org,rows in recs.items() if len(rows)}

def getcommongroup(lineage):
    groups = ["genus","family","order","phyl"]
    allids = {}
    allgroup = {}
    common = [False,allgroup.keys(),allgroup.values()]
    for group in groups:
        allgroup = {rec[group+"id"]:rec[group+"name"] for org,rec in lineage.items()}
        if len(allgroup.keys())==1 and not common[0]:
            common = [group,allgroup.keys()[0],allgroup.values()[0]]
        allids[group] = allgroup.keys()
    return common, allids

def getoutgrouporgs(common,refrecs):
    group = "phyl" #default to phyl scope
    ingroupset = set()
    if common[0]:
        group = common[0]
        ingroupset.add(common[1])
    else:
        ingroupset.update(common[1])

    #Filter sorted reference list to remove ingroups
    return [rec for rec in refrecs if rec[group+"id"] not in ingroupset]

def getrefrecs(recs,top=list()):
    #reads distances from refs and outputs sorted list of reference organisms
    refrecs = {}
    orglist = []
    for org,rec in recs.items():
        orglist.append(org)
        for row in rec:
            if row[0] not in refrecs:
                refrecs[row[0]] = {"orgname":row[1],"id":row[0],"genusname":row[5],"genusid":row[4], "familyid":row[6],
                                "familyname":row[7],"orderid":row[8],"ordername":row[9],"phylid":row[10],"phylname":row[11], "taxid":row[12],
                                "strain":row[13],"refseq":row[-2],"typestrain":row[-1],"dlist":[],"plist":[]}
            refrecs[row[0]]["dlist"].append(row[2])
            refrecs[row[0]]["plist"].append(row[3])
    #Get median distances and pvalues
    for id in refrecs.keys():
        refrecs[id]["dist"] = mean(refrecs[id]["dlist"])
        mindist = min(refrecs[id]["dlist"])
        maxdist = max(refrecs[id]["dlist"])
        refrecs[id]["mindist"] = mindist
        refrecs[id]["minorg"] = orglist[refrecs[id]["dlist"].index(mindist)]
        refrecs[id]["maxdist"] = maxdist
        refrecs[id]["maxorg"] = orglist[refrecs[id]["dlist"].index(maxdist)]
        refrecs[id]["pval"] = mean(refrecs[id]["plist"])
        refrecs[id]["top"] = 0
        if id in top:
            refrecs[id]["top"] = 1
    return refrecs, orglist

def getalloutgroups(allids,refrecs, glimit=1000):
    #get top 'glimit' orgs outside of each group scope
    oglist = []
    for group,allset in allids.items():
        temp = [rec for rec in refrecs if rec[group+"id"] not in allset]
        oglist.extend(temp[:glimit])
    return oglist

# sorted(refrecs.values(), key=lambda row: row["dist"])

# Get ids of reference genomes that are closest to each species, preference weighted for typestrains.
# Try to divide number of genomes equally among query genomes.
def getnearestrefs(recs,NOlimit=25):
    #limit number of nearest to each organism
    toprefids=set()
    orglimit = int(floor((NOlimit)/len(recs.keys())))
    if not orglimit >= 1:
        orglimit = 1
    for reclist in recs.values():
        #impose requirement that all recs must be of the same genus
        gid = reclist[0][4]
        orgs = [r[0] for r in reclist if r[4]==gid and r[0] not in list(toprefids)]
        toprefids.update(orgs[:orglimit])
    toprefids = list(toprefids)
    return toprefids[:NOlimit]

def getdistances(indir,outdir,reffile="",cpu=1,limit=50,outputfile="",TStol=0.05,NOlimit=25,OGlimit=100,maxdist=0.5):
    status = False
    print indir
    print outdir
    if not reffile or not os.path.exists(reffile):
        reffile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"refseq.msh")
        log.info("Loading default refseq MASH database")
    if not outputfile:
        listfile = writefilelist(os.path.realpath(indir),os.path.realpath(outdir))
        if not listfile:
            log.error("No Sequences found.")
            return False
        outputfile = os.path.join(os.path.realpath(outdir),"mash_distances.txt")
        status = mashdist(listfile,reffile,outputfile,cpu)
    elif os.path.exists(os.path.realpath(outputfile)):
        outputfile = os.path.realpath(outputfile)
        log.info("Using precomputed mash file: %s"%outputfile)
        status = True
    if status:
        recs = parse(outputfile,maxdist=maxdist,TStol=TStol)
        topids = getnearestrefs(recs,NOlimit=NOlimit)
        refrecs, orglist = getrefrecs(recs,topids)

        # Sort by nearest relative to query first, mean distance to all (TypeStrains are prefered within tolerance)
        refrecs = sorted(refrecs.values(), key=lambda x: (x["top"]*-1,x["dist"]-TStol if x["typestrain"] else x["dist"]))

        #Get query organism lineage by closest hit lineage
        orgrecs = getlineage(recs)
        commonrank, allids = getcommongroup(orgrecs)
        OGorgs = getalloutgroups(allids,refrecs,glimit=OGlimit)

        with open(os.path.join(outdir,"reflist.json"),"w") as fil:
            json.dump({"reforgs":refrecs[:limit],"queryorgs":orgrecs.values(),"orglist":orglist,"commonrank":commonrank,"outgroups":OGorgs},fil,indent=2)
    return False

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Use MASH to calculate distances of genome in input directory to mash sketch file""")
    parser.add_argument("indir", help="Directory where fasta geneomes are located")
    parser.add_argument("outdir", help="Directory where results are to be stored")
    parser.add_argument("-c", "--cpu", help="Turn on Multi processing set # Cpus (default: maxcpus)", type=int, default=cpu_count())
    parser.add_argument("-l", "--limit", help="limit of number of genomes to prioritize in total (default 500)", type=int, default=500)
    parser.add_argument("-nl", "--nearestlimit", help="limit of number of nearest organisms relative to each node (default 25)", type=int, default=25)
    parser.add_argument("-ogl", "--outgrouplimit", help="limit of number of outgroups per group scope (default: 100 for each genus,family,order,phyl)", type=int, default=100)
    parser.add_argument("-ts", "--typestrain", help="MASH distance tolerance for typestrains, gives extra priority to typestrains by subtracting tolerance from distance measure (default 0.05)", type=float, default=0.05)
    parser.add_argument("-r", "--reffile", help="Reference sketch file (default: refseq.msh)",default="")
    parser.add_argument("-m", "--mashfile", help="Use precomuted mash output file and skip MASH (default: none)",default="")
    parser.add_argument("-mx", "--maxmashdist", help="Limit results to maximum mash distance (default: 0.5)",default=0.5)
    args = parser.parse_args()
    getdistances(args.indir,args.outdir,args.reffile,args.cpu,limit=args.limit,outputfile=args.mashfile,TStol=args.typestrain,NOlimit=args.nearestlimit,OGlimit=args.outgrouplimit,maxdist=args.maxmashdist)