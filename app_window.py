import re
import time
import datetime
import numpy as np
import pandas as pd
import pyqtgraph as pg
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import drawer_and_up


def timestamps_from_dates(array):
    to_ret = []
    for dt in array:
        if "/" in dt:
            pattern = "%d/%m/%Y %H:%M"
        else:
            pattern = "%Y-%m-%d %H:%M:%S"
        to_ret.append(time.mktime(datetime.datetime.strptime(dt, pattern).timetuple()))
    return to_ret


def date_from_timestamp(value):
    pattern = "%d/%m/%Y %H:%M"
    res = datetime.datetime.fromtimestamp(value).strftime(pattern)
    return res


def reformat_dates(value):
    ts = timestamps_from_dates([value])
    date = date_from_timestamp(ts[0])
    return date


class MainWindow(QtW.QWidget):

    def __init__(self, config_dict):
        super().__init__()
        self.config_dict = config_dict
        self.table = None
        self.plot = None
        self.file_title = None
        self.df = None
        self.file_keeper = drawer_and_up.filehandler.FileHandler("no_path/nowhere.np", config_dict)
        self.scatter_plots = dict()
        self.line_plots = dict()
        self.button_add_row = None
        self.button_delete_row = None
        self.button_save_changes = None
        self.chosen_points = list()
        self.init_ui()

    def init_ui(self):
        button_open_file = QtW.QPushButton('Open Table')
        button_open_file.clicked.connect(self.get_text_file)
        button_new_file = QtW.QPushButton('Create Table')
        button_new_file.clicked.connect(self.create_text_file)
        self.button_save_changes = QtW.QPushButton('Save changes')
        self.button_save_changes.clicked.connect(self.save_changes)
        self.button_save_changes.setEnabled(False)
        self.button_save_changes.setStyleSheet("background-color: lightgray")

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
        self.table.cellChanged.connect(self.table_changed)
        self.table.itemSelectionChanged.connect(self.table_clicked)

        self.plot = drawer_and_up.pyqtdrawer.Plotter(self.config_dict["PlotWidget"])
        self.draw_plot()
        legend_plot = drawer_and_up.pyqtdrawer.LegendPlotter(self.config_dict["Plot"]["PointsStyle"])

        grid = QtW.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(button_open_file, 1, 0)
        grid.addWidget(button_new_file, 1, 1)
        grid.addWidget(self.button_save_changes, 1, 2)
        grid.addWidget(self.file_title, 2, 0, 1, 1)
        grid.addWidget(button_default_view, 2, 2)
        grid.addWidget(self.button_add_row, 3, 0)
        grid.addWidget(self.button_delete_row, 3, 1)
        grid.addWidget(self.table, 4, 0, 10, 3)
        grid.addWidget(self.plot.pw, 1, 3, 12, 6)
        grid.addWidget(legend_plot.pw, 13, 3, 1, 6)

        self.setLayout(grid)

        self.setGeometry(50, 50, 1250, 650)
        self.setWindowTitle('Hicomuna {}'.format(self.config_dict["Version"]))
        self.show()

    def closeEvent(self, event):
        """
        Перезаписанный метод, при нажатии кнопки закрытия предлагает либо сохранить изменённый файл (если был изменён),
        либо просто спрашивает, закрыть или нет.
        :param event: event == close file
        :return:
        """
        if self.file_keeper.status_saved:
            reply = QtW.QMessageBox.question(self, 'Message',
                                             "Quit?", QtW.QMessageBox.Yes |
                                             QtW.QMessageBox.No, QtW.QMessageBox.No)
            if reply == QtW.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            self.ask_if_save_file()
            reply = QtW.QMessageBox.question(self, 'Message',
                                             "Quit?", QtW.QMessageBox.Yes |
                                             QtW.QMessageBox.No, QtW.QMessageBox.No)
            if reply == QtW.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def load_any_file(self):
        try:
            self.file_title.setText(self.file_keeper.file_name)
            # загружаем содержимое файла
            self.df = self.file_keeper.load_file()
            # нужно убедиться, что DataFrame не пуст (иначе хер нам, а не сортировка)
            if self.df.size > 0:
                # сортируем значения по дате (на всякий случай)
                self.df.sort_values(by="DATE", key=timestamps_from_dates, inplace=True)
                # исправляем запятые
                self.df["VALUE"] = self.df["VALUE"].apply(lambda x: re.sub(",", ".", x))
                self.df["DATE"] = self.df["DATE"].apply(lambda x: reformat_dates(x))
            # временно выключаю проверку события изменения таблицы для безошибочной записи в таблицу новых данных
            self.file_keeper.set_status_opening(True)
            self.update_table()
            # а затем обратно включаю её
            self.file_keeper.set_status_opening(False)
            # обновляем график
            self.update_plot()
            self.set_default_view()
            self.button_add_row.setEnabled(True)
            self.button_delete_row.setEnabled(True)
            self.button_save_changes.setEnabled(False)
            self.button_save_changes.setStyleSheet("background-color: lightgray")
        except ValueError as e:
            msg = QtW.QMessageBox()
            msg.setWindowTitle("Loading file error")
            msg.setText(str(e))
            msg.setIcon(QtW.QMessageBox.Critical)
            msg.exec_()

    def get_text_file(self):
        if not self.file_keeper.status_saved:
            self.ask_if_save_file()
        dialog = QtW.QFileDialog()
        dialog.setFileMode(QtW.QFileDialog.AnyFile)
        dialog.setFilter(QtC.QDir.Files)

        if dialog.exec_():
            file_name = dialog.selectedFiles()
            self.file_keeper = drawer_and_up.filehandler.FileHandler(file_name[0],
                                                                     self.config_dict["Table"])
            self.load_any_file()

    def ask_if_save_file(self):
        save_reply = QtW.QMessageBox.question(self, 'Message',
                                              "Save changes?", QtW.QMessageBox.Yes |
                                              QtW.QMessageBox.No, QtW.QMessageBox.No)

        if save_reply == QtW.QMessageBox.Yes:
            self.file_keeper.save_file(self.df)
            self.button_save_changes.setEnabled(False)
            self.button_save_changes.setStyleSheet("background-color: lightgray")

    def create_text_file(self):
        if not self.file_keeper.status_saved:
            self.ask_if_save_file()
        file_name = QtW.QFileDialog.getSaveFileName(self, 'Create File')
        try:
            self.file_keeper = drawer_and_up.filehandler.FileHandler(file_name[0],
                                                                     self.config_dict["Table"])
            self.file_keeper.create_file()
            self.load_any_file()
        except ValueError as e:
            msg = QtW.QMessageBox()
            msg.setWindowTitle("Creating file error")
            msg.setText(str(e))
            msg.setIcon(QtW.QMessageBox.Critical)
            msg.exec_()

    def add_new_row(self):
        rows_pull = set()
        date = None
        for elem in self.table.selectedItems():
            rows_pull.add(elem.row())
        for row in rows_pull:
            sub_section = self.df.loc[row]
            date = sub_section["DATE"]
        w = drawer_and_up.popup.InputDialog(self.config_dict["InputDialog"], date)
        values = w.get_results()
        if values is not None:
            self.df = pd.concat([self.df, values], ignore_index=True)
            self.add_or_delete_action()

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
                self.df = self.df.drop(self.df.index[index.row()])
                self.table.removeRow(index.row())
            self.add_or_delete_action()

    def save_changes(self):
        self.file_keeper.save_file(self.df)
        self.button_save_changes.setEnabled(False)
        self.button_save_changes.setStyleSheet("background-color: lightgray")

    def set_default_view(self):
        """
        Приводит график к одному, стандартному виду. Меняет масштаб осей: 0 .. 90 для скорости, 0 .. 30000 для AC,
        минимальная и максимальная даты для нижней оси
        :return:
        """
        self.plot.p1.setYRange(-1, 90)
        self.plot.p2.setYRange(0, 30000)
        if (self.df is None) or (len(self.df["DATE"].values) == 0):
            x_ = timestamps_from_dates(["01/01/2021 01:10", "01/01/2021 17:41"])
        else:
            x_ = timestamps_from_dates([self.df["DATE"].values[0], self.df["DATE"].values[-1]])
        self.plot.p1.setXRange(x_[0], x_[1])

    def update_table(self):
        self.table.setData(self.df.to_dict('index'))

    def add_or_delete_action(self):
        self.df.sort_values(by="DATE", key=timestamps_from_dates, inplace=True)
        self.file_keeper.set_status_opening(True)
        self.update_table()
        # а затем обратно включаю её
        self.file_keeper.set_status_opening(False)
        self.file_keeper.set_status_saved(False)
        self.update_plot()
        self.set_default_view()
        self.file_keeper.set_status_saved(False)
        self.button_save_changes.setEnabled(True)
        self.button_save_changes.setStyleSheet("background-color: yellow")

    # TODO: переписать, добавить проверку исключений
    def table_changed(self, row, column):
        # если в таблицу записываются данные, а не вносятся изменения, то просто ничего не делаем
        if self.file_keeper.status_opening:
            pass
        # а вот если вносятся изменения, то вносим их
        else:
            item = self.table.item(row, column)
            temp_var = re.sub(",", ".", item.text())
            self.df.iat[row, column] = temp_var
            self.file_keeper.set_status_saved(False)
            self.update_plot()
            self.set_default_view()
            self.file_keeper.set_status_saved(False)
            self.button_save_changes.setEnabled(True)
            self.button_save_changes.setStyleSheet("background-color: yellow")

    def update_plot(self):
        """
        Обновление данных на графике,
        обновляются все объявленные серии, прочим передаётся пустой массив.
        :return:
        """
        for heading in self.config_dict["Plot"]["ToUpdate"]:
            mask = self.df[self.df["TYPE"] == heading].index
            if len(mask) > 0:
                x_ = timestamps_from_dates(self.df[self.config_dict["Plot"]["AxisItems"]["bottomAxis"]][mask].values)
                y_ = self.config_dict["Plot"]["Coefficients"][heading] * self.df["VALUE"][mask].values.astype(float)
            else:
                x_, y_ = [], []
            self.scatter_plots[heading].setData(x=x_, y=y_,
                                                **self.config_dict["Plot"]["PointsStyle"][heading])

        mask = self.df[(self.df["TYPE"] == "Event") & (self.df["VALUE"] != "")].index
        if len(mask) > 0:
            x_ = timestamps_from_dates(self.df[self.config_dict["Plot"]["AxisItems"]["bottomAxis"]][mask].values)
            y_ = np.array([-1 for _ in range(len(x_))])
        else:
            x_, y_ = [], []
        self.scatter_plots["Event"].setData(x=x_, y=y_,
                                            **self.config_dict["Plot"]["PointsStyle"]["Event"])

    def draw_plot(self):
        """
        Вызывается один раз при запуске приложения для первичной отрисовки графика
        :return:
        """
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
            for s_d in np.where(self.df["DATE"] == date)[0]:
                try:
                    table_var = float(self.df.loc[s_d]["VALUE"]
                                      ) * self.config_dict["Plot"]["Coefficients"][self.df.loc[s_d]["TYPE"]]
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
            sub_section = self.df.loc[row]
            date = sub_section["DATE"]
            heading = sub_section["TYPE"]
            points = self.scatter_plots[heading].scatter.points()
            for point in points:
                if date == date_from_timestamp(point.pos()[0]):
                    self.chosen_points.append(point)
                    point.setPen("#000000")


if __name__ == '__main__':
    print("a b o b a")
