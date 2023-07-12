import pandas as pd


def format_file(file):
    """
    Fill missing values in the file by copying the values of the previous row.
    This is necessary because in the Google Sheet, each session on a block is a new
    row, where the constants (e.g. block name, grade, etc.) are merged. When exported
    to CSV, these merged cells are empty, so we need to fill them in.

    Some other minor formatting is done:
    - The 'Sent' column is filled with 'no' if it is empty
    - The 'Tries' column is incremented by the previous row's value if the 'Boulder'
        column is empty (meaning that this row is new session on the same boulder).
    - The 'Grade' column is set to type string
    """

    # load the file
    df = pd.read_csv(file)

    # Fill NaN values of the 'Sent' column with 'no'
    df["Sent"] = df["Sent"].fillna("no")

    # find the rows where the 'Boulder' column is null
    null = df[df["Line"].isnull()]["Tries"]

    # add the previous value of the 'Tries' column to the rows where null is True
    for i in range(len(null)):
        df.loc[null.index[i], "Tries"] += df.loc[null.index[i] - 1, "Tries"]

    # fill NaN values with the the values from the previous row
    # TODO: don't do this for all columns!
    df = df.fillna(method="ffill")

    # set 'Grade' column to type string
    df = df.astype({"Grade": "str"})

    # save the file
    df.to_csv(file, index=False)
