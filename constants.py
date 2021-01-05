
from panda3d.core import NodePath, LineSegs, KeyboardButton
from os.path import join
from collections import namedtuple
from json import loads

_base_obj_path = join("assets", "Models", "OBJ format")
_grass_path = join("assets", "grass_07", "grass_07.obj")
_Object = namedtuple("Object", "path scale position perspective")

SCREEN_WIDTH, SCREEN_HEIGHT = 1256, 600
camera_angle = 6
left, right, space = KeyboardButton.left(), \
                            KeyboardButton.right(), \
                                KeyboardButton.space()


def fetch_objects() -> list:

    list_objects = []
    with open(join("assets", "maps", "map1.json"), "r") as my_file:
        data = my_file.read()
        objects = loads(data)
        for obj in objects:
            list_objects.append(_Object(path=join(_base_obj_path, obj["file"]), 
                    scale=(obj["scale"],) * 3, position=(obj["position_x"], obj["position_y"], obj["position_z"]), 
                        perspective=(obj["perspective_h"], obj["perspective_p"], obj["perspective_r"])))

    return list_objects


ball_blue = _Object(path=join(_base_obj_path, "ball_blue.obj"), 
                scale=(2.5,) * 3, position=(-4.8, 9.8, 0), perspective=(0,) * 3)


ball_green = _Object(path=join(_base_obj_path, "ball_green.obj"), 
                scale=(2.5,) * 3, position=(-4.8, 9.8, 0), perspective=(0,) * 3)


ball_red = _Object(path=join(_base_obj_path, "ball_red.obj"), 
                scale=(2.5,) * 3, position=(-4.8, 9.8, 0), perspective=(0,) * 3)


club_blue = _Object(path=join(_base_obj_path, "club_blue.obj"), 
                scale=(1.5,) * 3, position=(-5, 10, 0.3), perspective=(90, 90, 135))


club_green = _Object(path=join(_base_obj_path, "club_green.obj"), 
                scale=(1.5,) * 3, position=(-5, 10, 0.3), perspective=(90, 90, 135))


club_red = _Object(path=join(_base_obj_path, "club_red.obj"), 
                scale=(1.5,) * 3, position=(-5, 10, 0.3), perspective=(90, 90, 135))


flag_red = _Object(path=join(_base_obj_path, "flag_red.obj"), 
                scale=(1.5,) * 3, position=(2, 8.6, -0.94), perspective=(90, 90, 135))


grass = _Object(path=_grass_path, 
                scale=(4.5, 10, 4.5), position=(-60, -60, -2), perspective=(0, 0, 0))


class PowerLine():
    def __init__(self):
        
        self.np = NodePath('pen')

    def create( self, pos, size):

        segs = LineSegs()
        segs.setThickness(3.0)
        segs.moveTo(pos[0], pos[1], pos[2])
        segs.setColor(255, 255, 255, 1)
        segs.drawTo(pos[0] + size, pos[1], pos[2])
        return segs.create()

