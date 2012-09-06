import math

def getNearestMarker(marker):
    dist = -1
    minDist = -1
    nearest = -1
    for i in range(0, len(allDetectedMarker)+1):
        dist = math.sqrt(allDetectedMarker[i][0][0] + allDetectedMarker[i][1][0])
        if(dist < minDist or minDist == -1):
            minDist = dist
            nearest = i
    return nearest

#allDetectedMarker = [[[0.4],[0.1],[],[], []], [[0.2],[0.2],[],[], []], [[0.4],[0.0],[],[], []], [[0.2],[0.1],[],[], []], [[0.5],[0.1],[],[], []], [[0.0],[0.0],[],[], []]]
#print allDetectedMarker[0][0][0]
#print getNearestMarker(allDetectedMarker)

a = True
if(a):
    print True