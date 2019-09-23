from .splitter.tmux import Tmux
from .thinker.pwngdb import Pwngdb


class Mind():
    """A builder to create a splitmind.
    It splits always on the last created split if no 'of' is given or an other split is selected.
    To split the original starting point use select(None) or use an 'of' which is not defined yet"""
    def __init__(self, splitter=Tmux, thinker=Pwngdb):
        if callable(splitter):
            splitter = splitter()
        if callable(thinker):
            thinker = thinker()
        self.splitter = splitter
        self.thinker = thinker
        self.last = None


    def left (self, *args, of=None, display=None):
        self.last = self.splitter.left(*args, of=of or self.last, display=display)
        return self
    def right(self, *args, of=None, display=None):
        self.last = self.splitter.right(*args, of=of or self.last, display=display)
        return self
    def above(self, *args, of=None, display=None):
        self.last = self.splitter.above(*args, of=of or self.last, display=display)
        return self
    def below(self, *args, of=None, display=None):
        self.last = self.splitter.below(*args, of=of or self.last, display=display)
        return self
    def show(self, display, on=None):
        self.last = self.splitter.show(on=on or self.last, display=display)
        return self
    def select(self, display):
        """Selects the given display to continue from there.
        Use None for the main split"""
        if display is None:
            self.last = None
        else:
            self.last = self.splitter.get(display)
        return self

    def build(self):
        """Builds the splitmind, by telling the thinker where to put his thoughts"""
        self.thinker.setup(self.splitter.splits())
