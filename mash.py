#!/usr/bin/env python
import argparse, subprocess, glob, os, tempfile, setlog, pickle, base64
from numpy import median,floor
from multiprocessing import cpu_count

log = setlog.init(toconsole=True)

def mashdist(listfile,reffile,outputfile,cpu=1):
    cmd = ["mash","dist",reffile,"-l", listfile]
    if(cpu > 1):
        cmd = cmd[:2] + ["-p",str(cpu)] + cmd[2:]
    with open(outputfile,"w") as ofil:
        try:
            subprocess.call(cmd, stdout=ofil)
            log.debug("MASH dist: finished %s"%outputfile)
            return True
        except subprocess.CalledProcessError as e:
            log.error("MASH dist: error, could not process %s - %s"%(listfile,e))
            return False

def writefilelist(indir,outdir):
    try:
        flist = glob.glob(os.path.join(os.path.realpath(indir),"*.fa"))
        tf = tempfile.NamedTemporaryFile(prefix="queryflist_",suffix=".txt",dir=os.path.realpath(outdir),delete=False)
        tf.write("\n".join(flist))
        tf.close()
        log.info("List of files generated %s"%tf.name)
        return tf.name
    except IOError:
        log.error("Failed to generate file list")
        return False

def parse(mashresult,taxdb="",maxdist=0.5):
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
                                lookup["phylum_id"],lookup["phylum_name"],lookup["taxid"],refseq,typestrain])
        for qorg in recs:
            recs[qorg] = sorted(recs[qorg], key=lambda row: (row[2],row[-1]))
    return recs

def getlineage(recs):
    return {org:{"orgname":org,"id":base64.encodestring(org).strip(),"genusname":rows[0][5],"genusid":rows[0][4], "familyid":rows[0][6],
                 "familyname":rows[0][7],"orderid":rows[0][8],"ordername":rows[0][9],"phylid":rows[0][10],"phylname":rows[0][11]} for org,rows in recs.items() if len(rows)}

def getcommongroup(lineage):
    groups = ["genus","family","order","phyl"]
    common = (None,None,None)
    for group in groups:
        allgroup = {rec[group+"id"]:rec[group+"name"] for org,rec in lineage.items()}
        if len(allgroup.keys())==1:
            common = (group,allgroup.keys()[0],allgroup.values()[0])
            break
    return common

def getrefrecs(recs):
    #reads distances from refs and outputs sorted list of reference organisms
    refrecs = {}
    orglist = []
    for org,rec in recs.items():
        orglist.append(org)
        for row in rec:
            if row[0] not in refrecs:
                refrecs[row[0]] = {"orgname":row[1],"id":row[0],"genusname":row[5],"genusid":row[4], "familyid":row[6],
                                "familyname":row[7],"orderid":row[8],"ordername":row[9],"phylid":row[10],"phylname":row[11], "taxid":row[-3],
                                "refseq":row[-2],"typestrain":row[-1],"dlist":[],"plist":[]}
            refrecs[row[0]]["dlist"].append(row[2])
            refrecs[row[0]]["plist"].append(row[3])
    #Get median distances and pvalues
    for id in refrecs.keys():
        refrecs[id]["dist"] = median(refrecs[id]["dlist"])
        refrecs[id]["mindist"] = min(refrecs[id]["dlist"])
        refrecs[id]["maxdist"] = max(refrecs[id]["dlist"])
        refrecs[id]["pval"] = median(refrecs[id]["plist"])
    return refrecs, orglist

# sorted(refrecs.values(), key=lambda row: row["dist"])

#Get ids of reference genomes that are closest to each species, number of genomes divided equally among query genomes
def getnearestrefs(recs,limit=25,offset=0):
    #limit number of nearest to each organism
    orglimit = int(floor((limit)/len(recs.keys())))
    if not orglimit >= 1:
        orglimit = 1
    for reclist in recs.values():
        #impose requirement that all recs must be of the same genus
        gid = reclist[0][4]
        toprefids.update([r[0] for r in reclist[:orglimit] if r[4]==gid])
    #Recursively look for more if there is significant overlap
    if len(toprefids) < limit and not offset > limit:
        toprefids = getnearestrefs(recs,limit,orglimit)
    if len(toprefids) > limit:
        toprefids = toprefids[:25]
    return toprefids

def getdistances(indir,outdir,reffile="",cpu=1,limit=50):
    if not reffile or not os.path.exists(reffile):
        reffile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"refseq.msh")
        log.info("Loading default refseq MASH database")
    listfile = writefilelist(os.path.realpath(indir),os.path.realpath(outdir))
    outputfile = os.path.join(os.path.realpath(outdir),"mash_distances.txt")
    if listfile and mashdist(listfile,reffile,outputfile,cpu):
        recs = parse(outputfile)
        refrecs = getrefrecs(recs)
    return False

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Use MASH to calculate distances of genome in input directory to mash sketch file""")
    parser.add_argument("indir", help="Directory where fasta geneomes are located")
    parser.add_argument("outdir", help="Directory where results are stored (jobid)")
    parser.add_argument("-c", "--cpu", help="Turn on Multi processing set # Cpus (default: maxcpus)", type=int, default=cpu_count())
    parser.add_argument("-l", "--limit", help="limit of number of genomes to prioritize", type=int, default=50)
    parser.add_argument("-r", "--reffile", help="Reference sketch file (default: refseq.msh)",default="")
    args = parser.parse_args()
    getdistances(args.indir,args.outdir,args.reffile,args.cpu)