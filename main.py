from modules import *
from modules.utils import *
from nicegui import ui
import utils
import asyncio

class AutoCoder():

    def __init__(self):
        
        self.coder = Coder()
        self.code = None
        self.corrector = Corrector()
        self.fixer = Fixer()

        # Initialize the UI
        self.tabs = {}
        self.containers = {}
        # Prompt
        self.prompt = None
        self.prompt_value = None

        with ui.splitter(value=15).classes('w-full h-screen') as splitter:
            with splitter.before:
                with ui.tabs().props('vertical').classes('w-full') as self.window:
                    self.tabs['main'] = ui.tab('Main')
                    self.tabs['code'] = ui.tab('Code')
                    self.tabs['terminal'] = ui.tab('Terminal')
            with splitter.after:
                with ui.scroll_area().classes('w-full h-full'):
                    with ui.tab_panels(self.window, value=self.tabs['main']).props('vertical').classes('w-full'):
                        with ui.tab_panel(self.tabs['main']):
                            self.prompt = ui.input(label='Prompt', placeholder='Write a prompt here').classes('w-full')
                            ui.button('Generate Code', on_click=lambda: self.generate_code())
                        with ui.tab_panel(self.tabs['code']):
                            self.containers['code'] = ui.column().classes('w-full h-full')
                        with ui.tab_panel(self.tabs['terminal']):
                            self.terminal = utils.Terminal(self.fixer)
                            self.containers['terminal'] = ui.column().classes('w-full h-full')

    async def generate_code(self):
        '''
        Generate code based on the prompt.
        '''
        self.prompt_value = self.prompt.value
        if not self.prompt_value:
            ui.notify("Please provide a prompt.")
            return
        ui.label("Generating code...")
        self.code = await self.coder.run(self.prompt_value)
        ui.label("Code generated successfully.")
        await self.check_code()

    async def check_code(self):
        '''
        Check the code.
        '''
        self.window.set_value(self.tabs['code'])
        with self.containers['code']:
            ui.label("Please check if the following code is correct:")
            editor = ui.codemirror(self.code).classes('w-full h-full')
            with ui.row():
                ui.button('Save', on_click=lambda: self.save_code(editor))
                ui.button('AI Modification', on_click=lambda: self.correct_code())
                ui.button('Run Code', on_click=lambda: self.run_code())
        
    async def save_code(self, editor):
        '''
        Save the modified code.
        '''
        code = editor.value

    async def correct_code(self):
        '''
        Correct the code if it is not correct.
        '''
        with ui.dialog() as dialog, ui.card():
            ui.label("Please provide correction feedback")
            reason = ui.input(label='Reason', placeholder='Write a reason here')
            with ui.row():    
                ui.button('Submit', on_click=lambda: dialog.submit(reason.value))
                ui.button('Cancel', on_click=dialog.close)
                
        result = await dialog
        if result is None: 
            return
        self.code = await self.corrector.run(self.prompt_value, self.code, result)
        await self.check_code()

    async def run_code(self):
        '''
        Run the code.
        '''
        file = await write_to_cache(self.code, type='python')
        return_code, result, error = await run(['python', file])
        if return_code != 0:
            ui.label("Error in code execution.")
            ui.code(error).classes('w-full')
            with ui.row():
                ui.button('Fix Code', on_click=lambda: self.fix_code(error))
        else:
            ui.label("Code executed successfully.")
            ui.label("The result is:")
            ui.code(result).classes('w-full')

    async def fix_code(self, error):
        '''
        Fix the code given an error.
        '''
        self.window.set_value(self.tabs['terminal'])
        commands = await self.fixer.fix(error)
        await self.terminal.push_command(commands)
        self.terminal.output.push("Fix commands are generated. Click the button to run them.")

auto_coder = AutoCoder()
ui.run(title='Auto Coding', reload=False, reconnect_timeout=600)
