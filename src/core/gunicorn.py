import multiprocessing
from logging import Formatter
from typing import Any, Dict, Mapping, Callable

from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger

from core.config import settings


# =========================
# Custom Gunicorn Logger
# =========================
class GunicornLogger(Logger):
    """
    Custom Gunicorn logger with unified log format
    for access and error logs.
    """

    def setup(self, cfg) -> None:
        super().setup(cfg)

        formatter = Formatter(
            fmt=settings.logging.fmt,
            datefmt=settings.logging.date_fmt,
        )

        self._set_handler(  # type: ignore
            log=self.access_log,
            output=cfg.accesslog,
            fmt=formatter,
        )
        self._set_handler(  # type: ignore
            log=self.error_log,
            output=cfg.errorlog,
            fmt=formatter,
        )


# =========================
# Gunicorn options builder
# =========================
def get_app_options(
    host: str,
    port: int,
    timeout: int,
    workers: int | None,
    log_level: str,
) -> Dict[str, Any]:
    """
    Build gunicorn configuration with sane defaults.
    """

    cpu_workers = multiprocessing.cpu_count() * 2 + 1

    return {
        # networking
        "bind": f"{host}:{port}",
        # workers
        "workers": workers or cpu_workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "preload_app": False,
        # timeouts
        "timeout": timeout,
        "graceful_timeout": timeout + 10,
        "keepalive": 5,
        # logging
        "loglevel": log_level,
        "logger_class": GunicornLogger,
        "accesslog": "-" if settings.logging.access else None,
        "errorlog": "-",
        # security / stability
        "max_requests": 1000,
        "max_requests_jitter": 50,
    }


# =========================
# Gunicorn Application
# =========================
class Application(BaseApplication):
    """
    Programmatic Gunicorn application.
    """

    def __init__(
        self,
        application: Callable,
        options: Mapping[str, Any] | None = None,
    ):
        self.application = application
        self.options = options or {}
        super().__init__()

    def load(self) -> Callable:
        return self.application

    def load_config(self) -> None:
        """
        Apply only valid gunicorn settings.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)
