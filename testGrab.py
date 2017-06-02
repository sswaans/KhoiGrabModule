import viz
import viztask
import vizproximity

import steamvr

import grab_move

viz.go()

hmd = steamvr.HMD()
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())

viz.addChild('piazza.osgb')

controllers = steamvr.getControllerList()
assert(len(controllers) == 2)
viz.link(controllers[0],controllers[0].addModel()) # = viz.addChild('box.wrl')
viz.link(controllers[1],controllers[1].addModel()) # = viz.addChild('box.wrl')
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

grabMod = grab_move.grab_mod(items, controllers, destinations, True)