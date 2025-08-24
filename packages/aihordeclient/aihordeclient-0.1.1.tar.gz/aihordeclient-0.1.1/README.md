# AIHordeclient

AIHordeclient is a lib to connect to https://aihorde.net/api/v2 and
ease plugin development.

## USAGE

* See [stablehorde-gimp3](https://github.com/ikks/gimp-stable-diffusion/)
* See [libreoffice-stable-horde](https://github.com/ikks/libreoffice-stable-diffusion/)

## DEVELOPING

Install [uv](https://docs.astral.sh/uv/)

To make a simple compatibility test for python3.8 run:

```
uv run src/aihordeclient.py
```

We avoid to have external dependencies far from python standard libraries,
which are huge.

```
uv build
```

More [uv instructions](https://docs.astral.sh/uv/guides/projects/#running-commands)


# AUTHORS

Most of the code descends from
[AITurtle Gimp 2.10.X plugin](https://github.com/blueturtleai/gimp-stable-diffusion)
initial work.

# THANKS

* AIHorde
