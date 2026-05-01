"""Data fetcher: wraps akshare for A-share data acquisition.

Uses Tencent (tx) API as primary source — more stable than Eastmoney (em).
"""

import datetime

import akshare as ak
import pandas as pd

from app.database import SessionLocal
from ...[truncated]