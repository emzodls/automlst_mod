#!/usr/bin/env python

class automlstjob(object):
    def __init__(self,**kwargs):
        self.id=kwargs.get("id",'')
        self.workflow=kwargs.get("workflow","auto")
        self.genomes=kwargs.get("genomes","")
        self.reference=kwargs.get("reference","NA")
    def getdict(self):
        return self.__dict__
