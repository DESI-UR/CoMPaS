
import numpy

import sys

import random

import configparser

import importlib.util as iu

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
                    
    def evaluate(self):
        running = False
        output = os.system("$(squeue -u {} | grep {})".format(self._user, self._jobid))
        while len(output) > 1: # this needs to be checked on the cluster. not sure
            # script is still running.
            # wait till it is complete
            running = True
            output = os.system("$(squeue -u {} | grep {})".format(self._user, self._jobid))
        value = self._function(self._output)
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
        self._user     = slurm_config.get('config', 'user')
        self._partition= slurm_config.get('config', 'partition')
        self._walltime = slurm_config.get('config', 'walltime')
        self._mem      = slurm_config.get('config', 'memory')
        self._envcmd   = slurm_config.get('config', 'environment_command')
        self._jobname  = "integration"
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
            os.mkdir("/scratch/{}/tmp".format(self._user))
        except:
            continue
        try:
            os.mkdir("/scratch/{}/tmp/scripts".format(self._user))
        except:
            continue
        try:
            os.mkdir("/scratch/{}/tmp/results".format(self._user))
        except:
            continue
        
        self._output = "/scratch/{}/tmp/output_{}".format(self._user, random.getrandbits(64))

        # the command line to execute for the slurm job is constructed here.
        sbatch_cmd = "#!/bin/bash \n" + \
            "\n" + \
            "#SBATCH --export=ALL \n" + \
            "#SBATCH --mem={} \n".format(self._mem) + \
            "#SBATCH --time={} \n".format(self._walltime) + \
            "#SBATCH --job-name={} \n".format(self._jobname) + \
            "#SBATCH --error={} \n".format(errfile) + \
            "#SBATCH --output={} \n".format(logfile) + \
            "#SBATCH --partition={} \n".format(self._partition)
        sbatch_cmd +=  "\n"

        # the execution line is constructed here. the user must have provided an environment call
        # in the configuration file.
        exec_cmd = "{} \n".format(self._envcmd) + \
            "srun KITCAT_integrate -p {} ".format(self._prefix) + \
            "-o {}".format(self._output)
            "-c {} ".format(self._cosmo_config)

        # the scripts are stored in the temporary directory in user's scratch area
        if tempdir == None:
            tempdir = '/scratch/{}/tmp/scripts'.format(self._user)

        # the complete batch job script is written here.
        filename = "{}/{}.sh".format(tempdir, self._jobname)
        fid = open(filename, "w")
        fid.write("{}{}".format(sbatch_cmd, exec_cmd))
        fid.close()

        # there are no dependent jobs upon this particular job.
        # in any case, it is defined empty.
        extra_arg = ""

        # this method stores the job id on the computer cluster
        # this will be later used for holding the fitter methid.
        self._jobid = os.system("$(sbatch --parsable {} {})".format(extra_arg, filename))
        
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
