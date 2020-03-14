import copy
try:
    import pwndbg
    from pwndbg.commands.context import contextoutput, output, clear_screen
except ImportError as err:
    # Most likely not run from gdb but something else..
    pass

class Pwndbg():
    def banners(self, splits):
      panes = splits
      for tty in set(pane.tty for pane in panes if pane.settings.get("clearing", True)):
        with open(tty,"w") as out:
          clear_screen(out)
      for pane in [p for p in panes if p.display is not None]:
        sec = pane.display
        size = pane.size()
        with open(pane.tty,"w") as out:
          b = pwndbg.ui.banner(sec, target=out, width=size[0])
          out.write(b+"\n")
          out.flush()

    def setup(self, splits, nobanner=None):
        """Sets up pwndbg to display sections in the given splits using display == section"""
        if nobanner is not None:
            for split in splits:
                if "banner" not in split.settings:
                    split.settings["banner"] = False
        for split in [s for s in splits if s.display is not None and s.tty is not None]:
            contextoutput(split.display, split.tty, True, **split.settings)
        self.banners(s for s in splits if s.tty is not None)
