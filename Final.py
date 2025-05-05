import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from sqlalchemy import create_engine

# Map Plotting
def plot_india_map(df, color_column, title):
    url = (
        "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/"
        "raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    )
    response = requests.get(url)
    india_states = response.json()

    df['state'] = df['state'].str.title()
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',
        locations='state',
        color=color_column,
        color_continuous_scale='blues',
        title=title
    )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Business Case Study"])

# Database connection
engine = create_engine("mysql+mysqlconnector://root:uvasripradeep@127.0.0.1/Phonepe")

# Home page display
if page == "Home":
    st.header("PhonePe Transaction Insights")
    st.write("""
        This project aims to analyze and visualize aggregated values of payment categories, 
        create maps for total values at state and district levels, and identify top-performing 
        states, districts.
    """)
    
   
    col1, col2 = st.columns([3, 1])  

    # Column 1 - Centered Map
    with col1:
# Load and display the map for total transaction amount by state
        df_map_home = pd.read_sql(
            """
            SELECT State, SUM(Transaction_amount) AS Total_Transaction_Amount
            FROM aggregated_transactions
            GROUP BY State
            """, engine
        )
        df_map_home.rename(columns={'State': 'state'}, inplace=True)
        df_map_home['state'] = df_map_home['state'].str.title()
        plot_india_map(df_map_home, 'Total_Transaction_Amount', 'Total Transaction Amount by State (All Time)')
 # Column 2 - Tab selection for State/District view
    with col2:
        view_option = st.radio("Select View", ["State", "District"])

        if view_option == "State":
# Load and display top 10 States by Transaction Amount
            df_top_states = pd.read_sql("""
                SELECT State, SUM(Transaction_amount) AS Total_Transaction_Amount
                FROM aggregated_transactions
                GROUP BY State
                ORDER BY Total_Transaction_Amount DESC
                LIMIT 10
            """, engine)
            st.subheader("Top 10 States by Transaction Amount")
            st.dataframe(df_top_states)

        elif view_option == "District":
# Load and display top 10 Districts by Transaction Amount
            df_top_districts = pd.read_sql("""
                SELECT entityName AS District, State, SUM(amount) AS Total_Transaction_Amount
                FROM top_transaction
                WHERE type = 'districts'
                GROUP BY entityName, State
                ORDER BY Total_Transaction_Amount DESC
                LIMIT 10
            """, engine)
            st.subheader("Top 10 Districts by Transaction Amount")
            st.dataframe(df_top_districts)
      
