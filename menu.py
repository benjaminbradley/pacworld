
import pygame
import colors

COLOR_SELECTED = colors.PINK
COLOR_UNSELECTED = colors.WHITE
BORDER_PADDING = 10
BORDER_WIDTH = 5
COLOR_BACKGROUND = colors.BLACK
COLOR_BORDER = colors.GREEN

# A general purpose menu class
class Menu(object):
  
  def __init__(self, menu_options):
    self.menu_options = menu_options
    self.selected_option_index = 0
    self.menu_option_keys = list(menu_options.keys())
    self.rendered_options_plain = None
    self.rendered_options_selected = None
    self.options_rendered = False
    self.max_width = None
    self.item_height = None
    self.menu_rect = None
    self.top = None
    self.left = None
  
  def draw(self, surface):
    if not pygame.font.get_init():
      pygame.font.init()
    if not self.options_rendered:
      # pre-render all the text, once
      font = pygame.font.Font(None, 30)
      self.rendered_options_plain = []
      self.rendered_options_selected = []
      for key in self.menu_option_keys:
        text = self.menu_options[key]
        textBitmap = font.render(text, True, COLOR_UNSELECTED)
        self.rendered_options_plain.append(textBitmap)
        textBitmap = font.render(text, True, COLOR_SELECTED)
        self.rendered_options_selected.append(textBitmap)
        # figure out menu item dimensions and max width
        if self.max_width is None or self.max_width < textBitmap.get_width():
          self.max_width = textBitmap.get_width()
        if self.item_height is None:
          self.item_height = textBitmap.get_height()
      self.options_rendered = True
      

    # draw it..
    if self.menu_rect is None:
      centerx = int(surface.get_width() / 2)
      centery = int(surface.get_height() / 2)
      width = int(self.max_width + BORDER_PADDING*2 + BORDER_WIDTH*2)
      height = int(len(self.menu_option_keys)*self.item_height + BORDER_PADDING*2 + BORDER_WIDTH*2)
      self.left = centerx - int(width/2)
      self.top = centery - int(height/2)
      self.menu_rect = pygame.Rect(self.left, self.top, width, height)
    # draw the background
    pygame.draw.rect(surface, COLOR_BACKGROUND, self.menu_rect)
    # add a padding border
    pygame.draw.rect(surface, COLOR_BORDER, self.menu_rect, BORDER_WIDTH)
    # render each menu item
    for i in range(len(self.menu_option_keys)):
      # render currently selected item in highlight
      if(i == self.selected_option_index):
        textBitmap = self.rendered_options_selected[i]
      else:
        textBitmap = self.rendered_options_plain[i]
      x = self.left + BORDER_PADDING + BORDER_WIDTH
      y = self.top + BORDER_PADDING + i*self.item_height
      surface.blit(textBitmap, (x,y))


  def selectUp(self):
    self.selected_option_index -= 1
    if(self.selected_option_index < 0): self.selected_option_index = len(self.menu_option_keys)-1

  def selectDown(self):
    self.selected_option_index += 1
    if(self.selected_option_index >= len(self.menu_option_keys)): self.selected_option_index = 0

  # go into a blocking loop until a selection is chosen or menu is cancelled
  def dialog(self, surface, pacjoy = None):
    self.selected_option_index = 0
    self.draw(surface)
    pygame.display.update()
    # go into an event loop
    old_joy_value_y = None
    selection = None
    while selection == None:
      old_selection = self.selected_option_index
      for event in pygame.event.get():
        # check for keyboard up/down/enter
        if(event.type == pygame.KEYDOWN):
          if(event.key == pygame.K_ESCAPE): return None
          elif(event.key == pygame.K_UP):
            self.selectUp()
          elif(event.key == pygame.K_DOWN):
            self.selectDown()
          elif(event.key == pygame.K_RETURN):
            return self.menu_option_keys[self.selected_option_index]
        # check for joystick button
        elif(event.type == pygame.JOYBUTTONDOWN):
          return self.menu_option_keys[self.selected_option_index]
        # check for joystick movement
        if pacjoy is not None:
          joy_value_y = pacjoy.get_joy_axis_y()
          if(joy_value_y == -1 and joy_value_y != old_joy_value_y):  # -1 = up, down = 1
            self.selectUp()
          elif(joy_value_y == 1 and joy_value_y != old_joy_value_y):
            self.selectDown()
          old_joy_value_y = joy_value_y
      # draw an update, if needed
      if old_selection != self.selected_option_index:
        self.draw(surface)
        pygame.display.update()
    return selection




if __name__ == '__main__':  # Begin test code
  screen = pygame.display.set_mode((800, 600))
  pygame.display.set_caption("Menu test")
  menu = Menu({
    0: 'zero zero zero zero zero',
    1: 'one',
    2: 'two two two two'
  })
  result = menu.dialog(screen)
  print("Result of menu is: {}".format(result))
