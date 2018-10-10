# seeing-double
Identifying binary stars using their light curves only

To generate a training and testing set, clone this repository and cd into it.

The function assemble_data in 'make_training_set.py' will generate synthetic
light curves and save them to a directory of your choice (default is current
directory). Example usage:

'''python
lc_dir = "/Users/ruthangus/.kplr/data/lightcurves"
assemble_data(10, lc_dir, ftrain=.8, fdouble=.5, ndays=70, path=".",
                saveplot=True)
'''
