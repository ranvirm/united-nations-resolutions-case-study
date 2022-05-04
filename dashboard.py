import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pandasql import sqldf


# pysqlsetup
pysqldf = lambda q: sqldf(q, globals())


# streamlit setup
st.set_page_config(layout="wide")


# variables
start_year = 1899
end_year = 2011


start_year = st.sidebar.select_slider(
    label='Start Year',
    options=range(1899, 2012),
    value=start_year,
)

end_year = st.sidebar.select_slider(
    label='End Year',
    options=range(1899, 2012),
    value=end_year,
)

st.title("Case Study: United Nations Resolutions", )


# load data
data_dir = "data/feature_data"
conflicts_raw = pd.read_csv(f"{data_dir}/conflicts")
resolutions = pd.read_csv(f"{data_dir}/resolutions")
members = pd.read_csv(f"{data_dir}/members")
resolution_parts = pd.read_csv(f"{data_dir}/resolution_parts")
un_sessions = pd.read_csv(f"{data_dir}/un_sessions")

# parse dates
members['joined_on'] = pd.to_datetime(members['joined_on'], format="%Y/%m/%d")
resolutions['date'] = pd.to_datetime(resolutions['date'], format="%Y/%m/%d")

# remove outliers
conflicts = conflicts_raw[conflicts_raw['casualties'] < 14000000]

# filter dfs
conflicts = conflicts[conflicts['start'] >= start_year][conflicts['start'] <= end_year]
resolutions = resolutions[resolutions['year'] >= start_year][resolutions['year'] <= end_year]
members = members[members['year_joined'] >= start_year][members['year_joined'] <= end_year]
un_sessions = un_sessions[un_sessions['year'] >= start_year][un_sessions['year'] <= end_year]


# body

# resolutions section

st.header("UN Resolutions")

st.subheader("Resolutions Passed Over Time")

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig1.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_resolutions'], name="N Resolutions"),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions["percent_passed"], name="% Resolutions Passed"),
    secondary_y=True,
)

# members vs passed
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig2.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_members'], name="N Members"),
    secondary_y=False,
)

fig2.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions["percent_passed"], name="% Resolutions Passed"),
    secondary_y=True,
)


r1Col1, r1Col2 = st.columns(2)

with r1Col1:
    st.plotly_chart(fig1, use_container_width=True)

with r1Col2:
    st.plotly_chart(fig2, use_container_width=True)


st.text('While there appears to be no relation between the volume of resolutions tabled and those that are passed,')
st.text('the percentage of resolutions passed seems to be positively correlated with the total number of voting members.')

st.subheader("How Close Were the Votes?")
st.text('Understanding the closeness of votes could give us insight into how unanimous votes were.')
st.text('Resolutions with low vote margins were wholly agreed upon, whether passed or not and vice versa.')
st.text('Below we explore how close votes were using a calculated vote margin which is the difference between number of YES and NO  votes.')
st.text('A higher vote margin indicates a more unanimous decision while those with low margins indicate a more indecisive vote.')



vote_margin_all = px.histogram(
    resolutions,
    x='vote_margin',
)

st.plotly_chart(vote_margin_all, use_container_width=True)

st.caption("Histogram of all vote margins")
st.text('The above indicates that the majority of votes were unanimous.')
st.text('Does this view change when looking at resolutions passed and not passed separately?')


vote_margin_passed = px.histogram(
    resolutions[resolutions['resolution_passed'] == 1],
    x='vote_margin',
)

st.plotly_chart(vote_margin_passed, use_container_width=True)

st.caption("Histogram of all vote margins for resolutions that were passed")
st.text('The above indicates that the majority of votes where the resolution was passed were unanimous.')

vote_margin_not_passed = px.histogram(
    resolutions[resolutions['resolution_passed'] == 0],
    x='vote_margin',
)

st.plotly_chart(vote_margin_not_passed, use_container_width=True)

st.caption("Histogram of all vote margins for resolutions that were not passed")
st.text('The above shows that the majority of votes not passed were not passed with a high margin.')
st.text('This indicates that resolutions which were not passed, were not passed with very close votes.')
st.text('This could represent opportunities for swinging the vote by convincing just a few members to change their votes on these resolutions.')
st.text('More analysis needs to be done on the topics which had a low vote margin to understand how to influence future votes on those topics.')

