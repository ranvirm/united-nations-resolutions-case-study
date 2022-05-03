import pandas as pd

conflicts = pd.read_csv("data/raw_data/conflicts.csv")
resolutions = pd.read_csv("data/raw_data/resolutions.csv")
members = pd.read_csv("data/raw_data/members.csv")


def rename_cols(df):
    col_names = df.columns.format()
    new_col_names = {}
    for name in col_names:
        new_col_names[name] = name.lower().replace(" ", '_')

    return df.rename(columns=new_col_names)


conflicts = rename_cols(conflicts)
resolutions = rename_cols(resolutions)
members = rename_cols(members)

# members clean up

# remove "note" from name
members['country'] = members.apply(lambda country: country[0].split("[")[0], axis=1)
# remove additional info from name
members['country'] = members.apply(lambda country: country[0].split("(")[0], axis=1)

# resolutions clean up
resolutions = resolutions.rename(
    columns={
        'session': 'session_id',
        'rcid': 'resolution_id',
        'abstain': 'abstain',
        'yes': 'yes',
        'no': 'no',
        'importan': 'important',
        'date': 'date',
        'unres': 'unres',
        'amend': 'amend',
        'para': 'para',
        'short': 'short_desc',
        'length': 'length',
        'descr': 'long_desc'
    }
)

# replace "." in important with "0"
resolutions['important'] = resolutions["important"].apply(lambda x: 0 if x == "." else x)

resolutions['amend'] = resolutions["amend"].apply(lambda x: 0 if x is None else x)

resolutions['para'] = resolutions["para"].apply(lambda x: 0 if x is None else x)

# write
output_dir = "data/clean_data"
conflicts.to_csv(f"{output_dir}/conflicts", index=False)
resolutions.to_csv(f"{output_dir}/resolutions", index=False)
members.to_csv(f"{output_dir}/members", index=False)
