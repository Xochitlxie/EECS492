'''
read.py
-------
Contains functions for reading and printing out plans
'''

from structures import *
from configure import *
from variables import *
from topsort import * #added by Ryen

def sAr(line): return filter(lambda x: len(x) > 0, line.strip().split())  ## Strip a line And Remove empty words

## Takes an empty plan object and an empty variable tracker
## Fills these with the info in the file specified by "filename"
def readfile(filename, plan, tracker):
    infile = open(filename, "r")
    identifier = ''
    line = infile.readline()
    if not line:
        print "Could not read file."
        infile.close()
        return (False, 0, 0)

    line = line.strip()
    while len(line) == 0:
        line = infile.readline()
        if line: line = line.strip()
        else: return (False, 0, 0)

    locations = int(sAr(line)[-1])

    line = infile.readline()
    robots = int(sAr(line)[-1])

    line = infile.readline()
    cranes = int(sAr(line)[-1])

    line = infile.readline()
    piles = int(sAr(line)[-1])

    line = infile.readline()
    containers = int(sAr(line)[-1])

    tracker = VariableTracker(locations, robots, cranes, piles, containers)
    plan = Plan()
    plan.nextVar = tracker.getFirstVar()

    start = Action(Actions.START)
    end = Action(Actions.FINISH)
    goal = False

    line = infile.readline()
    while line:
        line = line.strip()
        if line.startswith('#') or len(line) == 0:
            line = infile.readline()
            continue
        line_arr = sAr(line)
        identifier = line_arr[0]
        if (identifier == "initial"):
            line = infile.readline()
            continue
        if (identifier == "goal"):
            line = infile.readline()
            goal = True
            continue

        try:
            p_id = Name2Predicate[identifier]
        except:
            print "Bad identifier"
            return (False, 0, 0)

        arg1 = arg2 = ''
        ## Two-argument propositions
        if p_id in [Predicates.ADJACENT, Predicates.ATTACHED, Predicates.BELONG, Predicates.AT, Predicates.LOADED, Predicates.HOLDING, Predicates.IN, Predicates.ON, Predicates.TOP]:
            try:
                arg1 = line_arr[1]
                arg2 = line_arr[2]
            except:
                print "Incomplete predicate"
                return (False, 0, 0)
            newPred = Predicate(p_id, tracker.getId(arg1), tracker.getId(arg2))

        ## One-argument propositions
        elif p_id in [Predicates.OCCUPIED, Predicates.UNLOADED, Predicates.EMPTY, Predicates.FREE]:
            try:
                arg1 = line_arr[1]
            except:
                print "Incomplete predicate"
                return (False, 0, 0)
            newPred = Predicate(p_id, tracker.getId(arg1))

        else: pass

        if (goal): plan.open_conditions.append((newPred,1))
        else: start.addList.append(newPred)

        line = infile.readline()

    infile.close()
    plan.steps.append(start)
    plan.steps.append(end)

    plan.orderings.append((0,1))

    return (True, plan, tracker)



## Print a single predicate p
## Maybe useful for debugging
def printPredicate(p, tracker):
    print Predicate2Name[p.type_t],
    for i in range(2):
        if (p.args[i] < 0): break
        print tracker.getName(p.args[i])

def printPredicate2(outfile, p, tracker):
    print >>outfile, Predicate2Name[p.type_t],
    for i in range(2):
        if (p.args[i] < 0): break
        print >>outfile, tracker.getName(p.args[i]), ' ',

## Print a single action A
## Maybe useful for debugging
def printAction(A, tracker):
    print Action2Name[A.type_t],
    for i in range(5):
        if (A.args[i] < 0): break
        print tracker.getName(A.args[i]),

    print
    print "     Prereqs:",

    prereqs = A.getPrereqs()
    for i in range(len(prereqs)):
        printPredicate(prereqs[i], tracker)
        print ",",

    print
    print "     Added:",

    for i in range(len(A.addList)):
        printPredicate(A.addList[i], tracker)
        print ",",

    print
    print "     Deleted:",

    for i in range(len(A.deleteList)):
        printPredicate(A.deleteList[i], tracker)
        print ",",

    print

