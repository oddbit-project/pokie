from rick_db import fieldmapper


@fieldmapper(tablename='settings', pk='id_settings')
class SettingsRecord:
    id = 'id_settings'
    module = 'module'
    key = 'key'
    value = 'value'
