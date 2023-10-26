
class Widgets:
    # Initialize the class with empty dictionaries for each widget name
    def __init__(self):
        self.buttons = {}
        self.canvases = {}
        self.checkbuttons = {}
        self.entries = {}
        self.frames = {}
        self.labels = {}
        self.labelframes = {}
        self.listboxes = {}
        self.menus = {}
        self.menubuttons = {}
        self.messages = {}
        self.optionmenus = {}
        self.panedwindows = {}
        self.radiobuttons = {}
        self.scales = {}
        self.scrollbars = {}
        self.texts = {}
        self.toplevels = {}


class WidgetOrganizer:
    def __init__(self) -> None:
        self._widgets = Widgets()

    @property
    def widget(self):
        return self._widgets