import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
import random
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

# 设置网页
st.set_page_config(page_title="质量透视", page_icon=":bar_chart:", layout="wide")

st.header('企业状况')

@st.cache
def get_data(data):
    df=pd.read_csv(data)
    df = df.dropna(subset=['year','prod_map'],axis=0)
    df.reset_index(inplace=True)
    return df
df_compay=get_data('注册资本规模.csv')

year = st.sidebar.multiselect(
    "选择时间:",
    options=df_compay["year"].unique(),
    default=df_compay["year"].unique(),
)
area = st.sidebar.multiselect(
    "选择地区:",
    options=df_compay["prov_name"].unique(),
    default=['北京市','上海市','浙江省','江苏省']
    # default=df["prov_name"].unique()
)

prod_type = st.sidebar.multiselect(
    "选择行业:",
    options=df_compay["prod_type1"].unique(),
    # default=df_compay["prod_type1"].unique()
    default=[18]
)

df_selection = df_compay.query(
    "prov_name == @area & year ==@year & prod_type1 == @prod_type"
)

df_company_life=pd.pivot_table(df_selection,index=['prod_type1'],columns=['is_qld'],values=['存活年份','注册规模人民币'],aggfunc=['mean'])
# with c1:
#     fig = go.Figure(data=[
#         go.Bar(name='不合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','存活年份','不合格')]),
#         go.Bar(name='合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','存活年份','合格')])
#     ])
# c1=st.columns(1)
# with c1:
trace_basic = [
    go.Bar(name='不合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','存活年份','不合格')]),
    go.Bar(name='合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','存活年份','合格')])]
layout_basic = go.Layout(
    title='企业年龄',
    xaxis_tickangle=-45
)
figure_basic = go.Figure(data=trace_basic, layout=layout_basic)
# Plot
st.plotly_chart(figure_basic)


trace_basic = [
    go.Bar(name='不合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','注册规模人民币','不合格')]),
    go.Bar(name='合格', x=df_company_life.index, y=df_company_life.loc[:,('mean','注册规模人民币','合格')])]
layout_basic = go.Layout(
    title='企业规模（单位：万人民币）',
    xaxis_tickangle=-45
)
figure_basic = go.Figure(data=trace_basic, layout=layout_basic)
# Plot
st.plotly_chart(figure_basic)
