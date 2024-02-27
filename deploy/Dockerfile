version: '3.7'

services:
#   web:
#     restart: unless-stopped
#     build:
#       context: ./backend
#       dockerfile: Dockerfile.prod
#     command: gunicorn oss_ldms.wsgi:application  --workers=17 --timeout=7200 --bind 0.0.0.0:8000
#     volumes:
#       - static_volume:/home/app/web/static
#       - media_volumes:/home/app/web/media
#       - dataset_volumes:/home/app/web/datasets
#       #- ~/oss_ldms_media:/home/app/web/media
#     # ports:
#     #   - 8000:8000
#     expose:
#       - 8000 # port 8000 is only exposed internally, to other Docker services. The port will no longer be published to the host machine.
#     env_file:
#       - ./.env.prod.misland
#       # .env ensures we can use environment variables within docker-compose. Else any other file will not make the variables accessible
#       - .env
#     links:
#       - db
#       - redis
#   migration:
#     restart: unless-stopped
#     build:
#       context: ./backend
#       dockerfile: Dockerfile.prod
#     #command: gunicorn oss_ldms.wsgi:application --timeout=7200 --bind 0.0.0.0:8000
#     command: bash -c "python manage.py migrate && python manage.py rqworker default low high extra_high --with-scheduler"
#     volumes:
#        - static_volume:/home/app/web/static
#        - media_volumes:/home/app/web/media
#        - dataset_volumes:/home/app/web/datasets
#       #- ~/oss_ldms_media:/home/app/web/media
#     # ports:
#     #   - 8000:8000
#     # expose:
#     #   - 8000 # port 8000 is only exposed internally, to other Docker services. The port will no longer be published to the host machine.
#     env_file:
#       - ./.env.prod.misland
#       - .env
#     links:
#       - web
#       - redis
  db:
    restart: unless-stopped
    image: kartoza/postgis:9.6-2.4
    #image: kartoza/postgis:$POSTGRES_MAJOR_VERSION-$POSTGIS_MAJOR_VERSION.${POSTGIS_MINOR_RELEASE}
    volumes:
      #- postgres_data:/var/lib/postgresql/data/
      # kartoza-postgis dockerhub recommends mounting the parent location. This is different from other postgres images
      - postgres_data:/var/lib/postgresql
      - postgres_pgconf:/etc/postgresql
      - postgres_pglog:/var/log/postgresql
    env_file:
      #- ./.env.prod.db
      - ./.env.prod.misland
      # .env ensures we can use environment variables within docker-compose. Else any other file will not make the variables accessible
      - .env
    environment:
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
      - POSTGRES_DBNAME=${POSTGRES_DBNAME}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASS=${POSTGRES_PASS}
      #   - POSTGRES_MAJOR_VERSION=${POSTGRES_MAJOR_VERSION}
      #   - POSTGIS_MAJOR_VERSION=${POSTGIS_MAJOR_VERSION}
      #   - POSTGIS_MINOR_RELEASE=${POSTGIS_MINOR_RELEASE}
#   nginx:
#     restart: unless-stopped
#     build: ./nginx
#     volumes:
#       - static_volume:/home/app/web/static
#       - media_volumes:/home/app/web/media
#       - dataset_volumes:/home/app/web/datasets
#       #- ~/oss_ldms_media:/home/app/web/media
#     ports:
#       - 1337:80
#     depends_on:
#       - web
#   redis:
#     restart: always
#     image: redis:latest
#     ports:
#       - "6380:6379"
#     volumes:
#       - redisdata:/data
  geoserver:
    image: kartoza/geoserver:2.20.1
    restart: always
    ports:
      - "8600:8080"
    environment:
      - GEOSERVER_DATA_DIR=${GEOSERVER_DATA_DIR}
      - GEOWEBCACHE_CACHE_DIR=${GEOWEBCACHE_CACHE_DIR}
      - GEOSERVER_ADMIN_PASSWORD=${GEOSERVER_ADMIN_PASSWORD}
      - GEOSERVER_ADMIN_USER=${GEOSERVER_ADMIN_USER}
      - RESET_ADMIN_CREDENTIALS=${RESET_ADMIN_CREDENTIALS}
      - INITIAL_MEMORY=${INITIAL_MEMORY}
      - MAXIMUM_MEMORY=${MAXIMUM_MEMORY}
    volumes:
      #- geoserver_data:/opt/geoserver/data_dir 
      - geoserver_data:${GEOSERVER_DATA_DIR}
    env_file: 
      - ./.env.prod.misland
      - .env
    links:
      - db
#   dbbackups:
#     image: kartoza/pg-backup:9.6
#     #image: kartoza/pg-backup:$POSTGRES_MAJOR_VERSION
#     volumes:
#       - db-backups:/backups
#     env_file:
#       - ./.env.prod.misland
#       # .env ensures we can use environment variables within docker-compose. Else any other file will not make the variables accessible
#       - .env
#     environment:
#       - PGHOST=${POSTGRES_HOST}
#       - PGUSER=${POSTGRES_USER}
#       - PGPASSWORD=${POSTGRES_PASS}
#       - PGPORT=${POSTGRES_PORT}
#       - PGDATABASE=${POSTGRES_DBNAME}
#       - DUMPPREFIX=${DUMPPREFIX}
#       - CRON_SCHEDULE=${CRON_SCHEDULE}
#       - REMOVE_BEFORE=${REMOVE_BEFORE}
#     #   - POSTGRES_MAJOR_VERSION=${POSTGRES_MAJOR_VERSION}
#     #   - POSTGIS_MAJOR_VERSION=${POSTGIS_MAJOR_VERSION}
#     #   - POSTGIS_MINOR_RELEASE=${POSTGIS_MINOR_RELEASE}
#     #   - DUMPPREFIX=PG_gis
#     #   - POSTGRES_HOST=db
#     #   - POSTGRES_USER=docker
#     #   - POSTGRES_PASS=docker
#     #   - POSTGRES_PORT=5432
#     #  #- CRON_SCHEDULE="*/1 * * * *"
#     restart: on-failure
#     depends_on:
#       - db
#       # db:
#       #   condition: service_healthy
volumes:
  postgres_data:
  postgres_pgconf:
  postgres_pglog:
#   static_volume:
#   media_volumes:
#     driver: local
#     driver_opts:
#       type: 'none'
#       o: 'bind'
#       device: '/home/ubuntu/oss_ldms_media'
#   dataset_volumes:
#     driver: local
#     driver_opts:
#       type: 'none'
#       o: 'bind'
#       device: '/home/ubuntu/datasets'
#   redisdata:
  geoserver_data:
#   db-backups: