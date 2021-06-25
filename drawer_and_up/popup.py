import re
from datetime import datetime, timedelta
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
        self.setCurrentIndex(self.q_dict["Default"])


def check_abstract_velocity(value):
    if value == "":
        var_name = True
    else:
        try:
            temp_var = re.sub(",", ".", value)
            var_name = float(temp_var)
            if (var_name < 0) or (var_name > 90):
                var_name = False
        except ValueError:
            var_name = False
    return var_name


def check_abstract_enoxa(value):
    if value == "":
        var_name = True
    else:
        try:
            temp_var = re.sub(",", ".", value)
            temp_var = float(temp_var) * 10000
            if (temp_var < 0) or (temp_var > 30000):
                var_name = False
            else:
                var_name = int(temp_var)
        except ValueError:
            var_name = False
    return var_name


def check_abstract_infusion(value):
    if value == "":
        var_name = True
    else:
        try:
            var_name = int(value)
        except ValueError:
            var_name = False
    return var_name


class InputDialog(QtW.QDialog):
    def __init__(self, q_dict):
        super(InputDialog, self).__init__()
        self.q_dict = q_dict
        self.setModal(True)

        self.date_edit = DateEdit()

        self.time_edit = QtW.QTimeEdit()
        self.time_edit.setTime(QtC.QTime.currentTime())

        self.type_edit = EventChoice(self.q_dict["Types"])
        self.type_edit.currentIndexChanged.connect(self.type_changed)

        self.types_keeper = {
            "Vtop": {
                "label": QtW.QLabel("Vtop, mkm/m"),
                "edit": QtW.QLineEdit()
            },
            "Vtail": {
                "label": QtW.QLabel("Vtail, mkm/m"),
                "edit": QtW.QLineEdit()
            },
            "Enoxa": {
                "label": QtW.QLabel("Enoxa, ml"),
                "edit": QtW.QLineEdit(),
                "multiplier": EventChoice(self.q_dict["Multiplies"])
            },
            "RecEnoxa": {
                "label": QtW.QLabel("RecEnoxa, ml"),
                "edit": QtW.QLineEdit(),
                "multiplier": EventChoice(self.q_dict["Multiplies"])
            },
            "Infusion": {
                "label": QtW.QLabel("Infusion, ME/h"),
                "edit": QtW.QLineEdit(),
                "multiplier": EventChoice(self.q_dict["Multiplies"])
            },
            "RecInfusion": {
                "label": QtW.QLabel("RecInfusion, ME/h"),
                "edit": QtW.QLineEdit(),
                "multiplier": EventChoice(self.q_dict["Multiplies"])
            },
            "Event": {
                "label": QtW.QLabel("Event"),
                "edit": EventChoice(self.q_dict["Events"])
            }
        }

        self.comment_edit = QtW.QTextEdit()

        self.init_ui()

        self.change_visibility()

    def init_ui(self):
        date_label = QtW.QLabel("Date")

        time_label = QtW.QLabel("Time")

        type_label = QtW.QLabel("Event type")

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

        grid.addWidget(type_label, 2, 0)
        grid.addWidget(self.type_edit, 2, 1)

        for elem in self.types_keeper:
            for i, sub_elem in enumerate(self.types_keeper[elem]):
                grid.addWidget(self.types_keeper[elem][sub_elem], 3, i)

        grid.addWidget(comment_label, 7, 0)
        grid.addWidget(self.comment_edit, 7, 1, 2, 4)

        grid.addWidget(reject_button, 9, 5)
        grid.addWidget(accept_button, 9, 6)

        self.setLayout(grid)

        self.setGeometry(50, 50, 450, 450)
        self.setWindowTitle('New point input')
        self.show()

    def change_visibility(self, chosen="Vtop"):
        for elem in self.types_keeper:
            if elem == chosen:
                for sub_elem in self.types_keeper[elem]:
                    # self.types_keeper[elem][sub_elem].setEnabled(True)
                    self.types_keeper[elem][sub_elem].setVisible(True)
            else:
                for sub_elem in self.types_keeper[elem]:
                    # self.types_keeper[elem][sub_elem].setEnabled(False)
                    self.types_keeper[elem][sub_elem].setVisible(False)

    def type_changed(self, index):
        key = self.q_dict["Types"]["Enum"][index]
        self.change_visibility(key)

    def get_results(self):
        result = self.exec_()
        if result == self.Accepted:
            values = self.check_values()
            return values
        else:
            self.close()

    def check_values(self):
        current_type_value = self.type_edit.currentText()

        sub_res = list()
        sub_errors = list()
        date = self.check_date()
        time = self.check_time()
        comment = self.check_comment()

        if (current_type_value == "Vtop") or (current_type_value == "Vtail"):
            v_value = self.check_velocity()
            if isinstance(v_value, bool):
                if v_value:
                    pass
                else:
                    sub_errors.append(current_type_value)
            else:
                sub_res.append((date + time, current_type_value, v_value, comment))
        elif current_type_value in ["Enoxa", "RecEnoxa", "Infusion", "RecInfusion"]:
            if (current_type_value == "Enoxa") or (current_type_value == "RecEnoxa"):
                value = self.check_enoxa()
            else:
                value = self.check_infusion()
            enoxa_multiplier = self.check_multiplier()
            if isinstance(value, bool):
                if value:
                    pass
                else:
                    sub_errors.append(current_type_value)
            else:
                as_datetime = datetime.strptime(date + time, "%d/%m/%Y %H:%M")
                if (current_type_value == "RecEnoxa") or (current_type_value == "RecInfusion"):
                    dts = [(as_datetime + i * timedelta(hours=int(24 / enoxa_multiplier))).strftime("%d/%m/%Y %H:%M")
                           for i in range(enoxa_multiplier)]
                else:
                    dts = [(as_datetime + i * timedelta(hours=int(24 / enoxa_multiplier))).strftime("%d/%m/%Y %H:%M")
                           for i in range(enoxa_multiplier)]
                for elem in dts:
                    sub_res.append((elem, current_type_value, value, comment))
        elif current_type_value == "Event":
            event_value = self.check_event()
            if isinstance(event_value, bool):
                if event_value:
                    pass
                else:
                    sub_errors.append(current_type_value)
            else:
                sub_res.append((date + time, current_type_value, event_value, comment))

        to_ret = np.array(sub_res,
                          dtype=[('DATE', '<U24'), ('TYPE', '<U11'),
                                 ('VALUE', '<U11'), ('COMMENT', '<U128')])
        if len(sub_errors) > 0:
            errors_text = ""
            for heading in sub_errors:
                errors_text += "* {0} \n".format(heading)
            msg = QtW.QMessageBox()
            msg.setWindowTitle("Error during handling input")
            msg.setText("The following fields were not added due to errors in values: \n" + errors_text)
            msg.setIcon(QtW.QMessageBox.Critical)
            msg.exec_()
        return to_ret

    def check_date(self):
        temp_var = self.date_edit.date().toPyDate()
        var_name = temp_var.strftime("%d/%m/%Y")
        return var_name

    def check_time(self):
        temp_var = self.time_edit.time().toPyTime()
        var_name = temp_var.strftime(" %H:%M")
        return var_name

    def check_velocity(self):
        """
        Получаем на вход значение из виджета top скорости, и передаем на вход в функцию, где чистим от запятых,
        превращаем в float, запускам проверку значения. Скорость должна быть 0 < vel <= 90.

        :return: True, если пустая, float, если прошла проверки, False, если ошибка
        """
        temp_var = self.types_keeper[self.type_edit.currentText()]["edit"].text()
        return check_abstract_velocity(temp_var)

    def check_enoxa(self):
        """
        Получаем из виджета значение в мл, подаем на вход проверочной функции.
        Там значение переводится в МЕ, проверяются границы — 0 <= enoxa <= 30000
        Водят в мл, *10000 -> получаем МЕ
        Ограничения от 0 до 30 000 МЕ

        :return: True, если пустая, int, если прошла проверки, False, если ошибка
        """
        temp_var = self.types_keeper[self.type_edit.currentText()]["edit"].text()
        return check_abstract_enoxa(temp_var)

    def check_infusion(self):
        """
        Получаем значение в МЕ/ч из виджета, запускаем проверку.
        :return: True, если пустая, int, если прошла проверки, False, если ошибка
        """
        temp_var = self.types_keeper[self.type_edit.currentText()]["edit"].text()
        return check_abstract_infusion(temp_var)

    def check_multiplier(self):
        temp_var = self.types_keeper[self.type_edit.currentText()]["multiplier"].currentText()
        return int(temp_var)

    def check_event(self):
        """
        Тут нет проверок, так как тяжело ошибиться...
        :return: True, если пустая, str, если заполнена
        """
        temp_var = self.types_keeper[self.type_edit.currentText()]["edit"].currentText()
        if temp_var == "":
            var_name = True
        else:
            var_name = temp_var
        return var_name

    def check_comment(self):
        """
        Тут нет проверок, так как тяжело ошибиться...
        :return: str
        """
        temp_var = self.comment_edit.toPlainText()
        var_name = temp_var
        return var_name
