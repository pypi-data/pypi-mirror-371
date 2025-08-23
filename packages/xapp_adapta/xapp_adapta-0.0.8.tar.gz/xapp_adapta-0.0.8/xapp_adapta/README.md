# A python module using `libadapta`

This is the `PyPI` readme. Included commands can be used for effect. Add
any commands to the `pyproject.toml` in the source linked below.

Are you sure you've changed any `xapp_adapta` references to be unique?
Please check `pyproject.toml` and also rename the module directory from
`xapp_adapta`. Also check that `_` is not `-`. Quite a bit auto fills the
about dialog, and the `[tool.domain]` section is for a domain base
for the unique naming of resources.

Included commands (add more):

- `adapta_test` the basic original python demo of `libadapta`. Added a try catch
  to make `àdwaita` be used instead if `àdapta` is not present. Plus more.
- `adapta_main` extends the test `MainWindow` class for effect.
- `adapta_make_local` to install `.desktop`, `.svg` and locale files.
  The `~/.local/share/applications/*.desktop` files might need `Èxec` edits.
  This is not automatic, and only has to be done once. There is no uninstall
  as yet.
- ...

Thanks

[Template Source](https://github.com/jackokring/mint-python-adapta)
