import pandas as pd
import numpy as np

import sys
import pickle
from pathlib import Path
import argparse



def dataset_review(args):

    str(args.source_dataset_file)

    filename1 = str(args.source_dataset_file)


    with open(filename1, 'rb') as f:
        X1 = pickle.load(f, encoding='bytes')



    df = pd.DataFrame([(k[0], k[1], v, v.shape) for k, v in X1.items()], 
                    columns=['Label1', 'Label2', 'Data', 'Shape'])
    df['num_examples'] = df['Shape'].apply(lambda x: x[0])
    df['vector_length'] = df['Shape'].apply(lambda x: x[2])



    # m_table = df.groupby(['Label1', 'Label2'])['m'].sum().unstack(fill_value=0)
    m_table = df.set_index(['Label1', 'Label2'])['num_examples']

    m_table_w_totals = m_table.unstack(fill_value=0)
    m_table_w_totals.loc['Total', :] = m_table_w_totals.sum()
    m_table_w_totals.loc[:, 'Total'] = m_table_w_totals.sum(axis=1)
    m_table_w_totals = m_table_w_totals.astype(int)




    n_table_avg = df.groupby(['Label1', 'Label2'])['vector_length'].mean().unstack(fill_value=0).astype(int)



    stats = {
    'Number of unique classes': df.groupby(['Label1', 'Label2']).ngroups,
    'Total number of examples in the dataset':df['num_examples'].sum(),
    'First labels': df['Label1'].nunique(),
    'Second labels': df['Label2'].nunique(),
    'Typical number of examples per unique class': df.sample()['num_examples'].values[0],  # Get 'n' from a random row
    'Typical example vector length': df.sample()['vector_length'].values[0],  # Get 'n' from a random row
    'Class with largest number of examples': df.loc[df['num_examples'].idxmax(), ['Label1', 'Label2']].tolist(),
    'Class with smallest number of examples': df.loc[df['num_examples'].idxmin(), ['Label1', 'Label2']].tolist(),
    }

    stats_table = pd.Series(stats).to_frame().rename(columns={0: 'Value'})


    return df, m_table, m_table_w_totals, n_table_avg,  stats_table




if __name__ == "__main__":
    #parse arguments if theyre provided
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_dataset_file", "-d", help="Source dataset (can be a path)")
    args = parser.parse_args()


    _, m_table, m_table_w_totals, n_table_avg,  stats_table = dataset_review(args)

    print("Number of examples per unique pair")
    print("----------------------------------")
    print(m_table)
    print()
    print("Number of examples per label and totals.")
    print("----------------------------------")
    print(m_table_w_totals)
    print()
    print("Example vector lengths per label.")
    print("----------------------------------")
    print(n_table_avg)
    print()
    print("Dataset Statistics.")
    print("----------------------------------")
    print(stats_table)
    print()
    