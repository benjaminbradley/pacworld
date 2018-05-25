
class Pacjoy(object):
  def __init__(self, joystick):
    self.joystick = joystick
    self.joystick.init()
    self.joy_axis_x = None
    self.joy_axis_y = None

  def setXaxis(self, i):
    self.joy_axis_x = i

  def setYaxis(self, i):
    self.joy_axis_y = i

  def get_joy_axis_y(self):
    return round(self.joystick.get_axis( self.joy_axis_y ))

  def get_joy_axis_x(self):
    return round(self.joystick.get_axis( self.joy_axis_x ))

  def get_button(self, i):
    return self.joystick.get_button(i)

  def get_axis(self, i):
    return self.joystick.get_axis(i)

  def get_numbuttons(self):
    return self.joystick.get_numbuttons()

  def get_numaxes(self):
    return self.joystick.get_numaxes()
