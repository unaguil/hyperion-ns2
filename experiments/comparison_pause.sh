#!/bin/bash

for i in 3 5 7
do
	python Experiment.py -c configurations/fgraphsearch_pause -i FloodedSearchPause$i.xml -d True -o ~/ -w ~/
	python Experiment.py -c configurations/fgraphsearch_pause -i FGraphSearchPause$i.xml -d True -o ~/ -w ~/
done
