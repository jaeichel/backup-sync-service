from marshmallow import Schema, fields, post_load, post_dump, validates_schema, ValidationError

import resilio_model


class BaseSchema(Schema):
    @post_dump
    def remove_none_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }

class AddSyncFolderRequestSchema(BaseSchema):
    path = fields.Str()
    secret = fields.Str()
    selective_sync = fields.Bool(data_key='selectivesync', required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.AddSyncFolderRequest(**data)


class AddSyncFolderResponseSchema(BaseSchema):
    can_encrypt = fields.Bool(data_key='canencrypt')
    encrypted_secret = fields.Str(data_key='encryptedsecret', required=False)
    folder_id = fields.Str(data_key='folderid')
    path = fields.Str()
    read_only_secret = fields.Str(data_key='readonlysecret', required=False)
    secret = fields.Str()
    secret_type = fields.Int(data_key='secrettype')

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.AddSyncFolderResponse(**data)        


class ConnectionInfoSchema(BaseSchema):
    host = fields.Str()
    user = fields.Str(missing=None)
    password = fields.Str(missing=None)
    auth = fields.Str(data_key='auth', missing=None)
    verify_ssl = fields.Bool(data_key='verifySSL', required=False)

    @validates_schema
    def validate_mutually_exclusive_values(self, data, partial, many):
        if (data['user'] is not None or data['password'] is not None) and data['auth'] is not None:
            raise ValidationError({
                'user': ['Specify either a user / password or auth'],
                'password': ['Specify either a user / password or auth'],
                'auth': ['Specify either a user / password or auth']
            })

        if (data['user'] is not None and data['password'] is None) or (data['user'] is None and data['password'] is not None):
            raise ValidationError({
                'user': ['Specify both a user and password'],
                'password': ['Specify both a user and password']
            })

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.ConnectionInfo(**data)


class SyncTypeField(fields.Field):
    def _serialize(self, value: resilio_model.SyncType, attr, obj, **kwargs):
        return value.value

    def _deserialize(self, value: str, attr, data, **kwargs) -> resilio_model.SyncType:
        return resilio_model.SyncType(value)


class FolderSchema(BaseSchema):
    # ignore unmapped fields
    class Meta:
        unknown = None

    can_encrypt = fields.Bool(data_key='canencrypt')
    encrypted_secret = fields.Str(data_key='encryptedsecret', required=False)
    folder_id = fields.Str(data_key='folderid')
    is_owner = fields.Bool(required=False)
    name = fields.Str()
    path = fields.Str(required=False)
    read_only_secret = fields.Str(data_key='readonlysecret', required=False)
    secret = fields.Str()
    secret_type = fields.Int(data_key='secrettype')
    share_id = fields.Str(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.Folder(**data)


class FoldersSchema(BaseSchema):
    folders = fields.List(fields.Nested(FolderSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.Folders(**data)


class IdentitySchema(BaseSchema):
    device_name = fields.Str(data_key='devicename')
    id = fields.Str()
    username = fields.Str()

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.Identity(**data)


class LocalStorageFirstRunTipsSchema(BaseSchema):
    add_folder = fields.Bool(data_key='addFolder')
    new_folder_share = fields.Bool(data_key='newFolderShare')

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.LocalStorageFirstRunTips(**data)


class LocalStorageStatusPanelTabSchema(BaseSchema):
    interval = fields.Int()
    table = fields.Bool(required=False, allow_none=True)

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.LocalStorageStatusPanelTab(**data)


class LocalStorageStatusPanelSchema(BaseSchema):
    active_tab_name = fields.Str(data_key='activeTabName')
    is_toggled = fields.Bool(data_key='isToggled')
    show = fields.Bool(data_key='show')
    tabs = fields.Dict(keys=fields.Str(), values=fields.Nested(LocalStorageStatusPanelTabSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.LocalStorageStatusPanel(**data)


class LocalStorageScheduleSettingsSchema(BaseSchema):
    dlrate = fields.Int(data_key='dlrate')
    is_dl_unlimit = fields.Bool(data_key='isDlUnlimit')
    is_ul_unlimit = fields.Bool(data_key='isUlUnlimit')
    schedule_type = fields.Int(data_key='scheduleType')
    ulrate = fields.Int(data_key='ulrate')
    
    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.LocalStorageScheduleSettings(**data)


class LocalStorageSchema(BaseSchema):
    active_tab = fields.Str(data_key='activeTab')
    custom_folder_names = fields.Dict(data_key='customFolderNames', required=False, keys=fields.Str(), values=fields.Str())
    first_run_tips = fields.Nested(LocalStorageFirstRunTipsSchema, data_key='firstRunTips', required=False)
    folder_share_options = fields.Dict(data_key='folderShareOptions', required=False)
    folders_added = fields.Bool(data_key='foldersAdded', required=False)
    has_been_pro = fields.Bool(data_key='hasBeenPro', required=False)
    hidden_devices = fields.List(fields.Str, data_key='hiddenDevices', required=False)
    status_panel = fields.Nested(LocalStorageStatusPanelSchema, data_key='statusPanel', required=False)
    schedule_settings = fields.Nested(LocalStorageScheduleSettingsSchema, data_key='scheduleSettings', required=False)
    tab_index = fields.Str(data_key='tabIndex', required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return resilio_model.LocalStorage(**data)
