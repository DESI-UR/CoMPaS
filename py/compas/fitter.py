
import numpy

import sys

import random

import importlib.util as iu

from configparser import SafeConfigParser

class fitter:

    def __init__(self, module_name):
        self._module_spec = iu.spec_from_file_location('fitter', module_name)
        self._module      = iu.module_from_spec(self._module_spec)
        self._module_spec.loader.exec_module(self._module)
        self._function    = self._module.evaluate
        self._cosmo_config= None
        
    def evaluate(self, var):
        value = self._function(var)
        return value
    
    def run_integration(self):
        return

    def get_cosmo_config(self):
        return self._cosmo_config
    
    def set_cosmo_config(self, config):
        if isinstance(config, str):
            # configuration is given as a file
            # no need further processing it
            self._cosmo_config = config
        elif isinstance(config, numpy.ndarray) or \
             isinstance(config, list) or \
             isinstance(config, dict):
            # the configuration is given as array
            # we need to process it so that KITCAT
            # can run properly
            # First, we read the template provided
            # with the package
            data_path   = "{}/data".format(sys.prefix)
            temp_config = "{}/configs/example.ini".format(data_path)
            filename    = "/tmp/config_{}.ini".format(random.getrandbits(64))
            self._cosmo_config = filename
            config = SafeConfigParser()
            config.read(temp_config)
            print(config)

            
f = fitter('/home/tyapici/DESI_Projects/CoMPaS/py/compas/example_fitter/fitter.py')
f.set_cosmo_config([1., 2., 3.])
print(f.evaluate(3))
