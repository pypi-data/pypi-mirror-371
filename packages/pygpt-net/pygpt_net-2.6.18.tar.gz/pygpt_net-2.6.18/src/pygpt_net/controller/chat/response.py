#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.19 07:00:00                  #
# ================================================== #

from typing import Dict, Any

from pygpt_net.core.text.utils import has_unclosed_code_tag
from pygpt_net.core.types import (
    MODE_AGENT_LLAMA,
    MODE_AGENT_OPENAI,
    MODE_ASSISTANT,
    MODE_CHAT,
)
from pygpt_net.core.bridge.context import BridgeContext
from pygpt_net.core.events import RenderEvent, KernelEvent, AppEvent
from pygpt_net.item.ctx import CtxItem
from pygpt_net.utils import trans


class Response:
    def __init__(self, window=None):
        """
        Response controller

        :param window: Window instance
        """
        super(Response, self).__init__()
        self.window = window

    def handle(
            self,
            context: BridgeContext,
            extra: Dict[str, Any],
            status: bool
    ):
        """
        Handle Bridge success

        :param status: Result status
        :param context: BridgeContext
        :param extra: Extra data
        """
        ctx = context.ctx
        if not status:
            error = None
            if "error" in extra:
                error = extra.get("error")
            self.window.controller.chat.log("Bridge response: ERROR")
            if error is not None:
                self.window.ui.dialogs.alert(error)
                self.window.update_status(error)
            else:
                self.window.ui.dialogs.alert(trans('status.error'))
                self.window.update_status(trans('status.error'))
        else:
            self.window.controller.chat.log_ctx(ctx, "output")  # log
            if self.window.controller.kernel.stopped():
                return

        ctx.current = False  # reset current state
        stream = context.stream
        mode = extra.get('mode', MODE_CHAT)
        reply = extra.get('reply', False)
        internal = extra.get('internal', False)
        self.window.core.ctx.update_item(ctx)

        # fix frozen chat
        if not status:
            data = {
                "meta": ctx.meta,
            }
            event = RenderEvent(RenderEvent.TOOL_CLEAR, data)
            self.window.dispatch(event)  # hide cmd waiting
            if not self.window.controller.kernel.stopped():
                self.window.controller.chat.common.unlock_input()  # unlock input
            # set state to: error
            self.window.dispatch(KernelEvent(KernelEvent.STATE_ERROR, {
                "id": "chat",
            }))
            return

        try:
            if mode != MODE_ASSISTANT:
                ctx.from_previous()  # append previous result if exists
                self.window.controller.chat.output.handle(
                    ctx,
                    mode,
                    stream,
                    is_response=True,
                    reply=reply,
                    internal=internal,
                    context=context,
                    extra=extra,
                )
        except Exception as e:
            extra["error"] = e
            self.failed(context, extra)

        if stream: 
            if mode not in self.window.controller.chat.output.not_stream_modes:
                return # handled in stream:handleEnd()

        # post-handle, execute cmd, etc.
        self.post_handle(
            ctx=ctx,
            mode=mode,
            stream=stream,
            reply=reply,
            internal=internal
        )

    def post_handle(
            self,
            ctx: CtxItem,
            mode: str,
            stream: bool,
            reply: bool,
            internal: bool
    ):
        """
        Post-handle response

        :param ctx: CtxItem
        :param mode: Mode of operation
        :param stream: True if stream mode
        :param reply: True if reply mode
        :param internal: True if internal mode
        """
        self.window.controller.chat.output.post_handle(ctx, mode, stream, reply, internal)
        self.window.controller.chat.output.handle_end(ctx, mode)  # handle end.

    def begin(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge begin

        :param context: BridgeContext
        :param extra: Extra data
        """
        msg = extra.get("msg", "")
        self.window.controller.chat.common.lock_input()  # lock input
        if msg:
            self.window.update_status(msg)

    def append(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge append (agent mode)

        :param context: BridgeContext
        :param extra: Extra data
        """
        global_mode = self.window.core.config.get('mode', MODE_AGENT_LLAMA)
        ctx = context.ctx
        if self.window.controller.kernel.stopped():
            output = ctx.output
            if output and has_unclosed_code_tag(output):
                ctx.output += "\n```"
            ctx.msg_id = None
            if ctx.id is None:
                self.window.core.ctx.add(ctx)  # store context to prevent current output from being lost
                self.window.controller.ctx.prepare_name(ctx)  # summarize if not yet

            # finish render
            self.window.dispatch(AppEvent(AppEvent.CTX_END))  # app event
            self.window.dispatch(RenderEvent(RenderEvent.RELOAD))  # reload chat window
            return

        # at first, handle previous context (user input) if not handled yet
        prev_ctx = ctx.prev_ctx
        stream = False
        if prev_ctx and prev_ctx.current:
            prev_ctx.current = False  # reset previous context
            self.window.core.ctx.update_item(prev_ctx)
            prev_ctx.from_previous()  # append previous result if exists
            self.window.controller.chat.output.handle(
                ctx=prev_ctx,
                mode=prev_ctx.mode,
                stream_mode=False,
            )
            self.window.controller.chat.output.post_handle(ctx=prev_ctx,
                                                           mode=prev_ctx.mode,
                                                           stream=False,
                                                           reply=False,
                                                           internal=False)

            self.window.controller.chat.output.handle_end(ctx=prev_ctx,
                                                          mode=prev_ctx.mode)  # end previous context


        # if next in agent cycle
        if ctx.partial:
            self.window.dispatch(AppEvent(AppEvent.CTX_END))  # app event

        # handle current step
        ctx.current = False  # reset current state
        mode = ctx.mode
        reply = ctx.reply
        internal = ctx.internal

        self.window.core.ctx.set_last_item(ctx)
        event = RenderEvent(RenderEvent.BEGIN, {
            "meta": ctx.meta,
            "ctx": ctx,
            "stream": stream,
        })
        self.window.dispatch(event)

        # append step input to chat window
        event = RenderEvent(RenderEvent.INPUT_APPEND, {
            "meta": ctx.meta,
            "ctx": ctx,
        })
        self.window.dispatch(event)

        if ctx.id is None:
            self.window.core.ctx.add(ctx)

        self.window.core.ctx.update_item(ctx)

        # update ctx meta
        if mode in (MODE_AGENT_LLAMA, MODE_AGENT_OPENAI) and ctx.meta is not None:
            self.window.core.ctx.replace(ctx.meta)
            self.window.core.ctx.save(ctx.meta.id)

            # update preset if exists
            preset = self.window.controller.presets.get_current()
            if preset is not None:
                if ctx.meta.assistant is not None:
                    preset.assistant_id = ctx.meta.assistant
                    self.window.core.presets.update_and_save(preset)

        try:
            self.window.controller.chat.output.handle(ctx, mode, stream)
        except Exception as e:
            self.window.controller.chat.log(f"Output ERROR: {e}")  # log
            self.window.controller.chat.handle_error(e)
            print(f"Error in append text: {e}")

        # post-handle, execute cmd, etc.
        self.window.controller.chat.output.post_handle(ctx, mode, stream, reply, internal)
        self.window.controller.chat.output.handle_end(ctx, mode)  # handle end.

        event = RenderEvent(RenderEvent.RELOAD)
        self.window.dispatch(event)

        # if continue reasoning
        if global_mode not in (MODE_AGENT_LLAMA, MODE_AGENT_OPENAI):
            return  # no agent mode, nothing to do

        # not agent final response
        if ctx.extra is None or (isinstance(ctx.extra, dict) and "agent_finish" not in ctx.extra):
            self.window.update_status(trans("status.agent.reasoning"))
            self.window.controller.chat.common.lock_input()  # lock input, re-enable stop button

        # agent final response
        if ctx.extra is not None and (isinstance(ctx.extra, dict) and "agent_finish" in ctx.extra):
            self.window.controller.agent.llama.on_finish(ctx)  # evaluate response and continue if needed

    def end(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge end

        :param context: BridgeContext
        :param extra: Extra data
        """
        msg = extra.get("msg", "")
        status = trans("status.finished")
        if msg:
            status = msg
        self.window.update_status(status)
        self.window.controller.agent.llama.on_end()
        self.window.controller.chat.common.unlock_input()  # unlock input
        # set state to: idle
        self.window.dispatch(KernelEvent(KernelEvent.STATE_IDLE, {
            "id": "chat",
        }))

    def failed(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge failed

        :param context: BridgeContext
        :param extra: Extra data
        """
        err = extra.get("error") if "error" in extra else None
        self.window.controller.chat.log(f"Output ERROR: {err}")  # log
        self.window.controller.chat.handle_error(err)
        self.window.controller.chat.common.unlock_input()  # unlock input
        print(f"Error in sending text: {err}")
        # set state to: error
        self.window.dispatch(KernelEvent(KernelEvent.STATE_ERROR, {
            "id": "chat",
        }))

    def update_status(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge evaluate

        :param context: BridgeContext
        :param extra: Extra data
        """
        msg = extra.get("msg", "")
        self.window.update_status(msg)

    def live_append(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        ctx = context.ctx
        data = {
            "meta": ctx.meta,
            "ctx": ctx,
            "chunk": extra.get("chunk", ""),
            "begin": extra.get("begin", False),
        }
        event = RenderEvent(RenderEvent.LIVE_APPEND, data)
        self.window.dispatch(event)

    def live_clear(
            self,
            context: BridgeContext,
            extra: Dict[str, Any]
    ):
        """
        Handle Bridge live clear

        :param context: BridgeContext
        :param extra: Extra data
        """
        ctx = context.ctx
        data = {
            "meta": ctx.meta,
            "ctx": ctx,
        }
        event = RenderEvent(RenderEvent.LIVE_CLEAR, data)
        self.window.dispatch(event)