# vote margin by number of members
vote_margin_n_members_df = pysqldf(q="select avg(vote_margin) as av_vote_margin, avg(n_members) as n_members, year from resolutions group by year")
vote_margin_n_members = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['n_members'], name="N Members"),
    secondary_y=False,
)
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['av_vote_margin'], name="Av. Vote Margin"),
    secondary_y=False,
)

st.plotly_chart(vote_margin_n_members, use_container_width=True)
st.caption("Average vote margin and number of members over time for all resolutions")

# vote margin by number of members for passed resolutions
vote_margin_n_members_df = pysqldf(q="select avg(vote_margin) as av_vote_margin, avg(n_members) as n_members, year from resolutions where resolution_passed = 1 group by year")
vote_margin_n_members = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['n_members'], name="N Members"),
    secondary_y=False,
)
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['av_vote_margin'], name="Av. Vote Margin"),
    secondary_y=False,
)

st.plotly_chart(vote_margin_n_members, use_container_width=True)
st.caption("Average vote margin and number of members over time for passed resolutions")

# vote margin by number of members for not passed resolutions
vote_margin_n_members_df = pysqldf(q="select avg(vote_margin) as av_vote_margin, avg(n_members) as n_members, year from resolutions where resolution_passed = 0 group by year")
vote_margin_n_members = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['n_members'], name="N Members"),
    secondary_y=False,
)
vote_margin_n_members.add_trace(
    go.Scatter(x=vote_margin_n_members_df['year'], y=vote_margin_n_members_df['av_vote_margin'], name="Av. Vote Margin"),
    secondary_y=False,
)

st.plotly_chart(vote_margin_n_members, use_container_width=True)
st.caption("Average vote margin and number of members over time for resolutions not passed")

st.text('The above 3 graphs gives insight into the relationship between the vote margin and number of voting members.')
st.text('For passed resolutions, there may be a positive correlation between number of members and vote margin,')
st.text('this could be a result of the UN becoming more cohesive with increasing number of members,')
st.text('because an increasing number of members may represent more cohesion among countries and therefore humanitarian values,')
st.text('represented by decisiveness in voting on resolutions.')
st.text("This also indicates that when the committee agrees on a matter, they strongly agree.")
st.text("\n")
st.text('For resolutions not passed, there seems to be no correlation between number of members and vote margin.')
st.text("This may indicate that resolutions which split the committee have remained the same over time,")
st.text("perhaps indicating a world view of those matters which has held over time and among countries.")
st.text("Interestingly, the last graph may indicate that there is little bias in new member selection")
st.text("because to maintain the same vote margin over time, new members had to be added in equal proportions")
st.text("in terms of whether they support contested resolutions or not.")

st.text("\n")
# top 10 vote margins for passed votes
st.text("Top 10 Highest Vote Margins for Passed Resolutions")
top_10_vote_margins_passed_df = pysqldf(q="select vote_margin, short_desc, long_desc from resolutions where resolution_passed = 1 order by vote_margin desc limit 10")
st.table(top_10_vote_margins_passed_df)

# top 10 vote margins for not passed votes
st.text("Top 10 Highest Vote Margins for Not Passed Resolutions")
top_10_vote_margins_not_passed_df = pysqldf(q="select vote_margin, short_desc, long_desc from resolutions where resolution_passed = 0 order by vote_margin desc limit 10")
st.table(top_10_vote_margins_not_passed_df)

# top 10 lowest vote margins for passed votes
st.text("Top 10 Lowest Vote Margins for Passed Resolutions")
top_10_lowest_vote_margins_passed_df = pysqldf(q="select vote_margin, short_desc, long_desc from resolutions where resolution_passed = 1 order by vote_margin asc limit 10")
st.table(top_10_lowest_vote_margins_passed_df)

# top 10 lowest vote margins for not passed votes
st.text("Top 10 Lowest Vote Margins for Not Passed Resolutions")
top_10_lowest_vote_margins_not_passed_df = pysqldf(q="select vote_margin, short_desc, long_desc from resolutions where resolution_passed = 0 order by vote_margin asc limit 10")
st.table(top_10_lowest_vote_margins_not_passed_df)


st.text("\n")
st.subheader("Exploring the Conflicts")

