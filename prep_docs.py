import pandas as pd
import psycopg
import sqlalchemy
from sqlalchemy import create_engine

def prep_docs(df, id=id, df_metadata=[]):
    df = df.rename(columns={id:'id'})
    content_columns = [x for x in df.columns.values if x not in df_metadata+['id']]
    content_list = []
    metadata_list = []
    for index, row in df.iterrows():
        if len(df_metadata)>0:
            content = "\n".join([f"{x}: {row[x]}" for x in content_columns])
            metadata = {
                    df_metadata[i]: row[df_metadata[i]] for i in range(len(df_metadata))
                }
            content_list.append(content)
            metadata_list.append(metadata)
        else:
            content = " ".join([f"{x}: {row[x]}" for x in content_columns])
            content_list.append(content)
            metadata_list = [{None:None}]*len(df)
    df['contents'] = content_list
    df['metadata'] = metadata_list
    return df[['id', 'contents', 'metadata']]
    


product_knowlegde = pd.read_csv("amker_product_knowledge_base.csv")
sales_governance = pd.read_csv("amker_sales_governance_framework.csv")

# content_columns = [x for x in sales_governance.columns.values if x not in ['Policy_Section_ID'] ]
# content_columns

sales_governance_records = prep_docs(sales_governance, id='Policy_Section_ID', df_metadata=['Last_Updated_Date'])
product_knowlegde = prep_docs(product_knowlegde, id='SKU_ID', df_metadata=[])
policy_sop_guide_docs = pd.concat([sales_governance_records,product_knowlegde], ignore_index=True)
policy_sop_guide_docs


USERNAME = 'postgres'      
PASSWORD = 'postgres'              
HOST = 'localhost'
PORT = '5432'
DATABASE = 'postgres' 

connection_string2 = f'postgresql+psycopg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
engine = create_engine(connection_string2)

# 4. Write the DataFrame to a new table
policy_sop_guide_docs.to_sql(
    name='policy_sop_guide_docs', 
    con=engine, 
    # schema="ai",
    if_exists='replace',      # Options: 'fail' (error if exists), 'replace' (drop and recreate), 'append'
    index=False,            # Set to True if you want the DataFrame index as a column
    dtype={"metadata": sqlalchemy.types.JSON} 
)