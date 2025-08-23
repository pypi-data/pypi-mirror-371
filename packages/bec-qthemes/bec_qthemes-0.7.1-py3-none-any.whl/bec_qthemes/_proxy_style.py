from __future__ import annotations

import platform

from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QProxyStyle, QStyle, QStyleOption

from bec_qthemes._icon.icon_engine import SvgIconEngine
from bec_qthemes._icon.svg import Svg
from bec_qthemes._resources.standard_icons import NEW_STANDARD_ICON_MAP


class qthemesStyle(QProxyStyle):
    """Style proxy to improve theme."""

    def __init__(self):
        """Initialize style proxy."""
        super().__init__()

    def standardIcon(  # noqa: N802
        self, standard_icon: QStyle.StandardPixmap, option: QStyleOption | None, widget
    ) -> QIcon:
        """Implement QProxyStyle.standardIcon."""
        icon_info = NEW_STANDARD_ICON_MAP.get(standard_icon)
        if icon_info is None:
            return super().standardIcon(standard_icon, option, widget)

        os_list = icon_info.get("os")
        if os_list is not None and platform.system() not in os_list:
            return super().standardIcon(standard_icon, option, widget)

        rotate = icon_info.get("rotate", 0)
        svg = Svg(icon_info["id"]).rotate(rotate)
        icon_engine = SvgIconEngine(svg)
        return QIcon(icon_engine)
