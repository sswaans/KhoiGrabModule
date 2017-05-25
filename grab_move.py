import viz
import viztask
import vizproximity
import vizshape
import vizact

import steamvr

class grab_mod:
	'Handles all grabbing interactions'
	def __init__(self, items, controllers, destinations, reqTrigger, handSensitivity = 0.09):
		#Items - list of node3d objects
		#Targets - list of node3d objects or locations
		self.items = items
		self.controllers = controllers
		self.destinations = destinations
		self.reqTrigger = reqTrigger
		self.grabProximityManager = vizproximity.Manager()
		self.placeProximityManager = vizproximity.Manager()
		self.grabbedItems = []
		self.handSensitivity = handSensitivity
		vizact.onkeydown('d', self.grabProximityManager.setDebug, viz.TOGGLE)
		self.grabProximityManager.onEnter(None,self.grabItem)
		self.placeProximityManager.onEnter(None, self.placeItem)
		for i in range(0, len(items)):
			items[i] = itemToGrab(items[i])
			items[i].setup(self.grabProximityManager)
		for controller in controllers:
			targetSphere = vizshape.addSphere(handSensitivity)
			targetSphere.disable(viz.RENDERING)
			viz.link(controller, targetSphere)
			target = vizproximity.Target(targetSphere)
			self.grabProximityManager.addTarget(target)
			self.placeProximityManager.addTarget(target)
		for destination in destinations:
			destination = itemToGrab(destination)
			destination.setup(self.placeProximityManager, sensorScale = [3,3,3])
	def addItem(self, item):
		item = itemToGrab(item)
		self.items.append(item)
	
	def activateRange(self,e):
		pass
		
	def grabItem(self, e):
		itemGrabbed = e.sensor.getSource()._node
		link = viz.link(e.target.getSource()._node,itemGrabbed)
		self.grabbedItems.append([itemGrabbed, e.target.getSource(), link]) #make into a class
	
	def placeItem(self, e):
		print(self.grabbedItems)
		target = e.target.getSource()
		for grabbedItem in self.grabbedItems:
			if target == grabbedItem[1]:
				grabbedItem[2].remove()
				grabbedItem[0].setPosition(e.sensor.getSource()._node.getPosition())
				self.grabbedItems.remove(grabbedItem)

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
		