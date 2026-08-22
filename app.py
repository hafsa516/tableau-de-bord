import streamlit as st
import pandas as pd
import os
import tempfile
from io import BytesIO
from utils.excel_processor import process_excel_data
from utils.chart_generator import create_chart
from utils.ppt_generator import create_pptx

# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord des projets",
    page_icon="📊",
    layout="wide"
)

# Titre
st.title("📊 Tableau de bord des projets")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    uploaded_file = st.file_uploader(
        "📁 Téléchargez votre fichier Excel",
        type=['xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")
        
        # Afficher les informations du fichier
        file_details = {
            "Nom": uploaded_file.name,
            "Taille": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.json(file_details)

# Corps principal
if uploaded_file is not None:
    try:
        # Lire le fichier Excel
        df = pd.read_excel(uploaded_file, sheet_name='Compilation', header=2)
        
        st.subheader("📊 Aperçu des données")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Détection automatique des colonnes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Colonnes disponibles :**")
            for i, col in enumerate(df.columns):
                st.text(f"[{i}] {col}")
        
        with col2:
            projet_col = st.selectbox(
                "Sélectionnez la colonne PROJET",
                options=df.columns.tolist(),
                index=1 if len(df.columns) > 1 else 0
            )
        
        with col3:
            statut_col = st.selectbox(
                "Sélectionnez la colonne STATUT",
                options=df.columns.tolist(),
                index=22 if len(df.columns) > 22 else 0
            )
        
        # Colonne Commentaire livraisons
        commentaire_col = st.selectbox(
            "Sélectionnez la colonne Commentaire livraisons (optionnel)",
            options=["Aucune"] + df.columns.tolist(),
            index=0
        )
        
        if commentaire_col == "Aucune":
            commentaire_col = None
        
        # Bouton de traitement
        if st.button("🚀 Traiter les données", type="primary"):
            with st.spinner("Traitement en cours..."):
                # Traiter les données
                pivot_table, df_modified, statut_utilise = process_excel_data(
                    df, projet_col, statut_col, commentaire_col
                )
                
                # Afficher les résultats
                st.subheader("📊 Tableau croisé des statuts")
                st.dataframe(pivot_table, use_container_width=True)
                
                # Statistiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "📋 Nombre de projets",
                        len(pivot_table) - 1 if 'Total' in pivot_table.index else len(pivot_table)
                    )
                with col2:
                    st.metric(
                        "📊 Nombre de statuts",
                        len(pivot_table.columns) - 1 if 'Total' in pivot_table.columns else len(pivot_table.columns)
                    )
                with col3:
                    total_ref = pivot_table.loc['Total', 'Total'] if 'Total' in pivot_table.index and 'Total' in pivot_table.columns else pivot_table.sum().sum()
                    st.metric("📈 Total références", int(total_ref))
                
                # Graphiques
                st.subheader("📊 Visualisation des données")
                
                # Graphique global
                if 'Total' in pivot_table.index:
                    pivot_clean = pivot_table.drop('Total')
                else:
                    pivot_clean = pivot_table
                
                if 'Total' in pivot_clean.columns:
                    pivot_clean = pivot_clean.drop('Total', axis=1)
                
                categories = [str(col) for col in pivot_clean.columns]
                total_values = []
                for col in categories:
                    val = pivot_clean[col].sum()
                    total_values.append(int(val) if pd.notna(val) else 0)
                
                chart_buffer = create_chart(
                    total_values,
                    "Répartition des statuts - Tous les projets",
                    categories
                )
                
                st.image(chart_buffer, use_container_width=True)
                
                # Graphiques par projet
                if 'Total' in pivot_table.index:
                    pivot_projects = pivot_table.drop('Total')
                else:
                    pivot_projects = pivot_table
                
                if 'Total' in pivot_projects.columns:
                    pivot_projects = pivot_projects.drop('Total', axis=1)
                
                for project_name in pivot_projects.index:
                    with st.expander(f"📊 {project_name}"):
                        project_data = pivot_projects.loc[project_name]
                        categories = [str(col) for col in project_data.index]
                        values = [int(project_data[col]) if pd.notna(project_data[col]) else 0 for col in categories]
                        
                        chart_buffer = create_chart(
                            values,
                            f"Répartition des statuts - {project_name}",
                            categories
                        )
                        st.image(chart_buffer, use_container_width=True)
                
                # Téléchargement des résultats
                st.subheader("📥 Télécharger les résultats")
                
                # Télécharger le tableau Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    pivot_table.to_excel(writer, sheet_name='tables')
                    df_modified.to_excel(writer, sheet_name='Compilation_processed', index=False)
                
                st.download_button(
                    label="📥 Télécharger le fichier Excel traité",
                    data=output.getvalue(),
                    file_name="resultats_traitement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Télécharger le PowerPoint (simplifié)
                try:
                    pptx_path = create_pptx(pivot_table, "temp.pptx")
                    with open(pptx_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le PowerPoint",
                            data=f.read(),
                            file_name="tableau_de_bord.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    os.remove(pptx_path)
                except Exception as e:
                    st.warning(f"⚠️ Génération du PowerPoint : {e}")
                
                st.success("✅ Traitement terminé avec succès !")
                
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {e}")
        st.code(f"{e}")

else:
    st.info("👈 Veuillez télécharger un fichier Excel dans la barre latérale")
    
    # Instructions
    st.markdown("""
    ### 📝 Instructions
    
    1. **Téléchargez** votre fichier Excel via la barre latérale
    2. Le fichier doit contenir une feuille nommée **"Compilation"**
    3. La ligne 3 du fichier doit contenir les en-têtes des colonnes
    4. Les colonnes nécessaires sont :
       - **PROJET** : identifiant du projet
       - **STATUT** : statut du projet (1.0, 2.0, 3.0, ...)
    5. Cliquez sur **"Traiter les données"**
    
    ### 🎨 Légende des statuts
    
    | Code | Signification |
    |------|---------------|
    | 1.0 | Point Bloquant |
    | 2.0 | A consulter |
    | 3.0 | Attente de devis |
    | 4.0 | Demande C/O |
    | 5.0 | A faire |
    | 5.1 | Devis en Validation |
    | 6.0 | Attente de livraison |
    | 6.1 | Attente de livraison (CONF W) |
    | 6.2 | Attente de livraison (Sans CONF) |
    | 7.0 | Litige |
    | 7.1 | Litige |
    | 8.0 | Réceptionné |
    | 9.0 | Terminé |
    """)

# Pied de page
st.markdown("---")
st.markdown("🔧 **Développé avec Streamlit** - SEGULA Technologies")
