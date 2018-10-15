import math
import heapq
import numpy as np
import math
import pygame

INPUT_PATH = 'input.txt'
OUTPUT_PATH = "output.txt"

"""
Colors for graph
The Wall (1): brown rgb(165, 42, 42)
Maps (0): silver rgb(192, 192, 192)
Opened node (3): bisque rgb(255, 228, 196)
Current_node (node is passed by robot) (4): darkorange rgb(255, 140, 0)
Source (8): aqua rgb(0, 255, 255)
Goal (9): violet rgb(238, 130, 238)
path (2): green rgb(0, 128, 0)
"""
BROWN = (165, 42, 42)
SILVER = (192, 192, 192)
BISQUE = (255, 228, 196)
DARKORANGE = (255, 140, 0)
AQUA = (0, 255, 255)
VIOLET = (238, 130, 238)
GREEN = (0, 128, 0)

MARGIN = 2
WINDOW_SIZE = []
WIDTH = 20
HEIGHT = 20


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

def g_value(g_valueOfparent):
	return g_valueOfparent +1
def Euclidean_heuristic(node, goal):
    D=2.5
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
    
    maps[source[0]][source[1]]=8
    maps[goal[0]][goal[1]]=9
    global WINDOW_SIZE
    WINDOW_SIZE = [WIDTH*size+size*MARGIN,HEIGHT*size+size*MARGIN]

    inputFile.close()
    return maps,size,source,goal
def writeOutputData(outputPath,graph,source,goal,path):
    outputFile = open(outputPath,"w")

    step = len(path)+2
    outputFile.write('%d\n'%step)

    #soure
    outputFile.write('({},{})\t'.format(source[0],source[1]))
    #path
    if(step>0):
        for (x,y) in path:
            outputFile.write('({},{})\t'.format(x,y))
    #goal
    outputFile.write('({},{})\n'.format(goal[0],goal[1]))

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

def aStarSearch(graph,source,goal,screen,clock):
    openList = PriorityQueue();

    passedList = []
    passedList.append(source)

    g_values={}
    g_values[source]=0

    parentNode = {}
    parentNode[source]=0
    openList.push(Euclidean_heuristic(source,goal),source)
    
    path = []
    drawMaps(graph,source,goal,screen)

    while not openList.empty():

        current = openList.get();
        current_node = current[1]
        graph.maps[current_node[0]][current_node[1]]=4

        if(current_node == goal):
            print('yeahhhhhh')
            path = reTrackingPath(graph,parentNode,current_node)
            drawPathLine(graph,goal,path,screen)
            break;

        for neighbor in graph.neighbors(current_node):
            neighbor_g_value =  g_value(g_values[current_node])
            if(neighbor not in passedList):
                graph.maps[neighbor[0]][neighbor[1]]=3
                AStartValueOfNeighbor = neighbor_g_value + Euclidean_heuristic(neighbor,goal)
                g_values[neighbor]=neighbor_g_value
                openList.push(AStartValueOfNeighbor,neighbor)
                parentNode[neighbor]=current_node
                passedList.append(neighbor)
                print(neighbor,AStartValueOfNeighbor,neighbor_g_value,Euclidean_heuristic(neighbor,goal))
        drawProcess(graph,source,screen)
        clock.tick(60)
    return path
def reTrackingPath(graph,parentNode,current_node):
	path =[]
	#node before goal
	current_node=parentNode[current_node];

	while parentNode[current_node] != 0:
		graph.maps[current_node[0]][current_node[1]]=2
		path.append(current_node)
		current_node = parentNode[current_node]
	path.reverse()    
	return path
def wait():
	while True:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				return
def drawMaps(graph,source,goal,screen):
	maps = graph.maps
	# fill full maps
	screen.fill(SILVER)
	for (x,y),value in np.ndenumerate(maps):
		#if The Wall
		if(maps[x][y]==1):
			pygame.draw.rect(screen,BROWN,[(WIDTH+MARGIN)*y+MARGIN,(HEIGHT+MARGIN)*x+MARGIN,WIDTH,HEIGHT])
	pygame.draw.rect(screen,AQUA,[(WIDTH+MARGIN)*source[1]+MARGIN,(HEIGHT+MARGIN)*source[0]+MARGIN,WIDTH,HEIGHT])
	pygame.draw.rect(screen,VIOLET,[(WIDTH+MARGIN)*goal[1]+MARGIN,(HEIGHT+MARGIN)*goal[0]+MARGIN,WIDTH,HEIGHT])
	pygame.display.flip()

def drawProcess(graph,source,screen):
	maps = graph.maps
	for (x,y),value in np.ndenumerate(maps):
		#if Opened nodes
		if(maps[x][y]==3):
			pygame.draw.rect(screen,BISQUE,[(WIDTH+MARGIN)*y+MARGIN,(HEIGHT+MARGIN)*x+MARGIN,WIDTH,HEIGHT])
		#if passed nodes
		elif(maps[x][y]==4):
			pygame.draw.rect(screen,DARKORANGE,[(WIDTH+MARGIN)*y+MARGIN,(HEIGHT+MARGIN)*x+MARGIN,WIDTH,HEIGHT])
	#draw source node again to distinguish with passed nodes
	pygame.draw.rect(screen,AQUA,[(WIDTH+MARGIN)*source[1]+MARGIN,(HEIGHT+MARGIN)*source[0]+MARGIN,WIDTH,HEIGHT])
	pygame.display.flip()

def drawPathLine(graph,goal,path,screen):
	pygame.draw.rect(screen,VIOLET,[(WIDTH+MARGIN)*goal[1]+MARGIN,(HEIGHT+MARGIN)*goal[0]+MARGIN,WIDTH,HEIGHT])
	for (x,y) in path:
		pygame.draw.rect(screen,GREEN,[(WIDTH+MARGIN)*y+MARGIN,(HEIGHT+MARGIN)*x+MARGIN,WIDTH,HEIGHT])
	pygame.display.flip()

def main():
    maps,size,source,goal= readInputData(INPUT_PATH)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("A* Search")
    clock = pygame.time.Clock()

    graph = Graph(maps,size)

    path = aStarSearch(graph, source, goal,screen,clock)

    #print(maps)
    #pygame.time.delay(5000)
    wait()
    
    writeOutputData(OUTPUT_PATH,graph,source,goal,path)


if __name__ == '__main__':
    main()









