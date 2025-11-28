<!-- omit in toc -->
# Command groups
There are two command groups on this CLI APP:
- [Builder](#builder)
- [Manager](#manager)

The CLI APP has two main flags that can be used with any command, this are:
- `-v, --verbose`: Disables all console clears.
- `-y, --no-confirm`: Disables all confirmations via prompts and sets all confirmations to true.

```{warning}
Do not use `-y, --no-confirm` with create command.
```

## Builder
The builder command group is incharge of writing and editing files on the CWD.

## Manager
The manager command group is incharge of running docker commands.

```{toctree}
:maxdepth: 2
:hidden:

builder
manager
```
