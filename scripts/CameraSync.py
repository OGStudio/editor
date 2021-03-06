
import pymjin2

class CameraSyncImpl(object):
    def __init__(self, client):
        # Refer.
        self.c = client
        self.isInSync = False
    def __del__(self):
        # Derefer.
        self.c = None
    def cameraToNode(self):
        pos = self.c.get("camera.position")[0]
        rot = self.c.get("camera.rotation")[0]
        self.c.set("node.$SCENE.$NODE.position", pos)
        self.c.set("node.$SCENE.$NODE.rotation", rot)
    def nodeToCamera(self):
        self.isInSync = True
        pos = self.c.get("node.$SCENE.$NODE.position")[0]
        rot = self.c.get("node.$SCENE.$NODE.rotation")[0]
        self.c.set("camera.position", pos)
        self.c.set("camera.rotation", rot)
        self.isInSync = False
    def setPosition(self, key, value):
        if (self.isInSync):
            return
        self.nodeToCamera()
    def setRotation(self, key, value):
        if (self.isInSync):
            return
        self.nodeToCamera()
    def setSync(self, key, value):
        #print "setSync", key, value
        src = value[0]
        if (src == "node"):
            self.nodeToCamera()
        else:
            self.cameraToNode()

class CameraSync(object):
    def __init__(self, sceneName, nodeName, env):
        # Create.
        self.c = pymjin2.EnvironmentClient(env, "CameraSync")
        self.impl = CameraSyncImpl(self.c)
        # Prepare.
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        #print "CameraSync. node name:", nodeName
        self.impl.nodeToCamera()
        self.c.provide("camera.sync", self.impl.setSync)
        # Listen to node orientation changes.
        self.c.listen("node.$SCENE.$NODE.position", None, self.impl.setPosition)
        self.c.listen("node.$SCENE.$NODE.rotation", None, self.impl.setRotation)
        #print "{0} CameraSync.__init__({1}, {2})".format(id(self), sceneName, nodeName)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy
        del self.impl
        del self.c
        #print "{0} CameraSync.__del__".format(id(self))

def SCRIPT_CREATE(sceneName, nodeName, env):
    return CameraSync(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

