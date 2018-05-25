from menu import Menu

MENU_CANCEL = None
MENU_POWEROFF = 1
MENU_CONFIRM = 1

pacmenu_instance = None
def getMenu():
  global pacmenu_instance
  if not pacmenu_instance:
    pacmenu_instance = Menu({
      MENU_CANCEL: 'cancel',
      -1: 'please cancel',
      -2: 'really you want to cancel',
      MENU_POWEROFF: 'power off',
    })
  return pacmenu_instance

pacconfirm_instance = None
def getConfirmMenu():
  global pacconfirm_instance
  if not pacconfirm_instance:
    pacconfirm_instance = Menu({
      MENU_CANCEL: 'no, not really, cancel!',
      MENU_CONFIRM: 'yes, really',
    })
  return pacconfirm_instance
