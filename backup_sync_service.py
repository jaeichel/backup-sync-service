import argparse
from enum import Enum
import json
import os
import signal
import time

from marshmallow import Schema, fields, post_load

import backup_sync_model
import backup_sync_schema
import resilio_api


class BackupDestinationService:
    def __init__(self, *, config: backup_sync_model.DestinationServiceConfig) -> None:
        self.config = config

        self.destination_api = resilio_api.ResilioSyncAPI(connection_info=config.destination.connection_info)
        self.source_apis = [resilio_api.ResilioSyncAPI(connection_info=source.connection_info) for source in config.sources]

    def update_sources(self) -> None:
        for source_config, source_api in zip(self.config.sources, self.source_apis):
            self.update_source(source_config, source_api)
    
    def update_source(self, source_config: backup_sync_model.BackupSource, source_api: resilio_api.ResilioSyncAPI) -> None:
        dest_folder_secrets_to_ids = BackupDestinationService._map_folder_secrets_to_folder_ids(self.destination_api)

        dest_local_storage = self.destination_api.get_local_storage()
        dest_local_storage_change = False

        source_username = source_api.get_user_identity().username
        source_folders = source_api.get_sync_folders()
        for folder in source_folders:
            if folder.is_owner:
                sync_type = source_config.sync_type
                if folder.name in source_config.folders and source_config.folders[folder.name].sync_type:
                    sync_type = source_config.folders[folder.name].sync_type

                
                if sync_type == backup_sync_model.SyncType.READ_WRITE:
                    path = os.path.join(source_config.root_dest_folder, folder.name if folder.name != 'encrypted' else f'{folder.name}_')
                    secret = folder.read_write_secret
                elif sync_type == backup_sync_model.SyncType.READ_ONLY:
                    path = os.path.join(source_config.root_dest_folder, folder.name if folder.name != 'encrypted' else f'{folder.name}_')
                    secret = folder.read_only_secret
                elif sync_type == backup_sync_model.SyncType.ENCRYPTED:
                    path = os.path.join(source_config.root_dest_folder, 'encrypted', folder.name)
                    secret = folder.encrypted_secret
                elif sync_type == backup_sync_model.SyncType.EXCLUDE:
                    secret = None
                else:
                    print('Error', 'desired secret not available', folder)
                    secret = None

                if secret is not None:
                    new_folder_name = f'{source_username} - {folder.name}'
                    if folder.name in source_config.folders and source_config.folders[folder.name].custom_name:
                        new_folder_name = f'{source_username} - {source_config.folders[folder.name].custom_name}'

                    if secret not in dest_folder_secrets_to_ids:
                        try:
                            resp = self.destination_api.add_sync_folder(path=path, secret=secret)
                            print('Success', new_folder_name, resp.folder_id)
                            dest_folder_secrets_to_ids[secret] = resp.folder_id
                        except Exception as e:
                            print('Error', new_folder_name, secret[0:4])
                            print(e)

                    if secret in dest_folder_secrets_to_ids and (
                            dest_folder_secrets_to_ids[secret] not in dest_local_storage.custom_folder_names or
                            dest_local_storage.custom_folder_names[dest_folder_secrets_to_ids[secret]] != new_folder_name
                        ):
                        dest_local_storage.custom_folder_names[dest_folder_secrets_to_ids[secret]] = new_folder_name
                        dest_local_storage_change = True

        self.destination_api.set_local_storage(dest_local_storage)

    @staticmethod
    def _map_folder_secrets_to_folder_ids(api_client: resilio_api.ResilioSyncAPI):
        folders = api_client.get_sync_folders()
        folder_map = {}
        for folder in folders:
            folder_map[folder.secret] = folder.folder_id
        return folder_map


class BackupSyncService:
    def __init__(self, *, config: backup_sync_model.BackupSyncConfig) -> None:
        self.config = config
        self.services = [BackupDestinationService(config=service_config) for service_config in config.services]

    def update_destinations(self) -> None:
        for service in self.services:
            try:
                service.update_sources()
                print(f'updated {service.config.destination.connection_info.host}')
            except Exception as e:
                print(e)


def signal_handler(signal, frame):
    print('\nterminating...')
    exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync folders from one user to another')
    parser.add_argument('config', type=str)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    with open(args.config, 'r') as f:
        config = backup_sync_schema.BackupSyncConfigSchema().load(json.load(f))
        while True:
            service = BackupSyncService(config=config)
            service.update_destinations()
            time.sleep(30)
