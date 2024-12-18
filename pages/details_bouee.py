import os
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from accueil import bouees
from commands.read_insitu import read_hf
from glob import glob
import plotly.express as px

#---------------------------------Initialisation streamlit/congif page---------------------------------

st.set_page_config(page_title="App Coast-HF - détail", page_icon=":material/monitoring:",layout="wide")

#---------------------------------Initialisation des variables---------------------------------

data = {'min': None, 'varmin': None, 'max': None, 'varmax': None, 'mean': None, 'varmean': None},
periode = None # {'Dernières 24h', 'Semaine dernière', 'Mois dernier'}
parametre = None # {'Température', 'Salinité', 'Turbidité', 'Fluorescence'}
var_name = None # {'TEMP LEVEL1 (degree_Celsius)', 'PSAL LEVEL1 (psu)', 'TUR4 LEVEL1 (ntu)', 'FLU3 LEVEL1 (FFU)'}
unit = None #{'°C', 'PSU', 'NTU', 'FFU'}
df_plot = None

#------------------------------Définition des fonctions génériques-------------------------------

# 1. Fonction pour récupérer les n derniers fichiers modifiés
#TODO: pour l'instant on ne travaille que sur LAST, rendre la fonction plus simple ?
def get_last_n_files(search_pattern, n=1):
    # Récupération de la liste des fichiers
    try:
        listfile = glob(search_pattern)
    
        if len(listfile) == 0:
            print(f"Aucun fichier trouvé avec le pattern: {search_pattern}")
        else:
            # Création d'une liste de tuples (fichier, date de modification)
            files_with_dates = [(f, os.path.getmtime(f)) for f in listfile]
            
            # Tri des fichiers par date de modification (du plus récent au plus ancien)
            sorted_files = sorted(files_with_dates, key=lambda x: x[1], reverse=True)
            
            # Sélection des n premiers fichiers
            last_n_files = sorted_files[:n]
            
            # Affichage des fichiers sélectionnés pour test
            for file, timestamp in last_n_files:
                date = datetime.datetime.fromtimestamp(timestamp)
        return [f[0] for f in last_n_files]
    except:
        st.warning('Pas de données disponibles.')
        if st.button(" ← Retour à l'accueil"):
            st.session_state.parametre = "Température"
            st.session_state.periode = "Semaine dernière"
            st.switch_page("accueil.py")
    # Retourne uniquement les chemins des fichiers


# 2. Fonction pour calculer les statistiques & stocker les données
def stats_bouee(ftoread, periode, parametre):
    # Définition des dates de début et de fin en fonction de la période sélectionnée
    dend = datetime.datetime.now().strftime("%Y%m%d")
    if periode == "Dernières 24h":
        dstart = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        dstart_var = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y%m%d")
    elif periode == "Mois dernier":
        dstart = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y%m%d")
        dstart_var = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime("%Y%m%d")
    else:
        dstart = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y%m%d")
        dstart_var = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y%m%d")

    # Définition du nom de la variable & de l'unité
    if parametre == 'Fluorescence':
        var_name = 'FLU3 LEVEL1 (FFU)'
        unit = 'FFU'
    elif parametre == 'Salinité':
        var_name = 'PSAL LEVEL1 (psu)'   
        unit = 'PSU'
    elif parametre == 'Turbidité':
        var_name = 'TUR4 LEVEL1 (ntu)'
        unit = 'NTU'
    else:
        var_name = 'TEMP LEVEL1 (degree_Celsius)'
        unit = '°C'

    # Lecture des données
    try:
        df = read_hf(ftoread, 
                    fullts=False, 
                    start=dstart, 
                    end=dend, 
                    qc_control=False, 
                    var=[var_name], 
                    verbose=False
                    )
        dfvar = read_hf(ftoread, 
                        fullts=False, 
                        start=dstart_var, 
                        end=dstart,
                        qc_control=False, 
                        var=[var_name], 
                        verbose=False)
        # Calcul des statistiques & stockage dans data
        data = {
                'min': f'{np.min(df[var_name]):.2f} {unit}',
                'varmin': f'{(np.min(df[var_name])-np.min(dfvar[var_name])):.2f} {unit}',
                'max': f'{np.max(df[var_name]):.2f} {unit}',
                'varmax': f'{(np.max(df[var_name])-np.max(dfvar[var_name])):.2f} {unit}',
                'mean': f'{np.nanmean(df[var_name]):.2f} {unit}',
                'varmean': f'{(np.nanmean(df[var_name])-np.nanmean(dfvar[var_name])):.2f} {unit}'
            }
    
        # Création du DataFrame pour le graphique
        df_plot = pd.DataFrame({
                'Date': df.index,
                'Paramètre': df[var_name]
            }).set_index('Date')
    except:
        st.warning('Pas de données disponibles.')
        if st.button(" ← Retour à l'accueil"):
            st.session_state.parametre = "Température"
            st.session_state.periode = "Semaine dernière"
            st.switch_page("accueil.py")
    
    return data, df_plot, unit

