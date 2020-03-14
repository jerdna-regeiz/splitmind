# splitmind

`splitmind` helps to setup a layout of splits to organize presented information.

Currently only `gdb` with `pwndbg` as information provider is supported and `tmux` for splitting.
It relies on the ability to ouput section of information to different tty.


![Example Image](docs/img/example.png)
*[Example configuration](docs/examples/example1.gdbinit)*

Note above example uses splitmind and following configuration:

## Install

```shell
git clone https://github.com/jerdna-regeiz/splitmind
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

## Documentation

Currently splitmind can only be used with Tmux and Pwndbg, but it is designed to be able to include
furthe input and output.

Conceptually there are two abstractions working together:
* **Splitter**, which setup the actual splits and provide the neccesary output files (tty, files,
    sockets,...)
* **Thinker** that generate content to be handed to the output, which must be made aware of the
splits (or rather the tty, files, sockets, ...)

A third is used as glue: the **Mind**, which works as an easy interface to connect a splitter and a
thinker. It works as a builder, creating the splits using the splitter and when finished handing the
generated splits to the thinker. The **Mind** is most likely the only interface you need.


### Mind
```python
Mind(self, splitter=<class 'splitmind.splitter.tmux.Tmux'>, thinker=<class 'splitmind.thinker.pwndbg.Pwndbg'>)
```
A builder to create a splitmind.
It splits always on the last created split if no 'of' is given or an other split is selected.
To split the original starting point use select(None) or use an 'of' which is not defined yet.
Further kwargs are always passed as is the the underlying splitter to be able to have splitter
specific additional functionality. Parameters not consumed by the splitter are passed as split
settings to the thinker

#### left
```python
Mind.left(self, *args, of=None, display=None, **kwargs)
```
Creates a split left of the current split.
:param str|split    of       : use this split instead of current
:param str          display  : the section to be displayed here
:param various      args     : further args are passed to the splitting cmd
:param dict         kwargs   : further keyword args are passed to the splitter method
#### right
```python
Mind.right(self, *args, of=None, display=None, **kwargs)
```
Creates a split right of the current split.
:param str|split    of       : use this split instead of current
:param str          display  : the section to be displayed here
:param various      args     : further args are passed to the splitting cmd
:param dict         kwargs   : further keyword args are passed to the splitter method
#### above
```python
Mind.above(self, *args, of=None, display=None, **kwargs)
```
Creates a split above of the current split.
:param str|split    of       : use this split instead of current
:param str          display  : the section to be displayed here
:param various      args     : further args are passed to the splitting cmd
:param dict         kwargs   : further keyword args are passed to the splitter method
#### below
```python
Mind.below(self, *args, of=None, display=None, **kwargs)
```
Creates a split below of the current split.
:param str|split    of       : use this split instead of current
:param str          display  : the section to be displayed here
:param various      args     : further args are passed to the splitting cmd
:param dict         kwargs   : further keyword args are passed to the splitter method
#### show
```python
Mind.show(self, display, on=None, **kwargs)
```
Does not create a split but tells to display given section on some already created split.
:param str|split    on       : which split to be used
:param str          display  : the section to be displayed here
:param dict         kwargs   : further keyword args are passed to the splitter method
#### select
```python
Mind.select(self, display)
```
Selects the given display to continue from there.
Use None for the main split
#### tell_splitter
```python
Mind.tell_splitter(self, **kwargs)
```
Tells the splitter to configure according to the passed keyword arguments.
Which arguments are available and what happens entirely depends on the implementation of the
splitter
#### build
```python
Mind.build(self, **kwargs)
```
Builds the splitmind, by telling the thinker where to put his thoughts
:param dict kwagrs : passed to thinker setup to applie thinker specific value


## TMUX

Tmux does handle the splits using `split-window`. Further `*args` are directly passed to the tmux
call. Tmux supports following additional and optional keywords:
- `cmd : str`: The command to run in the created split
- `use_stdin : boolean`: sets up the split to be able to receive content as stdin to the given cmd
- `size : str`: gives a size to the new split (as lines or as percentage)

Splits can be created without display to start running arbitrary commands aswell.

Example:

```python
python
import splitmind
(splitmind.Mind()
  .below(display="backtrace")
  .right(display="stack", cmd="grep rax", use_stdin=True)
  .right(display="regs")
  .below(cmd='sleep 1; htop')
  .below(of="stack", cmd='sleep 1; watch ls')
  .right(of="main", display="disasm")
  .show("legend", on="disasm")
).build()
end
```

## Pwndbg

Currently Pwndbg is the only thinker / content producer available.
It uses the `contextoutput` function to bind context sections to splits with the matching display
name.

All `split.settings` (keyword arguments not used by the splitter i.e. tmux) are passed as keyword
arguments to `contextoutput`

With the `build` one can specify following options:
* **nobanner** boolean: Banners of all configured outputs will be hidden. Same effect as specifying
banner=False on every split.

## Creating new splitter

You like screen? Please go ahead and create a splitter for it (and please submit a pullrequest).

Writing a new splitter is easy, just take a look at `splitmind.splitter.tmux`.
It just takes `left/right/above/below()`, as well as `show()`,`get()`, `splits()` and `close()` to
be implemented. (ABC class will be comming soon)

## Creating a new thinker

You don't use pwndbg, but have an other case where a splitted layout with automatic tty setup comes
in handy? Yeah! Please look at `splitmind.thnker.pwndbg`, it is even simpler than splitters are, as
they only require a `setup(splits)` method which will then do all the initialization of the content
creation process/programm.

## FAQ

* **How do I create a split containing the input/output of the program debugged by gdb?**
 ```python
(splitmind.Mind()
  .above(cmd='tty; tail -f /dev/null', clearing=False)
).build()
 ```
 Creating a pane which (important) does not clear, shows the used tty and then just reads /dev/null.
 Tailing /dev/null is important, so that the tty is not bothered at all by the running process.

 Then in `gdb` issue `tty /dev/pts/<ttynr>` with the shown tty. This will use the newly created
 pane as input/output of the debugged process. Just ignore the warning.
