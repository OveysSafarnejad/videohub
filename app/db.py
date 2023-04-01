import pathlib

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection

from . import config


BASE_URL = pathlib.Path(__file__).resolve().parent
CONNECT_BUNDLE = BASE_URL / "unencrypted/astradb_connect.zip"

settings = config.get_settings()

DB_CLIENT_ID = settings.db_client_id
DB_CLIENT_SECRET = settings.db_client_secret


def get_session():
    cloud_config= {
        'secure_connect_bundle': CONNECT_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(DB_CLIENT_ID, DB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))

    return session