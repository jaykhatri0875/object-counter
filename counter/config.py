import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, GetPredictionObjects

def dev_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'dev_counter')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))


def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'),
                                CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db))

# get prediction with out db logger, TODO
def dev_get_predictions():
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    # mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    # mongo_port = os.environ.get('MONGO_PORT', 27017)
    # mongo_db = os.environ.get('MONGO_DB', 'dev_counter')
    # FakeObjectDetector()
    return GetPredictionObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'))
def prod_get_predictions():
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    # mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    # mongo_port = os.environ.get('MONGO_PORT', 27017)
    # mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return GetPredictionObjects(TFSObjectDetector(tfs_host, tfs_port, 'rfcn'))

def get_predictions_action() -> GetPredictionObjects:
    env = os.environ.get('ENV', 'dev')
    get_predictions_fn = f"{env}_get_predictions"
    return globals()[get_predictions_fn]()

def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()
