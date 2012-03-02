#!/bin/bash

if [ "$#" -eq 1 ]
then
	for experiment in CompositionLength.xml CompositionWidth.xml SDistribution.xml SearchFreq.xml
	do
		python Experiment.py -c ~/experiments/fsearch/basic/$1 -i $experiment -d True -w ~/ -o ~/
	done
else
	echo "Argument with pause configuration time expected"
fi
