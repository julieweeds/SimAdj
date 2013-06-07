__author__ = 'juliewe'

import conf
import sys
import math
import numpy
import scipy.stats as stats
import matplotlib.pyplot as plt

def makesimlist(list):
    simlist = []
    while len(list)>0:
        id = list.pop()
        score=float(list.pop())
        simlist.append((score,id))
    return simlist

def mymean(total,count):
    return float(total)/float(count)

def mysd(squaretotal,total,count):
    mean = mymean(total,count)
    var=float(squaretotal)/float(count)-mean*mean
    if var <0:
        print "Warning: negative variance "+str(var)
        var=0
    return (mean,math.pow(var,0.5))

class Entry:

    def __init__(self,word,freq,width,k):
        self.word=word
        self.freq=freq
        self.width=width
        self.sims=[] #list of tuples (score,id)
        self.sorted=False
        self.size=0
        self.maxsim=-1
        self.avsim=-1
        self.sdsim=-1
        self.nosims=0
        self.totalsims=0
        self.totalsquares=0
        self.analysed=False
        self.k=k


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
        self.k=k

    def display(self):
        print self.word+"\t"+"\t"+str(self.freq)+"\t"+str(self.width)
        #print self.sims
        if self.nosims>0:
            print self.nosims, self.maxsim, self.avsim, self.sdsim
        print ""

    def output(self,outstream):
        outstream.write(self.word)
        for (score,word) in self.sims:
            outstream.write("\t"+word+"\t"+str(score))
        outstream.write("\n")

    def analyse(self):
        if self.analysed==False:
            for (score,neigh) in self.sims:
                if score > self.maxsim:
                    self.maxsim=score
                self.totalsims+=score
                self.totalsquares+=score*score
                self.nosims+=1
            (self.avsim,self.sdsim)=mysd(self.totalsquares,self.totalsims,self.k)
        self.analysed=True

    def garbage(self):
        self.sims=[] #remove list of tuples once processed to free memory

