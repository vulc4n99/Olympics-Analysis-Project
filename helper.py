import numpy as np


def medal_tally(df):
    # Drop duplicates to avoid double-counting medals
    medal_tally = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    # Group by region (country) and aggregate Gold, Silver, and Bronze medals
    medal_tally = medal_tally.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                                ascending=False).reset_index()

    # Calculate the total medals column
    medal_tally['Total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']

    # Convert the medal columns to integers
    medal_tally['Gold'] = medal_tally['Gold'].astype(int)
    medal_tally['Silver'] = medal_tally['Silver'].astype(int)
    medal_tally['Bronze'] = medal_tally['Bronze'].astype(int)
    medal_tally['Total'] = medal_tally['Total'].astype(int)

    return medal_tally


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = df['region'].dropna().unique().tolist()  # This should give you a list
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def fetch_medal_tally(df,year, country):
    medal_df = df.drop_duplicates(subset = ['Team' , 'NOC' , 'Games' , 'Year' , 'City' , 'Sport' , 'Event' , 'Medal'])
    flag = 0
    # Default case: Overall year and country
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df

    # Case: Overall year, specific country
    elif year == 'Overall' and country != 'Overall':
      flag = 1
      temp_df = medal_df[medal_df['region'] == country]

    # Case: Specific year, overall country
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]

    # Case: Specific year and specific country
    elif year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    # Group by 'region' if Overall country, otherwise by 'Year'
    if flag ==1 :
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    # Add the total medals column
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype(int)
    x['Silver'] = x['Silver'].astype(int)
    x['Bronze'] = x['Bronze'].astype(int)
    x['Total'] = x['Total'].astype(int)

    return x # Return the result


def data_over_time(df,col):
    nations_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index().sort_values('index')
    nations_over_time.rename(columns={"index": "Editions", "Year": col}, inplace=True)
    return nations_over_time

def most_successful(df, sport):
    # Dropping rows without medals
    temp_df = df.dropna(subset=['Medal'])

    # If a specific sport is selected, filter the dataframe
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count the number of medals for each athlete
    medal_count = temp_df['Name'].value_counts().reset_index()
    medal_count.columns = ['Name', 'Medals']

    # Merge with the original df to get other athlete details
    merged_df = medal_count.merge(df, on='Name', how='left')[['Name', 'Medals', 'Sport', 'region']].drop_duplicates('Name')

    # Sort by the number of medals and get the top 15
    top_15 = merged_df.sort_values(by='Medals', ascending=False).head(15)

    return top_15

def yearwise_medal_tally(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    # Create the pivot table
    pt = temp_df.pivot_table(index='Year', columns='Sport', values='Medal', aggfunc='count').fillna(0)

    # Check if the pivot table is empty
    if pt.empty:
        return None  # Return None if no data
    else:
        return pt.T


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df[temp_df['region'] == country]

    x = temp_df['Name'].value_counts().reset_index().head(10).merge(df, left_on='index', right_on='Name', how='left')[
        ['index', 'Name_x', 'Sport']].drop_duplicates('index')
    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df

def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    final.fillna(0, inplace=True)

    return final