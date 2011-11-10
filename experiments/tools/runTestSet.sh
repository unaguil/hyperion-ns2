#!/bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: `basename $0` {testset} {outputdir}"
  	exit $E_BADARGS
fi

testname=$(basename $1)-`date '+%Y-%m-%d-%H-%M-%S'`

mkdir $2
mkdir $2/$testname

for FILE in $(ls $1)
do
	command="python Experiment.py -c $1 -f $FILE -o $2/$testname/output-$FILE.txt"
	echo "Running $command"
	$command
done
