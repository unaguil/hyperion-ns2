#!/bin/bash

python Experiment.py -c configurations/comparison -i FloodedSearchInterval.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FloodedSearchCL.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FloodedSearchPause.xml -d True -o ~/ -w ~/
