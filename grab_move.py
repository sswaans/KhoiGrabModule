import viz
import viztask
import vizproximity
import vizshape
import vizact

import steamvr

class grab_mod:
	'Handles all grabbing interactions'
	def __init__(self, items, controllers, destinations, reqTrigger = False, itemsInHand = [], handSensitivity = 0.12):
		#Items - list of node3d objects
		#Targets - list of node3d objects or locations
		self.items = items
		self.itemsInHand = itemsInHand
		self.controllers = controllers
		self.destinations = destinations
		self.reqTrigger = reqTrigger
		self.grabProximityManager = vizproximity.Manager()
		self.placeProximityManager = vizproximity.Manager()
		self.grabbedItems = []
		self.handSensitivity = handSensitivity
		self.hoveredItem = None
		vizact.onkeydown('d', self.grabProximityManager.setDebug, viz.TOGGLE)
		self.grabProximityManager.onEnter(None,self.grabItem)
		self.grabProximityManager.onExit(None, self.exitNode)
		self.placeProximityManager.onEnter(None, self.placeItem)
		self.targets = [None, None]
		#viztask.schedule(self.grabItem)
		for i in range(0, len(items)):
			items[i] = itemToGrab(items[i])
			items[i].setup(self.grabProximityManager)
		for i in range(len(controllers)):
			targetSphere = vizshape.addSphere(handSensitivity)
			targetSphere.disable(viz.RENDERING)
			viz.link(controllers[i], targetSphere)
			target = vizproximity.Target(targetSphere)
			self.grabProximityManager.addTarget(target)
			self.placeProximityManager.addTarget(target)
			self.targets[i] = target

		for destination in destinations:
			destination = itemToGrab(destination)
			destination.setup(self.placeProximityManager, sensorScale = [3,3,3])
			
		for item in itemsInHand:
			item.disable(viz.RENDERING)
			
		vizact.onsensordown(controllers[0], steamvr.BUTTON_TRIGGER, self.triggerGrabItem, 0)
		vizact.onsensordown(controllers[1], steamvr.BUTTON_TRIGGER, self.triggerGrabItem, 1)
	def exitNode(self, e):
		self.hoveredItem = None
	def triggerGrabItem(self, controllerIndex):
		print("trigger grab called")
		if self.hoveredItem == None or not self.reqTrigger:
			return
		else:
			target = self.targets[controllerIndex]
			self.actuallyGrabItem(self.hoveredItem, target.getSource())
			
	def addItem(self, item):
		item = itemToGrab(item)
		self.items.append(item)
	
	def activateRange(self,e):
		pass
		
	def grabItem(self, e):
		#viztask.schedule(self.actuallyGrabItem(e))
		self.hoveredItem = e.sensor.getSource()._node
		if not self.reqTrigger:			
			self.actuallyGrabItem(e.sensor.getSource()._node, e.target.getSource());
		
	def actuallyGrabItem(self, item, controller):
		if len(self.itemsInHand) > 0:
			for i in range(len(items)):
				if item == self.items[i].item:
					self.itemsInHand[i].enable(viz.RENDERING)
					item.disable(viz.RENDERING)
					link = viz.link(controller._node, self.itemsInHand[i])
					self.grabbedItems.append([item._node, controller, link])
		else:
			itemGrabbed = item
			link = viz.link(controller._node,itemGrabbed)
			self.grabbedItems.append([itemGrabbed, controller, link]) #make into a class
		
	def placeItem(self, e):
		print(self.grabbedItems)
		target = e.target.getSource()		
		for grabbedItem in self.grabbedItems:
			if target == grabbedItem[1]:
				if len(self.itemsInHand) > 0:
					for i in range(len(items)):
						if grabbedItem[0] == self.items[i].item:
							self.destinations[i].enable(viz.RENDERING)
							self.itemsInHand[i].disable(viz.RENDERING)
							self.grabbedItems.remove(grabbedItem)
				grabbedItem[2].remove()
				grabbedItem[0].setPosition(e.sensor.getSource()._node.getPosition())
				self.grabbedItems.remove(grabbedItem)
				
	def vibrateController(self, i):
		self.controllers[i].setVibration(0.004)
	def waitTrigger(self, controller):
		yield viztask.waitSensorDown(controller, steamvr.BUTTON_TRIGGER)

class itemToGrab:
	'Base class for an item to grab'
	def __init__(self, itemNode):
		self.itemNode = itemNode
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
		
		proximityManager.addSensor(sensor)
		