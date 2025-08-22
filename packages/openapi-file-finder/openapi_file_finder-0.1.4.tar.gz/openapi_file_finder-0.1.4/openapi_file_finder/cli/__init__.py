from __future__ import annotations

import typer

from .check import check_apiblueprint
from .check import check_composer_apiblueprint
from .check import check_composer_swagger_php
from .check import check_dedoc_scramble
from .check import check_swagger_php
from .find import find
from .find import largest

app = typer.Typer()
app.command()(find)
app.command()(largest)
app.command()(check_swagger_php)
app.command()(check_apiblueprint)
app.command()(check_dedoc_scramble)
app.command()(check_composer_swagger_php)
app.command()(check_composer_apiblueprint)
