import viz
import viztask
import vizproximity
import vizshape
import vizact

import steamvr
'''
Grab module by Khoi Le 2017 - Stanford Virtual Human Interaction Lab

Initialize grab module with the following parameters:
Necessary:
- Items to grab, list of node3d objects
- Controllers, list of SteamVR controllers
- Destinations to put the objects, list of node3d objects

Pre-assigned parameters:
- itemsInHand, [] list of node3d objects that appear in hand.
	IMPORTANT: Order of list corresponds to items. (i.e [object1, object2] [itemInHand1, itemInHand2])
	itemInHand1 appears when object1 is grabbed. Do NOT pass in lists of different lengths.
- itemsAtDestination, [] list of node3d objects that appear when object placed destination.
	IMPORTANT: Order of list corresponds to destinations. (i.e [destination1, destination2] [itemAtDst1, itemAtDst2])
	itemAtDst1 appears at destination1 when destination1 is touched. Do NOT pass in lists of different lengths.
- oneItemOneDest, False, boolean determines if each item can only go to its corresponding destination
	(i.e blue ball goes in blue basket)
	IMPORTANT: Order of destinations list must correspond to items list.
		Do NOT pass in lists of different lengths if this is True.
- hideDestination, True, boolean determines whether the destination should be hidden after placing object
- regrab, False, boolean determines if participant can regrab an item they've already put down
- reqTrigger, False, boolean determines if participant needs to pull trigger to initialize grab. NOTE: participants
	do NOT need to hold the trigger to maintain grip (this would make it possible to drop objects, which is annoying
	to deal with in an experiment, and should be avoided unless necessary)
- growOnHover, True, boolean determines if hovering over an object enlarges it for user experience cues when reqTrigger is on.
- handSensitivity, double that represents the radius of the sphere around the hand
Examples:
BASIC TOUCH TO GRAB AND TOUCH DESTINATION TO RELEASE

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

See sample testGrab.py for more examples.
'''
def toggleView(node, state):
	'Helper function makes sure items disappear even in mirrors'
	if state:
		node.enable(viz.RENDERING)
		node.alpha(1)
	else:
		node.disable(viz.RENDERING)
		node.alpha(0)
		
