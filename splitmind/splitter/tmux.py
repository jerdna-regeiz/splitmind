import atexit
import time
from subprocess import check_output, CalledProcessError

from splitmind.models import Split

class TmuxSplit(Split):
    def size(self):
        return tmux_pane_size(self)

def read_tmux_output(res):
  try:
    res = res.decode("utf-8")
  except:
    pass
  return res.strip().split(":")

def tmux_split(*args, target=None, display=None, cmd="/bin/cat -", use_stdin=False, **kwargs):
    """
    Parameters
    ----------
    use_stdin : boolean
        If set to true, it will output to the stdin of the given command.
        But it is not as easy as you might think: Most of the time one would get a tty as proc/fd/*
        which is rather unsupportive to write to (hint: it won't go to stdin of the process).
        Therefore the command will be prepended with (cat)| wo have an other with a pipe as output
        to which we may write
    """
    if target is not None:
        args = list(args) + ["-t", target.id]
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


class Tmux():
    def __init__(self, cmd="/bin/cat -"):
        self.cmd = cmd
        self.panes = []
        atexit.register(self.close)

    def get(self, display):
        """Gets a split by the name of the display, or None if name is not found.
        If multiple panes got the same display name, it will return the first"""
        try:
            return [p for p in self.panes if p.display == display][0]
        except IndexError:
            return None

    def show(self, display, on=None):
        """Tells to display on an other split as well"""
        if isinstance(on, str):
            on = self.get(on)
        split = on._replace(display=display)
        self.panes.append(split)
        return split

    def split(self, *args, target=None, display=None, cmd=None, use_stdin=None, **kwargs):
        """
        TODO: documentation
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
        close_panes(self.panes)


