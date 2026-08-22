import pandas as pd
import re

def get_status_color(statut):
    """
    Retourne la couleur correspondante pour chaque statut
    """
    colors = {
        '1': '#000000', '1.0': '#000000',
        '2': '#FF0000', '2.0': '#FF0000',
        '3': '#FFA500', '3.0': '#FFA500',
        '4': '#0000FF', '4.0': '#0000FF',
        '5': '#FFD700', '5.0': '#FFD700',
        '5.1': '#FFD700',
        '6': '#00FF00', '6.0': '#00FF00',
        '6.1': '#90EE90',
        '6.2': '#FFB6C1',
        '7': '#FF0000', '7.0': '#FF0000',
        '7.1': '#FF0000',
        '8': '#008000', '8.0': '#008000',
        '9': '#00FF00', '9.0': '#00FF00',
        'Point Bloquant': '#000000',
        'A consulter': '#FF0000',
        'Attente de devis': '#FFA500',
        'Demande C/O': '#0000FF',
        'A faire': '#FFD700',
        'Devis en Validation': '#FFD700',
        'Attente de livraison': '#00FF00',
        'Litige': '#FF0000',
        'Réceptionné': '#008000',
        'Terminé': '#00FF00',
    }
    
    statut_str = str(statut).strip()
    if statut_str in colors:
        return colors[statut_str]
    
    for key, color in colors.items():
        if key in statut_str or statut_str in key:
            return color
    
    return '#808080'

def get_status_full_label(statut):
    """
    Retourne le libellé complet du statut pour la légende
    """
    labels = {
        '1': '1.0 - Point Bloquant',
        '1.0': '1.0 - Point Bloquant',
        '2': '2.0 - A consulter',
        '2.0': '2.0 - A consulter',
        '3': '3.0 - Attente de devis',
        '3.0': '3.0 - Attente de devis',
        '4': '4.0 - Demande C/O',
        '4.0': '4.0 - Demande C/O',
        '5': '5.0 - A faire',
        '5.0': '5.0 - A faire',
        '5.1': '5.1 - Devis en Validation',
        '6': '6.0 - Attente de livraison',
        '6.0': '6.0 - Attente de livraison',
        '6.1': '6.1 - Attente de livraison (CONF W)',
        '6.2': '6.2 - Attente de livraison (Sans CONF)',
        '7': '7.0 - Litige',
        '7.0': '7.0 - Litige',
        '7.1': '7.1 - Litige',
        '8': '8.0 - Réceptionné',
        '8.0': '8.0 - Réceptionné',
        '9': '9.0 - Terminé',
        '9.0': '9.0 - Terminé',
        'Point Bloquant': '1.0 - Point Bloquant',
        'A consulter': '2.0 - A consulter',
        'Attente de devis': '3.0 - Attente de devis',
        'Demande C/O': '4.0 - Demande C/O',
        'A faire': '5.0 - A faire',
        'Devis en Validation': '5.1 - Devis en Validation',
        'Attente de livraison': '6.0 - Attente de livraison',
        'Litige': '7.0 - Litige',
        'Réceptionné': '8.0 - Réceptionné',
        'Terminé': '9.0 - Terminé',
    }
    
    statut_str = str(statut).strip()
    if statut_str in labels:
        return labels[statut_str]
    
    for key, label in labels.items():
        if key in statut_str or statut_str in key:
            return label
    
    return statut_str

def process_excel_data(df, projet_col, statut_col, commentaire_col):
    """
    Traite les données Excel et retourne le tableau croisé
    """
    # Traitement spécial pour le statut 6
    df_modified = df.copy()
    df_modified[statut_col] = df_modified[statut_col].astype(str)
    df_modified['STATUT_MODIFIE'] = df_modified[statut_col]
    
    if commentaire_col and commentaire_col in df_modified.columns:
        df_modified[commentaire_col] = df_modified[commentaire_col].astype(str)
        
        for idx, row in df_modified.iterrows():
            statut_value = str(row[statut_col]).strip()
            commentaire = str(row[commentaire_col]).strip() if pd.notna(row[commentaire_col]) else ""
            
            if statut_value.startswith('6'):
                pattern = r'CONF\s*W\s*[\d-]+'
                if re.search(pattern, commentaire, re.IGNORECASE):
                    df_modified.at[idx, 'STATUT_MODIFIE'] = '6.1'
                else:
                    df_modified.at[idx, 'STATUT_MODIFIE'] = '6.2'
        
        statut_utilise = 'STATUT_MODIFIE'
    else:
        statut_utilise = statut_col
    
    # Création du tableau croisé
    df_modified = df_modified.dropna(subset=[projet_col], how='all')
    df_modified[projet_col] = df_modified[projet_col].astype(str)
    df_modified[statut_utilise] = df_modified[statut_utilise].astype(str)
    df_modified[statut_utilise] = df_modified[statut_utilise].replace('nan', 'Non défini')
    df_modified[statut_utilise] = df_modified[statut_utilise].replace('', 'Non défini')
    
    pivot_table = pd.crosstab(
        df_modified[projet_col],
        df_modified[statut_utilise],
        margins=True,
        margins_name='Total',
        dropna=False
    )
    
    return pivot_table, df_modified, statut_utilise
