from plugin_base import PluginBase
from llama_cpp import Llama
import openai
import os
import json

class LLMPlugin(PluginBase):
    def initialize(self, context):
        self.models = {
            "llama2-7b": "llama-2-7b.Q4_0.gguf",
            # Add more models as needed
        }
        self.current_model = "llama2-7b"
        self.mode = "local"
        self.llm = Llama(model_path=self.models[self.current_model])
        
        # Load API key from environment variable
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def get_lua_interface(self):
        return {
            'llm_complete': self.lua_callable(self.complete),
            'llm_chat': self.lua_callable(self.chat),
            'llm_set_model': self.lua_callable(self.set_model),
            'llm_set_mode': self.lua_callable(self.set_mode),
            'llm_list_models': self.lua_callable(self.list_models)
        }

    def set_model(self, model_name):
        if self.mode == "local":
            if model_name in self.models:
                self.current_model = model_name
                self.llm = Llama(model_path=self.models[self.current_model])
                return json.dumps({"status": "success", "message": f"Model set to {model_name}"})
            else:
                return json.dumps({"status": "error", "message": f"Model {model_name} not found"})
        else:
            self.current_model = model_name
            return json.dumps({"status": "success", "message": f"Online model set to {model_name}"})

    def set_mode(self, mode):
        if mode in ["local", "online"]:
            self.mode = mode
            return json.dumps({"status": "success", "message": f"Mode set to {mode}"})
        else:
            return json.dumps({"status": "error", "message": "Invalid mode. Choose 'local' or 'online'"})

    def list_models(self):
        if self.mode == "local":
            return json.dumps(list(self.models.keys()))
        else:
            return json.dumps(["gpt-3.5-turbo", "gpt-4"])  # Add more as needed

    def complete(self, prompt, max_tokens=100):
        if self.mode == "local":
            result = self.llm(prompt, max_tokens=max_tokens)
            return json.dumps({"text": result["choices"][0]["text"]})
        else:
            response = openai.completions.create(
                model=self.current_model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            return json.dumps({"text": response.choices[0].text})

    def chat(self, messages):
        if self.mode == "local":
            result = self.llm.create_chat_completion(messages)
            return json.dumps(result)
        else:
            response = openai.chat.completions.create(
                model=self.current_model,
                messages=messages
            )
            return json.dumps(response.to_dict())

    @property
    def name(self):
        return "llm"