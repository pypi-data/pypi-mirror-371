import glob
import numpy as np
import matplotlib.pylab as plt
import astropy.io.fits as fits

import pyklip.instruments.JWST as JWST
import pyklip.klip as klip

filelist = glob.glob("../../../DataCopy/jwst/1386/F1140C/jw*calints.fits")
filelist.sort()
print(len(filelist))
for filename in filelist:
    print(filename)

dataset = JWST.JWSTData(filepaths=filelist[:2], psflib_filepaths=filelist[2:])

print(dataset.mask_centers)