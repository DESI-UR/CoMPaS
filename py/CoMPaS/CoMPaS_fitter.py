
import numpy

import sys

import random

import pkg_resources

class fitter:

    def __init__(self, module_name):
        self._module_name = module_name
        self._module      = __import__(self._module_name)
        self._function    = getattr(self._module, 'evaluate')
        self._cosmo_config= None
        
    def evaluate(self, var):
        value = self._function(var)
        return value
    
    def run_integration(self):
        return

    
    def get_cosmo_config(self):
        return self._cosmo_config
    
    def set_cosmo_config(self, config):
        print(config)
        if isinstance(config, str):
            # configuration is given as a file
            # no need further processing it
            self._cosmo_config = config
        elif isinstance(config, numpy.ndarray) or isinstance(config, list):
            # the configuration is given as array
            # we need to process it so that KITCAT
            # can run properly
            # First, we read the template provided
            # with the package
            data_path = pkg_resources.resource_filename('CoMPaS', 'data/')
            print(data_path)
            filename = "/tmp/config_{}.ini".format(random.getrandbits(64))
            # #### WRITE TO TEMP FILE #### #
            self._cosmo_config = filename
            
f = fitter('example_fitter')
f.set_cosmo_config([1., 2., 3.])
print(f.evaluate(3))
