import os


class Config(object):
    BASIC_AUTH_USERNAME = os.environ.get("APP_USERNAME") or ""
    BASIC_AUTH_PASSWORD = os.environ.get("APP_PASSWORD") or ""
    INDEXER_PARALLELISM = int(os.environ.get("APP_INDEXER_PARALLELISM") or 1)
    PROXIMUS_HOST = os.environ.get("PROXIMUS_HOST") or "localhost"
    PROXIMUS_PORT = int(os.environ.get("PROXIMUS_PORT") or 5002)
    PROXIMUS_ADVERTISED_LISTENER = (
        os.environ.get("PROXIMUS_ADVERTISED_LISTENER") or None
    )
    PROXIMUS_INDEX_NAME = os.environ.get("PROXIMUS_INDEX_NAME") or "doc-search"
    PROXIMUS_NAMESPACE = os.environ.get("PROXIMUS_NAMESPACE") or "vector-demo"
    PROXIMUS_SET = os.environ.get("PROXIMUS_SET") or "doc-data"
    PROXIMUS_VERIFY_TLS = os.environ.get("VERIFY_TLS") or True
    PROXIMUS_MAX_RESULTS = int(os.environ.get("PROXIMUS_MAX_RESULTS") or 20)
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH") or 10485760)
