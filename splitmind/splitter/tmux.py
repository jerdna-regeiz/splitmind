import atexit
import time
from subprocess import check_output

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

def tmux_split(*args, target=None, display=None, cmd=("/bin/cat","-")):
    if target is not None:
        args = list(args) + ["-t", target.id]
    res = check_output('tmux split-window -P -d -F'.split(" ")
                      + ["#{pane_id}:#{pane_tty}"] + list(args)+ list(cmd))
    return TmuxSplit(*read_tmux_output(res), display)

def tmux_kill(paneid):
  check_output(['tmux','kill-pane','-t',paneid])

def tmux_pane_size(pane):
  res = check_output(['tmux','display','-p','-F', '#{pane_width}:#{pane_height}','-t',pane.id])
  return [int(x) for x in read_tmux_output(res)]


def close_panes(panes):
  for pane in set(pane.id for pane in panes):
    tmux_kill(pane)


class Tmux():
    def __init__(self, cmd=("/bin/cat","-")):
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

    def split(self, *args, target=None, display=None, cmd=None):
        if isinstance(target, str):
            target = self.get(target)
        split = tmux_split(*args, target=target, display=display, cmd=cmd or self.cmd)
        self.panes.append(split)
        return split
    def left (self, *args, of=None, display=None):
        return self.split("-hb", *args, target=of, display=display)
    def right(self, *args, of=None, display=None):
        return self.split("-h", *args, target=of, display=display)
    def above(self, *args, of=None, display=None):
        return self.split("-vb", target=of, display=display)
    def below(self, *args, of=None, display=None):
        return self.split("-v", target=of, display=display)
    def splits(self):
        return self.panes
    def close(self):
        close_panes(self.panes)