st.text("\n")
st.text("We now analyse the conflicts, looking at how they have changed over time and what we can understand about this.")
st.text("To assist the analysis we calculate a metric, intensity, which is the number of casualties per year.")

# conflict casualties vs duration
casualties_duration_df = pysqldf(q="select avg(casualties) as av_casualties, duration from conflicts where casualties < 14000000 group by duration")

casualties_duration = px.bar(
    casualties_duration_df,
    x='duration',
    y='av_casualties'
)

st.plotly_chart(casualties_duration, use_container_width=True)
st.caption("Conflict Avg. Casualties by Duration")

# conflict intensity vs duration
intensity_duration_df = pysqldf(q="select avg(intensity) as av_intensity, duration from conflicts where casualties < 14000000 group by duration")

intensity_duration = px.bar(intensity_duration_df, x='duration', y='av_intensity')

st.plotly_chart(intensity_duration, use_container_width=True)
st.caption("Conflict Avg. Intensity by Duration")

st.text("The key takeaway from the above 2 figures is that shorter conflicts tend to be more intense,")
st.text("that is, short conflicts have a higher number of casualties per year.")
st.text("This may be a result of most conflicts being very intense at the start but the data is lacking to prove this.")
st.text("This does tell us that the UN needs act decisively and quickly with ending conflicts.")

# # conflict start year vs intensity
# intensity_start_df = pysqldf(q="select avg(intensity) as av_intensity, start from conflicts where casualties < 14000000 group by start")
# intensity_start = make_subplots(specs=[[{"secondary_y": False}]])
#
# # Add traces
# intensity_start.add_trace(
#     go.Scatter(x=intensity_start_df['start'], y=intensity_start_df['av_intensity']),
#     secondary_y=False,
# )
#
# st.plotly_chart(intensity_start, use_container_width=True)
# st.caption("Conflict Intensity by Start Year")
#
# # conflict start year vs casualties
# casualties_start_df = pysqldf(q="select avg(casualties) as av_casualties, start from conflicts where casualties < 14000000 group by start")
# casualties_start = make_subplots(specs=[[{"secondary_y": False}]])
#
# # Add traces
# casualties_start.add_trace(
#     go.Scatter(x=casualties_start_df['start'], y=casualties_start_df['av_casualties']),
#     secondary_y=False,
# )
#
# st.plotly_chart(casualties_start, use_container_width=True)

# top 10 intense conflicts
top_10_intensity_df = pysqldf(q="select conflict, intensity from conflicts where casualties < 14000000 order by intensity desc limit 10")
top_10_intensity = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_intensity.add_trace(
    go.Bar(x=top_10_intensity_df['conflict'], y=top_10_intensity_df['intensity']),
    secondary_y=False,
)

st.plotly_chart(top_10_intensity, use_container_width=True)
st.caption("Top 10 Intense Conflicts - measured by casualties per year")

# top 10 casualties conflicts
top_10_casualties_df = pysqldf(q="select conflict, casualties from conflicts where casualties < 14000000 order by casualties desc limit 10")
top_10_casualties = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_casualties.add_trace(
    go.Bar(x=top_10_casualties_df['conflict'], y=top_10_casualties_df['casualties']),
    secondary_y=False,
)

st.plotly_chart(top_10_casualties, use_container_width=True)
st.caption("Top 10 Conflicts by Casualties")

# top 10 duration conflicts
top_10_duration_df = pysqldf(q="select conflict, duration from conflicts where casualties < 14000000 order by duration desc limit 10")
top_10_duration = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_duration.add_trace(
    go.Bar(x=top_10_duration_df['conflict'], y=top_10_duration_df['duration']),
    secondary_y=False,
)

st.plotly_chart(top_10_duration, use_container_width=True)
st.caption("Top 10 Longest Conflicts")

# conflict duration intensity heatmap

# duration_intensity_heatmap = px.density_heatmap(conflicts, x="duration", y="casualties")
# st.plotly_chart(duration_intensity_heatmap, use_container_width=True)

st.subheader("UN Sessions & Conflicts - any connection?")

# conflicts start year vs UN sessions
conflict_start_count_df = pysqldf(
    q="""
    select count(conflict) as n_conflicts, start from conflicts group by start
    """
)
conflict_sessions = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
conflict_sessions.add_trace(
    go.Scatter(x=conflict_start_count_df['start'], y=conflict_start_count_df['n_conflicts'], name="N Conflicts"),
    secondary_y=False,
)
conflict_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_resolutions'], name="N Resolutions"),
    secondary_y=True,
)

