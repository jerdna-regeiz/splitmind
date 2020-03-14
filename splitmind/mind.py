from .splitter.tmux import Tmux
from .thinker.pwndbg import Pwndbg


class Mind():
    """A builder to create a splitmind.
    It splits always on the last created split if no 'of' is given or an other split is selected.
    To split the original starting point use select(None) or use an 'of' which is not defined yet.
    Further kwargs are always passed as is the the underlying splitter to be able to have splitter
    specific additional functionality. Parameters not consumed by the splitter are passed as split
    settings to the thinker
    """
    def __init__(self, splitter=Tmux, thinker=Pwndbg):
        if callable(splitter):
            splitter = splitter()
        if callable(thinker):
            thinker = thinker()
        self.splitter = splitter
        self.thinker = thinker
        self.last = None


    def left (self, *args, of=None, display=None, **kwargs):
        """Creates a split left of the current split.
        :param str|split    of       : use this split instead of current
        :param str          display  : the section to be displayed here
        :param various      args     : further args are passed to the splitting cmd
        :param dict         kwargs   : further keyword args are passed to the splitter method"""
        self.last = self.splitter.left(*args, of=of or self.last, display=display, **kwargs)
        return self
    def right(self, *args, of=None, display=None, **kwargs):
        """Creates a split right of the current split.
        :param str|split    of       : use this split instead of current
        :param str          display  : the section to be displayed here
        :param various      args     : further args are passed to the splitting cmd
        :param dict         kwargs   : further keyword args are passed to the splitter method"""
        self.last = self.splitter.right(*args, of=of or self.last, display=display, **kwargs)
        return self
    def above(self, *args, of=None, display=None, **kwargs):
        """Creates a split above of the current split.
        :param str|split    of       : use this split instead of current
        :param str          display  : the section to be displayed here
        :param various      args     : further args are passed to the splitting cmd
        :param dict         kwargs   : further keyword args are passed to the splitter method"""
        self.last = self.splitter.above(*args, of=of or self.last, display=display, **kwargs)
        return self
    def below(self, *args, of=None, display=None, **kwargs):
        """Creates a split below of the current split.
        :param str|split    of       : use this split instead of current
        :param str          display  : the section to be displayed here
        :param various      args     : further args are passed to the splitting cmd
        :param dict         kwargs   : further keyword args are passed to the splitter method"""
        self.last = self.splitter.below(*args, of=of or self.last, display=display, **kwargs)
        return self
    def show(self, display, on=None, **kwargs):
        """Does not create a split but tells to display given section on some already created split.
        :param str|split    on       : which split to be used
        :param str          display  : the section to be displayed here
        :param dict         kwargs   : further keyword args are passed to the splitter method"""
        self.last = self.splitter.show(on=on or self.last, display=display, **kwargs)
        return self
    def select(self, display):
        """Selects the given display to continue from there.
        Use None for the main split"""
        if display is None:
            self.last = None
        else:
            self.last = self.splitter.get(display)
        return self

    def tell_splitter(self, target=None, **kwargs):
        """Tells the splitter to configure according to the passed keyword arguments.
        Which arguments are available and what happens entirely depends on the implementation of the
        splitter"""
        if target is None:
            target = self.last
        self.splitter.do(target=target, **kwargs)
        return self

    def build(self, **kwargs):
        """Builds the splitmind, by telling the thinker where to put his thoughts
        :param dict kwagrs : passed to thinker setup to applie thinker specific value
        """
        self.splitter.finish(**kwargs)
        self.thinker.setup(self.splitter.splits(), **kwargs)
