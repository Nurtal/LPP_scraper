from dbfread import DBF






def download_code_list():
    """Download dbf file from AMELI and extract list of LPP code"""


    # download file

    # Spécifiez le chemin vers le fichier .dbf
    file_path = 'LPP802/lpp_fiche_tot802.dbf'

    # Ouvrir et lire le fichier DBF
    table = DBF(file_path, encoding='unicode_escape')

    # Parcourir les enregistrements dans la table
    for record in table:
        print(record)  # Affiche c

    

    



if __name__ == "__main__":

    
