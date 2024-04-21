# <======================================================= Mapmanager ================================================================>
import pickle
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
                        if z0 == int(z):
                            self.addBlock((x, y, z0), texture_key='top_layer')
                        elif z0 == int(z) - 1:
                            self.addBlock((x, y, z0), texture_key='1_layer')
                        else:
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