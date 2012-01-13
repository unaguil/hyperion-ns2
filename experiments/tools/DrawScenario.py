from optparse import OptionParser
import re
import cairo
import math

TRANSMISSION_RANGE = 100.0

class Node:
    def __init__(self, id, x, y, z):
        self.__id = id
        self.__pos = (x, y, z)
        
    def getID(self):
        return self.__id
        
    def getPos(self):
        return self.__pos
    
    def __str__(self):
        return 'node[%s]: %s' % (self.__id, str(self.__pos))
    
def __parseScenario(scenarioFilePath):
    file = open(scenarioFilePath, 'r')
    
    xPattern = '\$node_\(([0-9]+)\) set X_ (.*?)$'
    yPattern = '\$node_\(([0-9]+)\) set Y_ (.*?)$'
    zPattern = '\$node_\(([0-9]+)\) set Z_ (.*?)$'
    
    nodes = []
    
    nodeID = None
    x = y = z = None
    
    for line in file:
        m = re.match(xPattern, line)
        if m is not None:
            nodeID = m.group(1)
            x = float(m.group(2))
        
        m = re.match(yPattern, line)
        if m is not None:
            nodeID = m.group(1)
            y = float(m.group(2))
            
        m = re.match(zPattern, line)
        if m is not None:
            nodeID = m.group(1)
            z = float(m.group(2))
    
        if nodeID is not None and x is not None and y is not None and z is not None:
            nodes.append(Node(nodeID, x, y, z))
            nodeID = None
            x = y = z = None
        
    return nodes

def __getDistance(nodeA, nodeB):
    x1, y1, z1 = nodeA.getPos()
    x2, y2, z2 = nodeB.getPos()
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance 

def __getNeighbours(nodes):
    neighbourTable = {}
    
    for node in nodes:
        neighbourTable[node] = []
        for otherNode in nodes:
            if otherNode is not node:
                distance = __getDistance(node, otherNode)
                #print node.getPos()
                #print otherNode.getPos()
                #print 'Distance from %s to %s : %f' % (node.getID(), otherNode.getID(), distance)
                if distance <= TRANSMISSION_RANGE:
                    #check inverse relation
                    if not otherNode in neighbourTable or not node in neighbourTable[otherNode]:
                        neighbourTable[node].append(otherNode)
                    
    return neighbourTable

def drawScenario(scenarioFilePath, outputFile, width, height):
    nodes = __parseScenario(scenarioFilePath) 
    
    WIDTH, HEIGHT = 1000, 1000
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context (surface)
    
    ctx.scale(WIDTH/1.0, HEIGHT/1.0)
    
    ctx.rectangle(0, 0, 1, 1)
    ctx.set_source_rgb(255, 255, 255)
    ctx.fill()
      
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.002)
    #draw neighbor connections
    neighbourTable = __getNeighbours(nodes)
    for node, neighbours in neighbourTable.items():
        x1, y1, z1 = node.getPos()
        _x1 = x1/width
        _y1 = y1/height
        
        for neighbour in neighbours:
            x2, y2, z2 = neighbour.getPos()
            _x2 = x2/width
            _y2 = y2/height
            #print 'Line from %s to %s' % (node.getID(), neighbour.getID())
            ctx.move_to(_x1, _y1)
            ctx.line_to(_x2, _y2)
            ctx.stroke()
    
    for node in nodes:
        x, y, z = node.getPos()
        _x = x/width
        _y = y/height
        
        #print '%s X: %f %f' %(node.getID(), _x, _y)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(0.002)   
        ctx.arc(_x, _y, .01, 0, 2*math.pi)
        ctx.fill()
        
        #draw node id
        ctx.select_font_face("Georgia")
        ctx.set_font_size(.01)
        x_bearing, y_bearing, _width, _height = ctx.text_extents(node.getID())[:4]
        ctx.move_to(_x - _width / 2 - x_bearing, _y - _height / 2 - y_bearing)
        ctx.set_source_rgb(1, 1, 1)
        ctx.show_text(node.getID())
        ctx.stroke() 
        
    surface.write_to_png (outputFile)

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputFile", help="experiment report used as input")
    parser.add_option("-o", "--output", dest="outputFile", help="Output file")
    parser.add_option("-W", "--width", dest="width", help="Scenario width")
    parser.add_option("-H", "--height", dest="height", help="Scenario height")
    
    (options, args) = parser.parse_args()
    
    if options.inputFile is None or options.outputFile is None or options.width is None or options.height is None:
        parser.print_usage()
    else:
        drawScenario(options.inputFile, options.outputFile, float(options.width), float(options.height))

if __name__ == '__main__':
     main()

