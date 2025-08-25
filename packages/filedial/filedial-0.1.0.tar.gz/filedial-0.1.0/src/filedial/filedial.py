from tkinter import Tk, filedialog
from typing import Literal


class _TkContext:
    __slots__ = ("root",)

    def __init__(self, topmost=True):
        self.root = Tk()
        self.root.withdraw()
        if topmost:
            self.root.attributes("-topmost", True)

    def close(self):
        self.root.destroy()
        print("Closed tk context")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _string_or_empty(value):
    # On Linux, if no path is selected for file or directory,
    # it may return an empty tuple instead of a string.
    # Make sure to return a string in any case.
    return value if isinstance(value, str) else ""


def select_directory(default=None) -> str:
    with _TkContext():
        return _string_or_empty(
            filedialog.askdirectory(mustexist=True, initialdir=default)
        )


def select_file_to_open() -> str:
    with _TkContext():
        return _string_or_empty(filedialog.askopenfilename())


def select_many_files_to_open() -> Literal[""] | tuple[str, ...]:
    with _TkContext():
        return filedialog.askopenfilenames()


def select_file_to_save() -> str:
    with _TkContext():
        return _string_or_empty(filedialog.asksaveasfilename())
