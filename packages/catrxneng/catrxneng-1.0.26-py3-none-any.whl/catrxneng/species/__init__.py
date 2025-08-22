from .co import CO
from .h2o import H2O
from .co2 import CO2
from .h2 import H2
from .c2h4 import C2H4
from .ch4 import CH4
from .n2 import N2
from .nh3 import NH3
from .ar import Ar
from .inert import Inert

# Build a case-insensitive mapping of class names to class objects for only those imported here
import inspect

CLASS_MAP = {}
for name, obj in list(locals().items()):
    if inspect.isclass(obj):
        CLASS_MAP[name.lower()] = obj
