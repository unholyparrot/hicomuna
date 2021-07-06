import os
import pandas as pd


def parse_filename(_path: str):
    file_name = os.path.basename(_path)
    _, extension = os.path.splitext(_path)
    return file_name, extension


class FileHandler:
    def __init__(self, path, q_dict):
        self._status_saved = True
        self._status_opening = False
        self._path = path
        self._file_name, self._file_extension = parse_filename(self._path)
        self.q_dict = q_dict

    @property
    def status_saved(self):
        return self._status_saved

    def set_status_saved(self, state=False):
        if isinstance(state, bool):
            self._status_saved = state
        else:
            raise ValueError("State bool type expected, got {}".format(type(state)))

    @property
    def status_opening(self):
        return self._status_opening

    def set_status_opening(self, state=True):
        if isinstance(state, bool):
            self._status_opening = state
        else:
            raise ValueError("State bool type expected, got {}".format(type(state)))

    @property
    def path(self):
        return self._path

    @property
    def file_name(self):
        return self._file_name

    @property
    def file_extension(self):
        return self._file_extension

    def load_file(self):
        if self.file_extension in [".xlsx", ".xls", ".ods"]:
            df = pd.read_excel(self.path, dtype=str)
        elif self.file_extension == ".csv":
            df = pd.read_csv(self.path, sep=self.q_dict["Delimiter"], dtype=str)
        else:
            raise ValueError("{0} is not CSV".format(self.file_name))
        return df

    def save_file(self, df: pd.DataFrame):
        if self.file_extension == ".xlsx":
            df.to_excel(self.path, index=False)
        elif self.file_extension == ".xls" or self.file_extension == ".ods":
            path, _ = os.path.splitext(self.path)
            new_path = path + ".xlsx"
            df.to_excel(new_path, index=False)
        elif self.file_extension == ".csv":
            df.to_csv(self.path, sep=self.q_dict["Delimiter"], index=False)
        else:
            raise ValueError("{0} does not have suitable extension".format(self.file_name))
        self.set_status_saved(True)

    def create_file(self):
        empty_df = pd.DataFrame(columns=self.q_dict["Headings"])
        self.save_file(empty_df)
