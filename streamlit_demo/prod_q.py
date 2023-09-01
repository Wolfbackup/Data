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

st.title('产品质量安全分析')
st.header('监督抽查情况')
# st.markdown('### 监督抽查情况')
# st.subheader('监督抽查情况')
#读取数据

@st.cache
def get_data(data):
    df=pd.read_csv(data)
    df = df.dropna(subset=['year','prov_name','prod_type1'],axis=0)
    df.reset_index(inplace=True)
    return df
df=get_data('national_supchk.csv')
df_recall=get_data('recall.csv')
# 侧边栏
st.sidebar.header("请在这里筛选:")

year = st.sidebar.multiselect(
    "选择时间:",
    options=df["year"].unique(),
    default=df["year"].unique(),
)
area = st.sidebar.multiselect(
    "选择地区:",
    options=df["prov_name"].unique(),
    default=['北京市','上海市','浙江省','江苏省']
    # default=df["prov_name"].unique()
)

prod_type = st.sidebar.multiselect(
    "选择行业:",
    options=df["prod_type1"].unique(),
    default=df["prod_type1"].unique()
)

df_selection = df.query(
    "prov_name == @area & year ==@year & prod_type1 == @prod_type"
)

# 主页面
# st.markdown("##")

# 核心指标
suk_total=len(df_selection) #抽查数
suk_uqld=len(df_selection[df_selection['is_qld']=='不合格']) #不合格数
uqld_rate=int(round(suk_uqld/suk_total,4)*10000)/100  #不合格发现率

# 3列布局
left_column, middle_column, right_column = st.columns(3)

# # 添加相关信息
with left_column:
    st.subheader("抽查总量:")
    st.subheader(f" {suk_total:,}")
with middle_column:
    st.subheader("不合格数:")
    st.subheader(f"{suk_uqld}")
with right_column:
    st.subheader("不合格发现率:")
    st.subheader(f"{uqld_rate}%")
#
# 分隔符
st.markdown("""---""")

df_prvo=pd.pivot_table(df_selection,index=['prov_name'],values=['id','is_qld'],aggfunc={'id':len,'is_qld':lambda x:(x=='不合格').sum()})
# df_prvo.reset_index(inplace=True)
df_prvo['不合格率']=round(df_prvo['is_qld']/df_prvo['id'],4)*100
df_prvo.rename(columns={'id':'抽查次数','is_qld':'不合格数'},inplace=True)

df_type=pd.pivot_table(df_selection,index=['prod_type1'],values=['id','is_qld'],aggfunc={'id':len,'is_qld':lambda x:(x=='不合格').sum()})
df_type['不合格率']=round(df_type['is_qld']/df_type['id'],4)*100
df_type.rename(columns={'id':'抽查次数','is_qld':'不合格数'},inplace=True)

col1, col2 = st.columns(2)

col1.bar_chart(df_prvo['抽查次数'])
col2.line_chart(df_prvo['不合格率'])
st.bar_chart(df_type['不合格率'])

df_map=df_selection.dropna(subset=['lon','lat'],axis=0)
show_enter = st.checkbox('显示不合格企业分布')
if show_enter:
    st.map(df_map[['lon','lat']])

st.markdown("""---""")

df_prod=pd.pivot_table(df,index=['prod_name1'],values=['id','is_qld'],aggfunc={'id':len,'is_qld':lambda x:(x=='不合格').sum()})
df_prod.reset_index(inplace=True)
df_prod['rate']=df_prod['is_qld']/df_prod['id']*100
df_prod.rename(columns={'prod_name1':'产品名称','id':'抽查次数','is_qld':'不合格数','rate':'不合格发现率'},inplace=True)

rate_selection = st.slider('不合格发现率:',
                          min_value=min(df_prod['不合格发现率']),
                          max_value=max(df_prod['不合格发现率']),
                          value=(min(df_prod['不合格发现率']), max(df_prod['不合格发现率'])))
suk_selection = st.slider('抽查次数:',
                          min_value=min(df_prod['抽查次数']),
                          max_value=max(df_prod['抽查次数']),
                          value=(min(df_prod['抽查次数']), max(df_prod['抽查次数'])))

mask = (df_prod['不合格发现率'].between(*rate_selection)) & (df_prod['抽查次数'].between(*suk_selection))


# 根据筛选条件, 得到有效数据
st.markdown(f'*有效数据: {len(df_prod[mask])}*')
show_data = st.checkbox('显示数据')
if show_data:
    st.table(df_prod[mask])

st.markdown("""---""")
st.subheader('国内外召回情况')

