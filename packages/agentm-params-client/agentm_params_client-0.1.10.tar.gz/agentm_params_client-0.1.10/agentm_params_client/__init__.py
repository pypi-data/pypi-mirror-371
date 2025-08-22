try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version('agentm-params-client')
except Exception:
    __version__ = '0'
from .client import ParamsClient
from .refresh import ParamsRefresher
__all__ = ['ParamsClient','ParamsRefresher','__version__']
