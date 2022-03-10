import yaml
import math
import subprocess
from datetime import datetime
from DiffusionProject.Utils.geometry import BoundaryGenerator

class Config:
    def __init__(self,path) -> None:
        self.__config = self.parse_config(path)
        self.__experiment_params = self.__config.get("ExperimentParams")
        self.__job_params = self.__config.get("JobParams")
        self.n_dims = self.__experiment_params.get("NDims")
        self.n_dimensional_qubits = self.__experiment_params.get("NQubits")
        self.boundaries = self.__experiment_params.get("Boundaries")
        self.job_files = []
        self.__savepath = None
        self.path = path

    @property
    def savepath(self):
        """path to save files, autogenerated using config `Name` and the date"""
        # only generate once
        if self.__savepath == None:
            now = datetime.now()
            dt_string = now.strftime("-%d-%m-%Y-%H-%M-%S")
            self.__savepath = "$WORK/Results/" + self.__config.get("Name","Experiment") + dt_string
        return self.__savepath


    def _build_job_filetree(self):
        """generate a directory to save job files"""
        subprocess.run("mkdir jobs", shell=True)

    def _build_save_directory(self):
        """generate a directory for output files"""
        # gen folder
        subprocess.run('mkdir {}'.format(self.savepath), shell=True)
        # copy config
        subprocess.run('cp $WORK/{} {}'.format(self.path, self.savepath), shell=True)
        # create list of `.pbs` files
        subprocess.run('touch {}/job_list.txt'.format(self.savepath), shell=True)
     
    @staticmethod
    def parse_config(path: str) -> dict:
        """parses the config `.yml` file at location `path`. Returns the """
        with open(path, "r") as yamlfile:
            data = yaml.load(yamlfile, Loader = yaml.FullLoader)
        
        return data

    @property
    def required_mem(self):
        """The maximum amount of system memory required to simulate the quantum system described by this config"""
        return (10**-9)*8*2**self.n_system_qubits

    @property
    def n_system_qubits(self):
        """The theoretical total number of qubits required to simulate the system, does not include overheads"""
        n_spacial_qubits = self.n_dims * self.n_dimensional_qubits
        n_boundary_qubits = 0

        for boundary in self.boundaries:
            n_boundary_qubits += boundary.get("n_qubits",0)
        
        return n_boundary_qubits + n_spacial_qubits

    def _write_boundary_string(self):
        """appends args to set boundary conditions in a call to `DiffusionProject.JobManager.Driver.py`"""
        boundary_string = ""

        for boundary in self.boundaries:
            if boundary.get("Geometry"):
                
                if boundary["Geometry"] == "Edges":
                    bitstrings = BoundaryGenerator.generate_boundaries(boundary["Geometry"],self.n_dimensional_qubits,boundary.get("Padding",0))

                # default to all dims if no dimension specified
                if boundary.get("Dim"):
                    dims = [boundary["Dim"]]
                else:
                    dims = [i for i in range(self.n_dims)]

                # apply all bitstrings to all dimensions specified
                for dimension in dims:
                    for bitstring in bitstrings:
                       boundary_string = boundary_string + ' --b {}-{}-{}-{}-{}'.format(boundary["Type"], dimension, bitstring, boundary.get("ControlClass",""), boundary.get("NQubits",""))

            
            else:
                # if boundary is fully defined by the user
                boundary_string = boundary_string +' --b {}-{}-{}-{}-{}'.format(boundary["Type"],boundary["Dim"],boundary["Bitstring"],boundary.get("ControlClass",""),boundary.get("NQubits",""))

        return boundary_string
        
    def _write_experiment_string(self, n_steps, use_GPU = False, IBM_device_name = None):
        python_call = ""

        driver_path = '/rds/general/user/db3115/home/DiffusionProject/JobManager/Driver.py'
        python_call = python_call + 'python3 {} --nd {} --nq {} --ns {}'.format(driver_path,self.n_dims,self.n_dimensional_qubits,n_steps)
    
        python_call = python_call + self._write_boundary_string()
        
        if self.__experiment_params.get("InitialState"):
            python_call = python_call +' --in {}'.format(self.__experiment_params.get("InitialState"))
        if self.__experiment_params.get("Coin"):
            python_call = python_call + ' --c {}'.format(self.__experiment_params.get("Coin"))
        if use_GPU:
            python_call = python_call + ' --GPU 1'
        if self.__experiment_params.get("Shots"):
            python_call = python_call + ' --s {}'.format(self.__experiment_params.get("Shots"))
        if IBM_device_name:
            python_call = python_call + ' --IBMDeviceName {}'.format(IBM_device_name)

        return python_call

    def _write_experiment(self, file, n_steps, use_GPU = False):
        file.write(self._write_experiment_string(n_steps, use_GPU))
        file.write("\n")
        self._write_file_transfer(file)


    def _write_file_transfer(self,file):
        file.write('cp -r * {}\n'.format(self.savepath))

    def _generate_batch_steps(self) -> list:
        """Divides up the experiments into batches"""
        batches = []
        batch_params = self.__experiment_params["BatchParams"]
        stepsize = batch_params["StepSize"]
        start = batch_params["StartIterations"]
        batchsize = self.__job_params.get("BatchSize",5)
        max_iterations = batch_params["MaxIterations"]

        n_steps = start
        batch = []
        while n_steps <= max_iterations:
            if len(batch) == batchsize:
                batches.append(batch)
                batch = []
            batch.append(n_steps)
            n_steps+=stepsize
        batches.append(batch)
        return batches
        

    def _generate_job_files(self):
        """generates the `.pbs` job files required to tun experiments"""
        if self.__experiment_params.get("Type","Single") == "Single":
            self._generate_job_file([self.__experiment_params["NSteps"]])
        else:
            batches = self._generate_batch_steps()
            for batch in batches:
                self._generate_job_file(batch)

    def _generate_job_file(self,step_numbers):
        """generates a `.pbs` jobs file """

        filename = 'batch{}.pbs'.format(len(self.job_files))
        use_GPU = self.__job_params.get("UseGPU", False)

        with open('jobs/{}'.format(filename), 'w') as f:
            f.write('#!/bin/bash\n')

            # PBS Settings
            if use_GPU:
                GPU = self.__job_params.get("GPUType", "P100")
                nGPUs = self.__job_params.get("NGPUs", 1)
                nCPUs = 4*nGPUs
                mem = 24*nGPUs
                walltime = min(self.__job_params.get('Walltime',24),24)
                f.write('#PBS -lselect=1:ncpus={}:mem={}gb:ngpus={}:gpu_type={}\n'.format(nCPUs,mem,nGPUs,GPU))
            else:
                walltime = min(self.__job_params.get('Walltime',72),72)
                nCPUs = self.__job_params.get("NCPUs", 8)
                mem = max(math.ceil(self.required_mem), self.__job_params.get("Memory",0))
                f.write('#PBS -lselect=1:ncpus={}:mem={}gb\n'.format(nCPUs,mem))
            f.write('#PBS -lwalltime={}:00:00\n'.format(walltime))

            # Keep tabs on job ID
            f.write('echo $PBS_JOBID >> {}/job_list.txt\n'.format(self.savepath))
            # setup load python
            f.write('source $WORK/test-env/bin/activate\n')
            f.write('export PYTHONPATH="${PYTHONPATH}:/rds/general/user/db3115/home/"\n')
            # run experiments
            for n_steps in step_numbers:
                self._write_experiment(f,n_steps, use_GPU)
            f.write('echo "BATCH COMPLETE"\n')

        self.job_files.append(filename)

    def _submit_job_files(self,verbose = True):
        for jobfile in self.job_files:
            subprocess.run("qsub jobs/{}".format(jobfile),shell=True)
        if verbose:
            subprocess.run("qstat -w -T", shell = True)


    def _remove_job_files(self):
        subprocess.run("rm -r jobs", shell=True)


    def _run_on_PBS(self):
        self._build_job_filetree()
        self._build_save_directory()
        self._generate_job_files()
        self._submit_job_files()
        if not self.__config.get("KeepJobFiles", False):
            self._remove_job_files()


    def _run_on_IBM(self):
        """run a single experiment on IBM devices"""
        assert self.__experiment_params.get("Type","Single") == "Single"
        device_name = self.__job_params.get('IBMDeviceName')
        subprocess.run(self._write_experiment_string(IBM_device_name=device_name))


    def run(self):
        if self.__job_params.get('IBMDeviceName'):
            self._run_on_IBM()
        else:
            self._run_on_PBS()

        