elif page == "Business Case Study":
    st.title("Business Case Study")

    question = st.selectbox("Select any Question", [
        "1. Decoding Transaction Dynamics on PhonePe",
        "2. Insurance Penetration and Growth Potential Analysis",
        "3. Transaction Analysis Across States and Districts",
        "4. User Registration Analysis",
        "5. Insurance Transactions Analysis"
    ])

    year = st.selectbox("Year", [2018,2019,2020, 2021, 2022, 2023])
    quarter = st.selectbox("Quarter", [1, 2, 3, 4])

    if question == "1. Decoding Transaction Dynamics on PhonePe":
        df_map = pd.read_sql(f"""
            SELECT State, SUM(Transaction_amount) AS Total_Transaction_Amount
            FROM aggregated_transactions
            WHERE Year = {year} AND Quarter = {quarter}
            GROUP BY State
        """, engine)
        df_map.rename(columns={'State': 'state'}, inplace=True)
        df_map['state'] = df_map['state'].str.title()
        plot_india_map(df_map, 'Total_Transaction_Amount', f'Transaction Amount by State - Q{quarter} {year}')

        df = pd.read_sql(f"""
            SELECT Transaction_type, SUM(Transaction_count) AS Total_Transaction_Count,
                   SUM(Transaction_amount) AS Total_Transaction_Amount
            FROM aggregated_transactions
            WHERE Year = {year} AND Quarter = {quarter}
            GROUP BY Transaction_type
        """, engine)

        st.dataframe(df)

        fig_bar = px.bar(df, x='Transaction_type', y='Total_Transaction_Amount',
                         title=f'Transaction Amount by Type - Q{quarter} {year}', color='Transaction_type')
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(df, names='Transaction_type', values='Total_Transaction_Amount',
                         title=f'Transaction Type Distribution - Q{quarter} {year}',
                         hole=0.5, color_discrete_sequence=px.colors.sequential.Reds)
        st.plotly_chart(fig_pie, use_container_width=True)

    elif question == "2. Insurance Penetration and Growth Potential Analysis":
        df_map = pd.read_sql(f"""
            SELECT State, SUM(Insurance_amount) AS Total_Insurance_Amount
            FROM aggregated_insurance
            WHERE Year = {year}
            GROUP BY State
        """, engine)
        df_map.rename(columns={'State': 'state'}, inplace=True)
        df_map['state'] = df_map['state'].str.title()
        plot_india_map(df_map, 'Total_Insurance_Amount', f'Insurance Amount by State - {year}')

        df = pd.read_sql(f"""
            SELECT State, SUM(Insurance_count) AS Total_Insurance_Count,
                   SUM(Insurance_amount) AS Total_Insurance_Amount
            FROM aggregated_insurance
            WHERE Year = {year}
            GROUP BY State
        """, engine)
        st.dataframe(df)
        fig_bar = px.bar(df, x='State', y='Total_Insurance_Amount',
                         title=f'Insurance Amount by State - {year}')
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(df, names='State', values='Total_Insurance_Amount',
                         title=f'Insurance Distribution by State - {year}',
                         hole=0.5, color_discrete_sequence=px.colors.sequential.Blues)
        st.plotly_chart(fig_pie, use_container_width=True)

    elif question == "3. Transaction Analysis Across States and Districts":
        df_map = pd.read_sql(f"""
            SELECT State, SUM(amount) AS Total_Amount
            FROM top_transaction
            WHERE type = 'districts'
            GROUP BY State
        """, engine)
        df_map.rename(columns={'State': 'state'}, inplace=True)
        df_map['state'] = df_map['state'].str.title()
        plot_india_map(df_map, 'Total_Amount', 'District Transaction Amount by State')

        df = pd.read_sql("""
            SELECT entityName AS District, State, SUM(count) AS Total_Transactions,
                   SUM(amount) AS Total_Amount
            FROM top_transaction
            WHERE type = 'districts'
            GROUP BY entityName, State
            ORDER BY Total_Amount DESC
            LIMIT 10
        """, engine)

        st.dataframe(df)

        fig_bar = px.bar(df, x='District', y='Total_Amount', color='State',
                         title='Top 10 Districts by Transaction Amount')
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(df, names='District', values='Total_Amount',
                         title='Transaction Distribution - Top 10 Districts',
                         hole=0.6, color_discrete_sequence=px.colors.sequential.OrRd)
        st.plotly_chart(fig_pie, use_container_width=True)

    elif question == "4. User Registration Analysis":
        df_map = pd.read_sql(f"""
            SELECT State, SUM(registeredUsers) AS Total_Users
            FROM top_user
            WHERE entity_type = 'districts' AND Year = {year} AND Quarter = {quarter}
            GROUP BY State
        """, engine)
        df_map.rename(columns={'State': 'state'}, inplace=True)
        df_map['state'] = df_map['state'].str.title()
        plot_india_map(df_map, 'Total_Users', f'Registered Users by State - Q{quarter} {year}')

        df = pd.read_sql(f"""
            SELECT name AS District, State, SUM(registeredUsers) AS Total_Registered_Users
            FROM top_user
            WHERE entity_type = 'districts' AND Year = {year} AND Quarter = {quarter}
            GROUP BY name, State
            ORDER BY Total_Registered_Users DESC
            LIMIT 10
        """, engine)

        st.dataframe(df)

        fig_bar = px.bar(df, x='District', y='Total_Registered_Users', color='State',
                         title=f'Top 10 Districts by Registered Users – Q{quarter} {year}')
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(df, names='District', values='Total_Registered_Users',
                         title=f'Registered Users Distribution - Q{quarter} {year}',
                         hole=0.6, color_discrete_sequence=px.colors.sequential.Purples)
        st.plotly_chart(fig_pie, use_container_width=True)

    elif question == "5. Insurance Transactions Analysis":
        df_map = pd.read_sql(f"""
            SELECT State, SUM(amount) AS Total_Insurance_Amount
            FROM top_insurance
            WHERE type = 'districts' AND Year = {year} AND Quarter = {quarter}
            GROUP BY State
        """, engine)
        df_map.rename(columns={'State': 'state'}, inplace=True)
        df_map['state'] = df_map['state'].str.title()
        plot_india_map(df_map, 'Total_Insurance_Amount', f'Insurance Amount by State - Q{quarter} {year}')

        df = pd.read_sql(f"""
            SELECT entityName AS District, State, SUM(count) AS Total_Insurance_Transactions,
                   SUM(amount) AS Total_Insurance_Amount
            FROM top_insurance
            WHERE type = 'districts' AND Year = {year} AND Quarter = {quarter}
            GROUP BY entityName, State
            ORDER BY Total_Insurance_Transactions DESC
            LIMIT 10
        """, engine)

        st.dataframe(df)

        fig_bar = px.bar(df, x='District', y='Total_Insurance_Transactions', color='State',
                         title=f'Top 10 Districts by Insurance Transactions – Q{quarter} {year}')
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(df, names='District', values='Total_Insurance_Transactions',
                         title=f'Insurance Transactions Distribution - Q{quarter} {year}',
                         hole=0.6, color_discrete_sequence=px.colors.sequential.Greens)
        st.plotly_chart(fig_pie, use_container_width=True)