class SimMatrix:

    def __init__(self,directory,k,flag,simsfile,testing):
        self.dir=directory
        self.simsfile=simsfile
        self.freqfile="entries.totals"
        self.outfile=self.simsfile+".adj"
        self.neighfile=self.simsfile+".adj.neighbours"
        self.entrydict = {} # word --> entry
        self.k=k
        self.maxwidth=0
        self.maxfreq=0
        self.adj_constant=0
        self.adjust_flag=flag #whether to adjust similarities
        self.testing=testing
        self.filteredS=["___FILTERED___"]

        if self.testing:
            self.batchcount=1000
        else:
            self.batchcount=1000

        self.analysed=False #have the entries been analysed statistically

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
                if word in self.filteredS:
                    print "Excluding entry for "+word
                else:
                    freq=int(fields[1])
                    width=int(fields[2])
                    self.entrydict[word]=Entry(word,freq,width,self.k)
                    if width > self.maxwidth:
                        self.maxwidth=width
                    if freq > self.maxfreq:
                        self.maxfreq=freq
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
        if self.adjust_flag:
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
            if word in self.filteredS:
                print "Excluding entry for "+word
            else:
                if word in self.entrydict.keys():
                    self.adjust(word,fields)  #adjust and add similarities
                    if self.adjust_flag:
                        self.entrydict[word].output(outstream)          #write sims output file if sims are adjusted
                    if self.entrydict[word].nosims>self.k:
                        self.entrydict[word].topk(self.k)   #keep only top k neighbours
                    if self.adjust_flag:
                        self.entrydict[word].display()  #display
                        self.entrydict[word].output(neighstream) #write neigh outputfile if sims are adjusted
                    self.entrydict[word].analyse() #compute stats for entry
                    self.entrydict[word].garbage()  #free memory
                else:
                    print "Error - no entry for word "+word
                    exit(1)
            if linesread%self.batchcount==0:
                print "Processed "+str(linesread)+" lines"
                if self.testing:
                    break
        if self.adjust_flag:
            neighstream.close()
            outstream.close()
        instream.close()
        print "Finished reading input."

    def output_neighs(self):

        print "Generating neighbour file...."

        neighstream=open(self.dir+self.neighfile,'w')
        done=0
        for word in self.entrydict.keys():
            if len(self.entrydict[word].sims)>0:
                self.entrydict[word].topk(self.k)   #keep only top k neighbours
                self.entrydict[word].display()  #display
                self.entrydict[word].output(neighstream)                                #write neighbour output file
            done+=1
            if done%self.batchcount==0:
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
                    entry.sims.append((score,neigh))
            else:
                entry.sims.append((score,neigh))

    def analyse(self):
        count=0
        maxtotal=0
        maxsquaretotal=0
        avtotal=0
        avsquaretotal=0
        grandtotal=0
        grandtotalcount=0
        grandsquaretotal=0

        for entry in self.entrydict.values():
            if entry.nosims>0:
                entry.analyse()
                #entry.display()
                count+=1
                maxtotal+=entry.maxsim
                maxsquaretotal+=entry.maxsim*entry.maxsim
                avtotal+=entry.avsim
                avsquaretotal+=entry.avsim*entry.avsim
                grandtotal+=entry.totalsims
                grandsquaretotal+=entry.totalsquares
                grandtotalcount+=entry.k

        (maxmean,maxsd)=mysd(maxsquaretotal,maxtotal,count)
        (avmean,avsd)=mysd(avsquaretotal,avtotal,count)
        (grandmean,grandsd)=mysd(grandsquaretotal,grandtotal,grandtotalcount)
        print "For nearest neighbour, mean similarity = "+str(maxmean)+", sd ="+str(maxsd)
        print "For all neighbours (k="+str(self.k)+"), mean mean similarity = "+str(avmean)+", sd = "+str(avsd)
        print "For all entries (n="+str(count)+"), mean similarity = "+str(grandmean)+", sd = "+str(grandsd)
        self.analysed=True

    def correlate(self):
        if self.analysed==False:
            self.analyse()
        x1s=[]
        x2s=[]
        y1s=[]
        y2s=[]
        name=[] #array of names associated with numpy arrays
        array=[]#array of numpy arrays
        for entry in self.entrydict.values():
            if entry.nosims>0:
                x1s.append(entry.width)
                x2s.append(entry.freq)
                y1s.append(entry.maxsim)
                y2s.append(entry.avsim)
        array=[numpy.array(x1s),numpy.array(x2s),numpy.array(y1s),numpy.array(y2s)]
        name=["width","freq","maxsim","avsim"]
        limit=[self.maxwidth,self.maxfreq,1,1]


        for i in range(len(name)):
            for j in range(len(name)):
                if j>i:
                    thispoly= numpy.poly1d(numpy.polyfit(array[i],array[j],1))

                    pr=stats.spearmanr(array[i],array[j])
                    mytitle = name[j]+" against "+name[i]
                    print mytitle
                    print "Spearman's r = "+str(pr[0])+" with p value = "+str(pr[1])
                    print thispoly
                    self.showpoly(array[i],array[j],thispoly,mytitle,pr,limit[i],limit[j])

    def showpoly(self,x,y,poly,title,pr,xl,yl):
        xp=numpy.linspace(0,xl,100)
        plt.plot(x,y,'.',xp,poly(xp),'-')
        plt.ylim(0,yl)
        plt.title(title)
        mytext1="srcc = "+str(pr[0])
        mytext2="p = "+str(pr[1])
        plt.text(0.05,yl*0.9,mytext1)
        plt.text(0.05,yl*0.8,mytext2)
        plt.show()


if __name__ =="__main__":
    parameters = conf.configure(sys.argv)

    if parameters["adj_neighs"]:
        simsfile="neighbours.strings"
    else:
        simsfile="sims"
    mymatrix= SimMatrix(parameters["directory"],parameters["k"],parameters["adjust_flag"],simsfile,parameters["testing"])
   # mymatrix.output_neighs()

