'''
structures.py
-------------
Contains the following classes and typedefs:
Predicate ## A predicate, with a type and arguments
Link ## A causal link
Threat ## A threat to a causal link
thrtCmp ## A comparator allowing threat objects to be sorted
Ordering ## An ordering constraint (typedef of (int,int))
Binding ## A variable binding (typedef of (int,int))
Action ## An action, with type, arguments, add list, delete list, and others
Plan ## An object for representing partially ordered plans
plan_not_found ## an exception class
'''

from configure import *
from variables import *
import copy

## An object representing a predicate
## Predicates have at least one argument, and at most two
## Unused arguments are always -1.
class Predicate:

    def __init__(self, t = -1, arg1 = -1, arg2 = -1):
        self.args = []
        self.type_t = t
        self.args.append(arg1)
        self.args.append(arg2)

    def is_equal(self, p):
        return (self.type_t == p.type_t) and (self.args[0] == p.args[0]) and (self.args[1] == p.args[1])

    def copyPredicate(self):
        copyPred = Predicate(self.type_t)
        copyPred.args = copy.copy(self.args)
        return copyPred

## A causal link
## Consists of a predicate, a "causal step", and a "recipient step"
## "causalStep" is an integer referring to a step in a plan which
##        adds predicate "pred" in fulfillment of the preconditions of
##        of the step "recipientStep"
##    In the paper's notation:
##    causalStep -----pred-----> recipientStep
class Link:

    def __init__(self, p, cstep, rstep):
        self.pred = p
        self.causalStep = cstep
        self.recipientStep = rstep

    def copyLink(self):
        copyL = Link(self.pred.copyPredicate(), self.causalStep, self.recipientStep)
        return copyL

## A threat to a causal link
## Represents the fact that the step identified by "actionId"
##     deletes the predicate of the causal link "threatened"
class Threat:
    def __init__(self, thrt, act):
        self.threatened = thrt
        self.actionId = act

    def copyThreat(self):
        copyT = Threat(self.threatened.copyLink(), self.actionId)
        return copyT
## Pairs representing ordering contraints and binding constraints
## The typedef is for ease of understanding
#typedef pair<int, int> Ordering;
#typedef pair<int, int> Binding;

