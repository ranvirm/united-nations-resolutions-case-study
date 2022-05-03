import pandas as pd
import sqlite3

# db connect
conn = sqlite3.connect('quantium.sqlite')
cur = conn.cursor()

# load clean data
data_dir = "data/feature_data"
conflicts = pd.read_csv(f"{data_dir}/conflicts")
resolutions = pd.read_csv(f"{data_dir}/resolutions")
members = pd.read_csv(f"{data_dir}/members")
resolution_parts = pd.read_csv(f"{data_dir}/resolution_parts")
un_sessions = pd.read_csv(f"{data_dir}/un_sessions")

# parse dates
members['joined_on'] = pd.to_datetime(members['joined_on'], format="%Y/%m/%d")
resolutions['date'] = pd.to_datetime(resolutions['date'], format="%Y/%m/%d")

# create tables
conflicts.to_sql('conflicts', conn, if_exists='replace', index=False)
resolutions.to_sql('resolutions', conn, if_exists='replace', index=False)
members.to_sql('members', conn, if_exists='replace', index=False)
resolution_parts.to_sql('resolution_parts', conn, if_exists='replace', index=False)
un_sessions.to_sql('un_sessions', conn, if_exists='replace', index=False)

