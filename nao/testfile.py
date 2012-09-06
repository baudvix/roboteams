def calculateAVG(array):
    avg = 0
    if(array != []):
        for elem in array:
            avg+=elem
        return avg/len(array)


def mostFrequent(lst):
    return max(set(lst), key=lst.count)

print calculateAVG([2, 1])
print mostFrequent(["a", "b", "a"])
