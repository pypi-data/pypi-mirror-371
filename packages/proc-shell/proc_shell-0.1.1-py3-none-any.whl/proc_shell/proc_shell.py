# proc_shell/full_proc_shell.py
import os
import shlex
import subprocess
import readline
import sys
import psutil  # for real /proc info simulation

class ProcShell:
    def __init__(self):
        self.env = os.environ.copy()
        self.cwd = os.getcwd()
        self.procs = psutil.pids()  # pseudo /proc processes

    def parse_command(self, cmd):
        try:
            return shlex.split(cmd)
        except ValueError as e:
            print(f"Parse error: {e}")
            return []

    def run_builtin(self, tokens):
        if not tokens:
            return True

        cmd = tokens[0]

        if cmd == "cd":
            path = tokens[1] if len(tokens) > 1 else os.path.expanduser("~")
            try:
                os.chdir(path)
                self.cwd = os.getcwd()
            except Exception as e:
                print(f"cd: {e}")
            return True
        elif cmd == "exit":
            sys.exit(0)
        elif cmd == "echo":
            print(" ".join(tokens[1:]))
            return True
        elif cmd == "export":
            for pair in tokens[1:]:
                if '=' in pair:
                    k, v = pair.split("=", 1)
                    self.env[k] = v
            return True
        elif cmd == "cat" and len(tokens) > 1:
            return self.read_proc(tokens[1])
        return False

    def read_proc(self, path):
        """Handle /proc pseudo-files."""
        if path.startswith("/proc"):
            parts = path.strip("/").split("/")
            if len(parts) == 2 and parts[1].isdigit():
                pid = int(parts[1])
                if pid in self.procs:
                    try:
                        p = psutil.Process(pid)
                        print(f"PID: {p.pid}\nName: {p.name()}\nStatus: {p.status()}")
                    except Exception as e:
                        print(f"/proc/{pid}: cannot read info ({e})")
                else:
                    print(f"/proc/{pid}: No such process")
                return True
            else:
                print(f"{path}: Unsupported /proc path")
                return True
        return False

    def run_external(self, tokens):
        background = False
        if tokens and tokens[-1] == "&":
            background = True
            tokens = tokens[:-1]

        try:
            if background:
                subprocess.Popen(tokens, cwd=self.cwd, env=self.env)
            else:
                subprocess.run(tokens, cwd=self.cwd, env=self.env)
        except FileNotFoundError:
            print(f"{tokens[0]}: command not found")
        except Exception as e:
            print(f"Error: {e}")

    def repl(self):
        print("Welcome to ProcShell! Type 'exit' to quit.")
        while True:
            try:
                cmd_line = input(f"{self.cwd} $ ")
                tokens = self.parse_command(cmd_line)
                if not tokens:
                    continue
                if not self.run_builtin(tokens):
                    self.run_external(tokens)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting ProcShell.")
                break

if __name__ == "__main__":
    shell = ProcShell()
    shell.repl()
