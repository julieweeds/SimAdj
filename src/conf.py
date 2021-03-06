__author__ = 'juliewe'

import re

def configure(arguments):

    factorPATT=re.compile('f=(.*)')

    parameters={}
    #set defaults
    #location
    parameters["on_apollo"]=True
    parameters["at_home"]=False
    parameters["local"]=False
    #metric
    parameters["metric"]="cosine"
    #feature type
    parameters["features"]="deps"
    #byblo neighbours
    parameters["byblo"]=True
    #thesaurus
    parameters["corpus"]="giga"
    parameters["thresholds"]="t100f100"
    parameters["pos"]="nouns"

    parameters["k"]=1000
    #do adjustments
    parameters["adjust_flag"]=True
    parameters["adj_neighs"]=True #adjust neighs file or sims file
    parameters["testing"]=False
    parameters["fr_method"]="none"
    parameters["factors"]=1000



    for argument in arguments:

        if argument == "on_apollo":
            parameters["on_apollo"]=True
            parameters["at_home"]=False
            parameters["local"]=False
        if argument == "local":
            parameters["on_apollo"]=False
            parameters["at_home"]=False
            parameters["local"]=True
        if argument == "at_home":
            parameters["on_apollo"]=False
            parameters["at_home"] =True
            parameters["local"]=False
        if argument == "cosine":
            parameters["metric"]="cosine"
        if argument == "lin":
            parameters["metric"]="lin"
        if argument == "linadj":
            parameters["metric"]="linadj"
        if argument == "windows":
            parameters["features"]="wins"
        if argument == "deps":
            parameters["features"]="deps"
        if argument == "byblo":
            parameters["byblo"]=True
        if argument =="nouns":
            parameters["pos"]=["N"]
        if argument == "adjust=False":
            parameters["adjust_flag"]=False
        if argument == "adjust=True":
            parameters["adjust_flag"]=True
        if argument == "testing":
            parameters["testing"]=True
        if argument=="nmf":
            parameters["fr_method"]="nmf"
        if argument=="svd":
            parameters["fr_method"]="svd"
        matchobj=factorPATT.match(argument)
        if matchobj:
            parameters["factors"]=matchobj.group(1)



    if parameters["features"]=="wins":
        parameters["windows"]=True
    else:
        parameters["windows"]=False


    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):

 #   if parameters["at_home"]:
 #       parameters["parent"] ="C:/Program Files/WordNet/2.1/dict/"
 #       parameters["out"]="C:/Users/Julie/Documents/Github/WordNet/data/"
    if parameters["local"]:
        parameters["parent"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/SimAdj/data/"
 #       parameters["out"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/WordNet/data/"
        #parameters["simsdir"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/STS/data/trial/STS2012-train/"
 #       parameters["simsdir"]="/Volumes/LocalScratchHD/juliewe/Documents/workspace/ThesEval/data/giga_t100/"

    if parameters["on_apollo"]:
        parameters["parent"]="/mnt/lustre/scratch/inf/juliewe/FeatureExtractionToolkit/Byblo-2.2.0/"

    if parameters["at_home"]:
        parameters["parent"]="C:/Users/Julie/Documents/Github/Wordnet/data/"

    parameters["thesaurus"]=parameters["corpus"]+"_"+parameters["thresholds"]+"_"+parameters["pos"]+"_"+parameters["features"]+"/"

    if parameters["fr_method"] != "none":
        parameters["thesaurus"]=parameters["thesaurus"]+parameters["fr_method"]+str(parameters["factors"])+"/"

    parameters["directory"]=parameters["parent"]+parameters["thesaurus"]

    return parameters


