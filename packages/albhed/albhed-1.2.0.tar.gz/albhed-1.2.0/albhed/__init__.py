"""Al Bhed translator function and CLI."""

from typing import Annotated

import typer

_ENGLISH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ALBHED = "ypltavkrezgmshubxncdijfqowYPLTAVKREZGMSHUBXNCDIJFQOW"


def albhed(text: str, *, revert: bool = False) -> str:
    """Translate text to/from Al Bhed.

    Args:
        text: Input string.
        revert: When True, converts from Al Bhed back to English. When False, converts English to Al Bhed.

    Returns:
        Translated string.

    """  # noqa: E501
    src = _ALBHED if revert else _ENGLISH
    dst = _ENGLISH if revert else _ALBHED
    return text.translate(str.maketrans(src, dst))


app = typer.Typer(no_args_is_help=True)


@app.command()
def cli(
    string: Annotated[
        list[str],
        typer.Argument(help="Text to translate", show_default=False),
    ],
    revert: Annotated[
        bool,
        typer.Option(
            "--revert",
            "-r",
            help="Revert the translation",
            rich_help_panel="Mode",
        ),
    ] = False,
) -> None:
    """Convert text to Al Bhed (or back with --revert)."""
    text = " ".join(string)
    typer.echo(albhed(text, revert=revert))


if __name__ == "__main__":
    app()
