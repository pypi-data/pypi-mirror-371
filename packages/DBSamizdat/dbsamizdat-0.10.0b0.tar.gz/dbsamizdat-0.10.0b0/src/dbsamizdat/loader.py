from logging import getLogger
from importlib import import_module
import inspect
from itertools import chain
import sys

from .samizdat import SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger, SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta
from .const import env

logger = getLogger(__name__)

AUTOLOAD_MODULENAME = "dbsamizdat_defs"

def module_not_found_help(modulename, exception, pypath):
    withsearchpath = f'''using Python import search path "{pypath}" ''' if pypath is not None else ''
    return f'''
Fatal: Loading module "{modulename}" {withsearchpath}failed with error:

=====================================================================
{exception}
=====================================================================

If you're unsure on how to solve this, try one of the following suggestions:
a.  Invoke dbsamizdat while you are inside a directory from which your module is importable.
    Thus `python -m {modulename}` should work from there, too.
b.  Set the PYTHONPATH environment variable to the directory from which your module is importable.
    Thus `PYTHONPATH="/path/to/some/project` python -m {modulename}` should work, too.
c.  If the error points to problems importing third-party modules, and you're using these
    third-party packages from a virtual environment, it'd be best to simply install dbsamizdat
    inside that virtual environment, too, and invoke your virtualenv's version of dbsamizdat.
    If that's not possible try using the PYTHONPATH environment variable to make those modules
    importable. You can see which paths you might want to add by loading your virtualenv and
    executing `python -c 'import sys; print("\\n".join(filter(None, sys.path)))'` .

    Documentation on the PYTHONPATH environment variable can be found here:
    https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH
'''


def get_samizdats(modulelist=tuple(), context=0):

    def issamizdat(thing):
        excluded_classes = {SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger}
        return inspect.isclass(thing) and isinstance(thing, (SamizdatMeta, SamizdatFunctionMeta, SamizdatTriggerMeta)) and (thing not in excluded_classes)

    sdmodules = []
    if not (context & env.DJANGO):
        for (pypath, modulename) in modulelist:
            try:
                if pypath is None:
                    sdmodules.append(import_module(modulename))
                else:
                    sys.path.insert(0, str(pypath))
                    sdmodules.append(import_module(modulename))
                    sys.path.pop(0)
            except ModuleNotFoundError as notfounderror:
                if (context & env.CLI):
                    exit(module_not_found_help(modulename, notfounderror, pypath))
                else:
                    raise
    else:
        # if we're running in Django, we will autoload definitions from:
        # - the modules named in settings.DBSAMIZDAT_MODULES
        # - the module with name AUTOLOAD_MODULENAME of each app
        try:
            from django.core.exceptions import ImproperlyConfigured
            from django.conf import settings
            from django.apps import apps
        except ImportError as e:
            exit(f"Loading Django modules failed:\n{e}")
        else:
            try:
                django_sdmodules = [import_module(sdmod) for sdmod in getattr(settings, 'DBSAMIZDAT_MODULES', [])]
                for appconfig in apps.get_app_configs():
                    try:
                        django_sdmodules.append(import_module('{}.{}'.format(appconfig.module.__package__, AUTOLOAD_MODULENAME)))
                    except ModuleNotFoundError as err:
                        if not err.msg.endswith(f"{AUTOLOAD_MODULENAME}'"):
                            raise err
                if not django_sdmodules:
                    logger.warn(f"""No settings.DBSAMIZDAT_MODULES defined, and none of your apps contain any "{AUTOLOAD_MODULENAME}" module to autoload.""")
                sdmodules += django_sdmodules
            except ImproperlyConfigured:
                # assume we're not running in a fully booted Django
                pass

    return {c for cname, c in chain.from_iterable(map(lambda m: inspect.getmembers(m, issamizdat), sdmodules))}
