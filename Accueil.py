import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# Au début de votre code, activez le mode débogage
st.set_option('client.showErrorDetails', True)


# Initialisation de l'état partagé et remise à zéro de la bouée sélectionnée
# if "bouee_selectionnee" not in st.session_state:
#     st.session_state.bouee_selectionnee = None
st.session_state.bouee_selectionnee = None

# 1. Données de bouées
bouees = {
    'MAREL - Entrée de la rade de Brest': {'lat': 48.35796, 'lon': -4.55175, 'id': 1, "plateforme": "6200450"},
    'SMART - Fond de la rade de Brest': {'lat': 48.318, 'lon': -4.336, 'id': 2, "plateforme": "IF000700"   },
    'ASTAN - Roscoff': {'lat': 48.7777, 'lon': -3.9375, 'id': 3, "plateforme": "EXIN0005"},
    'SMILE - Luc-Sur-Mer': {'lat': 49.3438, 'lon': -0.3074, 'id': 4, "plateforme": "6200310"},
    'SCENES - Baie de Seine': {'lat': 49.481, 'lon': 0.032, 'id': 5, "plateforme": "SCENES"},
    'MAREL - CARNOT - Boulogne-Sur-Mer': {'lat': 50.7405, 'lon': 1.5677, 'id': 6, "plateforme": "6200443"},
    'MOLIT - Baie de Vilaine': {'lat': 47.4600, 'lon': -2.6567, 'id': 7, "plateforme": "6200021"},
    'FERRET - Arcachon Ferret': {'lat': 44.6330, 'lon': -1.2330, 'id': 8, "plateforme": "EXIN0001"},
    'SOLA - Banyuls-Sur-Mer': {'lat': 42.48333, 'lon': 3.13333, 'id': 9, "plateforme": "EXIN0006"},
    'POEM - Perpignan': {'lat': 42.70416, 'lon': 3.06724, 'id': 10, "plateforme": "EXIN0003"},
    'BESSète - Sète': {'lat': 43.33416, 'lon': 3.64389, 'id': 11, "plateforme": "EXIN0007"},
    'MESURHO - Estuaire du Rhône': {'lat': 43.3189, 'lon': 4.8662, 'id': 12, "plateforme": "6100284"},
    'SOLEMIO - Marseille': {'lat': 43.23877, 'lon': 5.28526, 'id': 13, "plateforme": "EXIN0004"},
    'EOL - Villefranche-Sur-Mer': {'lat': 43.683, 'lon': 7.317, 'id': 14, "plateforme": "EXIN0002"},
    }

# 2. Fonction pour afficher la carte interactive
def afficher_carte():
    # Initialisation de la carte
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=5)
    
    # Ajout des bouées à la carte
    marker_cluster = MarkerCluster().add_to(m)
    for nom, info in bouees.items():
        
        icon = folium.CustomIcon(
            icon_image=os.path.join("Media","logo.png"),
            icon_size=(35, 35)
        )
        
        folium.Marker(
            [info['lat'], info['lon']], 
            tooltip=nom,
            icon=icon
        ).add_to(marker_cluster)
    
    # Affichage de la carte dans Streamlit
    output = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])
    return output

# 3. Page d'accueil
def page_accueil():
    st.set_page_config(page_title="App Coast-HF - accueil", page_icon=":material/monitoring:",layout="centered")

    st.title("Coast HF - Quelles données pour ma bouée ?") #Titre à changer
    
    # 3.1 Sélection d'une bouée
  
    # Ajout d'une option "Sélectionner une bouée" par défaut
    options = ["Sélectionner une bouée..."] + list(bouees.keys())
    
    # Si une bouée est sélectionnée, la présélectionner
    default_index = options.index(st.session_state.bouee_selectionnee) if st.session_state.bouee_selectionnee in options else 0
    
    # Donner un ID spécifique au selectbox
    bouee_selectionnee = st.selectbox(
        "Sélectionner une bouée:", 
        options,
        index=default_index,
        key="bouee_selector"
    )
    
    # 3.2 Affichage de la carte avec récupération du dernier clic
    try:
        output = afficher_carte()
    except Exception as e:
        st.error(f"Une erreur s'est produite : {str(e)}")
    
    # 3.3 Mentions légales 
    st.image(os.path.join("Media","COAST-HF-logo.png"), width=100)
    st.write("COAST-HF (Coastal OceAn observing SysTem – High Frequency) est un Service national d'observation appartenant à l'Infrastructure de Recherche ILICO. Ce réseau, labellisé par le CNRS, vise à fédérer et cordonner à l'échelle du littoral français un ensemble de plateformes fixes instrumentées de mesures in situ hautes fréquences pour des paramètres clés des eaux côtières.")
    st.write("Site web du projet : [Coast HF](https://coast-hf.fr)")

    # 3.4 Passage à la page détails
    # Via la carte - Vérification du dernier clic
    if output and "last_object_clicked" in output:
        clicked_position = output["last_object_clicked"]
        if clicked_position is not None:
            for nom, info in bouees.items():
                if (info['lat'], info['lon']) == (clicked_position['lat'], clicked_position['lng']):
                    st.session_state.bouee_selectionnee = nom
                    st.switch_page("pages/Data.py")
                    break

    # Via la selection de la bouée dans le selectbox
    if bouee_selectionnee != "Sélectionner une bouée...":
        st.session_state.bouee_selectionnee = bouee_selectionnee
        st.switch_page("pages/Data.py")

# 4. Appel de la page d'accueil
page_accueil()
