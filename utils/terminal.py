import os
import pty
import asyncio
from nicegui import ui
from utils.menu import Menu

class Terminal:
    def __init__(self, fixer, init_commands=None):
        self.fixer = fixer
        self.process = None
        self.master_fd = None
        self.error_info = None
        self.output = ui.log().classes("w-full h-96 bg-black text-white")
        self.command_input = ui.input(label='Command', placeholder='Enter command here').classes('w-full')
        self.command_input.on('keydown.enter', self.run_command)
        self.command_buffer = Menu(init_commands)
        with ui.row():
            ui.button('Next_Command', on_click=self.next_command)
            ui.button('Fix Current Error', on_click=self.fix_error)
            ui.button('Restart', on_click=self.restart)

    async def restart(self):
        '''
        Restart the terminal.
        '''
        if self.process:
            self.process.kill()
            self.process = None
        if self.master_fd:
            os.close(self.master_fd)
            self.master_fd = None
        self.output.push('Terminal restarted')
        await self.run_command()

    async def run_command(self):
        '''
        Run the command in the input field.
        '''
        # If process is running, send input to it
        if self.process and self.process.returncode is None:
            user_input = self.command_input.value + '\n'
            self.command_input.set_value('')
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, os.write, self.master_fd, user_input.encode())
            return

        # Start new process
        command = self.command_input.value.strip()
        if not command:
            command = '\n'
        self.command_input.set_value('')
        self.output.push(f'$ {command}')

        # Create pseudo-terminal
        master, slave = pty.openpty()
        self.master_fd = master

        self.error_info = None  # Reset error info before each command
        
        try:
            self.process = await asyncio.create_subprocess_shell(
                command,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                close_fds=True
            )
        except Exception as e:
            self.error_info = f"Process creation failed: {str(e)}"
            self.output.push(self.error_info)
            if slave: 
                os.close(slave)
            return

        if slave: 
            os.close(slave)  # Close slave in parent process

        asyncio.create_task(self.read_pty_output(master))

    async def read_pty_output(self, master):
        loop = asyncio.get_event_loop()
        try:
            while True:
                # Read from PTY (executor handles blocking call)
                data = await loop.run_in_executor(None, os.read, master, 1024)
                if not data:
                    break
                output = data.decode().strip()
                self.output.push(output)
                
                # Check for common error patterns in the output
                if "not found" in output or "error" in output.lower() or "failed" in output.lower():
                    self.error_info = output
                
        except OSError:
            pass  # PTY closed
        finally:
            os.close(master)
            if self.master_fd == master:
                self.master_fd = None
            
            # After process ends, check its return code
            if self.process:
                return_code = await self.process.wait()
                if return_code != 0 and not self.error_info:
                    self.error_info = f"Process exited with return code {return_code}"
                    self.output.push(self.error_info)
                self.process = None
    
    async def push_command(self, command: str or list):
        if isinstance(command, list):
            for cmd in command:
                self.command_buffer.add_new_item(cmd)
        else:
            self.command_buffer.add_new_item(command)

    async def next_command(self):
        if len(self.command_buffer.menu_items) == 0:
            ui.notify('No commands available', color='red')
            return
        command = self.command_buffer.menu_items[0]['name']
        self.command_buffer.delete_item(self.command_buffer.menu_items[0])
        self.command_input.set_value(command)
        await self.run_command()

    async def fix_error(self):
        '''
        Fix the last error.
        '''
        if self.error_info is None:
            ui.notify('No error to fix', color='red')
            return
        commands = await self.fixer.fix(self.error_info)
        await self.push_command(commands)
        self.output.push("The commands are added to the buffer.")

if __name__ in {"__main__", "__mp_main__"}:
    from menu import Menu
    terminal = Terminal(init_commands=['ls', 'pwd'])
    ui.run(title='Terminal')