def printVerbosePlan2(filename, plan, tracker):
    outfile = open(filename, "w")
    print >>outfile, "#Steps"
    for i in range(len(plan.steps)):
        act = plan.steps[i]
        print >>outfile, i, Action2Name[act.type_t],
        for j in range(5):
            if (act.args[j] < 0): break
            print >>outfile, tracker.getName(act.args[j]),

        print

    print "\n#Orderings"
    for i in plan.orderings:
        print >>outfile, i[0], " < ", i[1]

    print "\n#Causal Links"
    for i in range(len(plan.links)):
        print >>outfile, plan.links[i].causalStep, ",",
        printPredicate2(outfile, plan.links[i].pred, tracker)
        print >>outfile, ",", plan.links[i].recipientStep

    print "\n#Threats"
    for i in plan.threats:
        print >>outfile, i.actionId, ", (",
        print >>outfile, i.threatened.causalStep, ",",
        printPredicate2(outfile, i.threatened.pred, tracker)
        print >>outfile, ",", i.threatened.recipientStep,
        print >>outfile, ")"

    print "\n#Open Preconditions"
    for i in range(len(plan.open_conditions)):
        printPredicate2(outfile, plan.open_conditions[i][0], tracker)
        print >>outfile

## A printing function that prints your plan.
## Use it for generating output files
def printPlan(filename, plan, tracker):
    if len(plan.open_conditions) > 0 or len(plan.threats) > 0 or not isOrderConsistent(plan.orderings,len(plan.steps)):
        printVerbosePlan2(filename, plan, tracker)
        return
    outfile = open(filename, "w")
    print >>outfile, "actions"
    startStep = endStep = -1
    for i in range(len(plan.steps)):
        act = plan.steps[i]
        if (act.type_t == Actions.START): startStep = i
        if (act.type_t == Actions.FINISH): endStep = i
        print >>outfile, i, Action2Name[act.type_t],
        for j in range(5):
            if (act.args[j] < 0): break
            print >>outfile, tracker.getName(act.args[j]),

        print >>outfile, "\n"

    print >>outfile, "\nconstraints"
    for i in range(len(plan.orderings)):
        o = plan.orderings[i]
        ## Skip over start / end ordering constraints
        if (o[0] == startStep or o[1] == endStep): continue
        print >>outfile, o[0], " < ", o[1]
    print >>outfile, "\nlinks"
    for j in range(len(plan.links)):
        lnk = plan.links[j]
        print >>outfile, lnk.causalStep, ' ', lnk.recipientStep, ' ',
        printPredicate2(outfile, lnk.pred, tracker)

    outfile.close()


## A function that prints more information about a plan
## Possibly useful for debugging
def printVerbosePlan(plan, tracker):
    print "#Steps"
    for i in range(len(plan.steps)):
        act = plan.steps[i]
        print i, Action2Name[act.type_t],
        for j in range(5):
            if (act.args[j] < 0): break
            print tracker.getName(act.args[j]),

        print

    print "\n#Orderings"
    for i in plan.orderings:
        print i[0], " < ", i[1]

    print "\n#Causal Links"
    for i in range(len(plan.links)):
        print plan.links[i].causalStep, ",",
        printPredicate(plan.links[i].pred, tracker)
        print ",", plan.links[i].recipientStep

    print "\n#Threats"
    for i in plan.threats:
        print i.actionId, ", (",
        print i.threatened.causalStep, ",",
        printPredicate(i.threatened.pred, tracker)
        print ",", i.threatened.recipientStep,
        print ")"

    print "\n#Open Preconditions"
    for i in range(len(plan.open_conditions)):
        printPredicate(plan.open_conditions[i][0], tracker)
        print

