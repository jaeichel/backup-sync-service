import base64
from enum import Enum
import typing


class SyncType(Enum):
    READ_WRITE = 1,
    READ_ONLY = 2,
    ENCRYPTED = 3


class AddSyncFolderRequest:
    def __init__(self,
                *,
                path: str,
                secret: str,
                selective_sync: bool):
        self.path = path
        self.secret = secret
        self.selective_sync = selective_sync


class AddSyncFolderResponse:
    def __init__(self,
                 *,
                 can_encrypt: bool,
                 encrypted_secret: typing.Optional[str] = None,
                 folder_id: str,
                 path: str,
                 read_only_secret: typing.Optional[str] = None,
                 secret: str,
                 secret_type: SyncType) -> None:
        self.can_encrypt = can_encrypt
        self.encrypted_secret = encrypted_secret
        self.folder_id = folder_id
        self.path = path
        self.read_only_secret = read_only_secret
        self.read_write_secret = secret if secret_type == SyncType.READ_WRITE else None
        self.secret = secret
        self.secret_type = secret_type


class ConnectionInfo:
    def __init__(self,
                 *,
                 host: str,
                 user: typing.Optional[str] = None,
                 password: typing.Optional[str] = None,
                 auth: typing.Optional[str] = None,
                 verify_ssl: bool = True) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl

        if self.user is not None and self.password is not None:
            user_password = f'{self.user}:{self.password}'
            self.auth = base64.urlsafe_b64encode(user_password.encode('utf-8')).decode('utf-8')
        else:
            self.auth = auth


class Folder:
    def __init__(self,
                 *,
                 can_encrypt: bool,
                 encrypted_secret: typing.Optional[str] = None,
                 folder_id: str,
                 is_owner: typing.Optional[bool] = None,
                 name: str,
                 path: typing.Optional[str] = None,
                 read_only_secret: typing.Optional[str] = None,
                 secret: str,
                 secret_type: SyncType,
                 share_id: typing.Optional[str] = None) -> None:
        self.can_encrypt = can_encrypt
        self.encrypted_secret = encrypted_secret
        self.folder_id = folder_id
        self.is_owner = is_owner
        self.name = name
        self.path = path
        self.read_only_secret = read_only_secret
        self.read_write_secret = secret if secret_type == SyncType.READ_WRITE else None
        self.secret = secret
        self.secret_type = secret_type
        self.share_id = share_id


class Folders:
    def __init__(self, *, folders: typing.Sequence[Folder]) -> None:
        self.folders = folders


class Identity:
    def __init__(self, *, device_name: str, id: str, username: str) -> None:
        self.device_name = device_name
        self.id = id
        self.username = username


class LocalStorageFirstRunTips:
    def __init__(self, *, add_folder: bool, new_folder_share: bool) -> None:
        self.add_folder = add_folder
        self.new_folder_share = new_folder_share


class LocalStorageStatusPanelTab:
    def __init__(self, *, interval: int, table: bool = None) -> None:
        self.interval = interval
        self.table = table


class LocalStorageStatusPanel:
    def __init__(self,
                *,
                active_tab_name: str,
                is_toggled: bool,
                show: bool,
                tabs: typing.Dict[str, LocalStorageStatusPanelTab]) -> None:
        self.active_tab_name = active_tab_name
        self.is_toggled = is_toggled
        self.show = show
        self.tabs = tabs

class LocalStorageScheduleSettings:
    def __init__(self,
                 *,
                 dlrate: int,
                 is_dl_unlimit: bool,
                 is_ul_unlimit: bool,
                 schedule_type: int,
                 ulrate: int
                 ) -> None:
        self.dlrate = dlrate
        self.is_dl_unlimit = is_dl_unlimit
        self.is_ul_unlimit = is_ul_unlimit
        self.schedule_type = schedule_type
        self.ulrate = ulrate

class LocalStorage:
    def __init__(self,
                 *,
                 active_tab: str,
                 custom_folder_names: typing.Optional[typing.Dict[str, str]] = {},
                 first_run_tips: typing.Optional[LocalStorageFirstRunTips] = None,
                 folder_share_options: typing.Optional[typing.Dict] = {},
                 folders_added: typing.Optional[bool] = None,
                 has_been_pro: typing.Optional[bool] = None,
                 hidden_devices: typing.List[str] = [],
                 status_panel: typing.Optional[LocalStorageStatusPanel] = None,
                 schedule_settings: typing.Optional[LocalStorageScheduleSettings] = None,
                 tab_index: typing.Optional[str] = None
                 ) -> None:
        self.active_tab = active_tab
        self.custom_folder_names = custom_folder_names
        self.first_run_tips = first_run_tips
        self.folders_added = folders_added
        self.has_been_pro = has_been_pro
        self.hidden_devices = hidden_devices
        self.status_panel = status_panel
        self.schedule_settings = schedule_settings
        self.tab_index = tab_index
