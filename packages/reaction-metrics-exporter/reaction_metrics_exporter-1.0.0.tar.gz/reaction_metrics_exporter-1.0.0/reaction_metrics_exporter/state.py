import asyncio
from datetime import datetime, timedelta
import os
import pickle
import signal
import sys

import structlog

from .models.config import Config
from .models.metric import ReactionMetrics

logger = structlog.get_logger()
config = Config.get_config()


class StateMeta(type):
    # as long as dates are localized, comparison works even
    # when tz are different, e.g. Docker and host
    _last_log: datetime = datetime.now().astimezone()
    _last_export: datetime = datetime.now().astimezone()
    _wait_until: datetime = datetime.now().astimezone()

    # meant to be short-lived and keep unexported metrics across restarts
    _metrics = ReactionMetrics()

    # don't recall matches-related metrics beyond 15 minutes
    _limit = 15
    _start: datetime = datetime.now().astimezone()

    @property
    def last_log(cls) -> datetime:
        return cls._last_log

    @last_log.setter
    def last_log(cls, value: datetime):
        cls._last_log = value

    @property
    def last_export(cls) -> datetime:
        return cls._last_export

    @last_export.setter
    def last_export(cls, value: datetime):
        cls._last_export = value

    @property
    def wait_until(cls) -> datetime:
        return cls._wait_until

    @wait_until.setter
    def wait_until(cls, value: datetime):
        cls._wait_until = value

    @property
    def metrics(cls) -> ReactionMetrics:
        return cls._metrics

    @metrics.setter
    def metrics(cls, value: ReactionMetrics):
        cls._metrics = value


class State(metaclass=StateMeta):
    """singleton-ish to manage app's state."""

    # which signals means terminate for us
    _SIGNALS = ["SIGINT", "SIGTERM"]
    _inst = None

    @classmethod
    def init(cls):
        cls._state_file = f"{config.restore_dir}/state.pickle"
        cls._metrics_file = f"{config.restore_dir}/metrics.pickle"

        cls._load_state()
        cls._load_metrics()

        for sig in cls._SIGNALS:
            asyncio.get_running_loop().add_signal_handler(getattr(signal, sig), lambda sig=sig: cls._quit(sig))
        logger.debug(f"installed handlers for signals {cls._SIGNALS}")

    @classmethod
    def _load_state(cls):
        if not os.path.isfile(cls._state_file):
            return
        try:
            with open(cls._state_file, "rb") as f:
                state = pickle.load(f)
                last_log = datetime.fromtimestamp(state["last_log"]).astimezone()
                wait_until = datetime.fromtimestamp(state["wait_until"]).astimezone()
                last_export = datetime.fromtimestamp(state["last_export"]).astimezone()
                logger.debug(f"loaded state {state} from {cls._state_file}")
                if cls._recall(last_log):
                    cls.last_log = last_log
                else:
                    logger.info(f"ignoring last log date older than {cls._limit} minutes")
                cls.wait_until = wait_until
                cls.last_export = last_export
        except (pickle.PickleError, EOFError):
            logger.warning("cannot load previous state; reset")

    @classmethod
    def _load_metrics(cls):
        if not os.path.isfile(cls._metrics_file):
            return
        try:
            with open(cls._metrics_file, "rb") as f:
                cls.metrics: ReactionMetrics = pickle.load(f)
                logger.debug(f"loaded {cls.metrics.n_metrics} metrics from previous session")
                if not cls._recall(cls.last_export):
                    logger.info(f"discarding loaded matches and actions as they are older than 15 minutes")
                    cls.metrics.matches.clear()
                    cls.metrics.actions.clear()
        except (pickle.PickleError, EOFError):
            logger.warning("cannot load previous metrics; reset")

    @classmethod
    def _save_state(cls):
        with open(cls._state_file, mode="wb") as f:
            state = {"last_log": cls.last_log.timestamp(), "wait_until": cls.wait_until.timestamp(), "last_export": cls.last_export.timestamp()}
            pickle.dump(state, f)
            logger.debug(f"saved state {state} into {cls._state_file}")

    @classmethod
    def _save_metrics(cls):
        with open(cls._metrics_file, "wb") as f:
            pickle.dump(cls.metrics, f)
            logger.debug(f"saved {cls.metrics.n_metrics} unexported metrics")

    @classmethod
    def _quit(cls, sig: str):
        try:
            logger.info(f"signal {sig} catched, save state before exiting")
            cls._save_state()
            cls._save_metrics()
            logger.info("exiting.")
        except Exception as e:
            # catch anything so process can exit
            logger.exception(e)
        finally:
            sys.exit(0)

    @classmethod
    def _recall(cls, start: datetime) -> bool:
        return cls._start - timedelta(minutes=cls._limit) < start
