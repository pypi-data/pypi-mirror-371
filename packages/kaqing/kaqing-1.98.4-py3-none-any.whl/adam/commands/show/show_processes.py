from adam.commands.processes import Processes
from adam.commands.command import Command
from adam.repl_state import ReplState

class ShowProcesses(Command):
    COMMAND = 'show processes'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowProcesses, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowProcesses.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        Processes().run(Processes.COMMAND, state)

        return state

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ShowProcesses.COMMAND} [-s]\t show process overview  -s show commands on nodes'