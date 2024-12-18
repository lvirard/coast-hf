# -*- coding: utf8 -*-

"""
Misc tools for reading csv files (including QC) from Coriolis cotier / oco.

G. Charria (02/2022)



"""

# ---- Import general modules
import os,sys,datetime
import matplotlib.pyplot as mp
import numpy as np
import pandas as pd
import time

__all__ = ['read_hf','read_hf_sepQC']
__all__.sort()



# -------------------------------------------------------    

def read_hf(fil, 
        fullts=True, start='20190101', end='20190115',
        dispvar=False, var=['TEMP LEVEL1 (degree_Celsius)'],
        qc_control=True, chx_qc=[1,2],
        write_outdf=False, ftout='pkl',
        verbose=True):
    """
    
    Read csv files from COAST-HF.
    
    # fil: Fichier a lire (chemin absolu)
    
    # ---- Choix de la periode temporelle - format 'YYYYMMDD'
    # fullts = False # True: toute la series temporelle (ignore start/end) / False: periode entre start/end
    # start = '20080101'
    # end = '20080112'
    
    # ---- Variable a lire
    # Liste des variables a analyser (en dehors des informations de positions, de dates et de qc)
    # var = ['TEMP LEVEL1 (degree_Celsius)']
    # var = ['TEMP LEVEL1 (degree_Celsius)']
    # var = ['TEMP LEVEL1 (degree_Celsius)','PSAL LEVEL1 (psu)']
    # dispvar = False # True: le programme affiche la liste des variables disponibles (sans autre action) 
               # False: le programme s'execute sur la liste de variables demandees 
    
    # ---- Choix des QC retenus
    # qc_control=True # True: applique le choix de QC / False: ne tient pas compte des QC
    # chx_qc=[1,2] # Good and Probably good data
    # Liste des QC possibles: 0 - No QC was performed; 1 - Good data; 2- Probably good data; 3 - Bad data that are potentially correctable; 4 - Bad data; 5 - Value changed; 6 - Not used; 7 - Not used; 8 - Interpolated value; 9 - Missing value
    
    # ---- Ecriture des donnees luees dans un fichier:
    # write_outdf=True # True: Ecrit un fichier / False: N'ecrit pas de fichier
    # ftout = 'pkl' # Type de fichier de sortie: chier csvpkl' - fichier Pickle / 'csv' - fig 

    # ---- Autres parametres
    # verbose = True # Execute les print a l'execution / False: pas de print
    
    """

    if not fullts:
        dstart = pd.Timestamp(datetime.datetime(int(start[:4]),int(start[4:6]),int(start[6:])),tz='UTC')
        dend = pd.Timestamp(datetime.datetime(int(end[:4]),int(end[4:6]),int(end[6:])),tz='UTC')

    if verbose:
        print('-- Traitement du fichier: '+os.path.basename(fil))
        print('-- Lecture des variables existantes')
    # -- Lecture du debut du fichier pour la liste de variables
    df = pd.read_csv(fil,sep=",",nrows=1)
    varlist = df.keys()

    if dispvar:
        print(varlist)
        sys.exit() 

    if verbose:
        print('-- Identification des variables')
    # -- Variables de base    
    k_platform = [x for x in df.keys() if 'PLATFORM' in x]
    k_date = [x for x in df.keys() if 'DATE' in x]
    k_lat = [x for x in df.keys() if 'LATITUDE' in x]
    k_lon = [x for x in df.keys() if 'LONGITUDE' in x]
    k_qc = [x for x in df.keys() if 'QC' in x]

    # -- Variables demandee par l'utilisateur
    k_var=[]
    k_list = [k_platform[0],k_date[0],k_lat[0],k_lon[0],k_qc[0]]
    for v in var:
        vv = [x for x in df.keys() if v in x][0]
        k_var.append(vv)
        k_list.append(vv)
    
    # -- Lecture des donnees
    if verbose:
        print('-- Lecture des donnees du fichier ')
    if fullts:
        t = time.time()
        df = pd.read_csv(fil,sep=",", parse_dates=k_date, usecols=k_list)
        df=df.set_index(df[k_date[0]])
        elapsed = time.time()-t
        if verbose:
            print( "Elapsed time: %f seconds." %elapsed )
    
        # #- Tentative d'optimisation (chunksize) mais aussi long que methode au dessus - test sur Iroise - ...
        # t = time.time()
        # df_chunk = pd.read_csv(os.path.join(rep,f),sep=",", parse_dates=k_date, usecols=[k_platform[0],k_date[0],k_lat[0],k_lon[0],k_var[0]],chunksize=50000)
        # chunk_list=[]
        # for chunk in df_chunk:
        #     chunk_list.append(chunk)
        # df = pd.concat(chunk_list)
        # df=df.set_index(df[k_date[0]])
        # elapsed = time.time()-t
        # print( "Elapsed time: %f seconds." %elapsed )
        # #---
    
    
    else:
        t = time.time()
        df = pd.read_csv(fil,sep=",", parse_dates=k_date, usecols=k_list)
        df=df.set_index(df[k_date[0]])
        # df[df[k_date[0]].between(start, end)]  # Meme resultats que ligne en dessous
        df=df[(df.index>=dstart) & (df.index<=dend)]
        elapsed = time.time()-t
        if verbose:
            print( "Elapsed time (time selection): %f seconds." %elapsed )
    

    if verbose:
        print('-- Selection des QC')
    # QC for selected variables
    if qc_control:
        if len(var) > 1: # les dates avec les QC non retenus sont converties a np.nan
            for i,v in enumerate(var):
                k = k_var[i]
                nk_var=np.where(varlist == k)[0][0]
                qc_var=np.array([int(str(x)[nk_var:nk_var+1]) for x in df['QC']])
                df['QC '+k]=qc_var
                idx=np.array([],dtype='int32')
                for c in chx_qc:
                    idx=np.concatenate((idx,np.where(qc_var!=c)[0]))
                if len(chx_qc)>1:
                    idx = np.where(np.bincount(idx)>1)[0] # cherche les indices trouves plusieurs fois si chx_qc > 1 valeur        
                df[k][idx]=np.nan
        
        else: # les dates avec les QC non retenus sont supprimees
            k = k_var[0]
            nk_var=np.where(varlist == k)[0][0]
            qc_var=np.array([int(str(x)[nk_var:nk_var+1]) for x in df['QC']])
            df['QC '+k]=qc_var
            idx=np.array([],dtype='int32')
            for c in chx_qc:
                idx=np.concatenate((idx,np.where(qc_var==c)[0]))
            df = df.reset_index(drop=True)
            df=df.loc[idx]
            df=df.set_index(df[k_date[0]])
    df=df.drop(columns=['QC'])
    

    
    if write_outdf:
        
        f = os.path.basename(fil)
        if qc_control:    
            fout=f.split('.')[0]+'_s'+start+'_e'+end+'_var'+'_'.join([x[0:4] for x in var])+'_qc'+''.join([str(x) for x in chx_qc])+'.'+ftout
        else:
            fout=f.split('.')[0]+'_s'+start+'_e'+end+'_var'+'_'.join([x[0:4] for x in var])+'.'+ftout
        
        
        if ftout == 'pkl':
            df.to_pickle(os.path.join(repout,fout))
        elif ftout == 'csv':
            df.to_csv(path_or_buf=os.path.join(repout,fout),date_format='%Y-%m-%dT%H:%M:%SZ')
    

    # PLot
    # fig, ax = mp.subplots(nrows=1,ncols=1)
    # df.plot(y=k_var,ax = ax,label=[k_var[0]],linestyle='-',marker='.')
    
    
    return df
    




