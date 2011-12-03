#!/bin/python

import sys
import os

def main():
	if len(sys.argv) < 2:
		print 'Usage: CreateMeasureNames.py [measuresDir]'
		sys.exit()

	startingDir = sys.argv[1]
	if not os.path.isdir(startingDir):
		print 'Passed argument must be a directory'
		sys.exit()

	results = []
	createNames(startingDir, startingDir, results)
	for name in results:
		print '%s = ' % name

def createNames(currentPath, currentName, results):
	for entry in os.listdir(currentPath):
		if not '.svn' in entry and not '__' in entry and not '.pyc' in entry:
			path = currentPath + '/' + entry
			name = currentName + '.' + entry
			if os.path.isdir(path):
				createNames(path, name, results)
			else:
				results.append(name.split('.py')[0])

if __name__ == '__main__':
	main()
