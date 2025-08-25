# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
import os, re
import subprocess

def run_command(command: str|list, use_shell: bool=False, print_cmd: bool=False) -> None:
    """
    Run any shell command with a common function.
    
    Args:
        command (str/list): The command to be executed, can be in string or list format.
        use_shell (bool): Whether to use shell mode to execute (True if need to handle pipes/redirects).
        print_cmd (bool): Whether to print the executed command.
    
    Examples:
        #### List
        run_command(['ls', '-l', '/tmp'])
        
        #### string
        run_command('ls -l /tmp | grep log', use_shell=True)
    """
    try:
        if isinstance(command, list):
            printable_command = ' '.join(command)
        else:
            printable_command = command
        if print_cmd:
            print(f"Running command: {printable_command}")
        subprocess.run(
            command,
            check=True,
            shell=use_shell,
            # stderr=subprocess.PIPE,
            # stdout=subprocess.PIPE,
            # universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise SystemExit(1) 
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise SystemExit(1) 

def check_path_exists(path):
    return os.path.exists(path)

def clean_read1_name(r1name):
    pattern = re.compile(r'[._]?[R_]1.*$')
    return re.sub(pattern, '', r1name)