import subprocess,os,gzip,shutil
from Bio import SeqIO
from BCBio import GFF

def runbarrnap(genome,outfilePath = '.'):
    '''
    assumes write permission in current working directory
    :param genome: path to genome assumes assembly file name ("_genomic.fna.gz")
    :param outfile: target file with rRNA sequences detected in fasta format with header
    ">asmID:ribosomalSubunit:start-end:dir:acc"
    :return: True if successfully run, false if not
    '''
    if os.path.isfile(genome):
        fileName = os.path.split(genome)[1]
        asmID = fileName.split('.')[0]
        outfileName = asmID + '_rRNA.fasta'
        try:
            tempGenome = asmID + '.tmp'
            with gzip.open(genome) as in_file, open(tempGenome,'w') as out_file:
                shutil.copyfileobj(in_file,out_file)
        except IOError:
            tempGenome = asmID + '.tmp'
            shutil.copy(genome, tempGenome)
        ## unzip
        command = ['barrnap','--incseq',tempGenome]
        try:
            barrnapProc = subprocess.Popen(command,stdout=subprocess.PIPE)
            handle = GFF.parse(barrnapProc.stdout)
            seqs = []
            for seq in handle:
                for feat in seq.features:
                    rnaSeq = feat.extract(seq)
                    rSU = feat.qualifiers['name'][0]
                    eval = float(feat.qualifiers['score'][0])
                    start = feat.location.start
                    end = feat.location.end
                    dir = feat.location.strand
                    if 'note' in feat.qualifiers:
                        partial = 'partial'
                    else:
                        partial = 'full'
                    rnaSeq.name = "{}:{}:{}:{}-{}:{}:{}".format(asmID,rSU,eval,start,end,dir,partial)
                    rnaSeq.id = "{}:{}:{}:{}-{}:{}:{}".format(asmID,rSU,eval,start,end,dir,partial)
                    rnaSeq.description = ''
                    seqs.append(rnaSeq)
            with open(os.path.join(outfilePath,outfileName),'w') as outfile:
                SeqIO.write(seqs,outfile,'fasta')
        except Exception as e:
            print(e)
        os.remove(tempGenome)