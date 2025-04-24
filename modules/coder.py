from modules.base_module import BaseModule
from modules.utils import *
from nicegui import ui

class Coder(BaseModule):

    def __init__(self):
        super().__init__()
        self.name = "Coder"
        self.model = "gemini-2.0-flash"
        self.role = "Given a task, you should write a python code to solve it. You can import any package you need. Do not include any other information."
        self.examples = []

    async def run(self, task: str) -> str:
        '''
        Write a code to solve a task.
        '''
        code = self.query(task)
        return str2code(code)