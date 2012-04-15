#!/bin/bash

EXP_DIR=/home/kalgan/experiments/fsearch/home

for experiment in $(ls $EXP_DIR/*.xml)
do
	fileName=$(basename $experiment)
	if [ $fileName != AllMeasures.xml ];
	then
		python Experiment.py -c $EXP_DIR -i $(basename $experiment) -d True -w ~/ -o ~/
	fi
done
