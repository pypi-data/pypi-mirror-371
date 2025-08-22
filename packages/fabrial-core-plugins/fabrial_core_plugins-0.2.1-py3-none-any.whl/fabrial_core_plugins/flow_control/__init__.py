from fabrial import PluginCategory

from .items import HoldItem, LoopItem, SimultaneousItem


def categories() -> list[PluginCategory]:
    """Get the categories for this plugin."""
    return [PluginCategory("Flow Control", [HoldItem(), LoopItem(), SimultaneousItem()])]
