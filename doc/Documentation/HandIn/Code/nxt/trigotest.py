GRAD2CM = 1
CM2GRAD = 1
import math


def berechnePunkt(ausrichtung, entfernung, standort={'x':0.0, 'y':0.0}):
    pos = {'x':0.0, 'y':0.0}
    pos['x'] = standort['x'] + entfernung*GRAD2CM*math.cos(ausrichtung*(math.pi/180.0))
    pos['y'] = standort['y'] + entfernung*GRAD2CM*math.sin(ausrichtung*(math.pi/180.0))
    return pos

def berechneVektor(standort={'x':0.0, 'y':0.0}, ziel={'x': 0.0, 'y': 0.0}):
    relativ_ziel = {'x': ziel['x']-standort['x'],'y': ziel['y']-standort['y']}
    entfernung = math.sqrt(relativ_ziel['x']**2+relativ_ziel['y']**2)
    if relativ_ziel['x'] == 0: 
        winkel = 0
    elif relativ_ziel['x'] < 0:
        winkel = math.atan(relativ_ziel['y']/relativ_ziel['x'])*(180.0/math.pi)+180
    else:
        winkel = math.atan(relativ_ziel['y']/relativ_ziel['x'])*(180.0/math.pi)+360
    return {'winkel': winkel%360, 'entfernung': entfernung*CM2GRAD}

def test():
    for winkel in range(0,360, 90):
        p = berechnePunkt(winkel,math.sqrt(2))
        print "%d. Punkt: (%f,%f)" % (winkel ,p['x'],p['y'])
        v = berechneVektor(ziel=p)
        print "%d. Vektor: (%f,%f)" % (winkel ,v['winkel'],v['entfernung'])
        p2 = berechnePunkt(v['winkel'],v['entfernung'])
        print "%d. Punkt: (%f,%f)\n" % (winkel ,p2['x'],p2['y'])
test()
