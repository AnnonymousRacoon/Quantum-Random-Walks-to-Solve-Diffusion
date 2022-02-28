from DiffusionProject.Evaluation.Experiments import debugExperiment
from DiffusionProject.Algorithms.Walks import Backend

BACKEND = Backend(use_GPU=True)

experiment = debugExperiment(BACKEND,2)
experiment.run()
experiment = debugExperiment(BACKEND,3)
experiment.run()