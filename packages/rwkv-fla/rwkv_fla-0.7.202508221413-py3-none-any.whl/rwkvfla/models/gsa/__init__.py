# -*- coding: utf-8 -*-

from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

from rwkvfla.models.gsa.configuration_gsa import GSAConfig
from rwkvfla.models.gsa.modeling_gsa import GSAForCausalLM, GSAModel

AutoConfig.register(GSAConfig.model_type, GSAConfig, exist_ok=True)
AutoModel.register(GSAConfig, GSAModel, exist_ok=True)
AutoModelForCausalLM.register(GSAConfig, GSAForCausalLM, exist_ok=True)


__all__ = ['GSAConfig', 'GSAForCausalLM', 'GSAModel']
