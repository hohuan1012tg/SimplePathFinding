import math
import heapq
import numpy as np


INPUT_PATH = 'input.txt'
OUTPUT_PATH = "output.txt"

class Graph:
    def __init__(self,maps,size):
        self.maps=maps
        self.size = size

    def in_bounds(self,node):
        (x,y)=node
        return 0<= x < self.size and 0 <= y < self.size

    def isNotTheWall(self,node):
        (x,y) = node
        return self.maps[x][y]!=1

    def neighbors(self,node):
        (x,y)=node
        neighborsList = [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y+1),(x+1,y+1),(x+1,y),(x+1,y-1),(x,y-1)]
        neighborsList = list(filter(self.in_bounds,neighborsList))
        neighborsList = list(filter(self.isNotTheWall,neighborsList))
        return neighborsList

class PriorityQueue:
    def __init__(self):
        self.items=[]

    def empty(self):
        return len(self.items)==0

    def push(self,aStarValueOfItem,item):
        heapq.heappush(self.items,(aStarValueOfItem,item))

    def get(self):
        return heapq.heappop(self.items)



def Euclidean_heuristic(node, goal):
    D=1.0
    (x,y)=node;
    (a,b)=goal;
    dx = math.fabs(x - a)
    dy = math.fabs(y - b)
    return D*math.sqrt(dx*dx+dy*dy)

def readInputData(inputPath):
    inputFile = open(inputPath,'r')
    indata = inputFile.read()
    indata = indata.strip().split();
    indata = [int(i) for i in indata]
    size = indata[0];

    source =(indata[1],indata[2]);
    goal = (indata[3],indata[4]);

    indata = indata[5:]
    maps = np.reshape(indata,(-1,size))
    inputFile.close()
    
    return maps,size,source,goal
def writeOutputData(outputPath,graph,source,goal,path):
    outputFile = open(outputPath,"w")

    step = len(path)
    outputFile.write('%d\n'%step)

    #for node in path:
    # path.invert()
    # while (not path.isEmpty()):
    #     node = path.peek()
    #     path.pop()
    #     outputFile.write('({},{})\t'.format(node.mX,node.mY))
    for i in range(len(path)-1,0,1):
        outputFile.write('{}\t',path[i])
    outputFile.write('\n')

    maps = graph.maps
    size = graph.size


    pathingMap = [['']*size for i in range(size)]
    pathingMap = np.reshape(pathingMap,(-1,size))

    for (x,y), value in np.ndenumerate(maps):
        if (value==2):
            pathingMap[x][y]='x'
        elif (value == 1):
            pathingMap[x][y]='o';
        else:
            pathingMap[x][y]='-'
    pathingMap[source[0]][source[1]]='S'
    pathingMap[goal[0]][goal[1]]='G'

    for (x,y), value in np.ndenumerate(pathingMap):
        outputFile.write('%s '%value)
        if(y == (size-1)):
            outputFile.write('\n')
    outputFile.close()

def aStarSearch(graph,source,goal):
    openList = PriorityQueue();

    passedList = []
    parentNode = {}

    openList.push(Euclidean_heuristic(source,goal),source)
    parentNode[source]=0
    passedList.append(source)
    path = []

    while not openList.empty():

        current = openList.get();
        current_node = current[1]

        if(current_node == goal):
            print('yeahhhhhh')
            while parentNode[current_node] != 0:
                graph.maps[current_node[0]][current_node[1]]=2
                path.append(current_node)
                current_node = parentNode[current_node]
            break;

        for neighbor in graph.neighbors(current_node):
            if(neighbor not in passedList):
                AStartValueOfNeighbor = Euclidean_heuristic(neighbor,goal)
                openList.push(AStartValueOfNeighbor,neighbor)
                parentNode[neighbor]=current_node
                passedList.append(neighbor)
    return path

def main():

    maps,size,source,goal= readInputData(INPUT_PATH)
    graph = Graph(maps,size)

    path = aStarSearch(graph, source, goal)

    print(path)
    print(maps)

    writeOutputData(OUTPUT_PATH,graph,source,goal,path)


if __name__ == '__main__':
    main()









