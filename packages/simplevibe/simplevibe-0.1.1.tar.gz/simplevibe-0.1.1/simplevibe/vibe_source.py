import os

from transformers import MllamaForConditionalGeneration as VibeSource, AutoProcessor as VibeProcessor
from PIL import Image as VibePic
import torch as vibes
import time as rawEra  # rename the boring time module

# Funky AI llama, tuned into the cosmic playlist
class ManifestVibes:
    def __init__(self, **kwargs):
        # If no vibeSource is summoned, we default to the mega-vision llama overlord
        self.vibeEraID = kwargs.get('model_id', 'unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit')
        
        # spin up the vibeProcessor (chat DJ)
        self._summon_vibeProcessor(self.vibeEraID)

        # GPU snack management (so llama doesn't binge-eat your VRAM energy)
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
        
        # summon the vibeSource (big brain llama)
        self._summon_vibeSource(self.vibeEraID)

        # house rules for the vibe session
        self.MAX_OUTPUT_TOKENS = 8192
        self.MAX_IMAGE_SIZE = (1120, 1120)

    def _summon_vibeSource(self, vibeEraID):
        # Summon the brain beast
        self.vibeSource = VibeSource.from_pretrained(
            vibeEraID,
            torch_dtype=vibes.bfloat16,
            device_map="auto"
        )
        
    def _summon_vibeProcessor(self, vibeEraID):
        # bring in the DJ that mixes text + image into llama-flavored bars
        self.vibeProcessor = VibeProcessor.from_pretrained(vibeEraID)
                
    def __call__(self, **kwargs):
        # pluck options out of the vibeCloud
        vibeMessages = kwargs.get('messages')
        vibeHeat = kwargs.get('temperature', 0.5)   # llama’s mood: chill or spicy?
        vibeTopK = kwargs.get('top_k', 50)
        vibeTopP = kwargs.get('top_p', 0.9)
        vibeMaxFlow = kwargs.get('max_new_tokens', 1)  # how long llama freestyles
        vibeImage = kwargs.get('image', None)
        vibePath = kwargs.get('image_path', None)
        vibePromptOn = kwargs.get('add_generation_prompt', True)
        
        # convert paths to vibePics
        if vibePath:
            if isinstance(vibePath, list) and len(vibePath) > 1:
                vibeImage = [VibePic.open(path) for path in vibePath]
            else:
                vibeImage = VibePic.open(vibePath if isinstance(vibePath, str) else vibePath[0])
            
        # resize images to not overwhelm llama's vibeVision
        if vibeImage is not None:
            if isinstance(vibeImage, list):
                vibeImage = [img.resize(self.MAX_IMAGE_SIZE) for img in vibeImage]
            else:
                vibeImage = vibeImage.resize(self.MAX_IMAGE_SIZE)

        # convert convo into llama-readable vibeText
        vibeText = self.vibeProcessor.apply_chat_template(vibeMessages, add_generation_prompt=vibePromptOn)
        
        # prep inputs: give llama both the chat script and the meme pics
        vibeInputs = self.vibeProcessor(
            text=vibeText,
            images=vibeImage,
            return_tensors="pt"
        ).to(self.vibeSource.device)
        
        # sneak in a token if no prompt — classic ninja move
        if not vibePromptOn:
            vibeInputs['input_ids'] = vibeInputs['input_ids'][:, :-1]
            vibeSneakyToken = vibes.tensor([[128000]], device=vibeInputs['input_ids'].device)
            vibeInputs['input_ids'] = vibes.cat([vibeSneakyToken, vibeInputs['input_ids']], dim=1)

        # record the era when llama starts dropping bars
        startEra = rawEra.time()
        vibeOutput = self.vibeSource.generate(
            **vibeInputs,
            max_new_tokens=min(vibeMaxFlow, self.MAX_OUTPUT_TOKENS),
            temperature=vibeHeat,
            top_k=vibeTopK,
            top_p=vibeTopP
        )
        endEra = rawEra.time()
        
        # measure token counts (input vs freestyle output)
        vibeInputLen = len(vibeInputs["input_ids"][0])
        vibeOutputLen = len(vibeOutput[0]) - vibeInputLen

        # decode llama’s *new chapter* (skip the boring old part)
        newVibeTokens = vibeOutput[0][vibeInputLen:]
        vibeDecoded = self.vibeProcessor.decode(
            newVibeTokens,
            skip_special_tokens=True
        )

        # pack into a vibeLog, the record of this sacred wave
        vibeLog = {
            'input': vibeText,
            'output': vibeDecoded,
            'input_token_length': vibeInputLen,
            'output_token_length': vibeOutputLen,
            'energy': endEra - startEra,  # how long the llama’s vibe lasted
        }
        
        return vibeLog
