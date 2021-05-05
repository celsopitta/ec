
try:
    import binutil  # required to import from dreamcoder modules
except ModuleNotFoundError:
    import bin.binutil  # alt import if called as module

from dreamcoder.domains.arc.main import arc_options, main
from dreamcoder.recognition import DummyFeatureExtractor
from dreamcoder.dreamcoder import commandlineArguments
from dreamcoder.utilities import numberOfCPUs


if __name__ == '__main__':
    # print(retrieveARCJSONTasks('/Users/theo/Development/program_induction/ARC/data/training/007bbfb7.json')[1])

    args = commandlineArguments(
        enumerationTimeout=10, activation='tanh', iterations=10, recognitionTimeout=3600, 
        maximumFrontier=10, topK=2, pseudoCounts=1.0,
        helmholtzRatio=0, structurePenalty=1.,
        CPUs=numberOfCPUs(),
        extras=arc_options)
    main(args)