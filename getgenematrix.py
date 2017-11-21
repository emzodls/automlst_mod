#!/usr/bin/env python
# Copyright (C) 2015,2016 Mohammad Alanjary
# University of Tuebingen
# Interfaculty Institute of Microbiology and Infection Medicine
# Lab of Nadine Ziemert, Div. of Microbiology/Biotechnology
# Funding by the German Centre for Infection Research (DZIF)
#
# This file is part of ARTS
# ARTS is free software. you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version
#
# License: You should have received a copy of the GNU General Public License v3 with ARTS
# A copy of the GPLv3 can also be found at: <http://www.gnu.org/licenses/>.

import argparse, json, numpy as np, sqlite3 as sql

def getmat(db,pct=0.9,pct2=0.95,ev=0.001,bs=0,bh=True,rna=False,pfx="genematrix"):
    conn=sql.connect(db)
    cur=conn.cursor()
    tabletitle="HMMhits"
    if rna:
        tabletitle="RNAhits"
    orgs=sorted([x[0] for x in cur.execute("SELECT DISTINCT orgname FROM "+tabletitle)])
    counts=cur.execute("SELECT orgname,hmmhit,COUNT(*) FROM %s WHERE hmmcov >= %.4f AND evalue<=%s AND score>=%s AND flags>0 GROUP BY orgname,hmmhit"%(tabletitle,pct,ev,bs))
    countdict={}
    for x in counts:
        if x[1] not in countdict:
            countdict[x[1]]=[0]*len(orgs)
        countdict[x[1]][orgs.index(x[0])]=int(x[2])
    slist=[]
    thrsh=len(orgs)*pct2
    #save genematrix string:
    gmstr="#totalorgs:\t"+str(len(orgs))+"\n"
    gmstr+="#hmmhit\tOrgcount\tAvg\tStdev\t"+"\t".join(orgs)+"\n"
    for k,v in countdict.items():
        temp = [c for c in v if c > 0] #Exclude mising genes in statistics
        norg = len(temp)
        avgcount = np.mean(temp)
        stdcount = np.std(temp)

        if len([c for c in v if c==1]) >= thrsh:
            gmstr+="%s\t%d\t%.2f\t%.4f\t"%(k,norg,avgcount,stdcount)+"\t".join([str(c) for c in v])+"\n"
            slist.append(k)
    conn.close()
    #Write gene matrix to file:
    with open(pfx+".txt","w") as gmfil, open(pfx+".json","w") as jsonfil:
        gmfil.write(gmstr)
        json.dump({"count":countdict,"orgs":orgs,"slist":slist},jsonfil,indent=3)
    return countdict,orgs,slist

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Gets gene matrix and output table to stdout""")
    parser.add_argument("input", help="Sql database (READS TABLES: Seqs, HMMhits)")
    parser.add_argument("-p", "--pct", help="percent match of hmm model length to consider as hit (default: 0.9)", type=float, default=0.9)
    parser.add_argument("-p2", "--pct2", help="percent of orgs to consider as ubiquitous single copy gene (default: 0.95)", type=float, default=0.95)
    parser.add_argument("-e", "--evalue", help="Evalue threshold (default: 0.1)", type=float, default=0.001)
    parser.add_argument("-b", "--bitscore", help="Bitscore threshold (default: 0)", type=float, default=0)
    parser.add_argument("-pfx", "--prefix", help="filename prefix to save .txt matrix and .json object", default="genematrix")
    # parser.add_argument("-s", "--savefil", help="Save file to python pickle file (default: disabled)", default="")
    parser.add_argument("-bh", "--besthit", help="Only write best hit hmm for each gene (only lowest hmm allowed per gene)", action='store_true')
    parser.add_argument("-r", "--rna", help="Look at RNA table", action='store_true')
    args = parser.parse_args()
    result=getmat(args.input, args.pct, args.pct2, args.evalue, args.bitscore, args.besthit, args.rna, args.prefix)