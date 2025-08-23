#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.12.12 01:00:00                  #
# ================================================== #

from pygpt_net.core.events import RenderEvent


class Nodes:
    def __init__(self, window=None):
        """
        Theme nodes controller

        :param window: Window instance
        """
        self.window = window

    def apply(self, key: str, type: str):
        """
        Apply stylesheet to node

        :param key: UI node key
        :param type: stylesheet type
        """
        if key not in self.window.ui.nodes:
            return

        if type == 'font.toolbox':
            self.window.ui.nodes[key].setStyleSheet(self.window.controller.theme.style('font.toolbox'))
        elif type == 'font.chat.output':
            for pid in self.window.ui.nodes[key]:
                try:
                    self.window.ui.nodes[key][pid].setStyleSheet(self.window.controller.theme.style('font.chat.output'))
                except Exception as e:
                    pass
        elif type == 'font.chat.input':
            self.window.ui.nodes[key].setStyleSheet(self.window.controller.theme.style('font.chat.input'))
        elif type == 'font.ctx.list':
            self.window.ui.nodes[key].setStyleSheet(self.window.controller.theme.style('font.ctx.list'))

    def apply_all(self):
        """Apply stylesheets to nodes"""
        nodes = {
            'font.chat.input': [
                'input',
            ],
            'font.chat.output': [
                'output',
                'output_plain',
            ],
            'font.ctx.list': [
                'ctx.list',
            ],
            'font.toolbox': [
                'assistants',
                'assistants.new',
                'assistants.import',
                'assistants.label',
                'cmd.enabled',
                'dalle.options',
                'img_variants.label',
                'preset.clear',
                'preset.presets',
                'preset.presets.label',
                'preset.presets.new',
                'preset.prompt',
                'preset.prompt.label',
                'preset.temperature.label',
                'preset.use',
                'prompt.label',
                'prompt.mode',
                'prompt.mode.label',
                'prompt.model',
                'prompt.model.label',
                'temperature.label',
                'toolbox.prompt.label',
                'toolbox.preset.ai_name.label',
                'toolbox.preset.user_name.label',
                'vision.capture.auto',
                'vision.capture.enable',
                'vision.capture.label',
                'vision.capture.options',
            ],
        }

        # apply to nodes
        for type in nodes:
            for key in nodes[type]:
                if key == "output" and self.window.controller.chat.render.get_engine() != 'legacy':
                    continue
                self.apply(key, type)

        # apply to notepads
        num_notepads = self.window.controller.notepad.get_num_notepads()
        if num_notepads > 0:
            for id in self.window.ui.notepad:
                self.window.ui.notepad[id].textarea.setStyleSheet(self.window.controller.theme.style('font.chat.output'))

        # apply to calendar
        if 'note' in self.window.ui.calendar:
            self.window.ui.calendar['note'].setStyleSheet(self.window.controller.theme.style('font.chat.output'))

        # update value
        size = self.window.core.config.get('font_size')
        if 'note' in self.window.ui.calendar:
            self.window.ui.calendar['note'].value = size
        if num_notepads > 0:
            for id in range(1, num_notepads + 1):
                if id in self.window.ui.notepad:
                    self.window.ui.notepad[id].textarea.value = size

        # plain text/markdown
        for pid in self.window.ui.nodes['output_plain']:
            try:
                self.window.ui.nodes['output_plain'][pid].value = size
                self.window.ui.nodes['output_plain'][pid].update()
            except Exception as e:
                pass

        # ------------------------

        # zoom, (Chromium, web engine)
        if self.window.controller.chat.render.get_engine() == 'web':
            zoom = self.window.core.config.get('zoom')
            for pid in self.window.ui.nodes['output']:
                try:
                    self.window.ui.nodes['output'][pid].value = zoom
                    self.window.ui.nodes['output'][pid].update_zoom()
                except Exception as e:
                    pass
            event = RenderEvent(RenderEvent.ON_THEME_CHANGE)
            self.window.dispatch(event)

        # font size, legacy (markdown)
        elif self.window.controller.chat.render.get_engine() == 'legacy':
            for pid in self.window.ui.nodes['output']:
                self.window.ui.nodes['output'][pid].value = size
                self.window.ui.nodes['output'][pid].update()

        # update tools
        self.window.tools.setup_theme()
