import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import datetime
from ab_test import AB_Test, Hogwarts
import plotly.express as px

#загрузка данных и обработка столбца времени
uploaded_file = st.file_uploader("Choose a file")
data = None
try:
    data = pd.read_csv(uploaded_file, index_col='DateTime', parse_dates=['DateTime'])
    data.index = data.index.tz_localize(None)
except ValueError:
    data = None

#выбор столбца и периодов для проведения А/В теста
if data is not None:
    st.dataframe(data)
    names = list(data)
    name = st.selectbox('Выберите параметр для проведения тестирования', names)
    st.write('Вы выбрали: ', name)
    d1 = st.date_input("Начало периода первой выборки", datetime.date(2020, 1, 1))
    d1 = pd.Timestamp(d1)
    d2 = st.date_input("окончание периода первой выборки", datetime.date(2021, 1, 1))
    d2 = pd.Timestamp(d2)
    d3 = st.date_input("Начало периода второй выборки", datetime.date(2022, 1, 1))
    d3 = pd.Timestamp(d3)
    d4 = st.date_input("Окончание периода второй выборки", datetime.date(2023, 1, 1))
    d4 = pd.Timestamp(d4)
    time_period = [d1, d2, d3, d4]

    x, y = Hogwarts(data, name, time_period).get_two_population() # функция выбирает из датафрейма нужные данные за выбранный период
    try:
        result = AB_Test(x, y).get_result()
    except ValueError:
        st.write('Необходимо выбрать другой период, в выбраном периоде слишком мало значений для расчета статистик')
    st.write(' --- Результат расчета --- ')
    st.dataframe(result)

    # Create distplot with custom bin_size
    fig = ff.create_distplot([x, y], ['первая подвыборка', 'вторая подвыборка'], bin_size=1.0)
    fig2 = px.box(pd.DataFrame(x))
    fig3 = px.box(pd.DataFrame(y))
    # Plot!
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)


else:
    st.write('waiting your data file...')


