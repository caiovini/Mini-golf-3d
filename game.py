from direct.showbase.ShowBase import (ShowBase, 
                                      loadPrcFileData, 
                                      NodePath, 
                                      Vec3)

from panda3d.core import (DirectionalLight,
                          CollisionTraverser, 
                          CollisionHandlerEvent, 
                          CollisionSphere, 
                          CollisionCapsule, 
                          CollisionNode,
                          TextNode)

from panda3d.bullet import (BulletWorld,
                            BulletSphereShape,
                            BulletRigidBodyNode, 
                            BulletDebugNode, 
                            BulletTriangleMesh, 
                            BulletTriangleMeshShape)

from panda3d.physics import LinearVectorForce, ForceNode
from constants import *

import math

loadPrcFileData("", f"win-size {SCREEN_WIDTH} {SCREEN_HEIGHT}")
loadPrcFileData("", "window-title Mini-Golf-3d") 


class Game(ShowBase):

    def __init__(self):

        super().__init__(self)
        self.base = base
        self.base.setFrameRateMeter(True)

        # Create a traverser that Panda3D will automatically use every frame.
        self.base.cTrav = CollisionTraverser()
        # Create a handler for the events.
        self.collHandEvent = CollisionHandlerEvent()
        self.collHandEvent.addInPattern('into-%in')

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.accept("escape", self.base.finalizeExit)
        self.is_game_win = False
        self.blows = 0

        class PowerSpace():

            is_space_key_pressed = False

        self.power_space = PowerSpace()
        self.accept("space", lambda: setattr(self.power_space, "is_space_key_pressed", True))
        self.accept("space-up", lambda: setattr(self.power_space, "is_space_key_pressed", False))

        #debugNode = BulletDebugNode('Debug')
        #debugNode.showWireframe(True)
        #debugNode.showConstraints(True)
        #debugNode.showBoundingBoxes(False)
        #debugNode.showNormals(False)
        #debugNP = self.render.attachNewNode(debugNode)
        #debugNP.show()
        #self.world.setDebugNode(debugNP.node())
        
        self.ball, _ = self.create_model(ball_blue)
        self.club, _ = self.create_model(club_blue)
        self.flag, _ = self.create_model(flag_red)
        self.grass, _ = self.create_model(grass)

        grass_texture = self.loader.loadTexture(join("assets", "grass_07", "diffus.tga"))
        self.grass.setTexture(grass_texture, 1)

        # Create golf course and shapes
        models = fetch_objects()
        for m in models:
            model, geom_model = self.create_model(m)
            self.create_shape_mesh(geom=geom_model, model=model)

        self.collCount = 0
        ball_sphere, ball_sphere_name = self.create_collision_ball(self.ball, False)
        club_capsule, _ = self.create_collision_club(self.club, False)
        flag_capsule, flag_capsule_name = self.create_collision_flag(self.flag, False)
        
        self.base.cTrav.addCollider(ball_sphere, self.collHandEvent)
        self.base.cTrav.addCollider(club_capsule, self.collHandEvent)
        self.base.cTrav.addCollider(flag_capsule, self.collHandEvent)


        self.did_collide = False
        self.accept(f"into-{ball_sphere_name}", self.handle_collision_ball)
        self.accept(f"into-{flag_capsule_name}", self.handle_collision_flag)



        # Create shape for the ball using a sphere instead of a mesh
        self.shape_ball = BulletSphereShape(.1)
        node = BulletRigidBodyNode('Golf-ball')

        # Dynamic bodies have mass
        node.setMass(2.0)
        node.addShape(self.shape_ball)

        self.np_ball = self.render.attachNewNode(node)
        self.np_ball.setPos(self.ball.getPos())
        self.world.attachRigidBody(node)
        

        # Set simple directional light and attach to the camera
        dlight = DirectionalLight('directional-light')
        dlight.setColor((1.5, 1.5, 1.5, 1))
        dlnp = self.camera.attachNewNode(dlight)
        self.render.setLight(dlnp)


        self.base.disableMouse()
        self.camera.setPos(20 * math.sin(math.radians(camera_angle)),
                           20 * math.cos(math.radians(camera_angle)), camera_angle)
        self.camera.setH(camera_angle)
        self.camera.lookAt(self.ball)

        self.textPower = TextNode('node-power-text')
        self.textPower.setText("POWER")
        self.textPower.setTextColor(255, 255, 0, 1)
        self.textPowerPath = aspect2d.attachNewNode(self.textPower)
        self.textPowerPath.setScale(0.08)
        self.textPowerPath.setPos(-2.01, 0, 0.9)

        self.textBlows = TextNode('node-blows-text')
        self.textBlows.setText(f"Blows: {self.blows}")
        self.textBlows.setTextColor(255, 255, 0, 1)
        self.textBlowPath = aspect2d.attachNewNode(self.textBlows)
        self.textBlowPath.setScale(0.08)
        self.textBlowPath.setPos(-0.15, 0, 0.9)

        self.textGameWin = TextNode('node-game-win-text')
        self.textGameWin.setTextColor(255, 255, 0, 1)
        self.textGamePath = aspect2d.attachNewNode(self.textGameWin)
        self.textGamePath.setScale(0.10)
        self.textGamePath.setPos(-0.3, 0, 0)

        power_line = PowerLine()
        self.impulse_to_be_applied = 0.05
        self.np_ball_power_line = aspect2d.attachNewNode(power_line.create(Vec3(-2.01, 0, 0.85), self.impulse_to_be_applied))

        self.is_ball_moving = False
        ball_last_position = None
        def update(task):   

           
            nonlocal ball_last_position
            dt = globalClock.getDt()
            self.world.doPhysics(dt)
            self.ball.setPos(self.np_ball.getPos())
            self.ball.setHpr(self.np_ball.getHpr())

            # Case ball falls
            if(self.ball.getZ()) < -10:
                self.np_ball.setPos(-4.8, 9.8, 0)
                if not self.is_game_win:
                    return task.cont

            if ball_last_position != self.ball.getPos():

                ball_last_position = self.ball.getPos()
                self.camera.lookAt(self.ball)
                self.is_ball_moving = True
                if not self.is_game_win:
                    return task.cont

            # Execute once
            if self.is_ball_moving:
                self.club.setZ(self.ball.getZ() + 1.12)
                self.club.setX(self.np_ball.getX() - .2)
                self.club.setY(self.np_ball.getY() + .2)
                self.club.setR(135)
                self.did_collide = False

            self.camera.lookAt(self.ball)
            self.is_ball_moving = False
            if not self.is_game_win:
                return task.cont

        self.taskMgr.add(update)
        self.taskMgr.add(self.handle_keys_pressed, "keys_pressed")



    def handle_keys_pressed(self, task):

        is_down = base.mouseWatcherNode.is_button_down        
            
        if not self.is_ball_moving and not self.is_game_win:

            if is_down(left):
                self.club.setR(self.club.getR() + 5)

                # Reduce radius by dividing by 40
                self.club.setX(self.club.getX() - math.sin(math.radians(self.club.getR())) / 40)
                self.club.setY(self.club.getY() + math.cos(math.radians(self.club.getR())) / 40)

            if is_down(right):
                self.club.setR(self.club.getR() - 5)

                # Reduce radius by dividing by 40
                self.club.setX(self.club.getX() + math.sin(math.radians(self.club.getR())) / 40)
                self.club.setY(self.club.getY() - math.cos(math.radians(self.club.getR())) / 40)

            if not is_down(right) and not is_down(left):
                if is_down(space) and self.impulse_to_be_applied < 0.3:
                    
                    power_line = PowerLine()
                    self.impulse_to_be_applied += 0.01
                    self.np_ball_power_line.removeNode()
                    self.np_ball_power_line = aspect2d.attachNewNode(power_line.create(Vec3(-2.01, 0, 0.85), self.impulse_to_be_applied))

                if not self.power_space.is_space_key_pressed and self.impulse_to_be_applied > 0.05 and not self.did_collide:
                    
                    # Calculate direction to move the club and slow down speed by dividing by 10
                    # Move the club towards the ball
                    self.club.setX(self.club.getX() - math.cos(math.radians(self.club.getR())) / 10)
                    self.club.setY(self.club.getY() - math.sin(math.radians(self.club.getR())) / 10)



        return task.cont

    def handle_collision_flag(self, _):
        self.is_game_win = True
        self.textGameWin.setText("Game win !!!")

    def handle_collision_ball(self, _):


        if not self.is_ball_moving:
            self.blows += 1
            self.textBlows.setText(f"Blows: {self.blows}")
            self.did_collide = True
         
            # Which direction ball will move
            dx, dy = (self.ball.getX() - self.club.getX(),
                      self.ball.getY() - self.club.getY())


            self.np_ball.node().setActive(True)
            self.np_ball.node().applyCentralImpulse(Vec3(dx*self.impulse_to_be_applied*1000,
                                                         dy*self.impulse_to_be_applied*1000, 2))
            self.np_ball.node().setAngularFactor(Vec3(0, 0 ,0))

        
        self.impulse_to_be_applied = 0.05
        power_line = PowerLine()
        self.np_ball_power_line.removeNode()
        self.np_ball_power_line = aspect2d.attachNewNode(power_line.create(Vec3(-2.01, 0, 0.85), self.impulse_to_be_applied))
       

    def create_model(self, object) -> tuple:

        model = self.loader.loadModel(object.path)
        geomNodes = model.findAllMatches('**/+GeomNode')
        geomNode = geomNodes.getPath(0).node()

        model.set_scale(object.scale)
        model.setPos(object.position)
        model.setHpr(object.perspective)
        model.reparentTo(self.render)
        
        return model, geomNode.getGeom(0)

    def create_shape_mesh(self, geom, model) -> None:

        mesh = BulletTriangleMesh()
        mesh.addGeom(geom)

        shape_mesh = BulletTriangleMeshShape(mesh, dynamic=False)

        node = BulletRigidBodyNode(str(model)) # Name of imported obj
        node.addShape(shape_mesh)

        np = self.render.attachNewNode(node)
        np.setPos(model.getPos())
        np.setHpr(model.getHpr())

        self.world.attachRigidBody(node)

    def create_collision_ball(self, obj, show=False):
        
        # Get the size of the object for the collision sphere.
        bounds = obj.getChild(0).getBounds()
        center = bounds.getCenter()
        radius = bounds.getRadius() * 1.1

        # Create a collision sphere and name it something understandable.
        collSphereStr = f'CollisionHull{self.collCount}_{obj.name}'
        self.collCount += 1
        cNode = CollisionNode(collSphereStr)
        cNode.addSolid(CollisionSphere(center, radius))

        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()

        # Return a tuple with the collision node and its corrsponding string so
        # that the bitmask can be set.
        return (cNodepath, collSphereStr)

    def create_collision_club(self, obj, show=False):

        bounds = obj.getChild(0).getBounds()
        bottom = bounds.getCenter() * 2.4 # Aproximately

        # Create a collision capsule and name it something understandable.
        collCapsuleStr = f'CollisionHull{self.collCount}_{obj.name}'
        self.collCount += 1
        cNode = CollisionNode(collCapsuleStr)
        capsule = CollisionCapsule(-0.05, bottom[1], 0, 0.05, bottom[1], 0, 0.05)
        
        cNode.addSolid(capsule)

        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()

        # Return a tuple with the collision node and its corrsponding string so
        # that the bitmask can be set.
        return (cNodepath, collCapsuleStr)

    def create_collision_flag(self, obj, show=False):

        bounds = obj.getChild(0).getBounds()
        bottom = bounds.getCenter() * 1 # Aproximately

        # Create a collision capsule and name it something understandable.
        collCapsuleStr = f'CollisionHull{self.collCount}_{obj.name}'
        self.collCount += 1
        cNode = CollisionNode(collCapsuleStr)
        capsule = CollisionCapsule(bottom[0], bottom[1], bottom[2], 0, 0, 0, .05)
        
        cNode.addSolid(capsule)

        cNodepath = obj.attachNewNode(cNode)
        if show:
            cNodepath.show()

        # Return a tuple with the collision node and its corrsponding string so
        # that the bitmask can be set.
        return (cNodepath, collCapsuleStr)




if __name__ == "__main__":
    game = Game()
    game.run()
