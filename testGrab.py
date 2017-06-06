import viz
import viztask
import vizproximity

import steamvr

import grab_move

''' THIS IS THE DOCUMENTATION AND SAMPLE SCRIPTS FOR grab_move.py 
	KHOI LE 2017 - Stanford Virtual Human Interaction Lab
'''

# Set up testing environment and SteamVR
viz.go()

hmd = steamvr.HMD()
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())

viz.addChild('piazza.osgb')

controllers = steamvr.getControllerList() # The controller list to pass
assert(len(controllers) == 2)
viz.link(controllers[0],controllers[0].addModel()) # = viz.addChild('box.wrl')
viz.link(controllers[1],controllers[1].addModel()) # = viz.addChild('box.wrl')

''' SOAE SNAIL HUNT EXAMPLE PSEUDOCODE '''
'''
basket = basket object to grab flags from
flag = flag object to appear in hand
snails = list of snails in scene [snail1, snail2, snail3]
flagsAtSnails = list of flags on top of specific snails [flagThatGoesOnSnail1, flagThatGoesOnSnail2, flagThatGoesOnSnail3]
controllers = steamvr.getControllerList()

snailHuntGrabMod = grab_move.grab_mod([basket], controllers, snails, [flag], flagsAtSnails, hideDestination = False)
#if you want participant to pull trigger to grab a flag from basket, set reqTrigger = True

We pass in [basket] as a list of items where we grab from
We pass in our steamvr controllers
We pass in snails as the list of destinations where we want to put the objects
We pass in [flag] as a list of items to show up in our hand when we grab the basket
We pass in flagsAtSnails as the list of items at the destinations, which will show up at the corresponding
	destination when we place the item at that destination
We set hideDestination to False because we don't want the snails to disappear when we place the flag there.
'''
''' DARPA UNPACKING EXAMPLE PSEUDOCODE '''
'''
itemsInSuitcase = objects in suitcase [shampoo, conditioner]
itemsInHand = objects in hand [shampooHand, conditionerHand]
itemsOnShelf = materialized items on shelf [shampooShelf, conditionerShelf]
itemsShelfPlaceholder = ghosty items on shelf [shampooGhosty, conditionerGhosty]
controllers = steamvr.getControllerList()
unpackingGrabMod = grab_move.grab_mod(itemsInSuitcase, controllers, itemsShelfPlaceholder, itemsInHand, itemsOnShelf, oneItemOneDest = True)

We pass in itemsInSuitcase as the list of objects we want participant to grab
We pass in our steamvr controllers
We pass in itemsShelfPlaceholder as the list of destinations where we want our participant to put the objects
We pass in itemsInHand as the list of objects we want to be in participant hand
We pass in itemsOnShelf as the list of items at the destination which will appear when we place the object
	at the correct destination
We set oneItemOneDest to True because want each item to go to a specific spot
'''

''' BASIC TOUCH TO GRAB AND TOUCH DESTINATION TO RELEASE '''
#'''
box = viz.addChild('box.wrl')
box.setPosition([0, 1, 0])
box.setScale([.1,.1,.1])
items = [box]
dstbox = viz.addChild('box.wrl')
dstbox.setPosition([1, 1, 0])
dstbox.setScale([.05,.05,.05])
dstbox2 = viz.addChild('box.wrl')
dstbox2.setPosition([.3, 1, 0.3])
dstbox2.setScale([.05,.05,.05])
destinations = [dstbox, dstbox2]

grabMod = grab_move.grab_mod(items, controllers, destinations) 
#'''

''' PULL TRIGGER TO GRAB AND TOUCH DESTINATION TO RELEASE '''
'''
box = viz.addChild('box.wrl')
box.setPosition([0, 1, 0])
box.setScale([.1,.1,.1])
items = [box]
dstbox = viz.addChild('box.wrl')
dstbox.setPosition([1, 1, 0])
dstbox.setScale([.05,.05,.05])
dstbox2 = viz.addChild('box.wrl')
dstbox2.setPosition([.3, 1, 0.3])
dstbox2.setScale([.05,.05,.05])
destinations = [dstbox, dstbox2]

grabMod = grab_move.grab_mod(items, controllers, destinations, reqTrigger = True) 
'''

''' BASIC TOUCH TO GRAB AND TOUCH DESTINATION TO RELEASE WITH REGRAB '''
'''
box = viz.addChild('box.wrl')
box.setPosition([0, 1, 0])
box.setScale([.1,.1,.1])
items = [box]
dstbox = viz.addChild('box.wrl')
dstbox.setPosition([1, 1, 0])
dstbox.setScale([.05,.05,.05])
dstbox2 = viz.addChild('box.wrl')
dstbox2.setPosition([.3, 1, 0.3])
dstbox2.setScale([.05,.05,.05])
destinations = [dstbox, dstbox2]

grabMod = grab_move.grab_mod(items, controllers, destinations, regrab = True) 
'''

''' TOUCH TO GRAB, OBJECT APPEARS IN HAND, TOUCH DESTINATION TO RELEASE '''
'''
box = viz.addChild('box.wrl')
duck = viz.addChild('duck.wrl')
duck.setPosition([0.5, 1, 0.5])
duck.setScale([0.2,0.2,0.2])
box.setPosition([0, 1, 0])
box.setScale([.1,.1,.1])
items = [box]
itemsInHand = [duck]
dstbox = viz.addChild('box.wrl')
dstbox.setPosition([1, 1, 0])
dstbox.setScale([.05,.05,.05])
dstbox2 = viz.addChild('box.wrl')
dstbox2.setPosition([.3, 1, 0.3])
dstbox2.setScale([.05,.05,.05])
destinations = [dstbox, dstbox2]

grabMod = grab_move.grab_mod(items, controllers, destinations, itemsInHand)
'''

''' TOUCH TO GRAB, OBJECT APPEARS IN HAND, TOUCH DESTINATION TO RELEASE, NEW ITEM APPEARS AT DESTINATION 
	I.E DARPA - SOAE '''
'''
box = viz.addChild('box.wrl')
duck = viz.addChild('duck.wrl')
duck.setPosition([0.5, 1, 0.5])
duck.setScale([0.2,0.2,0.2])
box.setPosition([0, 1, 0])
box.setScale([.1,.1,.1])
items = [box]
itemsInHand = [duck]
dstbox = viz.addChild('box.wrl')
dstbox.setPosition([1, 1, 0])
dstbox.setScale([.05,.05,.05])
dstbox2 = viz.addChild('box.wrl')
dstbox2.setPosition([.3, 1, 0.3])
dstbox2.setScale([.05,.05,.05])
destinations = [dstbox, dstbox2]
ball = viz.addChild('basketball.osgb')
ball.setPosition(dstbox.getPosition())
ball2 = viz.addChild('basketball.osgb')
ball2.setPosition(dstbox2.getPosition())
itemsAtDest = [ball, ball2]

grabMod = grab_move.grab_mod(items, controllers, destinations, itemsInHand, itemsAtDest)
'''