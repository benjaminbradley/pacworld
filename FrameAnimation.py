
# class to cycle through an array of Surfaces
class FrameAnimation(object):
  def __init__(self):
    self.frames = []

  def addFrame(self, surface):
    """add a frame to the animation"""
    self.frames.append(surface)

  def getNumFrames(self):
    return len(self.frames)

  def getFrame(self, index):
    """get the specified frame of the animation"""
    return self.frames[index]

  def getNextFrame(self, index):
    """advance the index to the next frame"""
    index += 1
    if(index >= self.getNumFrames()): index = 0
    return index
