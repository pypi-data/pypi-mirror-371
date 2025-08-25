from testnewsdkwebdock.account import Account
from testnewsdkwebdock.events import Events
from testnewsdkwebdock.hooks import Hooks
from testnewsdkwebdock.images import Images
from testnewsdkwebdock.locations import Locations
from testnewsdkwebdock.profiles import Profiles
from testnewsdkwebdock.scripts import Scripts
from testnewsdkwebdock.servers import Servers
from testnewsdkwebdock.shellusers import ShellUsers
from testnewsdkwebdock.sshkeys import SshKeys
from testnewsdkwebdock.snapshots import Snapshots
from testnewsdkwebdock.operation import Operation


class Webdock:
    def __init__(self, token: str) -> None:
        self.string_token: str = token
        self.account: Account = Account(self)
        self.images: Images = Images(self)
        self.profiles: Profiles = Profiles(self)
        self.events: Events = Events(self)
        self.hooks: Hooks = Hooks(self)
        self.locations: Locations = Locations(self)
        self.scripts: Scripts = Scripts(self)
        self.servers: Servers = Servers(self)
        self.shellUsers: ShellUsers = ShellUsers(self)
        self.sshkeys: SshKeys = SshKeys(self)
        self.snapshots: Snapshots = Snapshots(self)
        self.operation: Operation = Operation(self)


# Export the main class for easy importing
__all__ = ['Webdock']
