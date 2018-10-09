import numpy as np
import math 

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)
     def invert(self):
         size = len(self.items)
         for i in range((int)(size/2)):
             itemTem = self.items[i]
             self.items[i]= self.items[size - i -1]
             self.items[size -i -1]=itemTem


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
	D=1.0
	dx = math.fabs(node.mX - goal.mX)
	dy = math.fabs(node.mY - goal.mY)
	return D*math.sqrt(dx*dx+dy*dy)

def isEqual(node1:Coordinate,node2:Coordinate):
	return (node1.mX == node2.mX and node1.mY==node2.mY)
		
def isGoToTheWall(current:Coordinate,x,y,maps):
	return (maps[current.mX+x][current.mY+y]==1)
def isLegalMove(current:Coordinate,x,y,maps,size):
	return (current.mX + x >= 0 and current.mY + y >=0 and 
				current.mX + x < size and current.mY + y < size 
				and not(x == y == 0) and not isGoToTheWall(current,x,y,maps))
def isPassedNode(currentNode:Coordinate,passedNodes):
	for node in passedNodes:
		if(node.mX==currentNode.mX and node.mY==currentNode.mY):
			return True;
	return False;



def pathFinding(source:Coordinate, goal: Coordinate, maps,size,path):
	path.push(source)
	passedNodes=[]
	passedNodes.extend([source])

	nextNode = source
	AStartOfNextNode=Euclidean_heuristic(source,goal)

	while (path.size()>0):
		current = path.peek()
		if(isEqual(current,goal)):
			print('yeahhhhhh')
			break
		#Loop from 1 to 8 position around current postion
		#to find out which is best next position for robot to move
		for i in range(-1,2):
			for j in range(-1,2):
				if(isLegalMove(current,i,j,maps,size)):
					node = Coordinate(current.mX+i,current.mY+j)
					AStartOfNode = Euclidean_heuristic(node,goal)
					if (AStartOfNode < AStartOfNextNode 
						and not isPassedNode(node,passedNodes)):
						AStartOfNextNode = AStartOfNode
						nextNode = node
		if(not isEqual(current,nextNode)):
			##Robot can move to next position
			passedNodes.extend([nextNode])
			path.push(nextNode)
			maps[nextNode.mX][nextNode.mY]=2
		else:
			#Robot can not move to next position
			#Robot need to rollback
			############
			maps[current.mX][current.mY]=0
			path.pop()
			if(isEqual(current,source)):
				break
			current=path.peek()
			nextNode=current
			AStartOfNextNode=Euclidean_heuristic(nextNode,goal)
	return maps,path


def writeOutputData(outputPath,maps,size,source:Coordinate,goal:Coordinate, step,path):
	outputFile = open(outputPath,"w")

	outputFile.write('%d\n'%step)
	#for node in path:
	path.invert()
	while (not path.isEmpty()):
		node = path.peek()
		path.pop()
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
	path = Stack()
	source = Coordinate(0,0)
	goal = Coordinate(0,0)
	maps=[[]]
	mapsSize = 0
	maps,mapsSize,source,goal = readInputData(INPUT_PATH,maps,mapsSize,source,goal)
	maps,path = pathFinding(source,goal,maps,mapsSize,path)
	step = path.size()
	print(maps,step);
	writeOutputData(OUTPUT_PATH,maps,mapsSize,source,goal, step,path)
if __name__ == '__main__':
	main()
