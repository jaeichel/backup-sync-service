from enum import Enum
import typing

import resilio_model


class SyncType(Enum):
    READ_WRITE = 1,
    READ_ONLY = 2,
    ENCRYPTED = 3,
    EXCLUDE = 4


class BackupSourceFolder:
    def __init__(self, *, custom_name: typing.Optional[str] = None, sync_type: typing.Optional[SyncType] = None):
        self.custom_name = custom_name
        self.sync_type = sync_type


class BackupSource():
    def __init__(self,
                 *,
                 connection_info: resilio_model.ConnectionInfo,
                 folders: typing.Dict[str, BackupSourceFolder] = {},
                 sync_type: SyncType,
                 root_dest_folder: str):
        self.connection_info = connection_info
        self.folders = folders
        self.sync_type = sync_type
        self.root_dest_folder = root_dest_folder


class BackupDestination():
    def __init__(self, *, connection_info: resilio_model.ConnectionInfo):
        self.connection_info = connection_info


class DestinationServiceConfig():
    def __init__(self, *, destination: BackupDestination, sources: typing.Sequence[BackupSource]):
        self.destination = destination
        self.sources = sources


class BackupSyncConfig():
    def __init__(self, *, services: DestinationServiceConfig):
        self.services = services
