
import numpy

import sys

import random

import configparser

import importlib.util as iu

#
#
# AT THIS POINT, I AM NOT CERTAIN WHETHER THE INTEGRATION SHOULD BE A PART OF THIS
# MODULE OR NOT. SO I AM STARTING AS IF IT SHOULD BE A PART OF IT.
# LATER I MAY CHANGE IT.
#

class fitter:

    def __init__(self, module_name, prefix):
        self._module_spec = iu.spec_from_file_location('fitter', module_name)
        self._module      = iu.module_from_spec(self._module_spec)
        self._module_spec.loader.exec_module(self._module)
        self._function    = self._module.evaluate
        self._cosmo_config= None
        self._slurm_config= ""
        self._prefix      = prefix
                    
    def evaluate(self, var):
        value = self._function(var)
        return value
    
    def run_integration(self, config=None):
        # it is possible that the user might have called the set_cosmo_config function
        # prior to calling this method. if not, the user should provide the information
        # yo this method.
        if config is not None:
            self.set_cosmo_config(config)

        # the configuration for the slurm job is read
        slurm_config = configparser.RawConfigParser()
        slurm_config.read(self._slurm_config)
        user     = slurm_config.get('config', 'user')
        partition= slurm_config.get('config', 'partition')
        walltime = slurm_config.get('config', 'walltime')
        mem      = slurm_config.get('config', 'memory')
        envcmd   = slurm_config.get('config', 'environment_command')
        jobname  = "integration"
        try:
            logfile  = slurm_config.get('config', 'logfile')
        except configparser.NoOptionError:
            logfile  = "/tmp/{}_log".format(jobname)
        try:
            errfile  = slurm_config.get('config', 'errorfile')
        except configparser.NoOptionError:
            errfile  = "/tmp/{}_err".format(jobname)

        # the scratch directory of the user is checked whether the required subdirectories
        # do exist. if not, they are created. in actuality, the script attempts to create
        # them, and if it fails it means they exist.
        try:
            os.mkdir("/scratch/{}/tmp".format(user))
        except:
            continue
        try:
            os.mkdir("/scratch/{}/tmp/scripts".format(user))
        except:
            continue
        try:
            os.mkdir("/scratch/{}/tmp/results".format(user))
        except:
            continue
        
        self._output = "/scratch/{}/tmp/output_{}".format(user, random.getrandbits(64))

        # the command line to execute for the slurm job is constructed here.
        sbatch_cmd = "#!/bin/bash \n" + \
            "\n" + \
            "#SBATCH --export=ALL \n" + \
            "#SBATCH --mem={} \n".format(mem) + \
            "#SBATCH --time={} \n".format(walltime) + \
            "#SBATCH --job-name={}_{} \n".format(jobname, executable) + \
            "#SBATCH --error={}_{} \n".format(errfile, executable) + \
            "#SBATCH --output={}_{} \n".format(logfile, executable) + \
            "#SBATCH --partition={} \n".format(partition)
        sbatch_cmd +=  "\n"

        # the execution line is constructed here. the user must have provided an environment call
        # in the configuration file.
        exec_cmd = "{} \n".format(envcmd) + \
            "srun KITCAT_integrate -p {} ".format(self._prefix) + \
            "-o {}".format(self._output)
            "-c {} ".format(self._cosmo_config)

        # the scripts are stored in the temporary directory in user's scratch area
        if tempdir == None:
            tempdir = '/scratch/{}/tmp/scripts'.format(user)

        # the complete batch job script is written here.
        filename = "{}/{}_{}.sh".format(tempdir, jobname, executable)
        fid = open(filename, "w")
        fid.write("{}{}".format(sbatch_cmd, exec_cmd))
        fid.close()

        # there are no dependent jobs upon this particular job.
        # in any case, it is defined empty.
        extra_arg = ""

        # the return value for this method is the job id on the computer cluster
        # this will be later used for holding the fitter methid.
        return os.system("$(sbatch --parsable {} {})".format(extra_arg, filename))

    def set_slurm_config(self, config):
        self._slurm_config = config
    
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
            data_path        = "{}/data".format(sys.prefix)
            temp_config_file = "{}/configs/example.ini".format(data_path)
            filename         = "/tmp/config_{}.ini".format(random.getrandbits(64))
            self._cosmo_config = filename
            temp_config = configparser.ConfigParser()
            temp_config.read(temp_config_file)
            
            if isinstance(config, numpy.ndarray) or isinstance(config, list):
                h0 = config[0]
                omega_m0 = config[1]
                omega_de0 = 1-omega_m0
            elif isinstance(config, dict):
                h0 = config['h0']
                omega_m0 = config['omega_m0']
                omega_de0 = 1-omega_m0
            else:
                raise Exception('inproper config input')
            temp_config['COSMOLOGY']['hubble0'] = "{}".format(h0)
            temp_config['COSMOLOGY']['omega_m0'] = "{}".format(omega_m0)
            temp_config['COSMOLOGY']['omega_de0'] = "{}".format(omega_de0)
            with open(self._cosmo_config, "w") as cfile:
                temp_config.write(cfile)

if __name__ == "__main__":
    f = fitter('/home/tyapici/DESI_Projects/CoMPaS/py/compas/example_fitter/fitter.py')
    f.set_cosmo_config([1., 2., 3.])
    print(f.evaluate(3))