class grab_mod:
	'Handles all grabbing interactions'
	def __init__(self, items, controllers, destinations, itemsInHand = [], itemsAtDestination = [], oneItemOneDest = False, hideDestination = True, regrab = False, reqTrigger = False, growOnHover = True, handSensitivity = 0.09):
		self.items = items
		self.itemsInHand = itemsInHand
		self.controllers = controllers
		self.destinations = destinations
		self.itemsAtDestination = itemsAtDestination
		self.reqTrigger = reqTrigger
		self.grabProximityManager = vizproximity.Manager()
		self.placeProximityManager = vizproximity.Manager()
		self.grabbedItems = []
		self.regrab = regrab
		self.growOnHover = growOnHover
		self.handSensitivity = handSensitivity
		self.hoveredItem = None
		self.oneItemOneDest = oneItemOneDest
		self.hideDestination = hideDestination
		vizact.onkeydown('d', self.grabProximityManager.setDebug, viz.TOGGLE)
		self.grabProximityManager.onEnter(None,self.grabItem)
		self.grabProximityManager.onExit(None, self.exitNode)
		self.placeProximityManager.onEnter(None, self.placeItem)
		self.targets = [None, None]
		#Initialize all items
		for i in range(0, len(items)):
			# If module will show special items in hand, link them to the itemToGrab objects
			if len(itemsInHand) > 0:
				if self.oneItemOneDest:
					items[i] = itemToGrab(items[i], itemsInHand[i], destinations[i])
				else:
					items[i] = itemToGrab(items[i], itemsInHand[i])
			else:
				if self.oneItemOneDest:
					items[i] = itemToGrab(items[i], destinations[i])
				else:
					items[i] = itemToGrab(items[i])
			items[i].setup(self.grabProximityManager)
		#Initialize controllers and targets
		for i in range(len(controllers)):
			targetSphere = vizshape.addSphere(handSensitivity)
			toggleView(targetSphere, False)
			viz.link(controllers[i], targetSphere)
			target = vizproximity.Target(targetSphere)
			self.grabProximityManager.addTarget(target)
			self.placeProximityManager.addTarget(target)
			self.targets[i] = target
		#Initialize destinations
		for destination in destinations:
			destination = itemToGrab(destination)
			destination.setup(self.placeProximityManager, sensorScale = [3,3,3])
		
		for item in itemsInHand:
			toggleView(item, False)
			
		for item in itemsAtDestination:
			toggleView(item, False)
			
		vizact.onsensordown(controllers[0], steamvr.BUTTON_TRIGGER, self.triggerGrabItem, 0)
		vizact.onsensordown(controllers[1], steamvr.BUTTON_TRIGGER, self.triggerGrabItem, 1)
	def exitNode(self, e):
		if(self.hoveredItem is not None and self.reqTrigger and self.growOnHover):
			tempScale = self.hoveredItem.getScale()
			self.hoveredItem.setScale(tempScale[0] * 0.95238, tempScale[1] * 0.95238, tempScale[2] * 0.95238)
		self.hoveredItem = None
	def triggerGrabItem(self, controllerIndex):
		print("trigger grab called")
		if self.hoveredItem == None or not self.reqTrigger:
			return
		else:
			if self.growOnHover:
				tempScale = self.hoveredItem.getScale()
				self.hoveredItem.setScale(tempScale[0] * 0.95238, tempScale[1] * 0.95238, tempScale[2] * 0.95238)
			target = self.targets[controllerIndex]
			self.actuallyGrabItem(self.hoveredItem, target.getSource())
			
	def addItem(self, item):
		item = itemToGrab(item)
		self.items.append(item)
	
	def activateRange(self,e):
		pass
		
	def grabItem(self, e):
		#viztask.schedule(self.actuallyGrabItem(e))
		for i in range(len(self.items)):
			if e.sensor.getSource()._node == self.items[i].itemNode:
				if self.items[i].recentlyGrabbed == True:
					return;
		#Vibrate correct controller
		if e.target == self.targets[0]:
			print("Vibrate 0")
			self.vibrateController(0)
		else:
			print("Vibrate 1")
			self.vibrateController(1)
		self.hoveredItem = e.sensor.getSource()._node
		if self.reqTrigger and self.growOnHover:
			#Enlarges object for visual cue
			tempScale = self.hoveredItem.getScale()
			self.hoveredItem.setScale(tempScale[0] * 1.05, tempScale[1] * 1.05, tempScale[2] * 1.05)
		else:			
			self.actuallyGrabItem(e.sensor.getSource()._node, e.target.getSource());
		
	def actuallyGrabItem(self, item, controller):
		if controller == self.targets[0].getSource():
			print("Vibrate 0")
			self.vibrateController(0)
		else:
			print("Vibrate 1")
			self.vibrateController(1)
		if len(self.itemsInHand) > 0:
			for i in range(len(self.items)):
				if item == self.items[i].itemNode:
					toggleView(self.itemsInHand[i], True)
					toggleView(item, False)
					link = viz.link(controller._node, self.itemsInHand[i])
					self.grabbedItems.append([self.items[i], controller, link])
		else:
			for i in range(len(self.items)):
				if item == self.items[i].itemNode:
					link = viz.link(controller._node,item)
					self.grabbedItems.append([self.items[i], controller, link]) #make into a class
		
	def placeItem(self, e):
		print(self.grabbedItems)
		target = e.target.getSource()
		if self.oneItemOneDest and not e.sensor.getSource()._node == grabbedItem[0].specificTarget:
			return
		if target == self.targets[0].getSource():
			print("Vibrate 0")
			self.vibrateController(0)
		else:
			print("Vibrate 1")
			self.vibrateController(1)
		for grabbedItem in self.grabbedItems:
			if target == grabbedItem[1]:
				
				if len(self.itemsInHand) > 0:
					for i in range(len(self.destinations)):
						if e.sensor.getSource()._node == self.destinations[i]:
							if len(self.itemsAtDestination) > 0:
								print("show new obj")
								if self.hideDestination:
									toggleView(self.destinations[i], False)
								toggleView(self.itemsAtDestination[i], True)
								toggleView(grabbedItem[0].itemInHand, False) #self.itemsInHand[i].disable(viz.RENDERING)
							else:
								if self.hideDestination:
									toggleView(self.destinations[i], False)
								else:
									toggleView(self.destinations[i], True)
				if not self.regrab:
					grabbedItem[0].destroySensor()
				grabbedItem[0].callSRG()
				grabbedItem[2].remove()
				grabbedItem[0].itemNode.setPosition(e.sensor.getSource()._node.getPosition())
				self.grabbedItems.remove(grabbedItem)
				
	def vibrateController(self, i):
		self.controllers[i].setVibration(0.004)
	def waitTrigger(self, controller):
		yield viztask.waitSensorDown(controller, steamvr.BUTTON_TRIGGER)

class itemToGrab:
	'Base class for an item to grab'
	def __init__(self, itemNode, itemInHand = None, specificTarget = None):
		self.itemNode = itemNode
		self.recentlyGrabbed = False
		self.itemInHand = itemInHand
		self.sensor = None
		self.specificTarget = None
		self.proximityManagers = []
		#self.targetNode = targetNode
	
	def setup(self, proximityManager, sensorType = "box", sensorScale = [1, 1, 1], target = None, itemInHand = None):
		sensor = None
		if sensorType == "box":
			sensor = vizproximity.addBoundingBoxSensor(self.itemNode, scale=sensorScale)
		elif sensorType == "sphere":
			sensor = vizproximity.addBoundingSphereSensor(self.itemNode)#, scale=sensorScale[0])
		else:
			print("Sensor type: " + sensorType + " is not valid. Defaulting to box sensor. ")
			sensor = vizproximity.addBoundingBoxSensor(self.itemNode)#, scale=sensorScale)
		self.sensor = sensor
		#viztask.schedule(self.setRecentlyGrabbed)
		proximityManager.addSensor(sensor)
		self.proximityManagers.append(proximityManager)
		
	def callSRG(self):
		viztask.schedule(self.setRecentlyGrabbed)
		
	def setRecentlyGrabbed(self):
		self.recentlyGrabbed = True
		print("grabbed true")
		yield viztask.waitTime(0.5)
		self.recentlyGrabbed = False
		print("grabbed false")
	
	def destroySensor(self):
		for manager in self.proximityManagers:
			manager.removeSensor(self.sensor)
		