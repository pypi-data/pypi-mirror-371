#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.11.26 02:00:00                  #
# ================================================== #

import os

from PySide6.QtGui import QStandardItemModel, Qt, QIcon
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QWidget

from pygpt_net.item.attachment import AttachmentItem
from pygpt_net.ui.widget.element.labels import HelpLabel
from pygpt_net.ui.widget.lists.attachment import AttachmentList
from pygpt_net.utils import trans

import pygpt_net.icons_rc

class Attachments:
    def __init__(self, window=None):
        """
        Attachments UI

        :param window: Window instance
        """
        self.window = window
        self.id = 'attachments'

    def setup(self) -> QVBoxLayout:
        """
        Setup attachments list

        :return: QVBoxLayout
        """
        self.setup_attachments()
        self.setup_buttons()

        empty_widget = QWidget()
        self.window.ui.nodes['input.attachments.options.label'] = HelpLabel(trans("attachments.options.label"))

        # buttons layout
        buttons = QHBoxLayout()
        buttons.addWidget(self.window.ui.nodes['attachments.btn.add'])
        buttons.addWidget(self.window.ui.nodes['attachments.btn.add_url'])
        buttons.addWidget(self.window.ui.nodes['attachments.btn.clear'])
        buttons.addWidget(empty_widget)
        buttons.addWidget(self.window.ui.nodes['input.attachments.options.label'])

        buttons.addWidget(self.setup_auto_index())
        buttons.addWidget(self.setup_send_clear())
        buttons.addWidget(self.setup_capture_clear())
        buttons.addStretch()

        self.window.ui.nodes['tip.input.attachments'] = HelpLabel(trans('tip.input.attachments'), self.window)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.window.ui.nodes['tip.input.attachments'])
        layout.addWidget(self.window.ui.nodes['attachments'])

        layout.addLayout(buttons)

        return layout

    def setup_send_clear(self) -> QWidget:
        """
        Setup send clear checkbox

        :return: QWidget
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.window.ui.nodes['attachments.send_clear'])

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def setup_capture_clear(self) -> QWidget:
        """
        Setup after capture clear checkbox

        :return: QWidget
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.window.ui.nodes['attachments.capture_clear'])

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def setup_auto_index(self) -> QWidget:
        """
        Setup auto index checkbox

        :return: QWidget
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.window.ui.nodes['attachments.auto_index'])

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def setup_buttons(self):
        """
        Setup buttons
        """
        self.window.ui.nodes['attachments.btn.add'] = QPushButton(QIcon(":/icons/add.svg"), trans('attachments.btn.add'))
        self.window.ui.nodes['attachments.btn.add_url'] = QPushButton(QIcon(":/icons/add.svg"), trans('attachments.btn.add_url'))
        self.window.ui.nodes['attachments.btn.clear'] = QPushButton(QIcon(":/icons/close.svg"), trans('attachments.btn.clear'))

        self.window.ui.nodes['attachments.btn.add'].clicked.connect(
            lambda: self.window.controller.attachment.open_add())
        self.window.ui.nodes['attachments.btn.add_url'].clicked.connect(
            lambda: self.window.controller.attachment.open_add_url())
        self.window.ui.nodes['attachments.btn.clear'].clicked.connect(
            lambda: self.window.controller.attachment.clear(remove_local=True))

        self.window.ui.nodes['attachments.send_clear'] = QCheckBox(trans('attachments.send_clear'))
        self.window.ui.nodes['attachments.send_clear'].stateChanged.connect(
            lambda: self.window.controller.attachment.toggle_send_clear(
                self.window.ui.nodes['attachments.send_clear'].isChecked()))

        self.window.ui.nodes['attachments.capture_clear'] = QCheckBox(trans('attachments.capture_clear'))
        self.window.ui.nodes['attachments.capture_clear'].stateChanged.connect(
            lambda: self.window.controller.attachment.toggle_capture_clear(
                self.window.ui.nodes['attachments.capture_clear'].isChecked()))

        self.window.ui.nodes['attachments.auto_index'] = QCheckBox(trans('attachments.auto_index'))
        self.window.ui.nodes['attachments.auto_index'].stateChanged.connect(
            lambda: self.window.controller.attachment.toggle_auto_index(
                self.window.ui.nodes['attachments.auto_index'].isChecked()))

    def setup_attachments(self):
        """
        Setup attachments list
        """
        self.window.ui.nodes[self.id] = AttachmentList(self.window)
        self.window.ui.models[self.id] = self.create_model(self.window)
        self.window.ui.nodes[self.id].setModel(self.window.ui.models[self.id])

    def create_model(self, parent) -> QStandardItemModel:
        """
        Create list model

        :param parent: parent widget
        :return: QStandardItemModel
        """
        model = QStandardItemModel(0, 4, parent)
        model.setHeaderData(0, Qt.Horizontal, trans('attachments.header.name'))
        model.setHeaderData(1, Qt.Horizontal, trans('attachments.header.path'))
        model.setHeaderData(2, Qt.Horizontal, trans('attachments.header.size'))
        model.setHeaderData(3, Qt.Horizontal, trans('attachments.header.ctx'))

        return model

    def update(self, data):
        """
        Update list

        :param data: Data to update
        """
        self.window.ui.models[self.id].removeRows(0, self.window.ui.models[self.id].rowCount())
        i = 0
        for id in data:
            path = data[id].path
            size = ""
            if data[id].type == AttachmentItem.TYPE_FILE:
                if path and os.path.exists(path):
                    size = self.window.core.filesystem.sizeof_fmt(os.path.getsize(path))
            ctx_str = ""
            if data[id].ctx:
                ctx_str = "YES"
            self.window.ui.models[self.id].insertRow(i)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 0), data[id].name)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 1),path)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 2), size)
            self.window.ui.models[self.id].setData(self.window.ui.models[self.id].index(i, 3), ctx_str)
            i += 1
