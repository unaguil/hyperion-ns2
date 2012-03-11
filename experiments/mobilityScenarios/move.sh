#!/bin/bash

name=mobility-100-200-700-700-0.00-5.00-1000

counter=0
for n in 2 3 5 11 12 13 14 15 17 18
do
	file=$name-$n.txt
	destination=/tmp/$name-$counter.txt
	echo "Renaming $file to $destination"
	cp $file $destination
	let counter+=1
done
