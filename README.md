### Install
pip install marshmallow

### Run
python backup_sync_service.py config.json

### Next steps for better security
- Currently one centralized sytem connects to all units and distributes keys to backup clients
- Ideally, each client would create a seperate and secure interface for each destination backup client
  - server A
    - sync service
    - source sync service api
      - (optional) account for dest sync service A - empty?
      - account for dest sync service B
      - account for dest sync service C
      - account for dest sync service D
