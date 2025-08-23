#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.07.25 22:00:00                  #
# ================================================== #

from typing import Optional, Any

from pygpt_net.core.types import (
    MODE_AGENT,
    MODE_EXPERT,
)
from pygpt_net.core.events import KernelEvent, RenderEvent
from pygpt_net.core.bridge import BridgeContext
from pygpt_net.core.ctx.reply import ReplyContext
from pygpt_net.item.ctx import CtxItem


class Experts:
    def __init__(self, window=None):
        """
        Experts controller

        :param window: Window instance
        """
        self.window = window
        self.is_stop = False

    def stop(self):
        """
        Stop experts
        """
        self.is_stop = True

    def stopped(self) -> bool:
        """
        Check if experts are stopped

        :return: True if experts are stopped
        """
        return self.is_stop

    def unlock(self):
        """Unlock experts"""
        self.is_stop = False

    def enabled(self, check_inline = True) -> bool:
        """
        Check if experts are enabled

         :param check_inline: check inline mode
        :return: True if experts are enabled
        """
        modes = [MODE_EXPERT]
        mode = self.window.core.config.get('mode')
        if not check_inline:
            if mode in modes:
                return True
            else:
                return False
        else:
            if mode in modes or self.window.controller.plugins.is_type_enabled("expert"):
                return True
            else:
                return False

    def append_prompts(
            self,
            mode: str,
            sys_prompt: str,
            parent_id: Optional[str] = None
    ):
        """
        Append prompt to the window

        :param mode: Mode
        :param sys_prompt: Prompt text
        :param parent_id: Parent ID
        """
        # if agent enabled
        if self.window.controller.agent.legacy.enabled():
            prev_prompt = sys_prompt
            sys_prompt = self.window.core.prompt.get("agent.instruction")
            if prev_prompt is not None and prev_prompt.strip() != "":
                sys_prompt = sys_prompt + "\n\n" + prev_prompt  # append previous prompt

        # expert or agent mode
        if ((self.enabled() or self.window.controller.agent.legacy.enabled(check_inline=False))
                and parent_id is None):  # master expert has special prompt
            if self.window.controller.agent.legacy.enabled():  # if agent then leave agent prompt
                sys_prompt += "\n\n" + self.window.core.experts.get_prompt()  # both, agent + experts
            else:
                sys_prompt = self.window.core.experts.get_prompt()
                # mode = "chat"  # change mode to chat for expert

        # if global mode is agent
        if mode == MODE_AGENT:
            sys_prompt = self.window.controller.agent.legacy.on_system_prompt(
                sys_prompt,
                append_prompt=None,  # sys prompt from preset is used here
                auto_stop=self.window.core.config.get('agent.auto_stop'),
            )

        return sys_prompt

    def handle(self, ctx: CtxItem) -> int:
        """
        Handle mentions (calls) to experts

        :param ctx: CtxItem
        """
        stream_mode = self.window.core.config.get('stream')
        num_calls = 0

        # extract expert mentions
        if self.enabled() or self.window.controller.agent.legacy.enabled(check_inline=False):
            # re-send to master
            if ctx.sub_reply:
                self.window.core.ctx.update_item(ctx)
                self.window.core.experts.reply(ctx)
            else:
                # call experts
                if not ctx.reply:
                    mentions = self.window.core.experts.extract_calls(ctx)
                    if mentions:
                        num_calls = 0
                        self.log("Calling experts...")
                        data = {
                            "meta": ctx.meta,
                            "ctx": ctx,
                            "stream": stream_mode,
                        }
                        event = RenderEvent(RenderEvent.END, data)
                        self.window.dispatch(event)  # close previous render
                        for expert_id in mentions:
                            if not self.window.core.experts.exists(expert_id):
                                self.log("Expert not found: " + expert_id)
                                continue
                            self.log("Calling: " + expert_id)
                            ctx.sub_calls += 1

                            # add to reply stack
                            reply = ReplyContext()
                            reply.type = ReplyContext.EXPERT_CALL
                            reply.ctx = ctx
                            reply.parent_id = expert_id
                            reply.input = mentions[expert_id]

                            # send to kernel
                            context = BridgeContext()
                            context.ctx = ctx
                            context.reply_context = reply
                            event = KernelEvent(KernelEvent.AGENT_CALL, {
                                'context': context,
                                'extra': {},
                            })
                            self.window.dispatch(event)

                            num_calls += 1
                        if num_calls > 0:
                            return num_calls  # abort continue if expert call detected

        return num_calls

    def log(self, data: Any):
        """
        Log data to debug

        :param data: Data to log
        """
        self.window.core.debug.info(data)