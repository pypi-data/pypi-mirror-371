# -*- coding: utf-8 -*-

from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

from rwkvfla.models.samba.configuration_samba import SambaConfig
from rwkvfla.models.samba.modeling_samba import SambaBlock, SambaForCausalLM, SambaModel

AutoConfig.register(SambaConfig.model_type, SambaConfig, exist_ok=True)
AutoModel.register(SambaConfig, SambaModel, exist_ok=True)
AutoModelForCausalLM.register(SambaConfig, SambaForCausalLM, exist_ok=True)


__all__ = ['SambaConfig', 'SambaForCausalLM', 'SambaModel', 'SambaBlock']
