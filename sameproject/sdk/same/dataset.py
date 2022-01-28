import yaml
import os
from urllib.parse import urlparse
import pandas as pd

def dataset(name, same_file='same.yaml'):
    try:
      env_var=os.environ['SAME_ENV'] if os.environ['SAME_ENV']!="" else "default"
    except:
      env_var="default"


    with open(same_file, 'r') as file:
        same_variables = yaml.safe_load(file)


    urlpar = urlparse(same_variables['datasets'][name][env_var])
    
    url = 'https://gateway.ipfs.io/ipfs/'+urlpar.netloc+urlpar.path if urlpar.scheme=='ipfs' else same_variables['datasets'][name][env_var]
    filename, file_extension = os.path.splitext(url)
    
    extensions = {
      '.csv': 'read_csv',
      '.dta': 'read_stata',
      '.feather': 'read_feather',
      '.html': 'read_html',
      '.json': 'read_json',
      '.orc': 'read_orc',
      '.parquet': 'read_parquet',
      '.pickle': 'read_pickle',
      '.sas': 'read_sas',
      '.sav': 'read_spss',
      '.sql': 'read_sql',
      '.txt': 'read_fwf',
      '.xml': 'read_xml',
      ('.hdf', '.h4', '.hdf4', '.he2', '.h5', '.hdf5', '.he5'): 'read_hdf',
      ('.xlsx', '.ods'): 'read_excel',
    }
    
    for key,value in list(extensions.items()):
      if type(key)==tuple:
        for ext in key:
          extensions[ext]=value
        extensions.pop(key)
    ds=eval("pd."+extensions[file_extension])(url)
    return ds