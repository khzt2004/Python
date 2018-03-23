# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 14:22:57 2018

@author: User
"""

# Import pandas module as 'pd'
%matplotlib inline
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
import xlrd
from pandasql import sqldf
from pandas import ExcelWriter
from numbers import Number
import os
os.getcwd()


# Create a dataframe
# specify file path for windows users: target_file = r'C:\Users\k6o\aseanoutput.xlsx'
target_file1 = r'C:\Users\User\Documents\airnz_test.csv'
xls_file1 = pd.read_csv(target_file1)
xls_file1.columns.values

['users', 'sessions', 'Booking_value', 'Research_value',
       'Post_Booking_vManage_value', 'Post_Booking_Other_value',
       'DoT_value', 'Ancillary_value', 'NULL_stage_value', 'flightSearch',
       'flightBooking', 'productRevenue', 'Booking_Lead_Days',
       'market_longhaul', 'market_domestic', 'market_tasman',
       'market_pacific', 'market_null', 'membership_elitegold',
       'membership_gold', 'membership_silver', 'membership_jade',
       'membership_null']
xls_file2 = xls_file1.pivot(index = 'Booking_value', 'Research_value',
       'Post_Booking_vManage_value', 'Post_Booking_Other_value',
       'DoT_value', 'Ancillary_value', 'NULL_stage_value', 'flightSearch',
       'flightBooking', 'productRevenue', 'Booking_Lead_Days',
       'market_longhaul', 'market_domestic', 'market_tasman',
       'market_pacific', 'market_null', 'membership_elitegold',
       'membership_gold', 'membership_silver', 'membership_jade',
       'membership_null', columns = )
xls_file3 = pd.pivot_table(xls_file2, values='D', index=['A', 'B'], columns=['C'])