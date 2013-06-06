
import sys, conf, AppAdj

if __name__=="__main__":
    parameters = conf.configure(sys.argv)
    parameters["adjust_flag"]=False
    simsfile="sims.adj.neighbours"
    mymatrix= AppAdj.SimMatrix(parameters["directory"],parameters["k"],parameters["adjust_flag"],simsfile,parameters["testing"])

    mymatrix.analyse()
    mymatrix.correlate()
