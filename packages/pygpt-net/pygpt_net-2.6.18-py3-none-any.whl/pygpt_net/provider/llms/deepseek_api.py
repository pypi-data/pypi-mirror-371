#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.06 01:00:00                  #
# ================================================== #
from typing import List, Dict

from pygpt_net.core.types import (
    MODE_LLAMA_INDEX,
)
from llama_index.core.llms.llm import BaseLLM as LlamaBaseLLM

from pygpt_net.provider.llms.base import BaseLLM
from pygpt_net.item.model import ModelItem


class DeepseekApiLLM(BaseLLM):
    def __init__(self, *args, **kwargs):
        super(DeepseekApiLLM, self).__init__(*args, **kwargs)
        self.id = "deepseek_api"
        self.name = "Deepseek API"
        self.type = [MODE_LLAMA_INDEX]

    def llama(
            self,
            window,
            model: ModelItem,
            stream: bool = False
    ) -> LlamaBaseLLM:
        """
        Return LLM provider instance for llama

        :param window: window instance
        :param model: model instance
        :param stream: stream mode
        :return: LLM provider instance
        """
        from llama_index.llms.deepseek import DeepSeek
        args = self.parse_args(model.llama_index, window)
        return DeepSeek(**args)

    def get_models(
            self,
            window,
    ) -> List[Dict]:
        """
        Return list of models for the provider

        :param window: window instance
        :return: list of models
        """
        items = []
        client = self.get_client(window)
        models_list = client.models.list()
        if models_list.data:
            for item in models_list.data:
                items.append({
                    "id": item.id,
                    "name": item.id,
                })
        return items
