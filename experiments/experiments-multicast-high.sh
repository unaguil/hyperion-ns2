#!/bin/bash

python Experiment.py -c ~/experiments/multicast/high/$1 -i InvalidSearches.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/high/$1 -i RepeatServicesFixedScenario.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/high/$1 -i NonRepeatServicesFixedScenario.xml -d True -w ~/ -o ~/
