import re
import os
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


def date_from_timestamp(value):
    return datetime.datetime.fromtimestamp(value).strftime("%d/%m/%Y %H:%M")


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
        self.chosen_points = list()
        self.init_ui()

    def init_ui(self):
        button_open_file = QtW.QPushButton('Open CSV file')
        button_open_file.clicked.connect(self.get_text_file)
        button_new_file = QtW.QPushButton('Create CSV file')
        button_new_file.clicked.connect(self.create_text_file)

        self.file_title = QtW.QLabel("Patient name")
        button_default_view = QtW.QPushButton("Default view")
        button_default_view.clicked.connect(self.set_default_view)

        self.button_add_row = QtW.QPushButton('Add new row')
        self.button_add_row.clicked.connect(self.add_new_row)
        self.button_add_row.setEnabled(False)
        self.button_delete_row = QtW.QPushButton('Delete row')
        self.button_delete_row.clicked.connect(self.delete_row)
        self.button_delete_row.setEnabled(False)

        self.table = pg.TableWidget(editable=True, sortable=False)
        self.table.itemSelectionChanged.connect(self.table_clicked)

        self.plot = drawer_and_up.pyqtdrawer.Plotter(self.config_dict["PlotWidget"])
        self.draw_plot()
        legend_plot = drawer_and_up.pyqtdrawer.LegendPlotter(self.config_dict["Plot"]["PointsStyle"])

        grid = QtW.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(button_open_file, 1, 0)
        grid.addWidget(button_new_file, 1, 1)
        grid.addWidget(self.file_title, 2, 0, 1, 1)
        grid.addWidget(button_default_view, 2, 2)
        grid.addWidget(self.button_add_row, 3, 0)
        grid.addWidget(self.button_delete_row, 3, 1)
        grid.addWidget(self.table, 4, 0, 10, 3)
        grid.addWidget(self.plot.pw, 1, 3, 12, 6)
        grid.addWidget(legend_plot.pw, 13, 3, 1, 6)

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
            self.file_title.setText(os.path.basename(file_name))
            # noinspection PyTypeChecker
            self.data_keeper = np.genfromtxt(file_name, delimiter=";", names=True,
                                             dtype=[('DATE', '<U24'), ('TYPE', '<U11'),
                                                    ('VALUE', '<U11'), ('COMMENT', '<U128')],
                                             encoding="utf-8")
            self.data_keeper = self.data_keeper[sort_dates(self.data_keeper["DATE"])]
            self.data_keeper["VALUE"] = np.array([re.sub(",", ".", x) for x in self.data_keeper["VALUE"]],
                                                 dtype='<U24')
            self.update_table()
            self.update_plot()
            self.button_add_row.setEnabled(True)
            self.button_delete_row.setEnabled(True)
        else:
            msg = QtW.QMessageBox()
            msg.setWindowTitle("CSV expected")
            msg.setText("{0} is not CSV".format(file_name))
            msg.setIcon(QtW.QMessageBox.Critical)
            msg.exec_()

    def get_text_file(self):
        dialog = QtW.QFileDialog()
        dialog.setFileMode(QtW.QFileDialog.AnyFile)
        dialog.setFilter(QtC.QDir.Files)

        if dialog.exec_():
            file_name = dialog.selectedFiles()
            self.filename = file_name[0]
            self.load_any_file(self.filename)

    def create_text_file(self):
        file_name = QtW.QFileDialog.getSaveFileName(self, 'Create File')

        if file_name[0].endswith('.csv'):
            with open(file_name[0], "w", encoding="utf-8") as fw:
                fw.write(";".join(self.config_dict["Table"]["Headings"]) + '\n')
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
                self.data_keeper = self.data_keeper[sort_dates(self.data_keeper["DATE"])]
            self.update_table()

    def delete_row(self):
        reply = QtW.QMessageBox.question(self, 'Message',
                                         "Are you sure to delete selected?", QtW.QMessageBox.Yes |
                                         QtW.QMessageBox.No, QtW.QMessageBox.No)

        if reply == QtW.QMessageBox.Yes:
            index_list = []
            for model_index in self.table.selectionModel().selectedRows():
                index = QtC.QPersistentModelIndex(model_index)
                index_list.append(index)

            for index in index_list:
                self.data_keeper = np.delete(self.data_keeper, index.row())
                self.table.removeRow(index.row())
            self.update_table()

    def set_default_view(self):
        self.plot.p1.setYRange(-1, 90)
        self.plot.p2.setYRange(0, 30000)

    def update_table(self):
        self.table.setData(self.data_keeper)
        self.table.cellChanged.connect(self.table_changed)

    def table_changed(self, row, column):
        item = self.table.item(row, column)
        temp_var = re.sub(",", ".", item.text())
        self.data_keeper[row][column] = temp_var
        with open(self.filename, "w", encoding="utf-8") as fw:
            fw.write(";".join(self.config_dict["Table"]["Headings"]) + '\n')
            for elem in self.data_keeper:
                fw.write(';'.join(map(str, elem)) + '\n')
        self.update_plot()

    def update_plot(self):
        for heading in self.config_dict["Plot"]["ToUpdate"]:
            mask = np.where(self.data_keeper["TYPE"] == heading)
            x_ = timestamps_from_dates(self.data_keeper[self.config_dict["Plot"]["AxisItems"]["bottomAxis"]][mask])
            y_ = self.config_dict["Plot"]["Coefficients"][heading] * self.data_keeper["VALUE"][mask].astype(float)
            self.scatter_plots[heading].setData(x=x_, y=y_,
                                                **self.config_dict["Plot"]["PointsStyle"][heading])

        mask = np.where((self.data_keeper["TYPE"] == "Event") & (self.data_keeper["VALUE"] != ""))
        x_ = timestamps_from_dates(self.data_keeper[self.config_dict["Plot"]["AxisItems"]["bottomAxis"]][mask])
        y_ = np.array([-1 for _ in range(len(x_))])
        self.scatter_plots["Event"].setData(x=x_, y=y_,
                                            **self.config_dict["Plot"]["PointsStyle"]["Event"])

    def draw_plot(self):
        x_ = timestamps_from_dates(["01/01/2021 01:10", "01/01/2021 17:41"])
        for heading in self.config_dict["Plot"]["AxisItems"]["leftAxis"]:
            y_ = [1, 2]
            self.scatter_plots[heading] = pg.PlotDataItem(x=x_, y=y_)
            self.plot.p1.addItem(self.scatter_plots[heading])
        for heading in self.config_dict["Plot"]["AxisItems"]["rightAxis"]:
            y_ = [2000, 3000]
            self.scatter_plots[heading] = pg.PlotDataItem(x=x_, y=y_)
            self.plot.p2.addItem(self.scatter_plots[heading])
        y_ = [-1, -1]
        self.scatter_plots["Event"] = pg.PlotDataItem(x=x_, y=y_,
                                                      **self.config_dict["Plot"]["PointsStyle"]["Event"])
        self.plot.p1.addItem(self.scatter_plots["Event"])
        for heading in self.scatter_plots:
            self.scatter_plots[heading].sigPointsClicked.connect(self.points_clicked)

    def points_clicked(self, scatter, pts):
        _ = scatter
        for point in self.chosen_points:
            point.resetPen()
        for elem in pts:
            self.chosen_points.append(elem)
            elem.setPen("#000000")
            date = date_from_timestamp(elem.pos()[0])
            value = elem.pos()[1]
            top_res = 0
            for s_d in np.where(self.data_keeper["DATE"] == date)[0]:
                try:
                    table_var = self.data_keeper[s_d]["VALUE"].astype(float) * \
                                self.config_dict["Plot"]["Coefficients"][self.data_keeper[s_d]["TYPE"]]
                    if table_var == value:
                        top_res = s_d
                except ValueError:
                    if value == -1:
                        top_res = s_d
            self.table.selectRow(top_res)

    def table_clicked(self):
        for point in self.chosen_points:
            point.resetPen()
        rows_pull = set()
        for elem in self.table.selectedItems():
            rows_pull.add(elem.row())
        for row in rows_pull:
            sub_section = self.data_keeper[row]
            date = sub_section["DATE"]
            heading = sub_section["TYPE"]
            points = self.scatter_plots[heading].scatter.points()
            for point in points:
                if date == date_from_timestamp(point.pos()[0]):
                    self.chosen_points.append(point)
                    point.setPen("#000000")


if __name__ == '__main__':
    print("a b o b a")
