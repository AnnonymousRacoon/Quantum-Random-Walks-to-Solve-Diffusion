import sys
from DiffusionProject.JobManager.config import Config

if __name__ =="__main__":
    config_path = str(sys.argv[1])
    config = Config(config_path)
    config.process_IBM_results()