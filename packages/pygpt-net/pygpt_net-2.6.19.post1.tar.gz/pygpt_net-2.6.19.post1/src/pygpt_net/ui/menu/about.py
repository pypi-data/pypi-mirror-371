#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.01.16 01:00:00                  #
# ================================================== #

from PySide6.QtGui import QAction, QIcon

from pygpt_net.utils import trans
import pygpt_net.icons_rc


class About:
    def __init__(self, window=None):
        """
        Menu setup

        :param window: Window instance
        """
        self.window = window

    def setup(self):
        """Setup about menu"""
        self.window.ui.menu['info.about'] = QAction(QIcon(":/icons/info.svg"), trans("menu.info.about"),
                                                    self.window)
        self.window.ui.menu['info.about'].setMenuRole(QAction.MenuRole.NoRole)
        self.window.ui.menu['info.changelog'] = QAction(QIcon(":/icons/history.svg"), trans("menu.info.changelog"),
                                                        self.window)
        self.window.ui.menu['info.updates'] = QAction(QIcon(":/icons/updater.svg"), trans("menu.info.updates"),
                                                      self.window)
        self.window.ui.menu['info.report'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.report"),
                                                      self.window)
        self.window.ui.menu['info.website'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.website"),
                                                      self.window)
        self.window.ui.menu['info.docs'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.docs"),
                                                   self.window)
        self.window.ui.menu['info.pypi'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.pypi"),
                                                   self.window)
        self.window.ui.menu['info.snap'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.snap"),
                                                   self.window)
        self.window.ui.menu['info.ms_store'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.ms_store"),
                                                   self.window)
        self.window.ui.menu['info.github'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.github"),
                                                     self.window)

        self.window.ui.menu['info.discord'] = QAction(QIcon(":/icons/public_filled.svg"), trans("menu.info.discord"),
                                                     self.window)

        self.window.ui.menu['info.license'] = QAction(QIcon(":/icons/info.svg"), trans("menu.info.license"),
                                                      self.window)

        self.window.ui.menu['donate.coffee'] = QAction(QIcon(":/icons/favorite.svg"), "Buy me a coffee",
                                                       self.window)
        self.window.ui.menu['donate.coffee'].setMenuRole(QAction.MenuRole.NoRole)
        self.window.ui.menu['donate.paypal'] = QAction(QIcon(":/icons/favorite.svg"), "PayPal",
                                                       self.window)
        self.window.ui.menu['donate.github'] = QAction(QIcon(":/icons/favorite.svg"), "GitHub Sponsors", self.window)

        self.window.ui.menu['donate.coffee'].triggered.connect(
            lambda: self.window.controller.dialogs.info.donate('coffee'))
        self.window.ui.menu['donate.paypal'].triggered.connect(
            lambda: self.window.controller.dialogs.info.donate('paypal'))
        self.window.ui.menu['donate.github'].triggered.connect(
            lambda: self.window.controller.dialogs.info.donate('github'))

        self.window.ui.menu['info.about'].triggered.connect(
            lambda: self.window.controller.dialogs.info.toggle('about'))
        self.window.ui.menu['info.changelog'].triggered.connect(
            lambda: self.window.controller.dialogs.info.toggle('changelog'))
        self.window.ui.menu['info.updates'].triggered.connect(
            lambda: self.window.controller.launcher.check_updates())
        self.window.ui.menu['info.report'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_report())
        self.window.ui.menu['info.website'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_website())
        self.window.ui.menu['info.docs'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_docs())
        self.window.ui.menu['info.pypi'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_pypi())
        self.window.ui.menu['info.snap'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_snap())
        self.window.ui.menu['info.ms_store'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_ms_store())
        self.window.ui.menu['info.github'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_github())
        self.window.ui.menu['info.discord'].triggered.connect(
            lambda: self.window.controller.dialogs.info.goto_discord())
        self.window.ui.menu['info.license'].triggered.connect(
            lambda: self.window.controller.dialogs.info.toggle(
                'license',
                width=500,
                height=480,
            ))

        self.window.ui.menu['menu.about'] = self.window.menuBar().addMenu(trans("menu.info"))
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.about'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.changelog'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.updates'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.report'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.docs'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.website'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.github'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.pypi'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.snap'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.ms_store'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.discord'])
        self.window.ui.menu['menu.about'].addAction(self.window.ui.menu['info.license'])

        self.window.ui.menu['menu.donate'] = self.window.ui.menu['menu.about'].addMenu(trans("menu.info.donate"))
        self.window.ui.menu['menu.donate'].addAction(self.window.ui.menu['donate.coffee'])
        self.window.ui.menu['menu.donate'].addAction(self.window.ui.menu['donate.paypal'])
        self.window.ui.menu['menu.donate'].addAction(self.window.ui.menu['donate.github'])
