from DiffusionProject.Evaluation.Experiments import debugExperiment
from DiffusionProject.Algorithms.Walks import Backend

BACKEND = Backend(use_GPU=False)

experiment = debugExperiment(BACKEND,2)
experiment.run()
experiment = debugExperiment(BACKEND,3)
experiment.run()