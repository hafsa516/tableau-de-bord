import streamlit as st
import pandas as pd
from io import BytesIO
from utils.excel_processor import process_excel_data
from utils.chart_generator import create_chart
from utils.ppt_generator import create_pptx

st.set_page_config(page_title="Tableau de bord des projets", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord des projets - SEGULA Technologies")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_file = st.file_uploader("📁 Téléchargez votre fichier Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, sheet_name='Compilation', header=2)
        
        st.subheader("📊 Aperçu des données")
        st.dataframe(df.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Colonnes disponibles :**")
            for i, col in enumerate(df.columns):
                st.text(f"[{i}] {col}")
        
        with col2:
            projet_col = st.selectbox("Sélectionnez la colonne PROJET", options=df.columns.tolist(), index=1 if len(df.columns) > 1 else 0)
        
        with col3:
            statut_col = st.selectbox("Sélectionnez la colonne STATUT", options=df.columns.tolist(), index=22 if len(df.columns) > 22 else 0)
        
        commentaire_col = st.selectbox("Colonne Commentaire livraisons (optionnel)", options=["Aucune"] + df.columns.tolist(), index=0)
        if commentaire_col == "Aucune":
            commentaire_col = None
        
        if st.button("🚀 Traiter les données", type="primary"):
            with st.spinner("Traitement en cours..."):
                pivot_table, df_modified, statut_utilise = process_excel_data(df, projet_col, statut_col, commentaire_col)
                
                st.subheader("📊 Tableau croisé des statuts")
                st.dataframe(pivot_table, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📋 Nombre de projets", len(pivot_table) - 1 if 'Total' in pivot_table.index else len(pivot_table))
                with col2:
                    st.metric("📊 Nombre de statuts", len(pivot_table.columns) - 1 if 'Total' in pivot_table.columns else len(pivot_table.columns))
                with col3:
                    if 'Total' in pivot_table.index and 'Total' in pivot_table.columns:
                        total_ref = pivot_table.loc['Total', 'Total']
                    else:
                        total_ref = pivot_table.sum().sum()
                    st.metric("📈 Total références", int(total_ref) if pd.notna(total_ref) else 0)
                
                st.subheader("📊 Visualisation des données")
                
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
                
                chart_buffer = create_chart(total_values, "Répartition des statuts - Tous les projets", categories)
                st.image(chart_buffer, use_container_width=True)
                
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
                        values = []
                        for col in categories:
                            val = project_data[col]
                            values.append(int(val) if pd.notna(val) else 0)
                        
                        chart_buffer = create_chart(values, f"Répartition des statuts - {project_name}", categories)
                        st.image(chart_buffer, use_container_width=True)
                
                # ============================================================
                # TÉLÉCHARGER LES RÉSULTATS
                # ============================================================
                st.subheader("📥 Télécharger les résultats")
                
                # 1. Télécharger Excel
                output_excel = BytesIO()
                with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                    pivot_table.to_excel(writer, sheet_name='tables')
                    df_modified.to_excel(writer, sheet_name='Compilation_processed', index=False)
                
                output_excel.seek(0)
                
                st.download_button(
                    label="📥 Télécharger le fichier Excel traité",
                    data=output_excel.getvalue(),
                    file_name="resultats_traitement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # 2. Télécharger PowerPoint
                try:
                    # Créer le PowerPoint dans un buffer
                    pptx_buffer = BytesIO()
                    create_pptx(pivot_table, pptx_buffer)
                    pptx_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Télécharger le PowerPoint",
                        data=pptx_buffer.getvalue(),
                        file_name="tableau_de_bord.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                except Exception as e:
                    st.warning(f"⚠️ Erreur lors de la création du PowerPoint : {e}")
                
                st.success("✅ Traitement terminé avec succès !")
                
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.code(str(e))

else:
    st.info("👈 Téléchargez un fichier Excel dans la barre latérale")
    st.markdown("""
    ### 📝 Instructions
    1. Téléchargez votre fichier Excel
    2. Le fichier doit contenir une feuille **"Compilation"**
    3. La ligne 3 doit contenir les en-têtes
    4. Colonnes nécessaires : **PROJET** et **STATUT**
    
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

st.markdown("---")
st.markdown("🔧 **SEGULA Technologies**")
