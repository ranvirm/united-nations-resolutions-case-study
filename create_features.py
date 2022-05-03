import pandas as pd
import sqlite3
from datetime import datetime
import re
from pandasql import sqldf
import pycountry

# pysqlsetup
pysqldf = lambda q: sqldf(q, globals())

# load clean data
data_dir = "data/clean_data"
conflicts = pd.read_csv(f"{data_dir}/conflicts")
resolutions = pd.read_csv(f"{data_dir}/resolutions")
members = pd.read_csv(f"{data_dir}/members")

# parse dates
members['joined_on'] = pd.to_datetime(members['joined_on'], format="%m/%d/%Y")
resolutions['date'] = pd.to_datetime(resolutions['date'], format="%d/%m/%Y")

# conflict duration
conflicts['duration'] = conflicts['end'] - conflicts['start']
conflicts['duration'] = conflicts.duration.apply(lambda x: 1 if x == 0 else x)

# conflict intensity
conflicts['intensity'] = conflicts['casualties']/conflicts['duration']
conflicts['intensity'] = conflicts.intensity.apply(lambda x: int(x))

# conflict countries
# conflicts['countries'] = conflicts['conflict'].apply(lambda x: )

# years as member
members['duration'] = members.joined_on.apply(lambda x: datetime.now().year - x.year)

# member year joined
members['year_joined'] = members['joined_on'].apply(lambda x: x.year)

# vote margin
resolutions['vote_margin'] = abs(resolutions['yes'] - resolutions['no'])

# number of members at time of resolution
resolutions['n_members'] = resolutions.date.apply(lambda x: members[members['joined_on'] < x].count()[1])

# total votes
resolutions['total_votes'] = resolutions.resolution_id.apply(
    lambda x: int(resolutions[resolutions['resolution_id'] == x]['yes']) + int(resolutions[resolutions['resolution_id'] == x]['no']) + int(resolutions[resolutions['resolution_id'] == x]['abstain'])
)

# percent abstain
resolutions['percent_abstain'] = resolutions.resolution_id.apply(
    lambda x: round(int(resolutions[resolutions['resolution_id'] == x]['abstain']) / int(resolutions[resolutions['resolution_id'] == x]['total_votes']), 2)
)

# percent yes
resolutions['percent_yes'] = resolutions.resolution_id.apply(
    lambda x: round(int(resolutions[resolutions['resolution_id'] == x]['yes']) / int(resolutions[resolutions['resolution_id'] == x]['total_votes']), 2)
)

# percent no
resolutions['percent_no'] = resolutions.resolution_id.apply(
    lambda x: round(int(resolutions[resolutions['resolution_id'] == x]['no']) / int(resolutions[resolutions['resolution_id'] == x]['total_votes']), 2)
)

# resolution passed
resolutions['resolution_passed'] = resolutions['resolution_id'].apply(
    lambda x: 1 if (resolutions[resolutions['resolution_id'] == x]['percent_yes'] >= 0.5).item() else 0
    if (resolutions[resolutions['resolution_id'] == x]['important']).item() == 1
    else 1 if (resolutions[resolutions['resolution_id'] == x]['percent_yes'] >= 0.66).item() else 0
)

# resolution group id
resolutions['resolution_group_id'] = resolutions.unres.apply(lambda x: f"{x.split('/')[0]}/{x.split('/')[1]}/{re.sub('[A-Z]', '', x.split('/')[2])}" if x is not None and len(x.split("/")) == 3 else x)

# resolution year
resolutions['year'] = resolutions['date'].apply(lambda x: x.year)

# tbl with number of resolutions per multipart resolution
resolution_parts = pysqldf("select resolution_group_id, count(*) as n_parts from resolutions group by resolution_group_id")

# un sessions tbl
un_sessions = pysqldf(
    """
    select strftime('%Y',date) as year,
       count(resolution_id) as n_resolutions,
       sum(resolution_passed) as n_passed,
       max(n_members) as n_members,
       round(cast(sum(resolution_passed) as float) / cast(count(resolution_id) as float), 2) as percent_passed,
       session_id
    from resolutions group by session_id
    """
)

# resolutions['long_desc'][resolutions['long_desc'].str.contains('BOER'.upper())]



# write
output_dir = "data/feature_data"
conflicts.to_csv(f"{output_dir}/conflicts", index=False)
resolutions.to_csv(f"{output_dir}/resolutions", index=False)
members.to_csv(f"{output_dir}/members", index=False)
resolution_parts.to_csv(f"{output_dir}/resolution_parts", index=False)
un_sessions.to_csv(f"{output_dir}/un_sessions", index=False)