#!/bin/bash

python Experiment.py -c configurations/comparison -i FloodedSearchPause.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FGraphSearchPause.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FloodedSearchCL.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FGraphSearchCL.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FloodedSearchCW.xml -d True -o ~/ -w ~/
python Experiment.py -c configurations/comparison -i FGraphSearchCW.xml -d True -o ~/ -w ~/
