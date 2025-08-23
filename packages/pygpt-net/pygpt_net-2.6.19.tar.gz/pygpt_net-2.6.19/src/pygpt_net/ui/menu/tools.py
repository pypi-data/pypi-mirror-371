#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.11.24 22:00:00                  #
# ================================================== #

from PySide6.QtGui import QAction, QIcon

from pygpt_net.utils import trans
import pygpt_net.icons_rc

class Tools:
    def __init__(self, window=None):
        """
        Tools menu setup

        :param window: Window instance
        """
        self.window = window

    def setup(self):
        """Setup tools menu"""
        # tab tools
        tab_tools = self.window.controller.tools.get_tab_tools()
        for key in tab_tools:
            self.window.ui.menu[key] = QAction(QIcon(":/icons/" + tab_tools[key][1] + ".svg"),
                                               trans("output.tab." + tab_tools[key][0]), self.window)
            self.window.ui.menu[key].triggered.connect(
                lambda checked=False, type=tab_tools[key][2] : self.window.controller.tools.open_tab(type)
            )
            self.window.ui.menu[key].setCheckable(False)

        # add menu
        self.window.ui.menu['menu.tools'] = self.window.menuBar().addMenu(trans("menu.tools"))

        # add tab tools
        for key in tab_tools:
            self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu[key])

        # add custom tools
        actions = self.window.tools.setup_menu_actions()
        if len(actions) == 0:
            return

        # add separator
        self.window.ui.menu['menu.tools'].addSeparator()

        # build custom tools menu
        for key in actions:
            self.window.ui.menu[key] = actions[key]
            self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu[key])

        # ------------------------------------------------- #

        # OpenAI vector stores
        self.window.ui.menu['menu.tools'].addSeparator()
        self.window.ui.menu['menu.tools.openai.stores'] = QAction(QIcon(":/icons/db.svg"),
                                                                    trans("dialog.assistant.store"), self.window)
        self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu['menu.tools.openai.stores'])
        self.window.ui.menu['menu.tools.openai.stores'].triggered.connect(
            lambda: self.window.controller.assistant.store.toggle_editor()
        )

        # Docker images rebuild:

        # IPython container
        self.window.ui.menu['menu.tools'].addSeparator()
        self.window.ui.menu['menu.tools.ipython.rebuild'] = QAction(QIcon(":/icons/reload.svg"),
                                                                    "Rebuild IPython Docker Image", self.window)
        self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu['menu.tools.ipython.rebuild'])
        self.window.ui.menu['menu.tools.ipython.rebuild'].triggered.connect(
            lambda: self.window.core.plugins.get("cmd_code_interpreter").builder.build_and_restart()
        )
        # Python Legacy container
        self.window.ui.menu['menu.tools.python_legacy.rebuild'] = QAction(QIcon(":/icons/reload.svg"),
                                                                          "Rebuild Python (Legacy) Docker Image", self.window)
        self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu['menu.tools.python_legacy.rebuild'])
        self.window.ui.menu['menu.tools.python_legacy.rebuild'].triggered.connect(
            lambda: self.window.core.plugins.get("cmd_code_interpreter").docker.build_and_restart()
        )
        # System container
        self.window.ui.menu['menu.tools.system.rebuild'] = QAction(QIcon(":/icons/reload.svg"),
                                                                   "Rebuild System Sandbox Docker Image", self.window)
        self.window.ui.menu['menu.tools'].addAction(self.window.ui.menu['menu.tools.system.rebuild'])
        self.window.ui.menu['menu.tools.system.rebuild'].triggered.connect(
            lambda: self.window.core.plugins.get("cmd_system").docker.build_and_restart()
        )
