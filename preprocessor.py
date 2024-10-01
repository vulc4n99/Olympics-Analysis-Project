import pandas as pd


def preprocess(df, region_df):

    # Filtering for summer Olympics
    df = df[df['Season'] == 'Summer']

    # Merge with region_df
    df = df.merge(region_df, on='NOC', how='left')

    df.drop_duplicates(inplace=True)

    # One hot encoding medals
    df = pd.concat([df, pd.get_dummies(df['Medal'], dummy_na=False)], axis=1)
    return df
