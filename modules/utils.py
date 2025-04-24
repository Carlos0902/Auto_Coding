import os
import sys
import subprocess
import threading
from typing import List, Tuple

def write(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
        f.write('\n')

def str2code(s: str) -> str:
    '''
    Make sure the string is a valid python code.
    '''
    s = s.replace('python', '')
    s = s.replace('```', '')
    return s.strip()

def str2shell(s: str) -> str:
    '''
    Make sure the string is a valid shell command.
    '''
    s = s.replace('shell', '')
    s = s.replace('bash', '')
    s = s.replace('sh', '')
    s = s.replace('```', '')
    return s.strip()

async def write_to_cache(s: str, type: str) -> str:
    '''
    Write a string to the cache.
    '''
    root = "cache"
    if not os.path.exists(root): os.mkdir(root)

    assert type in ["python", "sh"], "The type should be either 'python' or 'sh'."

    if type == 'python':
        file = os.path.join(root, "task.py")
    elif type == 'sh':
        file = os.path.join(root, "task.sh")
    with open(file, 'w') as f:
        f.write(s)
    
    return file

async def run(input: List[str]) -> Tuple[int, str, str]:
    '''
    Run anything with real-time output.
    Return: (returncode, stdout, stderr)
    '''
    print(f"Running command '{' '.join(input)}'...")
    
    proc = subprocess.Popen(
        input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    stdout_lines = []
    stderr_lines = []

    def read_stream(stream, buffer):
        for line in stream:
            buffer.append(line)
            print(line, end='', flush=True)  # Print immediately

    # Create threads for reading stdout and stderr
    stdout_thread = threading.Thread(
        target=read_stream, args=(proc.stdout, stdout_lines)
    )
    stderr_thread = threading.Thread(
        target=read_stream, args=(proc.stderr, stderr_lines)
    )

    # Start threads
    stdout_thread.start()
    stderr_thread.start()

    # Wait for process to complete
    proc.wait()
    
    # Wait for threads to finish reading remaining output
    stdout_thread.join()
    stderr_thread.join()

    # Combine captured lines into strings
    stdout = ''.join(stdout_lines)
    stderr = ''.join(stderr_lines)

    return proc.returncode, stdout, stderr
