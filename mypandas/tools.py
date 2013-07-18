import pandas
from my_data_structure import monkey_add
##############################################
##     labeled_df
##############################################
def add_top_label(df,name):
    """returns a DataFrame identical to df, with a top level of column labels
    you can use pandas.concat(df1,df2) to assemble distincts dataframes"""
    res = df.copy()
    res.columns = pandas.MultiIndex.from_tuples(zip([name]*len(df.columns),df.columns))
    return res

        
        
        
@monkey_add(pandas.DataFrame)
@monkey_add(pandas.Series)
def to_clipboard(obj,sep = "\t"):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    import StringIO
    output = StringIO.StringIO()
    obj.to_csv(output,sep = sep,index_label = "index")
    win32clipboard.SetClipboardText(output.getvalue())
    output.close()
    win32clipboard.CloseClipboard()