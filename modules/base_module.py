import yaml
from typing import *
from LLM.call import call

class BaseModule():

    def __init__(self):
        self.name = None
        self.role = None
        self.model = None
        with open ("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.api = config["api"]
        self.base_url = config["base_url"] if "base_url" in config else None
    
    def query(self, query: str) -> str:
        assert self.name != None, "The name of the module should be defined."
        assert self.role != None, "The prompt of the module should be defined."
        assert self.model != None, "The model of the module should be defined."

        prompt = f"You are a {self.name}."
        prompt += self.role
        if len(self.examples) > 0:
            prompt += "Here are some examples:\n"
            for example in self.examples:
                prompt += f"Example: {example}"

        return call(self.api, self.base_url, self.model, prompt, query)