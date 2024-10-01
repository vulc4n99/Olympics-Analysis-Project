import streamlit as st
import pandas as pd
from preprocessor import preprocess
import helper  # Ensure you import the helper module
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# Load the datasets
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

st.sidebar.title("Olympics Analysis")

# Call the preprocess function
df = preprocess(df, region_df)

# Streamlit UI code
user_menu = st.sidebar.radio(
    'Select an option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise analysis', 'Athlete wise analysis')
)

if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")

    # Get list of years and countries
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    # Call the updated medal_tally function with filters
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Set title based on selections
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Medal Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year))
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " Overall Performance")
    else:
        st.title("Overall Performance of " + selected_country + " in " + str(selected_year))

    # Reset index to start from 1 and rename it
    medal_tally.reset_index(drop=True, inplace=True)
    medal_tally.index += 1  # Start index from 1
    medal_tally.index.name = 'Sr. No.'  # Rename the index column

    # Display the filtered medal tally without the default index column
    # Displaying the DataFrame with controlled height
    st.dataframe(medal_tally, use_container_width=True, height=500)  # You can adjust height as needed

if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")

    # Create two columns to display the statistics side by side
    col1, col2 = st.columns(2)

    # First column for Editions, Hosts, and Sports
    with col1:
        st.subheader("Editions")
        st.write(editions)

        st.subheader("Hosts")
        st.write(cities)

        st.subheader("Sports")
        st.write(sports)

    # Second column for Events, Athletes, and Nations
    with col2:
        st.subheader("Events")
        st.write(events)

        st.subheader("Athletes")
        st.write(athletes)

        st.subheader("Nations")
        st.write(nations)


    # Continue with your existing code for visualizations
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x="Editions", y="region")
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x="Editions", y="Event")
    st.title("Events over time")
    st.plotly_chart(fig)

    athletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athletes_over_time, x="Editions", y="Name")
    st.title("Atheletes over the years")
    st.plotly_chart(fig)

    st.title("No of Events over time (for every sport)")
    fig, ax = plt.subplots(figsize=(15, 15))
    x = df.drop_duplicates(['Year', 'Sport', "Event"])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True)
    st.pyplot(fig)

    st.title("Most successful athletes")
    sports_list = df['Sport'].unique().tolist()
    sports_list.sort()
    sports_list.insert(0, 'Overall')
    selected_sport = st.selectbox("Select a sport", sports_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

if user_menu == 'Country-wise analysis':

    st.sidebar.title('Country-wise Analysis')

    # Get the list of countries and sort them
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    # Allow the user to select a country from the sidebar
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    # Generate and display the medal tally over the years
    country_df = helper.yearwise_medal_tally(df, selected_country)

    # Check if the country has any data for medals
    if not country_df.empty:
        fig = px.line(country_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally over the years")
        st.plotly_chart(fig)
    else:
        st.write(f"No data available for {selected_country}'s medal tally over the years.")

    # Generate and display the heatmap for sports
    st.title(f"{selected_country} excels in the following sports")
    pt = helper.country_event_heatmap(df, selected_country)

    # Check if there is valid data for the heatmap
    if pt is not None and not pt.empty:
        fig, ax = plt.subplots(figsize=(10, 10))
        ax = sns.heatmap(pt, annot=True)
        st.pyplot(fig)
    else:
        st.write(f"No data available to generate a heatmap for {selected_country}.")

    # Display the top 10 athletes for the selected country
    st.title(f"Top 10 athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)

    # Check if there are any top athletes
    if not top10_df.empty:
        st.table(top10_df)
    else:
        st.write(f"No data available for top athletes from {selected_country}.")

if user_menu == 'Athlete wise analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],show_hist=False, show_rug=False)
    fig.update_layout(autosize=False,width=1000,height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports(Gold Medalist)")
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)

    # Create the figure and axis
    fig, ax = plt.subplots()

    # Use proper keyword arguments for the scatter plot
    ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60,
                         ax=ax)

    # Display the plot in Streamlit
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)


st.sidebar.markdown("---")

# Adding your name at the bottom
st.sidebar.markdown("**Made by Sahil Akalwadi**")