# -------------------------------------------------------    

def read_hf_sepQC(fil, 
        fullts=True, start='20190101', end='20190115',
        dispvar=False, var=['Water_Temp_degreeC'],
        qc_control=True, chx_qc=[1,2],
        write_outdf=False, ftout='pkl',
        verbose=True):
    """
    
    Read csv files from COAST-HF with separation of QC.
    ( exemple: fichier processe issue de Seanoe pour Marel Carnot )

    # fil: Fichier a lire (chemin absolu)
    
    # ---- Choix de la periode temporelle - format 'YYYYMMDD'
    # fullts = False # True: toute la series temporelle (ignore start/end) / False: periode entre start/end
    # start = '20080101'
    # end = '20080112'
    
    # ---- Variable a lire
    # Liste des variables a analyser (en dehors des informations de positions, de dates et de qc)
    # var = ['TEMP LEVEL1 (degree_Celsius)']
    # var = ['TEMP LEVEL1 (degree_Celsius)']
    # var = ['TEMP LEVEL1 (degree_Celsius)','PSAL LEVEL1 (psu)']
    # dispvar = False # True: le programme affiche la liste des variables disponibles (sans autre action) 
               # False: le programme s'execute sur la liste de variables demandees 
    
    # ---- Choix des QC retenus
    # qc_control=True # True: applique le choix de QC / False: ne tient pas compte des QC
    # chx_qc=[1,2] # Good and Probably good data
    # Liste des QC possibles: 0 - No QC was performed; 1 - Good data; 2- Probably good data; 3 - Bad data that are potentially correctable; 4 - Bad data; 5 - Value changed; 6 - Not used; 7 - Not used; 8 - Interpolated value; 9 - Missing value
    
    # ---- Ecriture des donnees luees dans un fichier:
    # write_outdf=True # True: Ecrit un fichier / False: N'ecrit pas de fichier
    # ftout = 'pkl' # Type de fichier de sortie: chier csvpkl' - fichier Pickle / 'csv' - fig 

    # ---- Autres parametres
    # verbose = True # Execute les print a l'execution / False: pas de print
    
    """

    if not fullts:
        dstart = pd.Timestamp(datetime.datetime(int(start[:4]),int(start[4:6]),int(start[6:])),tz='UTC')
        dend = pd.Timestamp(datetime.datetime(int(end[:4]),int(end[4:6]),int(end[6:])),tz='UTC')

    if verbose:
        print('-- Traitement du fichier: '+os.path.basename(fil))
        print('-- Lecture des variables existantes')
    # -- Lecture du debut du fichier pour la liste de variables
    df = pd.read_csv(fil,sep=",",nrows=1)
    varlist = df.keys()

    if dispvar:
        print(varlist)
        sys.exit() 

    if verbose:
        print('-- Identification des variables')
    # -- Variables de base    
    # k_platform = [x for x in df.keys() if 'PLATFORM' in x]
    # k_date = [x for x in df.keys() if 'DATE' in x]
    k_date = [x for x in df.keys() if 'time' in x]
    k_lat = [x for x in df.keys() if 'Latitude' in x]
    k_lon = [x for x in df.keys() if 'Longitude' in x]
    # k_qc = [x for x in df.keys() if 'QC' in x]

    # -- Variables demandee par l'utilisateur
    k_var=[]
    # k_list = [k_platform[0],k_date[0],k_lat[0],k_lon[0],k_qc[0]]
    k_list = [k_date[0],k_lat[0],k_lon[0]]
    for v in var:
        vv = [x for x in df.keys() if v in x][0]
        k_var.append(vv)
        k_list.append(vv)
        k_list.append('QC_'+vv)
    
    # -- Lecture des donnees
    if verbose:
        print('-- Lecture des donnees du fichier ')
    if fullts:
        t = time.time()
        df = pd.read_csv(fil,sep=",", parse_dates=k_date, usecols=k_list)
        df=df.set_index(df[k_date[0]])
        elapsed = time.time()-t
        if verbose:
            print( "Elapsed time: %f seconds." %elapsed )
    
        # #- Tentative d'optimisation (chunksize) mais aussi long que methode au dessus - test sur Iroise - ...
        # t = time.time()
        # df_chunk = pd.read_csv(os.path.join(rep,f),sep=",", parse_dates=k_date, usecols=[k_platform[0],k_date[0],k_lat[0],k_lon[0],k_var[0]],chunksize=50000)
        # chunk_list=[]
        # for chunk in df_chunk:
        #     chunk_list.append(chunk)
        # df = pd.concat(chunk_list)
        # df=df.set_index(df[k_date[0]])
        # elapsed = time.time()-t
        # print( "Elapsed time: %f seconds." %elapsed )
        # #---
    
    
    else:
        t = time.time()
        df = pd.read_csv(fil,sep=",", parse_dates=k_date, usecols=k_list)
        df=df.set_index(df[k_date[0]])
        # df[df[k_date[0]].between(start, end)]  # Meme resultats que ligne en dessous
        df=df[(df.index>=dstart) & (df.index<=dend)]
        elapsed = time.time()-t
        if verbose:
            print( "Elapsed time (time selection): %f seconds." %elapsed )
    

    if verbose:
        print('-- Selection des QC')
    # QC for selected variables
    if qc_control:
        if len(var) > 1: # les dates avec les QC non retenus sont converties a np.nan
            for i,v in enumerate(var):
                k = k_var[i]
                qc_var=df['QC_'+k]
                # nk_var=np.where(varlist == k)[0][0]
                # qc_var=np.array([int(str(x)[nk_var:nk_var+1]) for x in df['QC']])
                df['QC '+k]=qc_var
                idx=np.array([],dtype='int32')
                for c in chx_qc:
                    idx=np.concatenate((idx,np.where(qc_var!=c)[0]))
                if len(chx_qc)>1:
                    idx = np.where(np.bincount(idx)>1)[0] # cherche les indices trouves plusieurs fois si chx_qc > 1 valeur        
                df[k][idx]=np.nan
                df=df.drop(columns=['QC_'+k])
        
        else: # les dates avec les QC non retenus sont supprimees
            k = k_var[0]
            qc_var=df['QC_'+k]
            # nk_var=np.where(varlist == k)[0][0]
            # qc_var=np.array([int(str(x)[nk_var:nk_var+1]) for x in df['QC']])
            df['QC '+k]=qc_var
            idx=np.array([],dtype='int32')
            for c in chx_qc:
                idx=np.concatenate((idx,np.where(qc_var==c)[0]))
            df = df.reset_index(drop=True)
            df=df.loc[idx]
            df=df.set_index(df[k_date[0]])
            df=df.drop(columns=['QC_'+k])

    
    if write_outdf:
        
        f = os.path.basename(fil)
        if qc_control:    
            fout=f.split('.')[0]+'_s'+start+'_e'+end+'_var'+'_'.join([x[0:4] for x in var])+'_qc'+''.join([str(x) for x in chx_qc])+'.'+ftout
        else:
            fout=f.split('.')[0]+'_s'+start+'_e'+end+'_var'+'_'.join([x[0:4] for x in var])+'.'+ftout
        
        
        if ftout == 'pkl':
            df.to_pickle(os.path.join(repout,fout))
        elif ftout == 'csv':
            df.to_csv(path_or_buf=os.path.join(repout,fout),date_format='%Y-%m-%dT%H:%M:%SZ')
    

    # PLot
    # fig, ax = mp.subplots(nrows=1,ncols=1)
    # df.plot(y=k_var,ax = ax,label=[k_var[0]],linestyle='-',marker='.')
    
    
    return df
    




