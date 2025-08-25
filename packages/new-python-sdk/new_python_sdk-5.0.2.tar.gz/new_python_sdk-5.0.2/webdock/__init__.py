class Webdock:
    def __init__(self, token: str) -> None:
        from account import Account
        from events import Events
        from hooks import Hooks
        from images import Images
        from locations import Locations
        from profiles import Profiles
        from scripts import Scripts
        from servers import Servers
        from shellusers import ShellUsers
        from sshkeys import SshKeys
        from snapshots import Snapshots
        from operation import Operation

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


