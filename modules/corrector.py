from modules.base_module import BaseModule
from modules.utils import *

class Corrector(BaseModule):

    def __init__(self):
        super().__init__()
        self.name = "Corrector"
        self.model = "gemini-2.0-flash"
        self.role = "Given a task, a wrong code to solve it and a reason about why it is wrong, you should correct the code. You should return the corrected code. Do not include any other information."
        self.examples = []

    async def run(self, task: str, code: str, reason: str) -> str:
        '''
        Correct a code.
        '''
        text = f"Task: {task}\nCode: {code}\nReason: {reason}"
        code = self.query(text)
        return str2code(code)