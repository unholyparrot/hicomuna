import sys
import time
import datetime
import numpy as np
import pyqtgraph as pg
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import drawer_and_up


def timestamps_from_dates(array):
    to_ret = []
    for elem in array:
        to_ret.append(time.mktime(datetime.datetime.strptime(elem, "%d/%m/%Y %H:%M").timetuple()))
    return to_ret


def sort_dates(array):
    sub_arr = timestamps_from_dates(array)
    return np.argsort(sub_arr)


class MainWindow(QtW.QWidget):

    def __init__(self, config_dict):
        super().__init__()
        self.config_dict = config_dict
        self.table = None
        self.plot = None
        self.file_title = None
        self.data_keeper = None
        self.filename = None
        self.scatter_plots = dict()
        self.line_plots = dict()
        self.button_add_row = None
        self.button_delete_row = None
        self.init_ui()

    def init_ui(self):
        button_open_file = QtW.QPushButton('Open CSV file')
        button_open_file.clicked.connect(self.get_text_file)
        button_new_file = QtW.QPushButton('Create CSV file')
        button_new_file.clicked.connect(self.create_text_file)

        self.file_title = QtW.QLabel("Patient name")

        self.button_add_row = QtW.QPushButton('Add new row')
        self.button_add_row.clicked.connect(self.add_new_row)
        self.button_add_row.setEnabled(False)
        self.button_delete_row = QtW.QPushButton('Delete row')
        self.button_delete_row.clicked.connect(self.delete_row)
        self.button_delete_row.setEnabled(False)

        self.table = pg.TableWidget(editable=True, sortable=False)

        self.plot = drawer_and_up.pyqtdrawer.Plotter(self.config_dict["PlotWidget"])
        self.draw_plot()
        # legend_plot = drawer_and_up.pyqtdrawer.LegendPlotter()

        grid = QtW.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(button_open_file, 1, 0)
        grid.addWidget(button_new_file, 1, 1)
        grid.addWidget(self.file_title, 2, 0, 1, 2)
        grid.addWidget(self.button_add_row, 3, 0)
        grid.addWidget(self.button_delete_row, 3, 1)
        grid.addWidget(self.table, 4, 0, 4, 2)
        grid.addWidget(self.plot.pw, 1, 2, 6, 4)
        # grid.addWidget(legend_plot, 7, 2, 3, 4)

        self.setLayout(grid)

        self.setGeometry(50, 50, 1250, 650)
        self.setWindowTitle('Hicomuna')
        self.show()

    def closeEvent(self, event):
        reply = QtW.QMessageBox.question(self, 'Message',
                                         "Are you sure to quit?", QtW.QMessageBox.Yes |
                                         QtW.QMessageBox.No, QtW.QMessageBox.No)

        if reply == QtW.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def load_any_file(self, file_name):
        if file_name.endswith('.csv'):
            self.file_title.setText(file_name)
            # noinspection PyTypeChecker
            self.data_keeper = np.genfromtxt(file_name, delimiter=",", names=True,
                                             dtype=[('Date', '<U32'), ('Vtop', '<f8'), ('Vtail', '<f8'),
                                                    ('Enoxa', '<i4'),
                                                    ('RecEnoxa', '<i4'), ('Infusion', '<i4'), ('RecInfusion', '<i4'),
                                                    ('Event', '<U32'), ('Comment', '<U32')], encoding="utf-8")
            self.data_keeper = self.data_keeper[sort_dates(self.data_keeper["Date"])]
            self.update_table()
            self.update_plot()
            self.button_add_row.setEnabled(True)
            self.button_delete_row.setEnabled(True)
        else:
            print("CSV extension expected.")

    def get_text_file(self):
        dialog = QtW.QFileDialog()
        dialog.setFileMode(QtW.QFileDialog.AnyFile)
        dialog.setFilter(QtC.QDir.Files)

        if dialog.exec_():
            file_name = dialog.selectedFiles()
            self.filename = file_name[0]
            self.load_any_file(self.filename)

    def create_text_file(self):
        file_name = QtW.QFileDialog.getSaveFileName(self, 'Save File')

        if file_name[0].endswith('.csv'):
            with open(file_name[0], "w", encoding="utf-8") as fw:
                fw.write(",".join(self.config_dict["Table"]["Headings"]) + '\n')
        else:
            print("Please, save in CSV")
        self.filename = file_name[0]
        self.load_any_file(self.filename)

    def add_new_row(self):
        w = drawer_and_up.popup.InputDialog(self.config_dict["InputDialog"])
        values = w.get_results()
        if values is not None:
            if len(self.data_keeper) == 0:
                self.data_keeper = values
            else:
                self.data_keeper = np.concatenate((self.data_keeper, values))
                self.data_keeper = self.data_keeper[sort_dates(self.data_keeper["Date"])]
            self.update_table()

    def delete_row(self):
        index_list = []
        for model_index in self.table.selectionModel().selectedRows():
            index = QtC.QPersistentModelIndex(model_index)
            index_list.append(index)

        for index in index_list:
            self.data_keeper = np.delete(self.data_keeper, index.row())
            self.table.removeRow(index.row())
        self.update_table()

    def update_table(self):
        self.table.setData(self.data_keeper)
        self.table.cellChanged.connect(self.table_changed)

    def table_changed(self, row, column):
        item = self.table.item(row, column)
        self.data_keeper[row][column] = item.text()
        with open(self.filename, "w", encoding="utf-8") as fw:
            fw.write(",".join(self.config_dict["Table"]["Headings"]) + '\n')
            for elem in self.data_keeper:
                fw.write(','.join(map(str, elem)) + '\n')
        self.update_plot()

    def update_plot(self):
        for heading in self.config_dict["Plot"]["ToUpdate"]:
            x_ = timestamps_from_dates(self.data_keeper[self.config_dict["Plot"]["AxisItems"]["bottomAxis"]])
            y_ = self.data_keeper[heading]
            self.scatter_plots[heading].setData(x=x_, y=y_)

    def draw_plot(self):
        x_ = timestamps_from_dates(["01/01/2021 01:10", "01/01/2021 17:41"])
        for heading in self.config_dict["Plot"]["AxisItems"]["leftAxis"]:
            y_ = [1, 2]
            self.scatter_plots[heading] = pg.ScatterPlotItem(x=x_, y=y_)
            self.plot.p1.addItem(self.scatter_plots[heading])
        for heading in self.config_dict["Plot"]["AxisItems"]["rightAxis"]:
            y_ = [2000, 3000]
            self.scatter_plots[heading] = pg.ScatterPlotItem(x=x_, y=y_)
            self.plot.p2.addItem(self.scatter_plots[heading])


if __name__ == '__main__':

    app = QtW.QApplication(sys.argv)
    ex = MainWindow({"Table": {"Headings": ["a", "b", "c", "d"]}})
    sys.exit(app.exec_())
