import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import numpy as np


class DateEdit(QtW.QDateEdit):
    def __init__(self, parent=None):
        # noinspection PyArgumentList
        super(DateEdit, self).__init__(parent, calendarPopup=True)
        self.setDate(QtC.QDate.currentDate())
        self._today_button = QtW.QPushButton(self.tr("Today"))
        self._today_button.clicked.connect(self._update_today)
        self.calendarWidget().layout().addWidget(self._today_button)

    @QtC.pyqtSlot()
    def _update_today(self):
        self._today_button.clearFocus()
        today = QtC.QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)


class EventChoice(QtW.QComboBox):
    def __init__(self, q_dict, parent=None):
        super(EventChoice, self).__init__(parent)
        self.q_dict = q_dict
        self.addItems(self.q_dict["Enum"])


class InputDialog(QtW.QDialog):
    def __init__(self, q_dict):
        super(InputDialog, self).__init__()
        self.q_dict = q_dict
        self.setModal(True)

        self.date_edit = DateEdit()

        self.time_edit = QtW.QTimeEdit()
        self.time_edit.setTime(QtC.QTime.currentTime())

        self.v_top_edit = QtW.QLineEdit()
        self.v_tail_edit = QtW.QLineEdit()

        self.enoxa_edit = QtW.QLineEdit()
        self.rec_enoxa_edit = QtW.QLineEdit()

        self.infusion_edit = QtW.QLineEdit()
        self.rec_infusion_edit = QtW.QLineEdit()

        self.event_edit = EventChoice(self.q_dict["Events"])
        self.comment_edit = QtW.QTextEdit()

        self.init_ui()
        # set initials values to widgets

    def init_ui(self):
        date_label = QtW.QLabel("Date")

        time_label = QtW.QLabel("Time")

        v_top_label = QtW.QLabel("V top, mkm/s")
        v_tail_label = QtW.QLabel("V tail, mkm/s")

        enoxa_label = QtW.QLabel("Enoxa, ME")
        rec_enoxa_label = QtW.QLabel("Recommended Enoxa, ME")

        infusion_label = QtW.QLabel("Infusion, ME/h")
        rec_infusion_label = QtW.QLabel("Recommended Infusion, ME/h")

        event_label = QtW.QLabel("Event")
        comment_label = QtW.QLabel("Comment / Event description")

        reject_button = QtW.QPushButton("Cancel")
        reject_button.clicked.connect(self.reject)
        accept_button = QtW.QPushButton("OK")
        accept_button.clicked.connect(self.accept)

        grid = QtW.QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(date_label, 1, 0)
        grid.addWidget(self.date_edit, 1, 1)
        grid.addWidget(time_label, 1, 2)
        grid.addWidget(self.time_edit, 1, 3)

        grid.addWidget(v_top_label, 2, 0)
        grid.addWidget(self.v_top_edit, 2, 1)
        grid.addWidget(v_tail_label, 2, 2)
        grid.addWidget(self.v_tail_edit, 2, 3)

        grid.addWidget(enoxa_label, 3, 0)
        grid.addWidget(self.enoxa_edit, 3, 1)
        grid.addWidget(rec_enoxa_label, 3, 2)
        grid.addWidget(self.rec_enoxa_edit, 3, 3)

        grid.addWidget(infusion_label, 4, 0)
        grid.addWidget(self.infusion_edit, 4, 1)
        grid.addWidget(rec_infusion_label, 4, 2)
        grid.addWidget(self.rec_infusion_edit, 4, 3)

        grid.addWidget(event_label, 5, 0)
        grid.addWidget(self.event_edit, 5, 1, 1, 4)
        grid.addWidget(comment_label, 6, 0)
        grid.addWidget(self.comment_edit, 6, 1, 2, 4)

        grid.addWidget(reject_button, 8, 5)
        grid.addWidget(accept_button, 8, 6)

        self.setLayout(grid)

        self.setGeometry(50, 50, 450, 450)
        self.setWindowTitle('New point input')
        self.show()

    def get_results(self):
        result = self.exec_()
        if result == self.Accepted:
            values = self.check_values()
            return values
            # get all values
            # val = self.some_widget.some_function()
            # val2 = self.some_widget2.some_another_function()
            # return val, val2, ...
        else:
            self.close()

    def check_values(self):
        date = self.check_date()
        time = self.check_time()
        v_top = self.check_top_velocity()
        v_tail = self.check_tail_velocity()
        enoxa = self.check_enoxa()
        rec_enoxa = self.check_rec_enoxa()
        infusion = self.check_infusion()
        rec_infusion = self.check_rec_infusion()
        event = self.check_event()
        comment = self.check_comment()

        to_ret = np.array([(date + time, v_top, v_tail, enoxa, rec_enoxa, infusion, rec_infusion, event, comment)],
                          dtype=[('Date', '<U32'), ('Vtop', '<f8'), ('Vtail', '<f8'), ('Enoxa', '<i4'),
                                 ('RecEnoxa', '<i4'), ('Infusion', '<i4'), ('RecInfusion', '<i4'),
                                 ('Event', '<U32'), ('Comment', '<U32')])

        return to_ret

    def check_date(self):
        temp_var = self.date_edit.date().toPyDate()
        var_name = temp_var.strftime("%d/%m/%Y")
        return var_name

    def check_time(self):
        temp_var = self.time_edit.time().toPyTime()
        var_name = temp_var.strftime(" %H:%M")
        return var_name

    def check_top_velocity(self):
        """
        Vel 0 .. 90
        :return:
        """
        temp_var = self.v_top_edit.text()
        var_name = float(temp_var)
        return float(var_name)

    def check_tail_velocity(self):
        """
        Vel 0 .. 90
        :return:
        """
        temp_var = self.v_tail_edit.text()
        var_name = float(temp_var)
        return var_name

    def check_enoxa(self):
        """
        Водят в мл, *10000 -> получаем МЕ
        Ограничения от 0 до 30 000 МЕ
        :return:
        """
        temp_var = self.enoxa_edit.text()
        var_name = int(temp_var)
        return var_name

    def check_rec_enoxa(self):
        """
        Водят в мл, *10000 -> получаем МЕ
        Ограничения  от 0 до 30 000 МЕ
        :return:
        """
        temp_var = self.rec_enoxa_edit.text()
        var_name = int(temp_var)
        return var_name

    def check_infusion(self):
        """
        Инфузия в МЕ \ ч, при попадании на график умножается на 12. В таблице в том виде, как ввели,
        на графике *12
        :return:
        """
        temp_var = self.infusion_edit.text()
        var_name = int(temp_var)
        return var_name

    def check_rec_infusion(self):
        """
        Инфузия в МЕ \ ч, при попадании на график умножается на 12. В таблице в том виде, как ввели,
        на графике *12
        :return:
        """
        temp_var = self.rec_infusion_edit.text()
        var_name = int(temp_var)
        return var_name

    def check_event(self):
        temp_var = self.event_edit.currentText()
        var_name = temp_var
        return var_name

    def check_comment(self):
        temp_var = self.comment_edit.toPlainText()
        var_name = temp_var
        return var_name
