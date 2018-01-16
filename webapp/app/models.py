#!/usr/bin/env python

class automlstjob(object):
    def __init__(self,**kwargs):
        self.id=kwargs.get("id",'')
        self.workflow=kwargs.get("workflow","2")
        self.genomes=kwargs.get("genomes","")
        self.reference=kwargs.get("reference","NA")
        #self.skip2 = kwargs.get("skip2","")
        #self.skip3 = kwargs.get("skip3","")
        self.skip = kwargs.get("skip")
        self.bootstr=kwargs.get("bootstr",0)
        self.mode=kwargs.get("mode","concatenated")
    def getdict(self):
        return self.__dict__
