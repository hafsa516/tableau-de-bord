# Dans app.py, remplacer la partie téléchargement PowerPoint par :

st.subheader("📥 Télécharger les résultats")

# Télécharger Excel
output_excel = BytesIO()
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    pivot_table.to_excel(writer, sheet_name='tables')
    df_modified.to_excel(writer, sheet_name='Compilation_processed', index=False)

st.download_button(
    label="📥 Télécharger le fichier Excel traité",
    data=output_excel.getvalue(),
    file_name="resultats_traitement.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Télécharger PowerPoint
try:
    # Créer le PowerPoint
    pptx_buffer = BytesIO()
    create_pptx(pivot_table, pptx_buffer)
    pptx_buffer.seek(0)
    
    st.download_button(
        label="📥 Télécharger le PowerPoint",
        data=pptx_buffer,
        file_name="tableau_de_bord.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
except Exception as e:
    st.warning(f"⚠️ Erreur lors de la création du PowerPoint : {e}")
