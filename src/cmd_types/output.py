"""
Module to define command output
"""
from dataclasses import dataclass

@dataclass
class CommandOutput:
    stdout: str = ""
    stderr: str = ""
    errcode: int = 0

    def __add__(self, other):
        if isinstance(other, str):
            self.stdout += other
            self.stderr += other
            return self
        elif not isinstance(other, CommandOutput):
            raise TypeError
        else:
            if other.stdout:
                self.stdout += other.stdout
            if other.stderr:
                self.stderr += other.stderr
            if other.errcode != 0:
                self.errcode = other.errcode
            return self

    def print(self):
        if self.stderr:
            print(self.stderr)
        if self.stdout:
            print(self.stdout)

    def strip(self):
        if self.stdout:
            self.stdout = self.stdout.strip()
        if self.stderr:
            self.stderr = self.stderr.strip()
        return self
