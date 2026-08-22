import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import pandas as pd

def get_status_color(statut):
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
    labels = {
        '1': '1.0 - Point Bloquant', '1.0': '1.0 - Point Bloquant',
        '2': '2.0 - A consulter', '2.0': '2.0 - A consulter',
        '3': '3.0 - Attente de devis', '3.0': '3.0 - Attente de devis',
        '4': '4.0 - Demande C/O', '4.0': '4.0 - Demande C/O',
        '5': '5.0 - A faire', '5.0': '5.0 - A faire',
        '5.1': '5.1 - Devis en Validation',
        '6': '6.0 - Attente de livraison', '6.0': '6.0 - Attente de livraison',
        '6.1': '6.1 - Attente de livraison (CONF W)',
        '6.2': '6.2 - Attente de livraison (Sans CONF)',
        '7': '7.0 - Litige', '7.0': '7.0 - Litige',
        '7.1': '7.1 - Litige',
        '8': '8.0 - Réceptionné', '8.0': '8.0 - Réceptionné',
        '9': '9.0 - Terminé', '9.0': '9.0 - Terminé',
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
    return statut_str

def create_chart(data, title, categories):
    """
    Crée un graphique avec Matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = [get_status_color(cat) for cat in categories]
    bars = ax.bar(categories, data, color=colors, edgecolor='black', linewidth=0.5, width=0.6)
    
    # Ajouter les valeurs sur les barres
    max_val = max(data) if max(data) > 0 else 1
    for bar, value in zip(bars, data):
        if value > 0:
            if value > max_val * 0.15:
                y_pos = value - (max_val * 0.02)
                va = 'top'
                color_text = 'white'
            else:
                y_pos = value + (max_val * 0.01)
                va = 'bottom'
                color_text = 'black'
            
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                    str(int(value)), ha='center', va=va,
                    fontsize=11, fontweight='bold', color=color_text)
    
    ax.set_xlabel('Statuts', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nombre de références', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_ylim(0, max_val * 1.15)
    
    # Légende
    legend_elements = []
    for cat in categories:
        full_label = get_status_full_label(cat)
        color = get_status_color(cat)
        legend_elements.append(mpatches.Patch(color=color, label=full_label))
    
    if legend_elements:
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
                  fontsize=8, title='Légende des statuts', title_fontsize=10)
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    return buffer
