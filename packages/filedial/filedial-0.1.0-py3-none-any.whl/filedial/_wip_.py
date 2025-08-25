"""
Unused functions based on tk_utils.
"""

from .filedial import _TkContext


def clipboard_set(text: str) -> None:
    with _TkContext() as ctx:
        ctx.root.clipboard_clear()
        ctx.root.clipboard_append(text)
        ctx.root.update()


def clipboard_get() -> str:
    with _TkContext() as ctx:
        return ctx.root.clipboard_get()


def get_screen_size() -> tuple[int, int]:
    """
    Return (width, height) of screen.
    (2024/05/22)
    https://stackoverflow.com/a/66248631
    """
    with _TkContext() as ctx:
        ctx.root.update_idletasks()
        ctx.root.attributes("-fullscreen", True)
        ctx.root.state("iconic")
        # width, height = self.root.maxsize()
        width = ctx.root.winfo_screenwidth()
        height = ctx.root.winfo_screenheight()
        return width, height
