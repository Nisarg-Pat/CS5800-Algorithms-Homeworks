#!/usr/local/bin/python3
############################################################
# Starter code for solving flow problems in graphs
# April 2022
#
############################################################
import sys
import os
import numpy as np

import simplegraphs
import simplegraphs as sg

MAX_WIDTH = 2000
MAX_HEIGHT = 2000


def gold(coords):
    # write your code here
    G = sg.emptyGraph(0)
    s = "S"
    t = "T"
    black = set()
    white = set()
    for x, y in coords:
        if x % 2 == y % 2:
            black.add((x, y))
        else:
            white.add((x, y))
    if len(black) != len(white):
        print("No solution exists")
        return
    for x, y in black:
        sg.addDirEdge(G, s, (x, y), 1)
        if (x, y + 1) in white:
            sg.addDirEdge(G, (x, y), (x, y + 1), 1)
        if (x, y - 1) in white:
            sg.addDirEdge(G, (x, y), (x, y - 1), 1)
        if (x - 1, y) in white:
            sg.addDirEdge(G, (x, y), (x - 1, y), 1)
        if (x + 1, y) in white:
            sg.addDirEdge(G, (x, y), (x + 1, y), 1)
    for x, y in white:
        sg.addDirEdge(G, (x, y), t, 1)
    Gf = maxflow(G, s, t)
    for u in Gf["adj"][s]:
        if Gf["adj"][s][u] != 1:
            print("No solution exists")
            return
    for v in black:
        for u in Gf["adj"][v]:
            if Gf["adj"][v][u] == 1:
                print("%d %d --> %d %d" % (v[0], v[1], u[0], u[1]))


def rounding(matrix):
    m = len(matrix)
    n = len(matrix[0])
    rSum = [0 for i in range(m)]
    cSum = [0 for i in range(n)]
    for i in range(m):
        for j in range(n):
            rSum[i] += matrix[i][j] % 10
            cSum[j] += matrix[i][j] % 10
    for val in rSum:
        if val % 10 != 0:
            print("No solution exists")
            return matrix
    for val in cSum:
        if val % 10 != 0:
            print("No solution exists")
            return matrix
    G = sg.emptyGraph(0)
    s = "S"
    t = "T"

    for i in range(m):
        for j in range(n):
            if matrix[i][j] % 10 != 0:
                sg.addDirEdge(G, ("r", i), ("c", j), 10)
    for i in range(m):
        sg.addDirEdge(G, s, ("r", i), rSum[i])
    for j in range(n):
        sg.addDirEdge(G, ("c", j), t, cSum[j])
    f = maxflow(G, s, t)
    for u in f["adj"][s]:
        if f["adj"][s][u] != G["adj"][s][u]:
            print("No solution exists")
            return matrix
    for i in range(m):
        for (c, j) in f["adj"][("r", i)]:
            matrix[i][j] = matrix[i][j] - (matrix[i][j] % 10) + f["adj"][("r", i)][(c, j)]
    return matrix


def maxflow(G, s, t):
    Gf = sg.copyGraph(G)
    distances, parents, layers = sg.BFS(Gf, s)
    while t in distances:
        maxValue, path = find_path(Gf, parents, s, t)
        augment(Gf, path, maxValue)
        distances, parents, layers = sg.BFS(Gf, s)
    f = sg.copyGraph(G)
    for v in G["adj"]:
        for u in G["adj"][v]:
            if u in Gf["adj"][v]:
                f["adj"][v][u] = max(0, G["adj"][v][u] - Gf["adj"][v][u])
    return f


def augment(Gf, path, maxValue):
    for current, nextNode in path:
        newValue = Gf["adj"][current][nextNode] - maxValue
        if newValue == 0:
            Gf["adj"][current].pop(nextNode)
        else:
            Gf["adj"][current][nextNode] = newValue
        if current in Gf["adj"][nextNode]:
            Gf["adj"][nextNode][current] += maxValue
        else:
            Gf["adj"][nextNode][current] = maxValue


def find_path(G, parents, s, t):
    current = t
    path = []
    minValue = float("inf")
    while (current != s):
        minValue = min(minValue, G["adj"][parents[current]][current])
        path.append((parents[current], current))
        current = parents[current]
    path.reverse()
    return minValue, path


############################################################
#
# The remaining functions are for reading and writing outputs, and processing
# the command line arguments. You shouldn't have to modify them.  You can use them to
# help you test
#
############################################################

def main(args=[]):
    # Expects 2 command-line arguments:
    # 1) name of a file describing the graph
    if len(args) < 2:
        print("Too few arguments! There should be at least 4.")
        print("flows.py <cmd> <file>")
        return

    task = args[0]
    if task == "gold":
        coords = read_input(args[1])
        gold(coords)
    elif task == "rounding":
        matrix = read_input(args[1])
        nm = rounding(matrix)
        if compare_matrix(matrix, nm):
            print_matrix(nm)
    elif task == "maxflow":
        # the following may help you test your maxflow solution
        graph_file = args[1]
        s = int(args[2])
        t = int(args[3])
        G = sg.readGraph(graph_file)  # Read the graph from disk
        flow = maxflow(G, s, t)
        print(flow)

    return


def read_input(filename):
    with open(filename, 'r') as f:
        blocks = [[int(x) for x in s.split()] for s in f.read().splitlines()]
    return blocks


def print_matrix(matrix):
    for r in matrix:
        print(*r)


# verifies that two matricies have the same size, same row and column sums
def compare_matrix(m1, m2):
    r1 = len(m1)
    r2 = len(m2)
    c1 = len(m1[0])
    c2 = len(m2[0])
    if r1 != r2 or c1 != c2:
        print('Sizes are different')
        return False

    for ri in range(0, r1):
        rs1 = sum(m1[ri])
        rs2 = sum(m2[ri])
        if rs1 != rs2:
            print('Row sum {ri} differ: {rs1} != {rs2}')
            return False

    for cj in range(0, c1):
        cs1 = 0
        cs2 = 0
        for i in range(0, r1):
            cs1 += m1[i][cj]
            cs2 += m2[i][cj]
        if cs1 != cs2:
            print('Col sum {cj} differ: {cs1} != {cs2}')
            return False

    return True


if __name__ == "__main__":
    main(sys.argv[1:])
