#!/bin/bash

mkdir ~/experiment3
nohup python Experiment.py -c ~/experiments/discovery/experiment3/ -i TTL.xml -d True -w ~/experiment3 -o ~/experiment3 &
