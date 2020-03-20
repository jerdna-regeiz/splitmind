import atexit
import os
import time
from subprocess import check_output, CalledProcessError

from splitmind.models import Split

class TmuxSplit(Split):
    def size(self):
        return tmux_pane_size(self)

def read_tmux_output(res, delimiter=':'):
  try:
    res = res.decode("utf-8")
  except:
    pass
  return res.strip().split(delimiter)

def tmux_split(*args, target=None, display=None, cmd="/bin/cat -", use_stdin=False, size=None,
               **kwargs):
    """
    Parameters
    ----------
    use_stdin : boolean
        If set to true, it will output to the stdin of the given command.
        But it is not as easy as you might think: Most of the time one would get a tty as proc/fd/*
        which is rather unsupportive to write to (hint: it won't go to stdin of the process).
        Therefore the command will be prepended with (cat)| wo have an other with a pipe as output
        to which we may write
    size : the size of the new split
        pecify the size of the new pane in lines (for vertical split) or in cells
        (for horizontal split), or as a percentage if ending with %
    """
    args = list(args)
    if target is not None:
        args += ["-t", target.id]
    if size is not None:
        args += ["-p", size[:-1]] if size.endswith("%") else ["-l", size]
    fd = "#{pane_tty}" if not use_stdin else "/proc/#{pane_pid}/fd/0"
    if use_stdin:
        cmd = "(cat)|"+cmd
    res = check_output('tmux split-window -P -d -F'.split(" ")
                       + ["#{pane_id}:"+fd] + list(args)+ [cmd])
    return TmuxSplit(*read_tmux_output(res), display, kwargs)

def tmux_kill(paneid):
    try:
        check_output(['tmux','kill-pane','-t',paneid])
    except CalledProcessError as err:
        print(err)

def tmux_pane_size(pane):
  res = check_output(['tmux','display','-p','-F', '#{pane_width}:#{pane_height}','-t',pane.id])
  return [int(x) for x in read_tmux_output(res)]


def close_panes(panes):
  for pane in set(pane.id for pane in panes):
    tmux_kill(pane)

def tmux_pane_border_status(value):
    check_output(['tmux','set' ,'pane-border-status', value])

def tmux_pane_title(pane, title):
    if pane is None:
        check_output(['tmux','select-pane','-T',title])
    else:
        check_output(['tmux','select-pane','-T',title,'-t',pane.id])

def tmux_window_options():
    return read_tmux_output(check_output(['tmux', 'show-options', '-w']), delimiter="\n")

class DummyTmux():
    def __new__(cls, *_args, **kwargs):
        print("Error: Splitmind-Tmux can only be used when running under tmux")
        return super(DummyTmux, cls).__new__(cls)

    def __init__(self, *_args, **kwargs):
        print("Error: Splitmind-Tmux can only be used when running under tmux")

    def __getattr__(self, name):
        return lambda *_, **_kw: None if name in [k for k,x in Tmux.__dict__.items() if callable(x)] else None

    def splits(self):
        return []

class Tmux():
    def __new__(cls, *_args, **_kwargs):
        if not "TMUX_PANE" in os.environ:
            return DummyTmux.__new__(DummyTmux)
        return super(Tmux, cls).__new__(cls)

    def __init__(self, cmd="/bin/cat -"):
        self.cmd = cmd
        self.panes = [TmuxSplit(os.environ["TMUX_PANE"], None, "main", {}) ]
        self._saved_tmux_options = tmux_window_options()
        if not [o for o in self._saved_tmux_options if o.startswith("pane-border-status")]:
            self._saved_tmux_options.append("pane-border-status off")
        atexit.register(self.close)

    def get(self, display):
        """Gets a split by the name of the display, or None if name is not found.
        If multiple panes got the same display name, it will return the first"""
        if isinstance(display, Split):
            return display
        try:
            return [p for p in self.panes if p.display == display][0]
        except IndexError:
            return None

    def show(self, display, on=None, **kwargs):
        """Tells to display on an other split as well"""
        if isinstance(on, str):
            on = self.get(on)
        split = on._replace(display=display, settings=on.settings.copy())
        split.settings.update(kwargs)
        self.panes.append(split)
        if display:
            tmux_pane_title(split,
                            ", ".join([sp.display for sp in self.panes if sp.tty == split.tty]))
        return split

    def split(self, *args, target=None, display=None, cmd=None, use_stdin=None, **kwargs):
        """
        Splits the tmux pane and associates the cmd & display with the new pane
        Parameters
        ----------
        use_stdin : boolean
            If set to true, it will output to the stdin of the given command.
            But it is not as easy as you might think: Most of the time one would get a tty as proc/fd/*
            which is rather unsupportive to write to (hint: it won't go to stdin of the process).
            Therefore the command will be prepended with (cat)| wo have an other with a pipe as output
            to which we may write
        """
        if isinstance(target, str):
            target = self.get(target)
        split = tmux_split(*args, target=target, display=display, cmd=cmd or self.cmd,
                           use_stdin=use_stdin, **kwargs)
        if display:
            tmux_pane_title(split, display)
        self.panes.append(split)
        return split

    def left (self, *args, of=None, display=None, **kwargs):
        return self.split("-hb", *args, target=of, display=display, **kwargs)
    def right(self, *args, of=None, display=None, **kwargs):
        return self.split("-h",  *args, target=of, display=display, **kwargs)
    def above(self, *args, of=None, display=None, **kwargs):
        return self.split("-vb", *args, target=of, display=display, **kwargs)
    def below(self, *args, of=None, display=None, **kwargs):
        return self.split("-v",  *args, target=of, display=display, **kwargs)
    def splits(self):
        return self.panes
    def close(self):
        close_panes(self.panes[1:])
        #restore options
        for option in [o for o in self._saved_tmux_options if o]:
            check_output(["tmux", "set"] + option.split(" "))

    def finish(self, **kwargs):
        """Finishes the splitting."""
        # tmux <2.6 does select the target pane. Later versions stay with the current.
        # To have consistent behaviour, we select the main pane after splitting
        check_output(['tmux', 'select-pane', "-t", os.environ["TMUX_PANE"]])


    def do(self, show_titles=None, set_title=None, target=None):
        """Tells tmux to do something. This is called by tell_splitter in Mind
        All actions are only done if according parameter is not None
        Parameters
        ----------
        show_titles : boolean|str
            If set to true or top, it will display pane titles in the top border
            If set to bottom, it will display pane titles in the bottom border
            If set to false, it will hide the titles in the border
        set_title : string
            Sets the title of a given target or if target is None of the current split
        target : string|split
            The target of actions. Either a string with display name or a ready split or None for
            the current split
        """
        if show_titles is not None:
            tmux_pane_border_status({"bottom":"bottom", False:"off"}.get(show_titles, "top"))
        if set_title is not None:
            tmux_pane_title(self.get(target), set_title)


