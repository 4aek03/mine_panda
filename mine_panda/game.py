from direct.showbase.ShowBase import ShowBase
import pickle
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight

from hero import *
from mapmanager import *

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
        base.camLens.setFov(120)

        self.setupLights()
        self.setupSkybox()

    # Основной фон игры чтобы весело было
    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        skybox.setScale(1000)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)

    # источники освещения
    def setupLights(self):
        mainLight = DirectionalLight('main light')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(60, -90, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.5, 0.5, 0.5, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

game = Game()
game.run()