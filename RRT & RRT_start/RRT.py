import pygame
from RRTbasePy import RRTGraph
from RRTbasePy import  RRTMap
import time


import pygame
from RRTbasePy import RRTGraph
from RRTbasePy import RRTMap
import time

def main():
    dimensions =(512,512)
    start=(50,50)
    goal = (400, 400)
    obsdim=30
    obsnum=60
    iteration=0
    t1 = 0

    pygame.init()
    map = RRTMap(start, goal, dimensions, obsdim, obsnum)
    graph = RRTGraph(start, goal, dimensions, obsdim, obsnum)

    obstacles = graph.makeobs()
    map.drawMap(obstacles)

    t1=time.time()
    while (not graph.path_to_goal()):
    # for i in range(100):
        time.sleep(0.005)
        elapsed = time.time()-t1
        t1 = time.time()
        #raise exception if timeout
        if elapsed > 10:
            print('timeout re-initiating the calculations')
            raise

        if iteration % 10 == 0:
            X, Y, Parent = graph.bias(goal)
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)

        else:
            X, Y, Parent = graph.expand()
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad*2, 0)
            pygame.draw.line(map.map, map.Blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]),
                             map.edgeThickness)


        if iteration % 5 == 0:
            pygame.display.update()
        iteration += 1

    map.drawPath(graph.getPathCoords())
    pygame.display.update()
    pygame.event.clear()
    #pygame.quit()
    pygame.event.wait(0)




if __name__ == '__main__':


    result=False
    while not result:
        try:
            main()
            result=True
        except:
            result=False

# x, y = graph.sample_envir()
# n = graph.number_of_nodes()
# graph.add_node(n, x, y)
# graph.add_edge(n-1, n)
# x1, y1 = graph.x[n], graph.y[n]
# x2, y2 = graph.x[n-1], graph.y[n-1]
# if graph.isFree():
#     pygame.draw.circle(map.map, map.Red, (graph.x[n],graph.y[n]), map.nodeRad, map.noeThickness)
#     if not graph.crossObstacle(x1, x2, y1, y2):
#         pygame.draw.line(map.map, map.Blue, (x1,y1), (x2,y2), map.edgeThickness)