#!/bin/bash

python Experiment.py -c ~/experiments/multicast/high/$1 -i CompositionLength.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/high/$1 -i Distribution.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/high/$1 -i Replication.xml -d True -w ~/ -o ~/
python Experiment.py -c ~/experiments/multicast/high/$1 -i SearchFreq.xml -d True -w ~/ -o ~/

