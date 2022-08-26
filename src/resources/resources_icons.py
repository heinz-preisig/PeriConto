import os

from PyQt5 import QtCore
from PyQt5 import QtGui

# ===========================================  icons ==============================
ICONS = {}
ICONS["+"] = "plus-icon.png"
ICONS["-"] = "minus-icon.png"
ICONS["->"] = "right-icon.png"
ICONS["<-"] = "left-icon.png"
ICONS["^"] = "up-icon.png"
ICONS["v"] = "down-icon.png"
ICONS["load"] = "load_button_hap.svg"
ICONS["exit"] = "exit_button_hap.svg"
ICONS["info"] = "info_button_hap.svg"
ICONS["accept"] = "accept_button_hap.svg"
ICONS["reject"] = "reject_button_hap.svg"
ICONS["back"] = "back_button_hap.svg"
ICONS["new"] = "new_button_hap.svg"
ICONS["dot_graph"] = "dot_graph_button_hap.svg"
ICONS["save"] = "save_button_hap.svg"
ICONS["delete"] = "delete_button_hap.svg"
ICONS["reset"] = "reset_button_hap.svg"
ICONS["screen_shot"] = "screen_shot_button_hap.svg"
ICONS["save_as"] = "save_as_button_hap.svg"
ICONS["plus"] = "plus_button_hap.svg"
ICONS["update"] = "update_button_hap.svg"
ICONS["next"] = "next_button_hap.svg"

size = 52
BUTTON_ICON_SIZE = QtCore.QSize(size, size)
round = 'border-radius: %spx; ' % (size / 2)
BUTTON_ICON_STYLE_ROUND = 'background-color: white; '
BUTTON_ICON_STYLE_ROUND += 'border-style: outset; '
BUTTON_ICON_STYLE_ROUND += 'border-width: 2px; '
BUTTON_ICON_STYLE_ROUND += round
BUTTON_ICON_STYLE_ROUND += 'border-color: white;    '
BUTTON_ICON_STYLE_ROUND += 'font: bold 14px;   '
BUTTON_ICON_STYLE_ROUND += 'padding: 6px;'


def roundButton(button, what, tooltip=None):
  button.setText("")
  button.setFixedSize(BUTTON_ICON_SIZE)
  button.setIcon(getIcon(what))
  button.setStyleSheet(BUTTON_ICON_STYLE_ROUND)
  button.setIconSize(BUTTON_ICON_SIZE)
  button.setToolTip(tooltip)
  # button.setStyleSheet("""QToolTip {
  #                            background-color: black;
  #                            color: white;
  #                            border: black solid 1px
  #                            }""")


def getIcon(what):
  try:
    what in ICONS.keys()
  except:
    print("assertation error %s is not in the icon dictionary" % what)
    os.exit()

  f_name = os.path.join(os.path.curdir, "resources", "icons", ICONS[what])
  # print("debugging .....", f_name)
  if os.path.exists(f_name):
    pm = QtGui.QPixmap(f_name)
    return QtGui.QIcon(pm)
  else:
    print("no such file : ", f_name)
    pass