## An object representing an action
## Actions have at least three arguments, and at most five
class Action:

    def copyAction(self):
        copyAct = Action(self.type_t)
        copyAct.args = copy.copy(self.args)
        copyAct.addList = []
        copyAct.deleteList = []
        if self.type_t == Actions.START or self.type_t == Actions.FINISH:
            for predicate in self.addList:
                copyAct.addList.append(predicate.copyPredicate())
            for predicate in self.deleteList:
                copyAct.deleteList.append(predicate.copyPredicate())
        else:
            copyAct.fillPredicates()
        return copyAct

    '''
    Action::adds
    ----
    *** You should implement this function *****

    Takes a Predicate p and a VariableTracker tracker
    Returns a list of lists of variable bindings
    Each list of bindings is one possible substitution that 
    would cause the action to add predicate p.
    
    Each list of bindings unifies p with one of the things 
    in the add list of the action.
    For example, "start" could add both "in c0 p0" and "in c1 p1"
    If you have a predicate "in x1 x2", then start could add this 
    predicate in two different ways.
    The return value would be (({x1,c0},{x2,p0}),({x1,c1},{x2,c2}))
    Where (,) is the list and {,} is a binding.

    If nothing unifies, returns an empty list of lists.
    '''

    def adds(self, p, tracker):
        returnList = [] ## list of list of bindings. Each binding is a pair of integers - (int, int).
        for addPredicate in self.addList:
            matchList = [] ##list of bindings. Each binding is a pair of integers - (int, int)
            ## if type not match, continue the next loop
            if addPredicate.type_t != p.type_t:
                continue
            # if two Predicate is equal, append a empty list into the return list
            if addPredicate.is_equal(p):
                returnList.append(matchList)
            else:
                if addPredicate.args[0] == p.args[0]:
                    if tracker.isVariable(addPredicate.args[1]) or tracker.isVariable(p.args[1]):
                        matchList.append((max(addPredicate.args[1],p.args[1]),min(addPredicate.args[1],p.args[1])))
                        returnList.append(matchList)
                    else:
                        break
                elif addPredicate.args[1] == p.args[1]:
                    if tracker.isVariable(addPredicate.args[0]) or tracker.isVariable(p.args[0]):
                        matchList.append((max(addPredicate.args[0],p.args[0]),min(addPredicate.args[0],p.args[0])))
                        returnList.append(matchList)
                    else:
                        break
                else:
                    if tracker.isVariable(addPredicate.args[0]) or tracker.isVariable(p.args[0]):
                        matchList.append((max(addPredicate.args[0],p.args[0]),min(addPredicate.args[0],p.args[0])))
                    else:
                        continue
                    if tracker.isVariable(addPredicate.args[1]) or tracker.isVariable(p.args[1]):
                        matchList.append((max(addPredicate.args[1],p.args[1]),min(addPredicate.args[1],p.args[1])))
                    else:
                        continue
                    if len(matchList) == 1:
                        returnList.append(matchList)
                    elif len(matchList) == 2:
                        if matchList[0] == matchList[1]:
                            matchList.pop()
                        elif matchList[0][0] == matchList[1][0] and not tracker.isVariable(matchList[0][1]) and not tracker.isVariable(matchList[1][1]):
                            continue
                        elif matchList[0][1] == matchList[1][0] and tracker.isVariable(matchList[0][0]) and not tracker.isVariable(matchList[1][1]):
                            matchList.insert(1,(matchList[0][0],matchList[1][1]))
                            matchList.pop(0)
                        elif matchList[0][0] == matchList[1][1] and tracker.isVariable(matchList[1][0]) and not tracker.isVariable(matchList[0][1]):
                            matchList.insert(1,(matchList[1][0],matchList[0][1]))
                            matchList.pop()
                        returnList.append(matchList)

        return returnList

        ## ****

    ## ******* The rest are implemented for you ***********

    ## Constructor
    def __init__(self, t, arg1 = -1, arg2 = -1, arg3 = -1, arg4 = -1, arg5 = -1):
        self.args = []
        self.type_t = t
        self.args.append(arg1)
        self.args.append(arg2)
        self.args.append(arg3)
        self.args.append(arg4)
        self.args.append(arg5)

        self.fillPredicates()


    ## A utility that fills addList and deleteList based on args
    ## Called in constructor, and again during variable substitution
    ## Implemented for you.
    ## This is called either during construction, or during a 
    ## variable rebinding.
    ## Clears the old lists and inserts predicates into them based on the
    ## action arguments
    ## Does nothing if action is start or finish
    def fillPredicates(self):
        self.addList = []
        self.deleteList = []
        ##self.prereqList = []

        if self.type_t == Actions.MOVE:
            '''
            move(r, l, m) # move robot r from location l to location m
                precond: adjacent(l, m), at(r, l), free(m)
                add: at(r, m), occupied(m), free(l)
                delete: occupied(l), at(r,l), free(m)
            '''
            self.addList.append(Predicate(Predicates.AT, self.args[0], self.args[2]))
            self.addList.append(Predicate(Predicates.OCCUPIED, self.args[2]))
            self.addList.append(Predicate(Predicates.FREE, self.args[1]))

            self.deleteList.append(Predicate(Predicates.OCCUPIED, self.args[1]))
            self.deleteList.append(Predicate(Predicates.AT, self.args[0], self.args[1]))
            self.deleteList.append(Predicate(Predicates.FREE, self.args[2]))

        elif self.type_t == Actions.TAKE:
            '''
            take(k,l,c,d,p) #crane k at location l takes c off of d in pile p
                precond: belong(k,l), attached(p,l), empty(k), top(c,p), on(c,d)
                add: holding(k,c), top(d,p)
                delete: empty(k), in(c,p), top(c,p), on(c,d)
            '''

            self.addList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            self.addList.append(Predicate(Predicates.TOP, self.args[3], self.args[4]))

            self.deleteList.append(Predicate(Predicates.EMPTY, self.args[0]))
            self.deleteList.append(Predicate(Predicates.IN, self.args[2], self.args[4]))
            self.deleteList.append(Predicate(Predicates.TOP, self.args[2], self.args[4]))
            self.deleteList.append(Predicate(Predicates.ON, self.args[2], self.args[3]))

        elif self.type_t == Actions.PUT:
            '''
            put(k,l,c,d,p) # crane k at location l puts c onto d in pile p
                precond: belong(k,l), attached(p,l), holding(k,c), top(d,p)
                add: empty(k), in(c,p), top(c,p), on(c,d)
                delete: holding(k,c), top(d,p)
            '''

            self.addList.append(Predicate(Predicates.EMPTY, self.args[0]))
            self.addList.append(Predicate(Predicates.IN, self.args[2], self.args[4]))
            self.addList.append(Predicate(Predicates.TOP, self.args[2], self.args[4]))
            self.addList.append(Predicate(Predicates.ON, self.args[2], self.args[3]))

            self.deleteList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            self.deleteList.append(Predicate(Predicates.TOP, self.args[3], self.args[4]))

        elif self.type_t == Actions.LOAD:
            '''
            load(k, l, c, r) # crane k at location l loads container c onto robot r
                precond: belong(k,l), holding(k,c), at(r,l), unloaded(r)
                add: empty(k), loaded(r,c)
                delete: holding(k,c), unloaded(r)
            '''

            self.addList.append(Predicate(Predicates.EMPTY, self.args[0]))
            self.addList.append(Predicate(Predicates.LOADED, self.args[3], self.args[2]))

            self.deleteList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            self.deleteList.append(Predicate(Predicates.UNLOADED, self.args[3]))

        elif self.type_t == Actions.UNLOAD:
            '''
            unload(k,l,c,r) # crane k at location l takes container c from robot r
                precond: belong(k,l), at(r,l), loaded(r,c), empty(k)
                add: holding(k,c), unloaded(r)
                delete: empty(k), loaded(r,c)
            '''

            self.addList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            self.addList.append(Predicate(Predicates.UNLOADED, self.args[3]))

            self.deleteList.append(Predicate(Predicates.EMPTY, self.args[0]))
            self.deleteList.append(Predicate(Predicates.LOADED, self.args[3], self.args[2]))

        else: pass


    ## Perform a substitution, substituting all instances of 
    ## variable "former" with "newval"
    ## Implemented for you
    def substitute(self, former, newval):
        subst = False
        for i in range(5):
            if (self.args[i] == former):
                self.args[i] = newval
                subst = True
        if (subst): self.fillPredicates()

    ## Returns a list of predicates consisting of the prerequisites
    ## for this particular action
    def getPrereqs(self):
        prereqList = []
        if self.type_t == Actions.MOVE:
            '''
            move(r, l, m) # move robot r from location l to location m
                precond: adjacent(l, m), at(r, l), free(m)
                add: at(r, m), occupied(m), free(l)
                delete: occupied(l), at(r,l), free(m)
            '''
            prereqList.append(Predicate(Predicates.ADJACENT, self.args[1], self.args[2]))
            prereqList.append(Predicate(Predicates.AT, self.args[0], self.args[1]))
            prereqList.append(Predicate(Predicates.FREE, self.args[2]))

        elif self.type_t == Actions.TAKE:
            '''
            take(k,l,c,d,p) #crane k at location l takes c off of d in pile p
                precond: belong(k,l), attached(p,l), empty(k), top(c,p), on(c,d)
                add: holding(k,c), top(d,p)
                delete: empty(k), in(c,p), top(c,p), on(c,d)
            '''
            prereqList.append(Predicate(Predicates.BELONG, self.args[0], self.args[1]))
            prereqList.append(Predicate(Predicates.ATTACHED, self.args[4], self.args[1]))
            prereqList.append(Predicate(Predicates.EMPTY, self.args[0]))
            prereqList.append(Predicate(Predicates.TOP, self.args[2], self.args[4]))
            prereqList.append(Predicate(Predicates.ON, self.args[2], self.args[3]))

        elif self.type_t == Actions.PUT:
            '''
            put(k,l,c,d,p) # crane k at location l puts c onto d in pile p
                precond: belong(k,l), attached(p,l), holding(k,c), top(d,p)
                add: empty(k), in(c,p), top(c,p), on(c,d)
                delete: holding(k,c), top(d,p)
            '''
            prereqList.append(Predicate(Predicates.BELONG, self.args[0], self.args[1]))
            prereqList.append(Predicate(Predicates.ATTACHED, self.args[4], self.args[1]))
            prereqList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            prereqList.append(Predicate(Predicates.TOP, self.args[3], self.args[4]))

        elif self.type_t == Actions.LOAD:
            '''
            load(k, l, c, r) # crane k at location l loads container c onto robot r
                precond: belong(k,l), holding(k,c), at(r,l), unloaded(r)
                add: empty(k), loaded(r,c)
                delete: holding(k,c), unloaded(r)
            '''
            prereqList.append(Predicate(Predicates.BELONG, self.args[0], self.args[1]))
            prereqList.append(Predicate(Predicates.HOLDING, self.args[0], self.args[2]))
            prereqList.append(Predicate(Predicates.AT, self.args[3], self.args[1]))
            prereqList.append(Predicate(Predicates.UNLOADED, self.args[3]))

        elif self.type_t == Actions.UNLOAD:
            '''
            unload(k,l,c,r) # crane k at location l takes container c from robot r
                precond: belong(k,l), at(r,l), loaded(r,c), empty(k)
                add: holding(k,c), unloaded(r)
                delete: empty(k), loaded(r,c)
            '''
            prereqList.append(Predicate(Predicates.BELONG, self.args[0], self.args[1]))
            prereqList.append(Predicate(Predicates.AT, self.args[3], self.args[1]))
            prereqList.append(Predicate(Predicates.LOADED, self.args[3], self.args[2]))
            prereqList.append(Predicate(Predicates.EMPTY, self.args[0]))

        else: pass

        return prereqList


    ## Returns true if there is a variable binding in which this action deletes the predicate
    ## Probably should also return the binding itself
    ## Calls the unification algorithm
    def deletes(self, p):
        for i in range(len(self.deleteList)):
            if (p.is_equal(self.deleteList[i])):
                return True
        return False


## A plan object
## We put ordering constraints into an std::set for easy element search
## We put threats into a set for easy insertion and deletion
## Everything else comes in lists
## You may want to modify this data structure, depending on how your algorithm works
## Just note that if you do so, you may also have to modify the read function
class Plan:

    def __init__(self):
        self.steps = []
        self.links = []
        self.threats = []
        self.open_conditions = []
        self.orderings = []
        self.nextVar = -1


    def planCopy(self):
        copyPlan = Plan()
        copyPlan.nextVar = self.nextVar
        for action in self.steps:
            copyPlan.steps.append(action.copyAction())
        for link in self.links:
            copyPlan.links.append(link.copyLink())
        for threat in self.threats:
            copyPlan.threats.append(threat.copyThreat())
        for ordering in self.orderings:
            copyPlan.orderings.append(copy.copy(ordering))
        for condition in self.open_conditions:
            copyPlan.open_conditions.append((condition[0].copyPredicate(), condition[1]))
        copyPlan.nextVar = self.nextVar
        return copyPlan



## An exception class, to be thrown if your search could not find a plan
class plan_not_found:
    def __init__(self): pass