conflict_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_passed'], name="N Resolutions Passed"),
    secondary_y=True,
)

st.text("Conflicts Start Year vs UN Sessions")
st.plotly_chart(conflict_sessions, use_container_width=True)

# conflicts end year vs UN sessions
conflict_end_count_df = pysqldf(
    q="""
    select count(conflict) as n_conflicts, end from conflicts group by end
    """
)
conflict_end_sessions = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
conflict_end_sessions.add_trace(
    go.Scatter(x=conflict_end_count_df['end'], y=conflict_end_count_df['n_conflicts'], name="N Conflicts"),
    secondary_y=False,
)
conflict_end_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_resolutions'], name="N Resolutions"),
    secondary_y=True,
)

conflict_end_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_passed'], name="N Resolutions Passed"),
    secondary_y=True,
)

st.text("Conflicts End Year vs UN Sessions")
st.plotly_chart(conflict_end_sessions, use_container_width=True)

st.text("From the above, it can be seen that, for the period of time that the number of conflicts was increasing,")
st.text("the number of UN resolutions tabled and passed was also increasing, possibly in response to the conflicts.")
st.text("\n")
st.text("Interestingly, it could be deduced that the increasing number of resolutions led to a decline in the")
st.text("number of conflicts in the following years.")
st.text("This may be a indication that the UN resolutions have been effective in reducing the number of conflicts.")


# conflicts casualties vs UN sessions
conflict_casualties_sum_df = pysqldf(
    q="""
    select avg(casualties) as total_casualties, start from conflicts group by start
    """
)
conflict_casualties_sessions = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
conflict_casualties_sessions.add_trace(
    go.Scatter(x=conflict_casualties_sum_df['start'], y=conflict_casualties_sum_df['total_casualties'], name="Av. Casualties"),
    secondary_y=False,
)
conflict_casualties_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_resolutions'], name="N Resolutions"),
    secondary_y=True,
)

conflict_casualties_sessions.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_passed'], name="N Resolutions Passed"),
    secondary_y=True,
)

st.text("Average Casualties per Conflict vs UN Sessions")
st.plotly_chart(conflict_casualties_sessions, use_container_width=True)


st.text("\n")
st.subheader("Correlation Plots")

st.plotly_chart(px.imshow(conflicts.corr()), use_container_width=True)
st.caption("Conflicts")

st.plotly_chart(px.imshow(resolutions.corr()), use_container_width=True)
st.caption("Resolutions")

st.plotly_chart(px.imshow(resolutions.corr()), use_container_width=True)
st.caption("UN Sessions")

# case study questions

st.header("Case Study Questions & Answers")

# q1
st.subheader("Q1. Which conflict resulted in the greatest number of casualties in the history of the UN?")
st.metric(
    label="Conflict with Highest Casualties",
    value=conflicts_raw["casualties"].max()
)

# q2
st.subheader("Q2. List the conflicts that are sitting in the top 5% by yearly casualties in the history of the UN.")
# top 10 casualties conflicts
n_conflicts = conflicts_raw['conflict'].count()
top_5_p_casualties_df = pysqldf(
    q=f"select conflict, casualties from conflicts_raw where start > (select min(year) from resolutions) order by intensity desc limit {int(n_conflicts*0.05)}"
)
st.table(top_5_p_casualties_df)

# q3
st.subheader("Q3. How would you estimate the proportion of historical conflicts that could be referred to as ‘civil war’?")
st.text("Use key words in the conflict name to identify conflicts which are likely to be civil wars")
st.text("The below sql query returns the following conflicts as possible civil wars")
civil_wars_df = pysqldf(
    q="""
    select conflict 
    from conflicts_raw
    where upper(conflict) like '%GOVT%' 
    or upper(conflict) like '%GVT%' 
    or upper(conflict) like '%REBEL%'
    or upper(conflict) like '%CIVIL%'
    """
)
percent_civil_wars = civil_wars_df['conflict'].count() / conflicts_raw['conflict'].count()
st.code(
    body="""
    select conflict 
from conflicts 
where upper(conflict) like '%GOVT%' 
    or upper(conflict) like '%GVT%' 
    or upper(conflict) like '%REBEL%'
    or upper(conflict) like '%CIVIL%'
    """,
    language="sql"
)

