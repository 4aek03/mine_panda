from direct.showbase.ShowBase import ShowBase
import pickle
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight

# import numpy as np

# удаления кеша текстур
loadPrcFile('block_tex/settings.prc')

# # рамдомайзер
# land1 = np.random.randint(3, 4, size=(40, 40))
# with open("land1.txt", "w") as file:
#     file.write('\n'.join(' '.join(str(j) for j in i) for i in land1))

class Game (ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.land = Mapmanager()
        x, y = self.land.loadLand('land1.txt')
        self.hero = Hero((x//4, y//4, 4), self.land)
        base.camLens.setFov(90)

        self.setupLights()
        self.setupSkybox()

    # Основной фон игры чтобы весело было
    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        # дистанция фона от центра
        skybox.setScale(1000)
        skybox.setBin('background', 1)
        # Глубина установки скайбокса или фона
        skybox.setDepthWrite(0)
        # Отключение подсветки скайбокса или фон не реагирует на освещение
        skybox.setLightOff()
        skybox.reparentTo(render)

    # источники освещения
    def setupLights(self):
        # точечный свет
        mainLight = DirectionalLight('main light')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(60, -90, 0)
        render.setLight(mainLightNodePath)

        # рассеянный свет
        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.5, 0.5, 0.5, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)


# <======================================================= Mapmanager ================================================================>

class Mapmanager:
    def __init__(self):
        self.model = 'block.egg'
        self.textures = {
            'block': 'texture/block.png',
            'top_layer': 'texture/kokoin.png',
            '1_layer': 'texture/dirt.png',
            '2_layer': 'texture/diamon.png'
        }
        self.colors = [(0.5, 0.5, 0.5, 0.5), (1, 1, 1, 1)]
        self.startNew()

    def startNew(self):
        self.land = render.attachNewNode('Land')

    def getColor(self, z):
        if z < len(self.colors):
            return self.colors[z]
        else:
            return self.colors[-1]

    def addBlock(self, position, texture_key='block'):
        self.block = loader.loadModel(self.model)
        self.block.setPos(position)
        color = self.getColor(int(position[2]))
        self.block.setColor(color)
        self.block.setTag('at', str(position))

        # Determine texture layers
        if texture_key == 'top_layer':
            self.block.setTexture(loader.loadTexture(self.textures['top_layer']))
        elif texture_key == '1_layer':
            self.block.setTexture(loader.loadTexture(self.textures['1_layer']))
        elif texture_key == '2_layer':
            self.block.setTexture(loader.loadTexture(self.textures['2_layer']))
        else:
            self.block.setTexture(loader.loadTexture(self.textures['block']))

        self.block.reparentTo(self.land)

    def loadLand(self, filename):
        self.clear()
        with open(filename, 'r') as file:
            y = 0
            for line in file:
                x = 0
                line = line.split(' ')
                for z in line:
                    for z0 in range(int(z) + 1):
                        if z0 == int(z):  # Set top layer texture
                            self.addBlock((x, y, z0), texture_key='top_layer')
                        elif z0 == int(z) - 1:  # Set 1_layer texture
                            self.addBlock((x, y, z0), texture_key='1_layer')
                        else:  # Set 2_layer texture
                            self.addBlock((x, y, z0), texture_key='2_layer')
                    x += 1
                y += 1
        return x, y

    def clear(self):
        self.land.removeNode()
        self.startNew()

    def findBlocks(self, pos):
        return self.land.findAllMatches('=at=' + str(pos))

    def isEmpty(self, pos):
        blocks = self.findBlocks(pos)
        return not bool(blocks)

    def findHighestEmpty(self, pos):
        x, y, z = pos
        z = 1
        while not self.isEmpty((x, y, z)):
            z += 1
        return (x, y, z)

    def buildBlock(self, pos):
        x, y, z = pos
        new = self.findHighestEmpty(pos)
        if new[2] <= z + 1:
            self.addBlock(new)

    def delBlock(self, pos):
        blocks = self.findBlocks(pos)
        for block in blocks:
            block.removeNode()

    def delBlockFrom(self, pos):
        x, y, z = self.findHighestEmpty(pos)
        pos = x, y, z - 1
        for block in self.findBlocks(pos):
            block.removeNode()

    def saveMap(self):
        blocks = self.land.getChildren()
        with open('my_map.dat', 'wb') as fout:
            pickle.dump(len(blocks), fout)
            for block in blocks:
                x, y, z = block.getPos()
                pos = (int(x), int(y), int(z))
                pickle.dump(pos, fout)

    def loadMap(self):
        self.clear()
        with open('my_map.dat', 'rb') as fin:
            length = pickle.load(fin)
            for _ in range(length):
                pos = pickle.load(fin)
                self.addBlock(pos)

# <======================================================= Hero ================================================================>


key_switch_camera = '1'
key_switch_mode = '2'

key_forward = 'w'
key_back = 's'
key_left = 'a'
key_right = 'd'

key_up = 'i'
key_down = 'k'

key_turn_left = 'j'
key_turn_right = 'l'

key_build = 'n'
key_destroy = 'm'

key_savemap = '0'
key_loadmap = '9'

key_downcam = 'u'
key_upcam = 'o'

class Hero():
    def __init__(self, pos, land):
        self.land = land
        self.mode = True
        self.hero = loader.loadModel('smiley')
        self.hero.setColor(1, 0.5, 0)
        self.hero.setScale(0.3)
        self.hero.setPos(pos)
        self.hero.reparentTo(render)
        self.cameraBind()
        self.accept_events()

    def cameraBind(self):
        base.disableMouse()
        base.camera.setH(180)
        base.camera.reparentTo(self.hero)
        base.camera.setPos(0, 0, 1.6)
        self.cameraOn = True

    def cameraUp(self):
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)
        base.enableMouse()
        self.cameraOn = False

    def changeView(self):
        if self.cameraOn:
            self.cameraUp()
        else:
            self.cameraBind()

    def turn_left(self):
        self.hero.setH((self.hero.getH() + 5) % 360)

    def turn_right(self):
        self.hero.setH((self.hero.getH() - 5) % 360)

    def look_at(self, angle):
        x_from = round(self.hero.getX())
        y_from = round(self.hero.getY())
        z_from = round(self.hero.getZ())

        dx, dy = self.check_dir(angle)
        x_to = x_from + dx
        y_to = y_from + dy
        return x_to, y_to, z_from

    def check_dir(self, angle):
        if angle >= 0 and angle <= 20:
            return (0, -1)
        elif angle <= 65:
            return (1, -1)
        elif angle <= 110:
            return (1, 0)
        elif angle <= 155:
            return (1, 1)
        elif angle <= 200:
            return (0, 1)
        elif angle <= 245:
            return (-1, 1)
        elif angle <= 290:
            return (-1, 0)
        elif angle <= 335:
            return (-1, -1)
        else:
            return (0, -1)

    def just_move(self, angle):
        pos = self.look_at(angle)
        self.hero.setPos(pos)

    def move_to(self, angle):
        if self.mode:
            self.just_move(angle)
        else:
            self.try_move(angle)

    def forward(self):
        angle = self.hero.getH() % 360
        self.move_to(angle)

    def back(self):
        angle = (self.hero.getH() + 180) % 360
        self.move_to(angle)

    def left(self):
        angle = (self.hero.getH() + 90) % 360
        self.move_to(angle)

    def right(self):
        angle = (self.hero.getH() + 270) % 360
        self.move_to(angle)

    def changeMode(self):
        if self.mode:
            self.mode = False
        else:
            self.mode = True

    def try_move(self, angle):
        pos = self.look_at(angle)
        if self.land.isEmpty(pos):
            pos = self.land.findHighestEmpty(pos)
            self.hero.setPos(pos)
        else:
            pos = pos[0], pos[1], pos[2] + 1
            if self.land.isEmpty(pos):
                self.hero.setPos(pos)

    def up(self):
        if self.mode:
            self.hero.setZ(self.hero.getZ() + 1)

    def down(self):
        if self.mode and self.hero.getZ() > 1:
            self.hero.setZ(self.hero.getZ() - 1)

    def build(self):
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        if self.mode:
            self.land.addBlock(pos)
        else:
            self.land.buildBlock(pos)

    def destroy(self):
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        if self.mode:
            self.land.delBlock(pos)
        else:
            self.land.delBlockFrom(pos)

    def accept_events(self):
        base.accept(key_turn_left, self.turn_left)
        base.accept(key_turn_left + '-repeat', self.turn_left)
        base.accept(key_turn_right, self.turn_right)
        base.accept(key_turn_right + '-repeat', self.turn_right)

        base.accept(key_forward, self.forward)
        base.accept(key_forward + '-repeat', self.forward)
        base.accept(key_back, self.back)
        base.accept(key_back + '-repeat', self.back)
        base.accept(key_left, self.left)
        base.accept(key_left + '-repeat', self.left)
        base.accept(key_right, self.right)
        base.accept(key_right + '-repeat', self.right)

        base.accept(key_switch_camera, self.changeView)
        base.accept(key_switch_mode, self.changeMode)

        base.accept(key_up, self.up)
        base.accept(key_up + '-repeat', self.up)
        base.accept(key_down, self.down)
        base.accept(key_down + '-repeat', self.down)

        base.accept(key_build, self.build)
        base.accept(key_destroy, self.destroy)

        base.accept(key_savemap, self.land.saveMap)
        base.accept(key_loadmap, self.land.loadMap)
game = Game()

game.run()