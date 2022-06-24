#/usr/bin/env python3
'''
Date: Jun 15, 2022

Assign tracing lat,lon to nodes in the sparse matrix

N[nodeI,nodeJ] = 1: nodeI--->nodeJ counts 1 times in the trajectory

Zhenning LI
'''
import pandas as pd
from scipy.sparse import load_npz


if __name__ == "__main__":
    # nodes file
    nodes_fn = '../input/input_china_east_lv2.csv'   
    
    # sparse matrix file
    sparse_fn = '../output/east_china_sparse_202107.npz'

    # output excel file
    out_excel_fn = '../output/east_china_sparse_202107.xlsx'
    air_in_file=pd.read_csv(
        nodes_fn, names=['idx','lat0', 'lon0', 'h0','city', 'province'], index_col='idx')
    
    node_pairs=load_npz(sparse_fn)
    nz_Xs,nz_Ys=node_pairs.nonzero()
    
    node_pairs=node_pairs.tocsr()

    city_pair_dic={}
    for idx, idy in zip(nz_Xs,nz_Ys):
        
        src_city=air_in_file.loc[idx,'city']
        src_province=air_in_file.loc[idx,'province']
        tgt_city=air_in_file.loc[idy,'city']
        tgt_province=air_in_file.loc[idy,'province']
        
        keyname=src_city+','+src_province+'-'+tgt_city+','+tgt_province
        
        if keyname in city_pair_dic:
            city_pair_dic[keyname]=city_pair_dic[keyname]+node_pairs[idx,idy]
        else:
            city_pair_dic[keyname]=node_pairs[idx,idy]
    df_out=pd.DataFrame.from_dict(city_pair_dic, orient='index',columns=['Linked_hours'])
    df_out.to_excel(out_excel_fn)