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
conflicts = pd.read_csv(f"{data_dir}/conflicts")
resolutions = pd.read_csv(f"{data_dir}/resolutions")
members = pd.read_csv(f"{data_dir}/members")
resolution_parts = pd.read_csv(f"{data_dir}/resolution_parts")
un_sessions = pd.read_csv(f"{data_dir}/un_sessions")

# parse dates
members['joined_on'] = pd.to_datetime(members['joined_on'], format="%Y/%m/%d")
resolutions['date'] = pd.to_datetime(resolutions['date'], format="%Y/%m/%d")

# remove outliers
conflicts = conflicts[conflicts['casualties'] < 14000000]

# filter dfs
conflicts = conflicts[conflicts['start'] >= start_year][conflicts['start'] <= end_year]
resolutions = resolutions[resolutions['year'] >= start_year][resolutions['year'] <= end_year]
members = members[members['year_joined'] >= start_year][members['year_joined'] <= end_year]
un_sessions = un_sessions[un_sessions['year'] >= start_year][un_sessions['year'] <= end_year]


# body

# resolutions section

st.header("UN Resolutions")

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

# st.plotly_chart(fig1, use_container_width=True)

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

# st.plotly_chart(fig2, use_container_width=True)

r1Col1, r1Col2 = st.columns(2)

with r1Col1:
    st.plotly_chart(fig1, use_container_width=True)

with r1Col2:
    st.plotly_chart(fig2, use_container_width=True)

vote_margin_all = px.histogram(
    resolutions,
    x='vote_margin',
)

st.plotly_chart(vote_margin_all, use_container_width=True)

vote_margin_passed = px.histogram(
    resolutions[resolutions['resolution_passed'] == 1],
    x='vote_margin',
)

st.plotly_chart(vote_margin_passed, use_container_width=True)

vote_margin_not_passed = px.histogram(
    resolutions[resolutions['resolution_passed'] == 0],
    x='vote_margin',
)

st.plotly_chart(vote_margin_not_passed, use_container_width=True)

# n members by year joined
members_year_joined_df = pysqldf(q="select count(country) as n_members, year_joined as year from members group by year_joined")
members_year_joined = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
members_year_joined.add_trace(
    go.Scatter(x=un_sessions['year'], y=un_sessions['n_members']),
    secondary_y=False,
)

st.plotly_chart(members_year_joined, use_container_width=True)


# conflict casualties vs duration
casualties_duration_df = pysqldf(q="select avg(casualties) as av_casualties, duration from conflicts where casualties < 14000000 group by duration")
casualties_duration = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
casualties_duration.add_trace(
    go.Bar(x=casualties_duration_df['duration'], y=casualties_duration_df['av_casualties']),
    secondary_y=False,
)

st.plotly_chart(casualties_duration, use_container_width=True)

# conflict intensity vs duration
intensity_duration_df = pysqldf(q="select avg(intensity) as av_intensity, duration from conflicts where casualties < 14000000 group by duration")
intensity_duration = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
intensity_duration.add_trace(
    go.Bar(x=intensity_duration_df['duration'], y=intensity_duration_df['av_intensity']),
    secondary_y=False,
)

st.plotly_chart(intensity_duration, use_container_width=True)

# conflict start year vs intensity
intensity_start_df = pysqldf(q="select avg(intensity) as av_intensity, start from conflicts where casualties < 14000000 group by start")
intensity_start = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
intensity_start.add_trace(
    go.Scatter(x=intensity_start_df['start'], y=intensity_start_df['av_intensity']),
    secondary_y=False,
)

st.plotly_chart(intensity_start, use_container_width=True)

# conflict start year vs casualties
casualties_start_df = pysqldf(q="select avg(casualties) as av_casualties, start from conflicts where casualties < 14000000 group by start")
casualties_start = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
casualties_start.add_trace(
    go.Scatter(x=casualties_start_df['start'], y=casualties_start_df['av_casualties']),
    secondary_y=False,
)

st.plotly_chart(casualties_start, use_container_width=True)

# top 10 intense conflicts
top_10_intensity_df = pysqldf(q="select conflict, intensity from conflicts where casualties < 14000000 order by intensity desc limit 10")
top_10_intensity = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_intensity.add_trace(
    go.Bar(x=top_10_intensity_df['conflict'], y=top_10_intensity_df['intensity']),
    secondary_y=False,
)

st.plotly_chart(top_10_intensity, use_container_width=True)

# top 10 casualties conflicts
top_10_casualties_df = pysqldf(q="select conflict, casualties from conflicts where casualties < 14000000 order by casualties desc limit 10")
top_10_casualties = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_casualties.add_trace(
    go.Bar(x=top_10_casualties_df['conflict'], y=top_10_casualties_df['casualties']),
    secondary_y=False,
)

st.plotly_chart(top_10_casualties, use_container_width=True)

# top 10 duration conflicts
top_10_duration_df = pysqldf(q="select conflict, duration from conflicts where casualties < 14000000 order by duration desc limit 10")
top_10_duration = make_subplots(specs=[[{"secondary_y": False}]])

# Add traces
top_10_duration.add_trace(
    go.Bar(x=top_10_duration_df['conflict'], y=top_10_duration_df['duration']),
    secondary_y=False,
)

st.plotly_chart(top_10_duration, use_container_width=True)

# conflict duration intensity heatmap

duration_intensity_heatmap = px.density_heatmap(conflicts, x="duration", y="casualties")
st.plotly_chart(duration_intensity_heatmap, use_container_width=True)

x= px.imshow(conflicts.corr())
st.plotly_chart(x, use_container_width=True)