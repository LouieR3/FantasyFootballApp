from credentials import CRED
import pandas as pd
from espn_api.football import League
import pandas as pd
import time
from tabulate import tabulate
from operator import itemgetter
# import xlsxwriter
from itertools import combinations
import itertools
import math
import numpy as np
import random

start_time = time.time()
espn_s2=CRED["louie_s2_pages"]
swid=CRED["louie_swid"]
league = League(league_id=1118513122, year=2024, espn_s2=espn_s2, swid=swid)
print(league)