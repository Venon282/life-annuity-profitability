import pandas as pd

def GetTables(path='./tables_fr.xlsx'):
    return pd.read_excel(path, engine="openpyxl", sheet_name=None)
