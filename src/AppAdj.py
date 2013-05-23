__author__ = 'juliewe'

import conf
import sys
import math


def makesimlist(list):
    simlist = []
    while len(list)>0:
        id = list.pop()
        score=float(list.pop())
        simlist.append((score,id))
    return simlist

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

    def addsimlist(self,simlist):
        self.sims.append(simlist)
        self.size=len(self.sims)

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

    def __init__(self,directory,k,flag):
        self.dir=directory
        self.simsfile="sims"
        self.freqfile="entries.totals"
        self.outfile=self.simsfile+".adj"
        self.neighfile=self.simsfile+".adj.neighbours"
        self.entrydict = {} # word --> entry
        self.k=k
        self.maxwidth=0
        self.adj_constant=0
        self.adjust_flag=flag #whether to adjust similarities

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

        print "Reading "+filename
        linesread=0
        for line in instream:
            linesread+=1
            l=line.rstrip()
            fields=l.split("\t")
            fields.reverse()
            word=str(fields.pop())
            if word in self.entrydict.keys():
                self.adjust(word,fields)  #adjust and add similarities
                self.entrydict[word].output(outstream)          #write sims output file
            else:
                print "Error - no entry for word "+word
                exit(1)
            if linesread%1000==0:
                print "Processed "+str(linesread)+" lines"
                #break


        outstream.close()
        instream.close()
        print "Finished reading input.  Generating neighbour file...."

        neighstream=open(neighfile,'w')
        done=0
        for word in self.entrydict.keys():
            if len(self.entrydict[word].sims)>0:
                self.entrydict[word].topk(self.k)   #keep only top k neighbours
                self.entrydict[word].display()  #display
                self.entrydict[word].output(neighstream)                                #write neighbour output file
            done+=1
            if done%1000==0:
                print "Completed "+str(done)+" neighbour sets"
        neighstream.close()


    def adjust(self,word,fields):
        #needs to be done at this level because need access to width/frequency info for all words
        entry = self.entrydict[word]
        mywidth = float(entry.width)
        oldsims=makesimlist(fields)
        for (score,neigh) in oldsims:
            if self.adjust_flag:
                if neigh in self.entrydict.keys():
                    neighwidth = float(self.entrydict[neigh].width)
                    adjfactor=2*mywidth*neighwidth/(mywidth+neighwidth) #harmonic mean of widths
                    adj = math.pow(self.adj_constant/adjfactor,0.5)
                    sim=1.0-(1.0/(score*adj + 1.0))
                    entry.sims.append((sim,neigh))
                else:
                    print "Error: target word not in dictionary "+neigh
                    entry.append((score,neigh))
            else:
                entry.append((score,neigh))


if __name__ =="__main__":
    parameters = conf.configure(sys.argv)
    mymatrix= SimMatrix(parameters["directory"],parameters["k"],parameters["adjust_flag"])
