import streamlit as st 
import utils
import data.source_code


st.title("Sleep Statistics")

st.write("Firtly, Lets draw our gender statistic pie chart")
st.plotly_chart(utils.graph_generator.generate_gender_chart())
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[0], language='python')

st.write("Then, occupation pie chart")
st.plotly_chart(utils.graph_generator.generate_occupation_chart(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[1], language='python')

st.write("May be stress level is occured by occupation")
st.plotly_chart(utils.graph_generator.generate_stress_occupation_chart(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[2], language='python')

st.write("Draw histogram to compare sleep duration and stress level")
st.plotly_chart(utils.graph_generator.generate_spray_graph(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[3], language='python')

st.write("Lets look at the main tendense more carefully.")
st.write("Firstly, we need to find the average values at each age and find changes and draw the graph.")
st.plotly_chart(utils.graph_generator.generate_graph(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[4], language='python')

st.write("We can see that Sleep Duration and Stress level have inverse dependence. Lets draw some more graphs if wee can find some patterns.")
st.plotly_chart(utils.graph_generator.generate_phyz(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[5], language='python')

st.write("We obtain, that after 35 yo there a bit linear dependence between physical activity and stress level. I am going to look at the patterns between sleep duration, quality of sleep and physical activity.")
st.plotly_chart(utils.graph_generator.generate_duration_vs_quality_vs_phyz(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[6], language='python')

st.write("We can see that there is such a big dependence, but from 45 till 54 there is exception. After previous analise I can mention, that level of stress affects the physical activity. But lets look at numeratic statistics. I am going to use numpy to do it.")
st.write("I am using Pirson's corelation formula.")
st.plotly_chart(utils.graph_generator.generate_pirsons_mtx(), use_container_width=True)
with st.expander("Show/Close code"):
    st.code(data.source_code.source_code_data_list[7], language='python')
st.write("We can see that sleep duration and sleep quality extremly decreases stress level, physical activity increases a bit sleep duration and quality of sleep, but physical activity has almost no effect on stress level.")