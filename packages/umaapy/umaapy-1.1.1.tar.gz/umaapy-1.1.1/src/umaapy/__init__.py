import os, logging, sys
import importlib.resources

from umaapy.util.dds_configurator import DDSConfigurator
from umaapy.util.event_processor import EventProcessor


def setup_logging(level="INFO", log_file=None):
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(root.level)
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(ch)

    # Optional file handler
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(root.level)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(fh)


setup_logging(level=os.getenv("UMAAPY_LOG_LEVEL", "INFO"))

DOMAIN_ID = int(os.getenv("DOMAIN_ID", "0"))
QOS_FILE = ""

with importlib.resources.path("umaapy.resource", "umaapy_qos_lib.xml") as module_qos_path:
    QOS_FILE = os.getenv("QOS_FILE", str(module_qos_path))


def get_configurator() -> DDSConfigurator:
    return DDSConfigurator(DOMAIN_ID, QOS_FILE)


def get_event_processor() -> EventProcessor:
    return EventProcessor()


def reset_dds_participant():
    DDSConfigurator.reset()
    get_configurator()


def reset_thread_pool():
    EventProcessor.reset()
    get_event_processor()


get_configurator()
get_event_processor()
