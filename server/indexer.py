import glob
import os
import threading
from multiprocessing import get_context
from threading import Thread
import logging

from tqdm import tqdm

from config import Config
from data_encoder import MODEL_DIM, encoder
from proximus_client import proximus_admin_client, proximus_client
from aerospike_vector import types_pb2

lock = threading.Lock()
extensions = [".md", ".mdx"]
doc_datasets_glob = "../documents/**/*"
doc_datasets_folder = "../documents"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_index():
    logger.info("Creating index")
    #for index in proximus_admin_client.indexList():
    #    if (
    #        index.id.namespace == Config.PROXIMUS_NAMESPACE
    #        and index.id.name == Config.PROXIMUS_INDEX_NAME
    #    ):
    #        logger.info("Index already exists")
    #        return
    #proximus_admin_client.indexDrop(namespace=Config.PROXIMUS_NAMESPACE, name=Config.PROXIMUS_INDEX_NAME)

    proximus_admin_client.indexCreate(
        namespace=Config.PROXIMUS_NAMESPACE,
        name=Config.PROXIMUS_INDEX_NAME,
        setFilter=Config.PROXIMUS_SET,
        vector_bin_name="doc_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types_pb2.VectorDistanceMetric.COSINE,
    )


def either(c):
    return "[%s%s]" % (c.lower(), c.upper()) if c.isalpha() else c


def index_data():
    lock.acquire()
    try:
        create_index()
        filenames = doc_data_files()

        to_index = []
        for filename in tqdm(filenames, "Checking for new files", total=len(filenames)):
            # Check if record exists
            try:
                if proximus_client.isIndexed(
                    Config.PROXIMUS_NAMESPACE,
                    Config.PROXIMUS_SET,
                    filename,
                    Config.PROXIMUS_INDEX_NAME,
                ):
                    # Record exists
                    continue
            except:
                pass
            to_index.append(filename)
        if len(to_index) > 0:
            logger.info("Found new files to index")
            if Config.INDEXER_PARALLELISM <= 1:
                for filename in tqdm(
                    to_index, "Indexing new files", total=len(to_index)
                ):
                    index_doc(filename)
            else:
                with get_context("spawn").Pool(
                    processes=Config.INDEXER_PARALLELISM
                ) as pool:
                    for _ in tqdm(
                        pool.imap(index_doc, to_index),
                        "Indexing new files",
                        total=len(to_index),
                    ):
                        pass

    except Exception as e:
        logger.warning("Error indexing:" + str(e))
        import traceback

        traceback.print_exc()

    lock.release()

    # Repeat indexing.
    threading.Timer(30, index_data).start()


def doc_data_files():
    filenames = sum(
        [
            glob.glob(
                "".join(either(char) for char in (doc_datasets_glob + x)),
                recursive=True,
            )
            for x in extensions
        ],
        [],
    )
    return filenames


def index_doc(filename):
    doc = {"doc_name": os.path.basename(filename)}
    logger.debug(f"Opening file {filename}")
    with open(filename, 'r') as file:
        data = file.read()
    logger.debug(f"Creating doc vector embedding {filename}")
    embedding = encoder(data)
    doc["doc_text"] = data
    doc["doc_embedding"] = embedding.tolist()
    # Insert record
    try:
        logger.debug(f"Inserting vector embedding into proximus {filename}")
        proximus_client.put(
            Config.PROXIMUS_NAMESPACE, Config.PROXIMUS_SET, doc["doc_name"], doc
        )
    except:
        print("failed")
        # Retry again
        pass


def relative_path(filename):
    return os.path.relpath(filename).split(doc_datasets_folder)[1]


def create_image_id(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def start():
    # Start indexing in a separate thread
    thread = Thread(target=index_data)
    thread.start()
