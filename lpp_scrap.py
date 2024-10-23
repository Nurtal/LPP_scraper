from dbfread import DBF
import requests
import zipfile
import os
from io import BytesIO
import shutil
from bs4 import BeautifulSoup
import re


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


def scrap_lpp_code(lpp_code):
    """Extract information associated to a LPP code"""

    # scrap page
    url = f"http://www.codage.ext.cnamts.fr/cgi/tips/cgi-fiche?p_code_tips={lpp_code}&p_date_jo_arrete=%25&p_menu=FICHE&p_site=AMELI"
    response = requests.get(url)

    # Step 2: Check if the request was successful
    m_list = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        stuff = soup.find_all('tr')

        for s in stuff:
            text = s.get_text()
            if not re.search("\nFiche\n", text):
                # print(text)
                # print("-"*45)
                m_list.append(text)

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")


    description_rank = -1
    data = {
        'code':lpp_code,
        'désignation':'',
        'description':'',
        'tarif':'',
        'prix_unitaire_réglementé':'',
        'montant_max_remboursement':'',
        'entente_prealable':'',
        'indications':'',
        'identifiant':'',
        'age_max':'',
        'nature_prestation':'',
        'type_prestation':'',
        'chapitre':'',
        'arbre':''
        
    }
    for x in range(len(m_list)):
        text = m_list[x]

        # hunt designation & description
        if re.search('^Désignation', text):
            d = text.split('Désignation:')
            if len(d) > 1:
                data['désignation'] = d[1]
                description_rank = x+1
            
        # hunt tarif
        if re.search('^Tarif:', text):
            t = text.split('Tarif:')
            if len(t) > 1:
                t = t[1].split("\xa0")[0].replace(' ', '').replace(',', '.')
                data['tarif'] = t

        # hunt Prix unitaire réglementé
        if re.search('^Prix unitaire réglementé', text):
            p = text.split('Prix unitaire réglementé:')
            if len(p) > 1:
                p = p[1].replace('Néant', '')
                data['prix_unitaire_réglementé'] = p

        # hunt Montant max remboursement
        if re.search('^Montant max remboursement', text):
            m = text.split('Montant max remboursement:')
            if len(m) > 1:
                m = m[1].replace('Néant', '')
                data['montant_max_remboursement'] = m

        # hunt Entente préalable
        if re.search('^Entente préalable', text):
            e = text.split('Entente préalable:')
            if len(e) > 1:
                data['entente_prealable'] = e[1]

        # hunt Indications
        if re.search('^Indications', text):
            i = text.split('Indications:')
            if len(i) > 1:
                data['indications'] = i[1]

        # hunt Identifiant
        if re.search('^Identifiant', text):
            i = text.split('Identifiant:')
            if len(i) > 1:
                data['identifiant'] = i[1].replace('Néant', '')

        # hunt Age max
        if re.search('^Age max', text):
            a = text.split('Age maxi:')
            if len(a) > 1:
                data['age_max'] = a[1].replace('Néant', '')

        # hunt Nature prestation
        if re.search('^Nature de prestation:', text):
            n = text.split('Nature de prestation:')
            if len(n) > 1:
                data['nature_prestation'] = n[1].replace("\\xa0", "")

        # hunt type prestation
        if re.search('^Type de prestation:', text):
            t = text.split('Type de prestation:')
            if len(n) > 1:
                data['type_prestation'] = t[1].replace("\\xa0", "")

        # hunt chapitre & arborescence
        if re.search('Arborescence', text):
            c = text.split("\n")
            arbre = ""
            e_cmpt = 0
            start = 999
            for e in c:

                # chapitre
                if re.search('^TITRE [0-9]', e):
                    data['chapitre'] = e
                    start = e_cmpt

                # branches
                if e_cmpt >= start and e != "":
                    arbre += f"{e}/"

                e_cmpt +=1
            data['arbre'] = arbre[:-1]

    # catch description
    if description_rank != -1:
        data['description'] = m_list[description_rank]

    # return scraped data
    return data
    

    



if __name__ == "__main__":

    # code_list = download_code_list()    
    c = "1152380"
    c = "3299070"

    scrap_lpp_code(c)
