# splitmind

`splitmind` helps to setup a layout of splits to organize presented information.

Currently only `gdb` with `pwngdb` as information provider is supported and `tmux` for splitting.
It relies on the ability to ouput section of information to different tty.


## Install

```shell
git clone https://github.com/jerdna/splitmind
echo "source $PWD/splitmind/gdbinit.py" >> ~/.gdbinit
```

It is not showing anything yet. You have to configure your layout yourself.
As as start, put this into your gdbinit

```python
python
import splitmind
(splitmind.Mind()
  .below(display="backtrace")
  .right(display="stack")
  .right(display="regs")
  .right(of="main", display="disasm")
  .show("legend", on="disasm")
).build()
end
```
