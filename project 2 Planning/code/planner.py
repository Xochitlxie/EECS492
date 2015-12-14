from configure import *
from structures import *
from variables import *
from topsort import *
from read import *
from Queue import PriorityQueue
from copy import deepcopy
import copy

## May find it useful to define a maximum search effort, e.g.
## MAX_SEARCH_EFFORT = 1000000


## ***** Implement Partial Order / SNLP planning here
## Take an initial partial plan, and a variable tracker,
## return a complete plan
## p is a Plan object
## tracker is a VariableTracker object

# Heuristic function, return a score for each plan,
# then the Priority Queue could sort the plan with it
def heuristic(p):
    return len(p.open_conditions)

# Perform binding
def perform(bind,p):
    for binding in bind:
        find = binding[0]
        replace = binding[1]
        for step in p.steps:
            step.substitute(find,replace)
            # open_conditions replace
        for opens in p.open_conditions:
            if opens[0].args[0] == find:
                opens[0].args[0] = replace
            if opens[0].args[1] == find:
                opens[0].args[1] = replace
            # link replace
        for lk in p.links:
            if lk.pred.args[0] == find:
                lk.pred.args[0] = replace
            if lk.pred.args[1] == find:
                lk.pred.args[1] = replace

# Compute the unsolved threats
def computeThreats(p):
    threatResolved = False
    for link in p.links:
        for i in range(len(p.steps)):
            action = p.steps[i]
            for predicate in action.deleteList:
                if link.pred.is_equal(predicate) and i != link.recipientStep:
                    threatResolved = False

                    for ordering in p.orderings:
                        if ordering[0] == i and ordering[1] == link.causalStep:
                            threatResolved = True
                            break
                        if ordering[0] == link.recipientStep and ordering[1] == i:
                            threatResolved = True
                            break

                    if not threatResolved:
                        p.threats.append(Threat(link.copyLink(), i))


# Create the potential Actions
def potentialAction(L,p):
    L.append(Action(Actions.MOVE, p.nextVar ,p.nextVar+1,p.nextVar+2))
    p.nextVar += 3
    L.append(Action(Actions.LOAD,p.nextVar,p.nextVar+1,p.nextVar+2,p.nextVar+3))
    p.nextVar += 4
    L.append(Action(Actions.UNLOAD,p.nextVar,p.nextVar+1,p.nextVar+2,p.nextVar+3))
    p.nextVar += 4
    L.append(Action(Actions.PUT,p.nextVar,p.nextVar+1,p.nextVar+2,p.nextVar+3,p.nextVar+4))
    p.nextVar += 5
    L.append(Action(Actions.TAKE,p.nextVar, p.nextVar+1,p.nextVar+2,p.nextVar+3,p.nextVar+4))
    p.nextVar += 5


def planSearch(p, tracker):
    q = PriorityQueue()
    q.put((heuristic(p),p))
    while not q.empty():
        pl = q.get()[1]
        ## If plan is not order consistent, drop this plan
        if not isOrderConsistent(pl.orderings, len(pl.steps)):
            continue
        ## If plan could work just return this plan as answer
        if len(pl.threats) == 0 and len(pl.open_conditions) == 0:
            return pl
        ## Threat should be resolved under this function with adding the ordering consistent
        if len(pl.threats) != 0:
            threat = pl.threats[0]
            pl.threats.pop(0)
            copyPlan_TA = pl.planCopy()
            copyPlan_TA.orderings.append((threat.actionId, threat.threatened.causalStep))
            copyPlan_BT = pl.planCopy()
            copyPlan_BT.orderings.append((threat.threatened.recipientStep, threat.actionId))
            q.put((heuristic(copyPlan_TA),copyPlan_TA))
            q.put((heuristic(copyPlan_BT),copyPlan_BT))
        ## if the threat size is zero, work with the open condition
        else:
            # Took the first one in the open_condition list as the Open predicate O
            O = pl.open_conditions[-1][0]
            pa = pl.open_conditions[-1][1]
            pl.open_conditions.pop(-1)
            #Add and search the binding could replace the variables
            for i in range(0,len(pl.steps)):
                actions = pl.steps[i]
                binding_result = actions.adds(O,tracker)
                for j in range(len(binding_result)):
                    pl_successor = pl.planCopy()
                    pl_successor.links.append(Link(O.copyPredicate(),i,pa))
                    if (i,pa) not in pl_successor.orderings:
                        pl_successor.orderings.append((i,pa))
                    #Perform all variable bindings in B on pl_successor
                    perform(binding_result[j],pl_successor)
                    #Compute all unresolved threats in pl_successor
                    computeThreats(pl_successor)
                    q.put((heuristic(pl_successor),pl_successor))
            #create list L of potential new actions
            L = []
            potentialAction(L,pl)
            for newAction in L:
                binding_newAction = newAction.adds(O,tracker)
                ## Add and search the binding could replace the variables based on those new actions
                for j in range(len(binding_newAction)):
                    pl_successor_newAction = pl.planCopy()
                    pl_successor_newAction.steps.append(newAction)
                    action_ID = len(pl_successor_newAction.steps) - 1
                    action_Pred = newAction.getPrereqs()
                    for pred in action_Pred:
                        pl_successor_newAction.open_conditions.append((pred.copyPredicate(),action_ID))
                    pl_successor_newAction.links.append(Link(O.copyPredicate(),action_ID,pa))
                    if (action_ID,pa) not in pl_successor_newAction.orderings and action_ID != pa:
                        pl_successor_newAction.orderings.append((action_ID,pa)) #A_new < Pa(O)
                    if (0,action_ID) not in pl_successor_newAction.orderings and 0 != action_ID:
                        pl_successor_newAction.orderings.append((0,action_ID)) #0 < A_new
                    if (action_ID,1) not in pl_successor_newAction.orderings and action_ID != 1:
                        pl_successor_newAction.orderings.append((action_ID,1)) #A_new < 1
                    perform(binding_newAction[j],pl_successor_newAction)
                    computeThreats(pl_successor_newAction)
                    q.put((heuristic(pl_successor_newAction),pl_successor_newAction))

    return p
