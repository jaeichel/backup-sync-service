FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /config

CMD [ "python", "./backup_sync_service.py", "/config/config.json"]