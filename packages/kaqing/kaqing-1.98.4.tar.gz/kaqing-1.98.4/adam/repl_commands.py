from adam.commands.app import App
from adam.commands.app_ping import AppPing
from adam.commands.frontend.code_start import CodeStart
from adam.commands.frontend.code_stop import CodeStop
from adam.commands.show.show_app_queues import ShowAppQueues
from adam.commands.cp import ClipboardCopy
from adam.commands.bash import Bash
from adam.commands.cd import Cd
from adam.commands.check import Check
from adam.commands.command import Command
from adam.commands.cqlsh import Cqlsh
from adam.commands.devices import DeviceApp, DeviceCass, DevicePostgres
from adam.commands.exit import Exit
from adam.commands.medusa.medusa import Medusa
from adam.commands.param_get import GetParam
from adam.commands.issues import Issues
from adam.commands.ls import Ls
from adam.commands.nodetool import NodeTool
from adam.commands.postgres.postgres import Postgres
from adam.commands.preview_table import PreviewTable
from adam.commands.processes import Processes
from adam.commands.pwd import Pwd
from adam.commands.reaper.reaper import Reaper
from adam.commands.repair.repair import Repair
from adam.commands.report import Report
from adam.commands.restart import Restart
from adam.commands.rollout import RollOut
from adam.commands.param_set import SetParam
from adam.commands.show.show import Show
from adam.commands.show.show_app_actions import ShowAppActions
from adam.commands.show.show_app_id import ShowAppId
from adam.commands.status import Status
from adam.commands.storage import Storage
from adam.commands.watch import Watch

class ReplCommands:
    def repl_cmd_list() -> list[Command]:
        return ReplCommands.app() + [CodeStart(), CodeStop()] + [DeviceApp(), DevicePostgres(), DeviceCass()] + ReplCommands.navigation() + \
               ReplCommands.cassandra_check() + ReplCommands.cassandra_ops() + ReplCommands.tools() + ReplCommands.exit()

    def navigation() -> list[Command]:
        return [Ls(), PreviewTable(), Cd(), Pwd(), ClipboardCopy(), GetParam(), SetParam()] + Show.cmd_list()

    def cassandra_check() -> list[Command]:
        return [Check(), Issues(), NodeTool(), Processes(), Report(), Status(), Storage()]

    def cassandra_ops() -> list[Command]:
        return Medusa.cmd_list() + [Restart(), RollOut(), Watch()] + Reaper.cmd_list() + Repair.cmd_list()

    def tools() -> list[Command]:
        return [Cqlsh(), Postgres(), Bash()]

    def app() -> list[Command]:
        return [ShowAppActions(), ShowAppId(), ShowAppQueues(), AppPing(), App(), ]
        # return [C3Echo(), C3IqCount(), C3()]

    def exit() -> list[Command]:
        return [Exit()]