from datetime import datetime
from html.parser import HTMLParser
import json
import typing
import requests
import urllib

from marshmallow import Schema, fields, post_load

import resilio_model
import resilio_schema


class ResilioSyncAPITokenParser(HTMLParser):
    def __init__(self):
        self.token = None
        HTMLParser.__init__(self)

    def handle_data(self, data):
        self.token = data


class ResilioSyncAPI:
    def __init__(self, *, connection_info: resilio_model.ConnectionInfo):
        self.host = connection_info.host
        self.auth = connection_info.auth
        
        self.session = None
        self.token = None
        self.verify_ssl = connection_info.verify_ssl

        self.init_session()
        self.refresh_token()

    def init_session(self):
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Safari/537.36',
        }

    def refresh_token(self):
        url = f'{self.host}/gui/token.html?t={ResilioSyncAPI._get_time_ms()}'
        resp = self.session.get(url, headers=self.headers, verify=self.verify_ssl)
        resp.raise_for_status()

        parser = ResilioSyncAPITokenParser()
        parser.feed(resp.text)
        self.token = parser.token

    def get_version(self):
        return self._get_basic_action('version')

    def get_user_language(self):
        return self._get_basic_action('userlang')

    def get_user_identity(self) -> resilio_model.Identity:
        return resilio_schema.IdentitySchema().load(self._get_basic_action('useridentity'))
    
    def get_settings(self):
        return self._get_basic_action('settings')
    
    def get_proxy_settings(self):
        return self._get_basic_action('proxysettings')

    def get_pause(self):
        return self._get_basic_action('pause')

    def get_md_local_storage(self):
        # returns str instead of json
        return json.loads(self._get_basic_action('mdlocalstorage'))

    def get_local_storage(self) -> resilio_model.LocalStorage:
        # returns str instead of json
        return resilio_schema.LocalStorageSchema().load(json.loads(self._get_basic_action('localstorage')))

    def get_license_agreed(self):
        return self._get_basic_action('licenseagreed')

    def get_license_info(self):
        return self._get_basic_action('getlicenseinfo')

    def get_history(self, *, start=0, length=1000, order=1):
        return self._get_basic_action('history', params={ 'start': start, 'length': length, 'order': order })

    def get_system_info(self):
        return self._get_basic_action('getsysteminfo')

    def get_sync_jobs(self):
        return self._get_basic_action('getsyncjobs')

    def get_sync_folders(self, *, discovery: int = 1) -> typing.Sequence[resilio_model.Folder]:
        return resilio_schema.FoldersSchema().load(self._get_basic_action('getsyncfolders', params={ 'discovery': discovery })).folders

    def get_statuses(self):
        return self._get_basic_action('getstatuses')

    def get_scheduler(self):
        return self._get_basic_action('getscheduler')

    def get_pending_requests(self):
        return self._get_basic_action('getpendingrequests')

    def get_notifications(self):
        return self._get_basic_action('getnotifications')

    def get_mf_devices(self):
        return self._get_basic_action('getmfdevices')

    def get_master_folder(self):
        return self._get_basic_action('getmasterfolder')

    def get_folders_storage_path(self):
        return self._get_basic_action('getfoldersstoragepath')
    
    def get_folder_settings(self):
        return self._get_basic_action('getfoldersettings')

    def get_app_info(self):
        return self._get_basic_action('getappinfo')

    def get_folder_preferences(self, id):
        return self._get_basic_action('folderpref', params={'id': id})

    def get_file_job_path(self):
        return self._get_basic_action('filejobpath')

    def get_debug_mode(self):
        return self._get_basic_action('debugmode')

    def get_credentials(self):
        return self._get_basic_action('credentials')

    def get_check_new_version(self):
        return self._get_basic_action('checknewversion')

    def get_advanced_settings(self):
        return self._get_basic_action('advancedsettings')

    def add_sync_folder(self, *,
                        path: str,
                        secret: str,
                        selective_sync: typing.Optional[bool] = False) -> resilio_model.AddSyncFolderResponse:
        request = resilio_model.AddSyncFolderRequest(path=path, secret=secret, selective_sync=selective_sync)
        params = resilio_schema.AddSyncFolderRequestSchema().dump(request)
        return resilio_schema.AddSyncFolderResponseSchema().load(self._get_basic_action('addsyncfolder', params=params))

    def set_local_storage(self, storage: resilio_model.LocalStorage):
        json_data = resilio_schema.LocalStorageSchema().dump(storage)
        return self._get_basic_action('setlocalstorage', params={ 'value': json.dumps(json_data) })

    def _get_basic_action(self, action: str, params: typing.Dict[str, typing.Any] = {}) -> typing.Dict[str, typing.Any]:
        url = f'{self.host}/gui/?token={self.token}&action={action}&t={ResilioSyncAPI._get_time_ms()}'
        for key in params:
            url += f'&{key}={urllib.parse.quote(str(params[key]), safe="")}'
        resp = self.session.get(url, headers=self.headers, verify=self.verify_ssl)
        resp.raise_for_status()
        data = resp.json()
        if 'status' in data:
            if data['status'] != 200:
                raise RuntimeExpection(resp.text)
            del data['status']
        if 'value' in data:
            return data['value']
        return data

    @staticmethod
    def _get_time_ms():
        return round(datetime.now().timestamp() * 1000)


if __name__ == '__main__':
    with open('secrets/test_connection_info.json', 'r') as connection_info_fs:
        connection_info_json = json.load(connection_info_fs)
        connection_info = resilio_schema.ConnectionInfoSchema().load(connection_info_json)
        api = ResilioSyncAPI(connection_info=connection_info)

    print(api.get_version())
    print(api.get_user_language())
    print(api.get_user_identity())
    print(api.get_settings())
    print(api.get_proxy_settings())
    print(api.get_pause())
    print(api.get_md_local_storage())
    print(api.get_local_storage())
    print(api.get_license_agreed())
    print(api.get_license_info())
    print(api.get_history(length=2))
    print(api.get_system_info())
    print(api.get_sync_jobs())
    print(api.get_sync_folders())
    print(api.get_statuses())
    print(api.get_scheduler())
    print(api.get_pending_requests())
    print(api.get_notifications())
    print(api.get_mf_devices())
    print(api.get_master_folder())
    print(api.get_folders_storage_path())
    print(api.get_folder_settings())
    print(api.get_app_info())
    print(api.get_check_new_version())

    folders = api.get_sync_folders()
    if len(folders['folders']) > 0:
        print(api.get_folder_preferences(folders['folders'][0]['id']))

    print(api.get_file_job_path())
    print(api.get_debug_mode())
    print(api.get_credentials())
    print(api.get_check_new_version())
    print(api.get_advanced_settings())
