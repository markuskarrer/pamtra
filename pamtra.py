#!/usr/bin/env python
"""
python implementation of pamtra.

"""

from optparse import OptionParser
import pyPamtra
import pyPamtraImport

parser = OptionParser()
parser.add_option("-n", "--namelist", dest="namelist",help="namelist file (default run_params.nml)",default="run_params.nml")
parser.add_option("-p", "--profile", dest="profile",help="profile file  (default standard.dat)", default="standard.dat")
parser.add_option("-t", "--type", dest="type",help="type of profile file  (default pamtraAscii1Mom)", default="pamtraAscii1Mom")
parser.add_option("-d", "--descriptor", dest="descriptor",help="descriptor file  (default descriptor_file.txt)", default="descriptor_file.txt")
parser.add_option("-f", "--freqs", dest="freqs",help="comma seperated list of frequencies (no blanks) (default 89.0)", default="89.0")
parser.add_option("-o", "--output", dest="output", help="output netcdf file (default output.nc)", default="output.nc")
parser.add_option("-l", "--parallelpython", dest="parallelpython",help="no. of processor to use (default 1)", default=1)
parser.add_option("-v", "--verbosity", dest="verbosity",help="verbosity of python part (default 1)", default=1)

(options, args) = parser.parse_args()

nmlFile = str(options.namelist)
profFile = str(options.profile)
profType = str(options.type)
freqs = options.freqs.split(",")
outFile=str(options.output)
parallelpython = int(options.parallelpython)
verbosity = int(options.verbosity)
descriptorFile = str(options.descriptor)
#import pdb;pdb.set_trace()

#read data
if profType == "pamtraAscii1Mom":
  pam = pyPamtra.pyPamtra()
  pam.readPamtraProfile(profFile)
  
elif profType == "pamtraAscii2Mom":
  pam = pyPamtra.pyPamtra() 
  pam.nmlSet["moments"]["n_moments"] = 2
  pam.readPamtraProfile(profFile)  
  
elif profType == "cosmoColGopSchneeferner":
  pam = pyPamtraImport.readCosmoDe1MomDataset(profFile,"collum",forecastIndex = 1,colIndex=0,tmpDir="/tmp/",fnameInTar="*Schneeferner*",concatenateAxis=1,debug=False,verbosity=verbosity)
  
else:
  raise ValueError("I don't know type="+profType)

pam.set["pyVerbosity"] = verbosity
  
#load and use nml file
pam.readNmlFile(nmlFile) #nml options needs to be known to pyPamtra as well!
pam.set["namelist_file"] = nmlFile # -> skip step of writing temporary nml file!

#read descriptorFile
pam.df.readFile(descriptorFile)


#run pamtra
if parallelpython>1:
  pam.runParallelPamtra(freqs,pp_servers=(),pp_local_workers=parallelpython,pp_deltaF=1,pp_deltaX=10,pp_deltaY = 10)  
else:
  pam.runPamtra(freqs)  

#write results
pam.writeResultsToNetCDF(outFile,profileVars="all",ncForm="NETCDF3_CLASSIC")