with st.expander("Possible Civil Wars - Click to View"):
    st.table(civil_wars_df)

st.metric(
    label="Percentage of Conflicts likely to be Civil Wars",
    value=f"{round(percent_civil_wars*100, 2)} %"
)

# q4
st.subheader("Q4. Which decade had the greatest number of resolutions proposed?")
decade_resolutions_df = pysqldf(
    q="""
    select
       cast(substr(cast(year as text), 0, 4) || '0' as integer) as decade, count(resolution_id) as n_resolutions
from resolutions
group by decade
order by n_resolutions desc
    """
)
st.metric(
    label="Decade with Highest No. of Proposed Resolutions",
    value=f"{decade_resolutions_df['decade'][decade_resolutions_df['n_resolutions'] == decade_resolutions_df['n_resolutions'].max()].item()}"
)
st.metric(
    label="No. of Proposed Resolutions",
    value=f"{decade_resolutions_df['n_resolutions'][decade_resolutions_df['n_resolutions'] == decade_resolutions_df['n_resolutions'].max()].item()}"
)


# q5 A
st.subheader("Q5 A. How many sessions had all the discussed resolutions passed?")
sessions_passed_df = pysqldf(
    q = """
    select *
from un_sessions
where n_resolutions = n_passed
    """
)
st.metric(
    label="No. of Sessions with All Resolutions Passed",
    value=f"{sessions_passed_df['session_id'].count()}"
)


# q5 B
st.subheader("Q5 B. Which of these had the greatest number of important issues discussed?")
st.text("Both sessions had an equal number of important issues discussed")
sessions_passed_highest_important = sessions_passed_df[sessions_passed_df['n_important'] == sessions_passed_df['n_important'].max()]
st.table(sessions_passed_highest_important)

# q6 A
st.subheader("Q6 A. What has been the success rate of important issues compared to general issues?")
n_issues_not_important = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
where important = 0
    """
)['count'].max()

n_issues_not_important_passed = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
where important = 0
and resolution_passed = 1
    """
)['count'].max()

n_issues_important = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
where important = 1
    """
)['count'].max()

n_issues_important_passed = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
where important = 1
and resolution_passed = 1
    """
)['count'].max()

n_issues = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
    """
)['count'].max()

n_issues_passed = pysqldf(
    q="""
    select count(resolution_id) as count
from resolutions
where resolution_passed = 1
    """
)['count'].max()

success_rate_not_important = n_issues_not_important_passed / n_issues_not_important
success_rate_important = n_issues_important_passed / n_issues_important
success_rate = n_issues_passed / n_issues

s_rate_col1, s_rate_col2, s_rate_col3 = st.columns(3)

with s_rate_col1:
    st.metric(
        label="Success Rate All Issues",
        value=f"{round(success_rate * 100, 2)} %"
    )

with s_rate_col2:
    st.metric(
        label="Success Rate Not Important",
        value=f"{round(success_rate_not_important * 100, 2)} %"
    )

with s_rate_col3:
    st.metric(
        label="Success Rate Important",
        value=f"{round(success_rate_important * 100, 2)} %"
    )

# q6 B
st.subheader("Q6 B. Based on your analysis of the data so far, what do you think could have driven this?")
st.text(f"The committe has a very high success rate in general, with the total success rate being {round(success_rate * 100, 2)}%")

# q7
st.subheader("Q7. What is the longest time period in years for which no new member joined the United Nations since it was established?")

# q8 A
st.subheader("Q8 A. What is the annualised growth rate in membership for the UN since it was established?")
un_sessions['member_growth_rate'] = un_sessions['n_members'].pct_change()
st.table(un_sessions)

# q8 B
st.subheader("Q8 B. What were the top 3 years with highest growth in membership?")
gg = pysqldf(
    q = """
   select year, member_growth_rate from un_sessions order by member_growth_rate desc limit 3
    """
)
st.table(gg)

# q9 A
st.subheader("Q9 A. Using this data, what attributes would you create to predict the likelihood of a successful resolution?")
st.plotly_chart(px.imshow(resolutions.corr()), use_container_width=True)
st.caption("Resolutions Corr Plot")

# q9 B
st.subheader("Q9 B. What additional information would you request from the UN?")
