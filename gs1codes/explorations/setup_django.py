import timeit
import sys
import os
import django
sys.path.extend([os.path.dirname(os.getcwd())])
django.setup()
from administration.common.constants import StateCodes
from administration.common.functions import Common, Queries
from django.db import connection
import pandas as pd
from administration.models.core import *