# Sequential search based guess function
def guesser():
    if not hasattr(guesser, "value"):
        guesser.value = 2
    else:
        guesser.value += 1
    return guesser.value


# Fast and efficient guess function
# Any idea what algorithm this is?
def fguesser(resp, maxval=100):
    if resp == "init" or not hasattr(fguesser, "left"):
        fguesser.left = 1
        fguesser.right = maxval
    else:
        if resp == "l" or resp == "L":
            fguesser.right = fguesser.mid - 1
        else:
            fguesser.left = fguesser.mid + 1

    fguesser.mid = (fguesser.left + fguesser.right) // 2
    #print(fguesser.left,fguesser.right,fguesser.mid)
    return fguesser.mid
