import numpy as np 

n=30;
source = (1,2)
goal = (28,15)
outputFile = open("test.txt","w")
outputFile.write('%d\n'%n)
outputFile.write('{} {}\n'.format(source[0],source[1]))
outputFile.write('{} {}\n'.format(goal[0],goal[1]))

matrix = np.random.randint(2,size=(n,n))
for i in range(100):
    x = np.random.randint(30)
    y = np.random.randint(30)
    matrix[x][y]=0
matrix[source[0]][source[1]]=0
matrix[goal[0]][goal[1]]=0

for (x,y),value in np.ndenumerate(matrix):
    outputFile.write('%d '%value)
    if(y == (n-1)):
        outputFile.write('\n')

