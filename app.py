import glob
import os
import json
import pandas as pd
import re
import sys

def get_columns_names(schemas, ds_name, sorting_key= 'column_position'):
    column_details=schemas[ds_name]
    columns=sorted(column_details,key=lambda col:col[sorting_key])
    return [col['column_name'] for col in columns]

def read_csv(file,schemas):
    file_path_list=re.split('[/\\\]',file)
    ds_name =file_path_list[-2]
    file_name=file_path_list[-1]
    columns=get_columns_names(schemas, ds_name)
    df=pd.read_csv(file,names=columns)
    return df

def to_json(df,tgt_base_dir,ds_name,file_name):
    json_file_path = f'{tgt_base_dir}/{ds_name}/{file_name}'
    os.makedirs(f'{tgt_base_dir}/{ds_name}',exist_ok=True)
    df.to_json(json_file_path,orient ='records',lines=True )

def file_convertor(src_base_dir,tgt_base_dir,ds_name):
    schemas= json.load(open(f'{src_base_dir}/schemas.json'))
    files = glob.glob(f'{src_base_dir}/{ds_name}/part-*',recursive=True)
    #return empty list if path is not correct
    if len(files)==0:
        raise  NameError(f'no file found for {ds_name}')
        

    for file in files:
        df=read_csv(file,schemas)
        file_name= re.split('[/\\\]',file)[-1]
        to_json(df,tgt_base_dir,ds_name,file_name)


def process_file(ds_names=None):
    # to get the environment variable value
    src_base_dir=os.environ.get('SRC_BASE_DIR')
    tgt_base_dir=os.environ.get('TGT_BASE_DIR')

    schemas =json.load(open(f'{src_base_dir}/schemas.json'))
    if not ds_names:
        #if ds_name is none than for all ds_name in scehmas will be executed.
        #schemas.keys() - return list of keys.
        ds_names=schemas.keys()
    for ds_name in ds_names:
        try:
            print(f'processing {ds_name}')
            file_convertor(src_base_dir,tgt_base_dir,ds_name)
        except NameError as ne:
            print(ne)
            print(f'Error processing {ds_name}')
            pass
        #if pass is not used than exception will raise and it will stop the program

if __name__=='__main__':

    if len(sys.argv)==2:
        #when to process particular files only. we send them in list form.
        #sys.argv takes value from terminal
        ds_names=json.loads(sys.argv[1])
        #converted to list from json array format.
        process_file(ds_names)
    else:
        process_file()


