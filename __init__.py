import astropy.units as u
import pytest
from astropy.coordinates import EarthLocation
from traitlets import TraitError
from traitlets.config.loader import Config

from ctapipe.containers import ArrayEventContainer
from ctapipe.core import Component
from ctapipe.io import DataLevel, EventSource, SimTelEventSource

#Add julia wrapper imports

def ReadSashDataset(myfile,elementname):
    #Reads Sash Dataset
    return hessarray

def ReadTTree(myfile,elementname):
    #Reads TTree
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