#------------------------------Configuration de la page---------------------------------

def page_details():
    # ------ 1. Configuration générale ------

    # 1.1 Initialisation du session_state & retour page accueil si problème 
    if "bouee_selectionnee" not in st.session_state : 
        try:
            last_selected = st.query_params.get('bouee')
            if last_selected in bouees:
                st.session_state.bouee_selectionnee = last_selected
            else:
                st.switch_page("accueil.py")
                return
        except:
            st.switch_page("accueil.py")
            return
        
    # 1.2 Mise à jour des paramètres d'URL & session_state avec la bouée sélectionnée
    st.query_params["bouee"] = st.session_state.bouee_selectionnee
    bouee_selectionnee = st.session_state.bouee_selectionnee

    # 1.3 Mise à jour des paramètres d'URL & session_state avec la période sélectionnée
    if "periode" not in st.session_state:
        st.session_state.periode = "Semaine dernière"
    periode = st.session_state.periode

    # 1.4 Mise à jour des paramètres d'URL & session_state avec le paramètre sélectionné
    if "parametre" not in st.session_state:
        st.session_state.parametre = "Température"
    parametre = st.session_state.parametre

    # 1.5 Chargement des données
    dirf = os.path.join('.','data')

    # 1.6 Récupération directe des informations de la bouée sélectionnée
    bouee_info = bouees[bouee_selectionnee]
    plat = bouee_info["plateforme"]

    # 1.7 Recherche des fichiers pour la plateforme sélectionnée
    search_pattern = os.path.join(dirf, f'*{plat}.csv')
    last_files = get_last_n_files(search_pattern, n=1)

    # 1.8 Vérification si les données sont disponibles & appel de la fonction stats_bouee
    if len(last_files) == 0:
        st.warning(f'Pas de données disponibles pour la bouée {bouee_selectionnee}')
        return
    else:
        ftoread = last_files[0]
        data, df_plot, unit = stats_bouee(ftoread, periode, parametre)

    # ------ 2. Mise en forme & insertion du contenu ------

    # 2.1 Création de deux colonnes principales
    col_menu, col_principal = st.columns([1,3])
    
    # 2.2 Colonne de gauche (menu)
    with col_menu:
        #2.2.1 Titre 
        st.sidebar.title("Navigation")               

        # 2.2.2 Sélecteur de bouée      
        options = list(bouees.keys())  
        
        # 2.2.3 Définition de la selectbox pour la sélection de la bouée
        selected_bouee = st.sidebar.selectbox(
            "Sélectionner une bouée:", 
            options,
            index=options.index(bouee_selectionnee),
            key="bouee_selector",
            on_change=lambda: st.session_state.update({'bouee_selectionnee': st.session_state.bouee_selector})
        )
        
        # 2.2.4 Changement de la bouée sélectionnée
        if selected_bouee != bouee_selectionnee:
            st.session_state.bouee_selectionnee = selected_bouee
            st.rerun()
        
        # 2.2.5 Bouton retour accueil
        if st.sidebar.button("← Retour à l'accueil"):
            st.switch_page("accueil.py")

       
        # 2.2.6 Formulaire de sélection de la période & du paramètre
        with st.sidebar.form("selection_donnees"):
            st.subheader("Sélection des données")
            
            parametre = st.selectbox(
                "Paramètre à afficher",
                ["Température", "Salinité", "Turbidité", "Fluorescence"]
            )
            #TODO: ajouter une option de type case à cocher "hauteur d'eau" afin d'intégrer les marées dans les graphs
            #hauteur_eau = st.checkbox("Hauteur d'eau", value=False)

            periode = st.selectbox(
                "Période",
                ["Semaine dernière", "Dernières 24h", "Mois dernier"]
            )
            #TODO: ajouter une option "Année dernière"
            
            # 2.2.7 Bouton pour actualiser les données
            if st.form_submit_button("Actualiser"):
                st.session_state.periode = periode  
                st.session_state.parametre = parametre
                st.rerun()

        # 2.2.8 Informations sur la bouée
        st.sidebar.subheader("Informations")
        st.sidebar.write(f"""
                         Les paramètres sont mesurés par des capteurs intégrés à la bouée directement sur place, dans l'eau de mer, toutes les 20 minutes.<br>
                         La température correspond donc à la température de l'eau.<br>
                         La salinité correspond à la concentration de sel dans l'eau. L'océan est en moyenne entre 33 et 34 PSU.<br>
                         La turbidité correspond à l'aspect plus ou moins trouble de l'eau. Une turbidité de 0 est une eau complètement transparente.<br>
                         La fluorescence mesure indirectement la concentration de phytoplancton dans l'eau. <br>
                         <br>
                         [Accéder à plus données pour {bouee_selectionnee}](https://data.coriolis-cotier.org/platform/{bouees[bouee_selectionnee]["plateforme"]})<br>
                         [Plus d'informations sur Coast-HF](https://coast-hf.fr)
                    """, unsafe_allow_html=True)

    # 2.3 Colonne principale (dashboard)
    with col_principal:
        #2.3.1 Titre de la page
        st.title(f"{bouee_selectionnee}")
        st.subheader(f"{parametre} - {periode}")
        
        # 2.3.2 Métriques principales
        col1, col2, col3 = st.columns(3)
        
        # 2.3.3 Vérification si les données sont disponibles
        has_data = all(value is not None for value in data.values())
        
        # 2.3.4 Affichage des métriques
        if has_data:
            if periode == 'Mois dernier':
                with col1:
                    st.metric("Moyenne", f'{data["mean"]}')
                with col2:
                    st.metric("Maximum", f'{data["max"]}')
                with col3:
                    st.metric("Minimum", f'{data["min"]}')
            else : 
                with col1:
                    st.metric("Moyenne", f'{data["mean"]}', f'{data["varmean"]}')
                with col2:
                    st.metric("Maximum", f'{data["max"]}', f'{data["varmax"]}')
                with col3:
                    st.metric("Minimum", f'{data["min"]}', f'{data["varmin"]}')
                if periode == "Dernières 24h":
                    st.write(f"L'indice mesuré correspond à la différence entre la veille et l'avant-veille, pour la moyenne, le maximum et le minimum.")
                else :
                    st.write(f"L'indice mesuré correspond à la différence entre la semaine qui vient de s'écouler et celle juste avant, pour la moyenne, le maximum et le minimum.")
        else:
            st.warning(f"⚠️ Les données remontées pour {bouee_selectionnee} sur la période '{periode}' sont insuffisantes.")
                           
        # Graphique 
        st.subheader(f"Évolution de la {parametre.lower()} - {periode}")

        try:
            # Vérification des données avant d'afficher le graphique
            if df_plot.empty or df_plot['Paramètre'].isna().all():
                st.warning(f"⚠️ Pas assez de données disponibles pour afficher le graphique sur la période '{periode}'.")
            else:
                # fig=px.line(df_plot)
                # st.plotly_chart(fig, x_label="Temps", y_label=(f'{parametre}, en {unit}'), theme="streamlit", use_container_width=True)
                # Création du graphique avec Plotly
                fig = px.line(df_plot, x=df_plot.index, y='Paramètre', markers=True)
                
                # Personnalisation des marqueurs
                fig.update_traces(marker=dict(size=4, symbol='circle'))  # Ajustez la taille, la couleur et le symbole

                # Ajustement des axes
                min_value = df_plot['Paramètre'].min()
                max_value = df_plot['Paramètre'].max()

                # Définir les limites de l'axe Y avec une marge
                fig.update_yaxes(title_text=(f'{parametre}, en {unit}'), range=[min_value - 0.3 * (max_value - min_value), max_value + 0.3 * (max_value - min_value)])

                # Personnaliser l'axe X pour le rendre plus lisible
                fig.update_xaxes(title_text='Temps', tickformat='%Y-%m-%d %H:%M', dtick='D1')  # Format de date et intervalle

                # Afficher le graphique
                st.plotly_chart(fig, use_container_width=True)
    
        except Exception as e:
            st.warning(f"⚠️ Impossible d'afficher le graphique pour la période sélectionnée: {str(e)}")

               
page_details() 