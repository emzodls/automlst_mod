#!/usr/bin/env python
import subprocess, os, setlog, argparse

global log
log=setlog.init(toconsole=True)

def runprodigal(infasta, outfasta):
    try:
        #crude check for format
        cmd = ["prodigal","-d",outfasta,"-i",infasta,"-f","gff"]
        with open(os.devnull,"w") as devnull:
            subprocess.call(cmd, stdout=devnull, stderr=devnull)
        return outfasta
    except Exception, e:
        log.error("Problem running prodigal, check fasta input.")
        return False

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Convert contigs of fasta sequence to multi-record fasta of open reading frames""")
    parser.add_argument("infasta", help="Input fasta file")
    parser.add_argument("outfasta", help="Output fasta file")
    args = parser.parse_args()
    runprodigal(args.infasta,args.outfasta)