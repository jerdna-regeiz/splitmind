import copy
import pwndbg
from pwndbg.commands.context import contextoutput, output, clear_screen

class Pwngdb():
    def banners(self, splits):
      panes = splits
      for tty in set(pane.tty for pane in panes):
        with open(tty,"w") as out:
          clear_screen(out)
      for pane in panes:
        sec = pane.display
        size = pane.size()
        with open(pane.tty,"w") as out:
          b = pwndbg.ui.banner(sec, target=out, width=size[0])
          out.write(b+"\n")
          out.flush()

    def setup(self, splits):
        """Sets up pwngdb to display sections in the given splits using display == section"""
        for split in splits:
            contextoutput(split.display, split.tty, True)
        self.banners(splits)
