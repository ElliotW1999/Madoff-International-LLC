import os
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import datetime as datetime
from pathlib import Path
# for deleting, moving data

db_file = "binanceData.db"
conn = None
try:
    conn = sqlite3.connect(db_file)
except Error as e:
    print(e)
cur = conn.cursor()

BBO = """Delete from bids where date like '12%'"""
cur.execute(BBO)
conn.commit()

BBO = """Delete from asks where date like '12%'"""
cur.execute(BBO)
conn.commit()

BBO = """Delete from trades where date like '12%'"""
cur.execute(BBO)
conn.commit()