# df_recall_selection = df_recall.query(
#     "prov_name == @area & year ==@year & prod_type1 == @prod_type"
# )
df_recall_prov=pd.pivot_table(df_recall,index=['prov_name'],values=['id',],aggfunc={'id':len})
df_recall_prov.reset_index(inplace=True)
df_recall_prov.rename(columns={'id':'召回数量'},inplace=True)

df_recall_prod=pd.pivot_table(df_recall,index=['prod_type1'],values=['id',],aggfunc={'id':len})
df_recall_prov.reset_index(inplace=True)
df_recall_prod.rename(columns={'id':'召回数量'},inplace=True)

# col_recall1, col_recall2 = st.columns(2)
# col_recall1.bar_chart(df_recall_prov['召回数量'])
# col_recall2.bar_chart(df_recall_prod['召回数量'])



# fig2, ax2 = plt.subplots()
# ax2.pie(df_recall_prod['召回数量'],labels=df_recall_prod.index)
# col_recall2.pyplot(fig2)
# st.bar_chart(df_recall_prov['召回数量'])

c1,c2=st.columns(2)
def random_color_generator(number_of_colors):
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                 for i in range(number_of_colors)]
    return colors


with c1:
    trace_basic = [go.Bar(
        x=df_recall_prov['prov_name'],
        y=df_recall_prov['召回数量'],
        textposition="outside",
        text=df_recall_prov['召回数量'],
        # marker_color=['#ff3385', '#ff00ff', '#ffff1a', '#1aff1a', '#00ccff']
        marker_color=random_color_generator(len(df_recall_prov['prov_name']))
    )]
    layout_basic = go.Layout(
        title='各省份召回情况',
        xaxis_tickangle=-45
    )
    figure_basic = go.Figure(data=trace_basic, layout=layout_basic)
    # Plot
    st.plotly_chart(figure_basic)

with c2:
    labels = df_recall_prod.index
    values = df_recall_prod['召回数量']
    trace = [go.Pie(labels=labels,
                    values=values,
                    # texttemplate=df_recall_prod['召回数量'],
                    textposition="outside",
                    hole=0.5,
                    hoverinfo='label+percent')
             ]
    layout = go.Layout(
        title='各行业召回情况'
    )
    fig = go.Figure(data=trace, layout=layout)
    st.plotly_chart(fig)


st.markdown("""---""")
st.subheader('重点行业分析')


# left_column, right_column = st.columns(2)
# left_column.write(st.bar_chart(df_prvo['抽查次数']), use_container_width=True)
# right_column.write(st.line_chart(df_prvo['不合格率']), use_container_width=True)

# # 各类商品销售情况(柱状图)
# sales_by_product_line = (
#     df_selection.groupby(by=["商品类型"]).sum()[["总价"]].sort_values(by="总价")
# )
# fig_product_sales = px.bar(
#     sales_by_product_line,
#     x="总价",
#     y=sales_by_product_line.index,
#     orientation="h",
#     title="<b>每种商品销售总额</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
#     template="plotly_white",
# )
# fig_product_sales.update_layout(
#     plot_bgcolor="rgba(0,0,0,0)",
#     xaxis=(dict(showgrid=False))
# )
#
# # 每小时销售情况(柱状图)
# sales_by_hour = df_selection.groupby(by=["小时"]).sum()[["总价"]]
# print(sales_by_hour.index)
# fig_hourly_sales = px.bar(
#     sales_by_hour,
#     x=sales_by_hour.index,
#     y="总价",
#     title="<b>每小时销售总额</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
#     template="plotly_white",
# )
# fig_hourly_sales.update_layout(
#     xaxis=dict(tickmode="linear"),
#     plot_bgcolor="rgba(0,0,0,0)",
#     yaxis=(dict(showgrid=False)),
# )
#
#
# left_column, right_column = st.columns(2)
# left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
# right_column.plotly_chart(fig_product_sales, use_container_width=True)
#
 # 隐藏streamlit默认格式信息
# hide_st_style = """
# #             <style>
# #             #MainMenu {visibility: hidden;}
# #             footer {visibility: hidden;}
# #             header {visibility: hidden;}
# #             </style>
# #             """
# # st.markdown(hide_st_style, unsafe_allow_html=True)









# df=pd.DataFrame({
#     'first':[1,2,3,4],
#     'second':[10,20,30,40]})
# df
# st.line_chart(df)
# map_data=pd.DataFrame(np.random.randn(100,2)/[50,50]+[32.76,188.4],
#                       columns=['lat','lon'])
# st.map(map_data)