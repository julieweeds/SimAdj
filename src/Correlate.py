
import sys, conf, AppAdj

if __name__=="__main__":
    parameters = conf.configure(sys.argv)
    parameters["adjust_flag"]=False
    simsfile="neighbours.strings"
    mymatrix= AppAdj.SimMatrix(parameters["directory"],parameters["k"],parameters["adjust_flag"],simsfile,parameters["testing"])

    for entry in mymatrix.entrydict.values():
        if len(entry.sims)>0:

            entry.analyse()
            entry.display()
