#!/bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: `basename $0` {testset} {outputdir}"
  	exit $E_BADARGS
fi

mkdir $2

for FILE in $(ls $1)
do
	command="python Experiment.py -c $1 -f $FILE -o $2/output-$FILE.txt"
	echo "Running $command"
	$command
done
