from dbfread import DBF
import requests
import zipfile
import os
from io import BytesIO
import shutil





def download_code_list()->list:
    """Download dbf file from AMELI and extract list of LPP code"""
    
    # download zip file from AMELI
    version = "802"
    dl_folder = "/tmp/lpp_db"
    url = f"http://www.codage.ext.cnamts.fr/codif/tips/download_file.php?filename=tips/LPP{version}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        zip_file = BytesIO(response.content)
        with zipfile.ZipFile(zip_file, 'r') as z:
            extract_path = dl_folder
            os.makedirs(extract_path, exist_ok=True)
            z.extractall(extract_path)
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

    # extract codes
    code_list = []
    file_path = f"{dl_folder}/lpp_fiche_tot{version}.dbf"
    table = DBF(file_path, encoding='unicode_escape')
    for record in table:
        if record['CODE_TIPS'] not in code_list:
            code_list.append(record['CODE_TIPS'])

    # delete tmp folder
    try:
        shutil.rmtree(dl_folder)
    except OSError as e:
        print(f"Error: {dl_folder} : {e.strerror}")

    # return codes
    return code_list

    

    



if __name__ == "__main__":

    code_list = download_code_list()    
