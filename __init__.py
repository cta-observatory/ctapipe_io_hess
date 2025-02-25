import astropy.units as u
import pytest
from astropy.coordinates import EarthLocation
from traitlets import TraitError
from traitlets.config.loader import Config

from ctapipe.containers import ArrayEventContainer
from ctapipe.core import Component
from ctapipe.io import DataLevel, EventSource, SimTelEventSource

#Add julia wrapper imports
from juliacall import Main as jl, convert as jlconvert

jl.seval("using UnROOT")

def PrintElement(myfile,elementname):
    jlstore = jl.seval("(k, v) -> (@eval $(Symbol(k)) = $v; return)")
    jlstore("myfile",myfile)
    jl.seval('f=ROOTFile(myfile)')
    jlstore("elementname",elementname)
    print(jl.seval("f"))
    myelement=jl.seval("f[elementname]")
    print(myelement)
    return myelement

def ReadSashDataset(myfile,elementname):
    #Reads Sash Dataset
    jlstore = jl.seval("(k, v) -> (@eval $(Symbol(k)) = $v; return)")
    jlstore("myfile",myfile)
    jl.seval('f=ROOTFile(myfile)')
    jlstore("elementname",elementname)
    #myelement=jl.seval("f[elementname]")
    hessarray = jl.seval("UnROOT.array(f, elementname, raw=true)")
    print(hessarray)
    return hessarray

def ReadTTreeLazyTree(myfile,treename,elementname):
    #Reads TTree
    jlstore = jl.seval("(k, v) -> (@eval $(Symbol(k)) = $v; return)")
    jlstore("myfile",myfile)
    jl.seval('f=ROOTFile(myfile)')
    jlstore("treename",treename)
    jlstore("elementname",elementname)
    jl.seval("macro p_str(s) s end")
    jl.seval('println(f,treename,Regex(join([elementname,\d/f.*])))')
    hesstree = jl.seval('t=LazyTree(f, treename, [Regex(join([elementname,r"\d/f.*"]))])')
    jl.seval('println(t)')
    print(hesstree)
    return hesstree

def ReadTTreeArray(myfile,elementname):
    #Reads TTree                                                                                                       
    jlstore = jl.seval("(k, v) -> (@eval $(Symbol(k)) = $v; return)")
    jlstore("myfile",myfile)
    jl.seval('f=ROOTFile(myfile)')
    jl.seval("treename",treename)
    jlstore("elementname",elementname)
    hessarray = jl.seval("LazyTree(f, elementname, raw=true)")
    print(names(hessarray))
    return hessarray


def DSTReader(filename,elementname):
    '''This function needs to contain a wrapper around julia code to read in data from a specific tree in the root file.'''
    #Needs to first open the ROOT DST, then determine the type of the tree
    myfile=openrootfile(filename)
    #Need to test hess era, and somehow check which telescopes present
    #From filename extract runnumber
    runnumber=filename[:10] #Check to read just the runnumber from the file
    
    if rumnumber<16000: #Check these runnumber limits
        subarray=hess1
    elif runnumber < 160000 and runnumber > 16000:
        subarray=hess2
    elif runnumber >160000:
        subarray=hessflashcam

    typeelement = myfile[reference] #Some sort of wrapped julia code here to determine DST element type

    if typeelement==SashDataSet:
        hessarray=ReadSashDataset(myfile,elementname)
    elif typeelement==TTree:
        hessarray=ReadTTree(myfile,elementname)
    #Add more elemtn types here
    
    return hessarray, subarray

class HESSEventSource(EventSource):
    """
    Simple working EventSource
    """

    def _generator(self):
        for i in range(5):
            myeventcontainer=ArrayEventContainer(count=i)
            #For every field in the arrayeventcontainer class, create instances of factories and fill with hess arrays i.e.
            pointing=TelescopePointingContainer()
            pointing.azimuth=DSTReader(filename,azimuthtreename)
            pointing.altitude=DSTReader(filename,altitudetreename)
            myeventcontainer.pointing=pointing

            yield myeventcontainer

    @staticmethod
    def is_compatible(file_path):
        with open(file_path, "rb") as f:
            marker = f.read(5)
        return marker == b"dummy"

    @property
    def subarray(self):
        return None

    @property
    def is_simulation(self):
        return False

    @property
    def scheduling_blocks(self):
        return dict()

    @property
    def observation_blocks(self):
        return dict()

    @property
    def datalevels(self):
        return (DataLevel.R0,)

    @property
    def reference_location(self):
        #Change this to the hess site
        return EarthLocation(lat=0, lon=0 * u.deg, height=0 * u.deg)


if __name__=="__main__":
    myfile="/lfs/l7/hess/users/marandon/CalibData/CT5/dst_NewScheme2/run023400-023599/run_023523_DST_001.root"
    #elementname="MuonStats_tree/TelescopeMuonEfficiency_1"
    treename="MuonStats_tree"
    elementname="TelescopeMuonEfficiency_"
    #PrintElement(myfile,elementname)
    #ReadSashDataset(myfile,elementname)
    ReadTTreeLazyTree(myfile, treename, elementname)
