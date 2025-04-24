from modules.base_module import BaseModule
from modules.utils import *

class Fixer(BaseModule):

    def __init__(self):
        super().__init__()
        self.name = "Fixer"
        self.model = "gemini-2.0-flash"
        self.role = "Given a bug, you should write shell commands to fix the bug. Do not include any other information."
        self.examples = []

    async def fix(self, bug: str) -> None:
        '''
        Return a shell solution given a bug.
        '''
        text = f"Bug:\n{bug}"
        command = self.query(text)
        commands = []
        commands.append(str2shell(command))
        if command.find("pip") != -1:
            commands.append(str2shell(command.replace("pip", "conda")))
        return commands