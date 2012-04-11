#!/bin/bash

#python Experiment.py -c ~/experiments/multicast/high/static -i NonRepeatServicesFixedScenario.xml -d True -w ~/static -o ~/static
python Experiment.py -c ~/experiments/multicast/high/100 -i SimultaneousSearches.xml -d True -w ~/100 -o ~/100
python Experiment.py -c ~/experiments/multicast/high/50 -i SimultaneousSearches.xml -d True -w ~/50 -o ~/50
