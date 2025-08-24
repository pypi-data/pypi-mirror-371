from ..event import SkEvent
from .container import SkContainer
from .textbutton import SkTextButton


class SkMenuItem(SkTextButton):
    def __init__(
        self,
        parent: SkContainer,
        text: str = "",
        *,
        style="SkMenuItem",
        align="left",
        **kwargs,
    ):
        super().__init__(parent, text=text, style=style, align=align, **kwargs)

        self.focusable = False

        self.bind("click", self._on_click)

    def _on_click(self, event: SkEvent):
        self.parent.event_trigger("hide", SkEvent(event_type="hide"))
