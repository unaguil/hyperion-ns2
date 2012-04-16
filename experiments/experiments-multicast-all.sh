#!/bin/bash

mkdir ~/100
nohup python Experiment.py -c ~/experiments/multicast/high/100 -i InvalidSearches.xml -d True -w ~/100 -o ~/100 &
nohup python Experiment.py -c ~/experiments/multicast/high/100 -i RepeatServicesFixedScenario.xml -d True -w ~/100 -o ~/100 &
nohup python Experiment.py -c ~/experiments/multicast/high/100 -i NonRepeatServicesFixedScenario.xml -d True -w ~/100 -o ~/100 &

mkdir ~/50
nohup python Experiment.py -c ~/experiments/multicast/high/50 -i InvalidSearches.xml -d True -w ~/50 -o ~/50 &
nohup python Experiment.py -c ~/experiments/multicast/high/50 -i RepeatServicesFixedScenario.xml -d True -w ~/50 -o ~/50 &
nohup python Experiment.py -c ~/experiments/multicast/high/50 -i NonRepeatServicesFixedScenario.xml -d True -w ~/50 -o ~/50 &

