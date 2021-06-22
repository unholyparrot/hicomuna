import sys
import json
import app_window
from PyQt5 import QtWidgets as QtW


if __name__ == '__main__':
    with open("configs.json", "r", encoding="utf-8") as cfg:
        configs = json.load(cfg)
    app = QtW.QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = app_window.MainWindow(configs)
    sys.exit(app.exec_())
