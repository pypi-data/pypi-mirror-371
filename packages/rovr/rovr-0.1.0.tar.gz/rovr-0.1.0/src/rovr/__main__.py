import click
from rich.console import Console

from .maps import VAR_TO_DIR
from .utils import config, normalise, set_nested_value


@click.command(help="A post-modern terminal file explorer")
@click.option(
    "--with",
    "with_features",
    multiple=True,
    type=str,
    help="Enable a feature (e.g., 'plugins.zen_mode').",
)
@click.option(
    "--without",
    "without_features",
    multiple=True,
    type=str,
    help="Disable a feature (e.g., 'interface.tooltips').",
)
@click.option(
    "--config-path",
    "config_path",
    multiple=False,
    type=bool,
    default=False,
    is_flag=True,
    help="Show the path to the config folder.",
)
def main(
    with_features: list[str], without_features: list[str], config_path: bool
) -> None:
    """A post-modern terminal file explorer"""

    if config_path:
        Console().print(
            f"[cyan]Config Path[/cyan]: [pink]{normalise(VAR_TO_DIR['CONFIG'])}[/pink]"
        )
        return

    for feature_path in with_features:
        set_nested_value(config, feature_path, True)

    for feature_path in without_features:
        set_nested_value(config, feature_path, False)

    from .app import Application

    Application(watch_css=True).run()
