import sys
import PyQt5.QtWidgets as QtW
import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Plotter(QtW.QWidget):
    def __init__(self, config):
        self.my_config = config
        super().__init__()
        self.pw = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem('bottom')})
        self.p1 = self.pw.plotItem
        # right axis of the plot & linking to view
        self.p2 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.p1)
        # setting up the axis names
        self.set_up_table_plot()
        # update while zooming
        self.update_views()
        self.p1.vb.sigResized.connect(self.update_views)

    def update_views(self):
        # view has resized; update auxiliary views to match
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        # need to re-update linked axes since this was called
        # incorrectly while views had different shapes.
        # (probably this should be handled in ViewBox.resizeEvent)
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

    def set_up_table_plot(self):
        self.pw.showGrid(x=True, y=True)
        for axs in ['left', 'right', 'bottom']:
            self.p1.getAxis(axs).setLabel(self.my_config["Axis"][axs]["label"],
                                          color=self.my_config["Axis"][axs]["color"])
        # self.p1.getAxis('left').setLabel("Velocity", color='#ff00e1')
        # self.p1.getAxis('right').setLabel('AC', color='#0000ff')
        # self.p1.getAxis('bottom').setLabel("Datetime", color='#E4DEFF')
        # self.pw.addLegend()


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)
    ex = Plotter({})
    sys.exit(app.exec_())
