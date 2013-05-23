__author__ = 'juliewe'

import conf
import sys
import math


class Entry:

    def __init__(self,word,freq,width):
        self.word=word
        self.freq=freq
        self.width=width
        self.sims=[] #list of tuples (score,id)
        self.sorted=False
        self.size=0


    def updatesims(self,list):

        while len(list)>0:
            id = list.pop()
            score = float(list.pop())
            self.sims.append((score,id))
            self.size+=1

#        print self.word+"\t"+str(self.size)

    def topk(self,k):

        if self.sorted == False:
            self.sims.sort()
            self.sims.reverse()
            self.sorted==True

        todo = len(self.sims)-k
        #print k, len(self.sims), todo
        while todo>0:
            self.sims.pop()
            todo-=1

    def display(self):
        print self.word+"\t"+"\t"+str(self.freq)+"\t"+str(self.width)
        print self.sims
        print ""

    def output(self,outstream):
        outstream.write(self.word)
        for (score,word) in self.sims:
            outstream.write("\t"+word+"\t"+str(score))
        outstream.write("\n")



class SimMatrix:

    def __init__(self,directory,k):
        self.dir=directory
        self.simsfile="sims"
        self.freqfile="entries.totals"
        self.outfile=self.simsfile+".adj"
        self.neighfile=self.simsfile+".adj.neighbours"
        self.entrydict = {} # word --> entry
        self.k=k
        self.maxwidth=0
        self.adj_constant=0

        #read files
        self.readtotals()
        self.readsims()


    def readtotals(self):

        filename=self.dir+self.freqfile
        instream=open(filename,'r')
        print "Reading "+filename
        linesread=0
        for line in instream:

            l=line.rstrip()
            fields=l.split("\t")
            if len(fields)==3: #valid data line
                word=fields[0]
                freq=int(fields[1])
                width=int(fields[2])
                self.entrydict[word]=Entry(word,freq,width)
                if width > self.maxwidth:
                    self.maxwidth=width
                linesread+=1

        instream.close()
        print "Read "+str(linesread)+" lines"
        self.setconstants()

    def setconstants(self):
        self.adj_constant = 2*float(self.maxwidth)


    def readsims(self):

        filename=self.dir+self.simsfile
        outfile=self.dir+self.outfile
        neighfile=self.dir+self.neighfile
        instream=open(filename,'r')
        outstream=open(outfile,'w')
        neighstream=open(neighfile,'w')
        print "Reading "+filename
        linesread=0
        for line in instream:
            linesread+=1
            l=line.rstrip()
            fields=l.split("\t")
            fields.reverse()
            word=str(fields.pop())
            if word in self.entrydict.keys():
                self.entrydict[word].updatesims(fields)  #read in sims
                self.adjust(word)                                    #adjust similarities for word
                self.entrydict[word].output(outstream)          #write sims output file
                self.entrydict[word].topk(self.k)   #keep only top k neighbours
                #self.entrydict[word].display()  #display
                self.entrydict[word].output(neighstream)                                #write neighbour output file
            else:
                print "Error - no entry for word "+word
                exit(1)
            if linesread%1000==0:
                print "Processed "+str(linesread)+" lines"
                #break

        neighstream.close()
        outstream.close()
        instream.close()


    def adjust(self,word):
        #needs to be done at this level because need access to width/frequency info for all words
        entry = self.entrydict[word]
        mywidth = float(entry.width)
        newsims=[]
        for (score,neigh) in entry.sims:
            if neigh in self.entrydict.keys():
                neighwidth = float(self.entrydict[neigh].width)
                adjfactor=2*mywidth*neighwidth/(mywidth+neighwidth) #harmonic mean of widths
                adj = math.pow(self.adj_constant/adjfactor,0.5)
                sim=1.0-(1.0/(score*adj + 1.0))
                newsims.append((sim,neigh))
            else:
                print "Error: target word not in dictionary "+neigh
                newsims.append((score,neigh))
        entry.sims=newsims


if __name__ =="__main__":
    parameters = conf.configure(sys.argv)
    mymatrix= SimMatrix(parameters["directory"],parameters["k"])
