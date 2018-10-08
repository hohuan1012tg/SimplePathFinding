import numpy as np
import math 
class Coordinate:
	__slots__ = ["mX","mY"]
	def __init__(self, x,y):
		self.mX=x
		self.mY=y


INPUT_PATH = 'input.txt'
OUTPUT_PATH = "output.txt"

def readInputData(inputPath,maps, size, source: Coordinate,goal:Coordinate):
	inputFile = open(inputPath,'r')
	indata = inputFile.read()
	indata = indata.strip().split();
	indata = [int(i) for i in indata]
	size = indata[0];

	source = Coordinate(indata[1],indata[2]);
	goal = Coordinate(indata[3],indata[4]);

	indata = indata[5:]
	maps = np.reshape(indata,(-1,size))
	inputFile.close()
	return maps,size,source,goal

def Euclidean_heuristic(node: Coordinate, goal: Coordinate):
	D=1
	dx = math.fabs(node.mX - goal.mX)
	dy = math.fabs(node.mY - goal.mY)
	return D*math.sqrt(dx*dx+dy*dy)


def pathFinding(source: Coordinate, goal: Coordinate, maps, size, path):
	totalSteps = size*size
	nextNode = source
	currentNodeDistance = Euclidean_heuristic(source,goal)
	path.extend([source])
	passedNodes=[]
	passedNodes.extend([source])

	for k in range(totalSteps):

		if (source.mX==goal.mX and source.mY==goal.mY):
			print("yeahhhhhh")
			return maps , path;
		#Loop from 1 to 8 position around current postion
		#to find out which is best next position for robot to move
		for i in range(-1,2):
			for j in range(-1,2):
				if(source.mX + i >= 0 and source.mY + j >=0 and 
				source.mX + i < size and source.mY +j < size 
				and not(i == j == 0)):
					if(maps[source.mX+i][source.mY+j]!=1):
						Node = Coordinate(source.mX+i,source.mY+j)
						Distance = Euclidean_heuristic(Node,goal)
						if(Distance < currentNodeDistance 
							and not isPassedNode(Node,passedNodes)):
							currentNodeDistance = Distance
							nextNode = Node
		##Robot can move to next position
		if(source.mX != nextNode.mX or source.mY!= nextNode.mY):
			source = nextNode
			maps[source.mX][source.mY]=2
			path.extend([source])
			passedNodes.extend([source])
			currentNodeDistance = Euclidean_heuristic(source,goal)
		else:
			#Robot can not move to next position
			#Robot need to rollback
			############
			removedNode = path[len(path)-1]
			maps[removedNode.mX][removedNode.mY]=0
			path=path[:-1]

			source=path[len(path)-1]
			nextNode = source
			currentNodeDistance = Euclidean_heuristic(source,goal)
	return  maps , path;

def isPassedNode(currentNode:Coordinate,passedNodes):
	for node in passedNodes:
		if(node.mX==currentNode.mX and node.mY==currentNode.mY):
			return True;
	return False;

def writeOutputData(outputPath,maps,size,source:Coordinate,goal:Coordinate, step,path):
	outputFile = open(outputPath,"w")

	outputFile.write('%d\n'%step)
	for node in path:
		outputFile.write('({},{})\t'.format(node.mX,node.mY))
	outputFile.write('\n')

	pathingMap = [['']*size for i in range(size)]
	pathingMap = np.reshape(pathingMap,(-1,size))

	for (x,y), value in np.ndenumerate(maps):
		if (value==2):
			pathingMap[x][y]='x'
		elif (value == 1):
			pathingMap[x][y]='o';
		else:
			pathingMap[x][y]='-'
	pathingMap[source.mX][source.mY]='S'
	pathingMap[goal.mX][goal.mY]='G'

	for (x,y), value in np.ndenumerate(pathingMap):
		outputFile.write('%s '%value)
		if(y == (size-1)):
			outputFile.write('\n')
	outputFile.close()

def main():
	path = []
	source = Coordinate(0,0)
	goal = Coordinate(0,0)
	maps=[[]]
	mapsSize = 0
	maps,mapsSize,source,goal = readInputData(INPUT_PATH,maps,mapsSize,source,goal)
	maps,path = pathFinding(source,goal,maps,mapsSize,path)
	step = len(path)
	print(maps);
	writeOutputData(OUTPUT_PATH,maps,mapsSize,source,goal, step,path)
if __name__ == '__main__':
	main()
