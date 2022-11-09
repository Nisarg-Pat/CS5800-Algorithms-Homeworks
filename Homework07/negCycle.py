############################################################
# Starter code for negative weight cycle assignment
# March 2022
# 
# This code is inspired heavily by 
# @adamdavisonsmith, Boston University
############################################################


import sys
import os
import heapq
import queue
import numpy as np
import simplegraphs as sg
import unitCycle


def bellmanFordSimple(G, s):
    # G is a dictionary with keys "n", "m", "adj" representing an *weighted* graph
    # G["adj"][u][v] is the cost (length / weight) of edge (u,v)
    # This algorithms finds least-costs paths to all vertices
    # Will not detect negative-cost cycles
    # Returns an dict of distances (path costs) and parents in the lightest-paths tree.
    #
    # This is basically the algorithm we covered in class (except it
    # finds paths from a source instead of to a desitnation).
    #
    n = G["n"]
    d = [{} for i in range(n)]
    for u in G["adj"]:
        d[0][u] = np.inf
    d[0][s] = 0
    parent = {s: None}
    for i in range(1, n):
        for v in G["adj"]:
            d[i][v] = d[i - 1][v]
        for u in G["adj"]:
            for v in G["adj"][u]:
                newlength = d[i - 1][u] + G["adj"][u][v]
                if newlength < d[i][v]:
                    d[i][v] = newlength
                    parent[v] = u
    distances = d[n - 1]
    return distances, parent


def findCycle(G, parent):
    newG = sg.emptyGraph(0)
    for v in parent:
        sg.addNode(newG, v)
    for v in G["adj"]:
        # if parent[v] is not None:
        sg.addDirEdge(newG, parent[v], v)
    return unitCycle.DFSFindCycle(newG)

def bellmanFordEarlyStop(G, s):
    # G is a dictionary with keys "n", "m", "adj" representing an *weighted* graph
    # G["adj"][u][v] is the cost (length / weight) of edge (u,v)
    # This algorithms finds least-costs paths to all vertices
    # Returns a dict of distances (path costs) and parents in the lightest-paths tree.
    #
    # This version stops early when no further changes observed.
    #
    n = G["n"]
    d = [{} for i in range(n + 1)]
    for u in G["adj"]:
        d[0][u] = np.inf
    d[0][s] = 0
    parent = {s: None}
    parentGraph = sg.emptyGraph(0)

    cycle_list = []
    for i in range(1, n + 1):
        # FOR THE PROGRAM TO RUN QUICKLY, YOU WILL HAVE TO CHANGE THE
        # MAIN LOOP But you should first get a correct algorithm, and
        # that does not require changing the main loop.
        changed = {}
        for v in G["adj"]:
            d[i][v] = d[i - 1][v]
        for u in G["adj"]:
            for v in G["adj"][u]:
                newlength = d[i - 1][u] + G["adj"][u][v]
                if newlength < d[i][v]:
                    d[i][v] = newlength
                    parent[v] = u
                    if v in parentGraph["adj"]:
                        parentGraph["adj"][v] = {}
                    sg.addDirEdge(parentGraph, v, u)
                    changed[v] = True
        if not changed:
            break
        cycle_list = unitCycle.DFSFindCycle(parentGraph)
        if cycle_list:
            break
    # if the last iteration had distances still changing,
    # there must exist a negative weight cycle reachable from s.
    if changed:
        cycle_list.reverse()
        negCycle = True
    else:
        negCycle = False
    distances = d[i]

    return distances, parent, i, negCycle, cycle_list


def negCycle(G):
    # This code returns
    # found: a boolean (where true indicates a negative-weight cycle was found)
    # cycle_list: either an empty list (if found is False) or a list of nodes
    # that form a negative-weight cycle.
    ########################################
    # Make a copy of G. Don't touch G again
    newG = sg.copyGraph(G)
    # Add a new source and 0-weight edges to all the original nodes.
    source = 'source'
    sg.addNode(newG, source)
    for v in newG["adj"]:
        sg.addDirEdge(newG, source, v, 0.0)
    #
    # Now look for negative cycles. YOU SHOULD MODIFY THE BF ALGORITHM
    distances, parent, i, negCycle, cycle_list = bellmanFordEarlyStop(newG, source)
    if negCycle:
        return True, cycle_list
    else:
        return False, []


############################################################
#
# The remaining functions are for reading and writing outputs, and processing
# the command line arguments. You shouldn't have to modify them (but
# you can, for testing, if you want).
#
############################################################


def writeNegCycleOutput(output_file, found, node_list):
    # This takes the outputs of negCycle and writes them
    # to a file with the name output_file
    with open(output_file, 'w') as f:
        f.write("{}\n{}\n".format(bool(found), node_list))
    return


def parseNegCycleOutput(student_out_filename):
    # This will read an output file (either yours or the one provided
    # with the starter and load its content into usable Python
    # variables Its output has the same format as negCycle (a Boolean
    # and a list of nodes).  This may be useful when you are testing
    # your code, but you don't need to use it.
    if not (os.path.isfile(student_out_filename)):
        return False, "Student file not found"
    with open(student_out_filename, "r") as f:
        raw = f.read().splitlines()
        if len(raw) < 2:
            return False, "Too few lines in student file"
        raw_bool = raw[0]
        raw_list = raw[1]
    # Parse first line
    if raw_bool == "True":
        neg_cycle_found = True
    elif raw_bool == "False":
        neg_cycle_found = False
    else:
        return False, "First line of output file could not be parsed as a Boolean."
    # Parse third line
    try:
        list_of_strings = raw_list.strip('][').split(',')
        if list_of_strings == ['']:
            list_of_nodes = []
        else:
            list_of_nodes = [int(x) for x in list_of_strings]
    except:
        return False, "Second line of output file could not be parsed as a list of integers."
    return (neg_cycle_found, list_of_nodes)


def main(args=[]):
    # Expects three to five command-line arguments:
    # 1) name of a file describing the graph
    # 2) name of a file where the output should be written
    if len(args) < 2:
        print("Too few arguments! There should be at least 2.")
        return
    graph_file = args[0]
    out_file = args[1]
    G = sg.readGraph(graph_file)  # Read the graph from disk
    neg_cycle_found, cycle_list = negCycle(G)  # This part actually does all the work
    writeNegCycleOutput(out_file, neg_cycle_found, cycle_list)  # Write the output
    if neg_cycle_found:
        is_cycle, cost = sg.checkCycle(G, cycle_list)  # This is just to show you how to use the checkCycle function.
        if not is_cycle:
            print("Your list of nodes is not a cycle :(")
        elif cost >= 0:
            print("Your list of nodes is a cycle but its cost isn't negative :(")
    return


if __name__ == "__main__":
    main(sys.argv[1:])
