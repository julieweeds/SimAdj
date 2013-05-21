__author__ = 'juliewe'

import conf


class Entry:

    def __init__(self,word,id):
        self.word=word
        self.id=id
        self.freq=-1
        self.width=-1
        self.sims=[] #list of tuples (score,id)
        self.sorted=False

    def updatetotals(self,freq,width):
        self.freq=freq
        self.width=width

    def updatesims(self,list):

        while len(list)>0:
            id = list.pop()
            score = list.pop()
            self.sims.append((score,id))

    def topk(self,k):

        if self.sorted == False:
            self.sims.sort()
            self.sorted==True

        todo = len(self.sims)-k
        while todo>0:
            self.sims.pop()

    def display(self):
        print self.word+"\t"+self.id+"\t"+self.freq+"\t"+self.width+"\n"
        print self.sims




class SimMatrix:

    def __init__(self,directory):
        self.dir=directory
        self.index="entries.strings"
        self.simsfile="sims"
        self.freqfile="entries.totals"
        self.entrydict = {} # word --> entry
        self.reverseentrydict={} # id --> entry


        #read files
        self.readindex()
        self.readtotals()
        self.readsims()


    def readindex(self):

        filename=self.dir+self.index
        instream=open(filename,'r')
        print "Reading "+filename
        linesread=0
        for line in instream:
            linesread+=1
            l=line.rstrip()
            fields=l.split("\t")
            word=fields[0]
            id=fields[1]
            self.entrydict[word]=Entry(word,id)
            self.reverseentrydict[id]=self.entrydict[word]

        instream.close()
        print "Read "+str(linesread)+" lines"


    def readtotals(self):

        filename=self.dir+self.freqfile
        instream=open(filename,'r')
        print "Reading "+filename
        linesread=0
        for line in instream:
            linesread+=1
            l=line.rstrip()
            fields=l.split("\t")
            word=fields[0]
            freq=fields[1]
            width=fields[2]
            self.entrydict[word].updatetotals(freq,width)

        instream.close()
        print "Read "+str(linesread)+" lines"

    def readsims(self):

        filename=self.dir+self.simsfile
        instream=open(filename,'r')
        print "Reading "+filename
        linesread=0
        for line in instream:
            linesread+=1
            l=line.rstrip()
            fields=l.split("\t")
            fields.reverse()
            id=fields.pop()
            self.reverseentrydict[id].updatesims(fields)
            if linesread%1000==0:
                print "Read "+str(linesread)+" lines"
                break
        instream.close()





if __name__ =="__main__":
    parameters = conf.configure(sys.argv)
    mymatrix= SimMatrix(parameters["directory"])
    for entry in mymatrix.entrydict.values():
        entry.topk(k)
        entry.display()
