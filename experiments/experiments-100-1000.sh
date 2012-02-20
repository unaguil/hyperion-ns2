#!/bin/bash

python Experiment.py -c ~/experiments/multicast/basic/1000 -i InvalidSearches.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/basic/1000 -i RepeatServicesFixedScenario.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/basic/1000 -i NonRepeatServicesFixedScenario.xml -d True -w ~/ -o ~/
