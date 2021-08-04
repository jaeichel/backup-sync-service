from marshmallow import Schema, fields, post_load

import backup_sync_model
import resilio_schema


class SyncTypeField(fields.Field):
    def _serialize(self, value: backup_sync_model.SyncType, attr, obj, **kwargs):
        return value.name

    def _deserialize(self, value: str, attr, data, **kwargs) -> backup_sync_model.SyncType:
        return backup_sync_model.SyncType[value]


class BackupSourceFolderSchema(Schema):
    custom_name = fields.Str(data_key='customName', required=False)
    sync_type = SyncTypeField(data_key='syncType', required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return backup_sync_model.BackupSourceFolder(**data)


class BackupSourceSchema(Schema):
    connection_info = fields.Nested(resilio_schema.ConnectionInfoSchema, data_key='connectionInfo')
    sync_type = SyncTypeField(data_key='syncType')
    root_dest_folder = fields.Str(data_key='rootDestFolder')
    folders = fields.Dict(keys=fields.Str(), values=fields.Nested(BackupSourceFolderSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return backup_sync_model.BackupSource(**data)


class BackupDestinationSchema(Schema):
    connection_info = fields.Nested(resilio_schema.ConnectionInfoSchema, data_key='connectionInfo')
    sources = fields.List(fields.Nested(BackupSourceSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return backup_sync_model.BackupDestination(**data)        


class DestinationServiceConfigSchema(Schema):
    destination = fields.Nested(BackupDestinationSchema)
    sources = fields.List(fields.Nested(BackupSourceSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return backup_sync_model.DestinationServiceConfig(**data)


class BackupSyncConfigSchema(Schema):
    services = fields.List(fields.Nested(DestinationServiceConfigSchema))

    @post_load
    def make_object(self, data, **kwargs):
        return backup_sync_model.BackupSyncConfig(**data)
