import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn 
from datetime import datetime
import glob
import os
import simple_colors
from simple_colors import *
from fpdf import FPDF, Align, XPos, YPos
import shutil
from pdfrw import  PdfReader
from pdfrw import PdfReader
from pdfrw.toreportlab import makerl
from pdfrw.buildxobj import pagexobj
import multiprocessing
from tkinter import *
import time
import PySimpleGUI as sg
import threading

def entries_extractor():

              sg.theme("LightGrey1")               
              sg.set_global_icon(r"vorlage/V_icon.ico")
              layout = [
 
                  [sg.Image(filename=r"vorlage/Vahle_Logo_gui.png", expand_x=True, expand_y=True)],
                  [sg.Text('')],
                  [sg.Text('* Required Fields')],

                  [sg.Text('Logo der kundenfirma: ', size =(55, 1)),sg.Input(key="company_logo", right_click_menu=[[''], ['Paste Logo']]), sg.FileBrowse()],
                  [sg.Text('* Referenzdaten Excel Datei: ', size =(55, 1)),sg.Input(key="company_logo1", right_click_menu=[[''], ['Paste']]), sg.FileBrowse()],
                  [sg.Text('Darstellung des Systems und der Komponenten: ', size =(55, 1)),sg.Input(key="self.smart_collector_components_pic", right_click_menu=[[''], ['Paste Bild1 pfad']]), sg.FileBrowse()],
                  [sg.Text('Stromabnehmer mit 3D-Sensor: ', size =(55, 1)),sg.Input(key="self.smart_collector_with_3d_sensor_pic", right_click_menu=[[''], ['Paste Bild2 pfad']]), sg.FileBrowse()],
                  [sg.Text('* Speichern unter : ', size =(55, 1)),sg.Input(key="self.save_directory", right_click_menu=[[''], ['Paste Pfad']]), sg.FolderBrowse()],
                  [sg.Text('Angaben zum System: ')],
                  [sg.Text('Name der Kundenfirma:', size =(55, 1)), sg.Input(key="company_name", right_click_menu=[[''], ['Paste Name']])],
                  [sg.Text('Name der Stromabnehmer Serie:', size =(55, 1)), sg.Combo(values=['KDS2/40', 'KUFR2/40','KESR', 'KESL'], key="Stromabnehmer_Serie")],
                  [sg.Text('Link zum Dashboard des kunden Firma:', size =(55, 1)), sg.Input(key="dashboard_link",right_click_menu=[[''], ['Paste Link']])],
                  [sg.Text('Kommentar zur Reihenfolge der Abnehmer (Deutsch Bericht Version):', size =(55, 1)), sg.Input(key="Stromabnehmer_order", right_click_menu=[[''], ['Paste Reinfolge DE']])],
                  [sg.Text('Kommentar zur Reihenfolge der Abnehmer (Englisch Bericht Version):', size =(55, 1)), sg.Input(key="Stromabnehmer_order_EN", right_click_menu=[[''], ['Paste Reinfolge EN']])],
                  [sg.Button('submit') , sg.Cancel()]
              ]
                
              window = sg.Window('VTC - Smart Collector Bericht Angaben', layout)
              while True:  
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'submit' or event =='Cancel':
                         break
                if event == 'Paste Logo':
                      window["company_logo"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste':
                      window["company_logo1"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Bild1 pfad':
                      window["self.smart_collector_components_pic"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Bild2 pfad':
                      window["self.smart_collector_with_3d_sensor_pic"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Pfad':
                      window["self.save_directory"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Name':
                      window["company_name"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Reinfolge DE':
                      window["Stromabnehmer_order"].update(sg.clipboard_get(), paste=True)                    
                elif event == 'Paste Link':
                      window["dashboard_link"].update(sg.clipboard_get(), paste=True)
                elif event == 'Paste Reinfolge EN':
                     window["Stromabnehmer_order_EN"].update(sg.clipboard_get(), paste=True)
              
              window.close()

              customer_company_logo=values["company_logo"]
              excel_file_path=values["company_logo1"]
              smart_collector_components_pic=values["self.smart_collector_components_pic"]
              smart_collector_with_3d_sensor_pic=values["self.smart_collector_with_3d_sensor_pic"]
              save_directory=values["self.save_directory"]
              customer_company_name=values["company_name"] 
              name_of_the_Stromabnehmer_series= values["Stromabnehmer_Serie"]
              armes_order_extra_section=values["Stromabnehmer_order"]
              link_to_customer_company_dashboard = values["dashboard_link"]    
              armes_order_extra_section_EN = values["Stromabnehmer_order_EN"]    
              return  customer_company_logo,excel_file_path,smart_collector_components_pic,smart_collector_with_3d_sensor_pic,save_directory,customer_company_name, name_of_the_Stromabnehmer_series,armes_order_extra_section, link_to_customer_company_dashboard, armes_order_extra_section_EN      


class Tools(pd.DataFrame):   
    
    def anomalies_warning_failure_plotter(mov_avg_df , positions_df, direction, plot_type): 
            
            dir = 'images'
            working_directory = os.path.abspath(dir)
            abstand_str = 'Abstand'
            auslenkung_str = 'Auslenkung'
            if direction == 'Abstand':  
                    filter_cols = mov_avg_df[[col for col in mov_avg_df.columns if (abstand_str  in col or 'Position' in col) ]]
                    seaborn.set(rc={'figure.figsize':(6,4)})
                    for idx, df_row in enumerate(positions_df.values):
                            figu = plt.figure(idx)
                            subset = filter_cols[filter_cols['Position'].between(df_row[0]-200, df_row[1]+200)]
                            subset_MA = subset.drop(['Abstand_Diff', 'Abstand_Normal', 'Abstand_Error'],  axis = 1)
                            subsetm = subset_MA.melt('Position', var_name='', value_name='Mittelwert')
                            seaborn.set_style("darkgrid")
                            seaborn.color_palette("pastel")
                            ax1 = seaborn.scatterplot(x="Position", y="Mittelwert", s=10, hue='', data=subsetm,  edgecolor="none")
                            seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                            plt.tight_layout()
                            plt.title('Hub', fontsize=16, loc='center', pad=15)
                            if plot_type == 'anomalie':      
                                  file_name=os.path.abspath(working_directory+'/Anomalie_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            elif plot_type == 'warning': 
                                  file_name=os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            elif plot_type == 'failure': 
                                  file_name=os.path.abspath(working_directory+'/Failure_Hub_'+ str(df_row[0]) +"_" + str(df_row[1])+'.jpeg')
                            plt.switch_backend('agg')       
                            figu.savefig(file_name)
                            plt.close()
            
            elif direction ==  'Auslenkung':  

                    filter_cols = mov_avg_df[[col for col in mov_avg_df.columns if (auslenkung_str  in col or 'Position' in col) ]]
                    seaborn.set(rc={'figure.figsize':(6,4)})
                    for idx, df_row in enumerate(positions_df.values):
                    
                                figu = plt.figure(idx)
                                subset = filter_cols[filter_cols['Position'].between(df_row[0]-200, df_row[1]+200)]
                                subset_MA = subset.drop(['Auslenkung_Diff', 'Auslenkung_Normal', 'Auslenkung_Error'],  axis = 1)
                                subsetm = subset_MA.melt('Position', var_name='', value_name='Mittelwert')
                                seaborn.set_style("darkgrid")
                                seaborn.color_palette("pastel")            
                                ax1 = seaborn.scatterplot(x="Position", y="Mittelwert", s=10, hue='', data=subsetm,  edgecolor="none")
                                seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                                plt.tight_layout()            
                                plt.title('Auslenkung', fontsize=16, loc='center', pad=15)
                                if plot_type == 'anomalie':
                                        file_name=os.path.abspath(working_directory+'/Anomalie_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                elif plot_type == 'warning': 
                                        file_name=os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                elif plot_type == 'failure': 
                                        file_name=os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +"_" + str(df_row[1])+'.jpeg')
                                plt.switch_backend('agg')
                                figu.savefig(file_name)                        
                                plt.close()

            elif direction == 'Lift':
                            
                    abstand_str = 'Lift'
                    auslenkung_str = 'Defelection'
                    filter_cols = mov_avg_df[[col for col in mov_avg_df.columns if (abstand_str  in col or 'Position' in col)]]
                    seaborn.set(rc={'figure.figsize':(6,4)})
                    for idx, df_row in enumerate(positions_df.values):
                                figu = plt.figure(idx)
                                subset = filter_cols[filter_cols['Position'].between(df_row[0]-200, df_row[1]+200)]
                                subsetm = subset.melt('Position', var_name='', value_name='Moving Average')
                                seaborn.set_style("darkgrid")
                                seaborn.color_palette("pastel")            
                                ax1 = seaborn.scatterplot(x="Position", y="Moving Average", s=10, hue='', data=subsetm,  edgecolor="none")
                                seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                                plt.tight_layout()
                                plt.title('Lift', fontsize=16, loc='center', pad=15)
                                if plot_type == 'anomalie':
                                        file_name = str(working_directory+'/Anomalie_Hub_EN_'+ str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')
                                elif plot_type == 'warning': 
                                        file_name = str(working_directory+'/Warning_Hub_EN_'+ str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')
                                elif plot_type == 'failure': 
                                        file_name = str(working_directory+'/Failure_Hub_EN_'+ str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')
                                plt.switch_backend('agg')
                                figu.savefig(file_name)
                                plt.close()
                    
            elif direction == 'Deflection':
                    abstand_str = 'Lift'
                    auslenkung_str = 'Deflection'
                    filter_cols = mov_avg_df[[col for col in mov_avg_df.columns if auslenkung_str  in col or 'Position' in col]]
                    seaborn.set(rc={'figure.figsize':(6,4)})
                    for idx, df_row in enumerate(positions_df.values):
                                figu = plt.figure(idx)
                                subset = filter_cols[filter_cols['Position'].between(df_row[0]-200, df_row[1]+200)]
                                subsetm = subset.melt('Position', var_name='', value_name='Moving Average')
                                seaborn.set_style("darkgrid")
                                seaborn.color_palette("pastel")            
                                ax1 = seaborn.scatterplot(x="Position", y="Moving Average", s=10, hue='', data=subsetm,  edgecolor="none")
                                seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                                plt.tight_layout()
                                plt.title('Deflection', fontsize=16, loc='center', pad=15)
                                if plot_type == 'anomalie':
                                        file_name = str(working_directory+'/Anomalie_Auslenkung_EN_'+ str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')                               
                                elif plot_type == 'warning':                                         
                                        file_name = str(working_directory+'/Warning_Auslenkung_EN_'+str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')
                                elif plot_type == 'failure': 
                                        file_name = str(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +"_" + str(df_row[1])+r'.jpeg')
                                plt.switch_backend('agg')
                                figu.savefig(file_name)
                                plt.close()
    
    def dataframe_filter(dataframe, filter_value): 
        
      if not dataframe.empty:  
        current_start = 0
        current_end = 0
        next_start = 0
        next_end = 0
        dataframe_refined = pd.DataFrame(columns = ['Start Position', 'End Position'])
        temp_df = pd.DataFrame(columns = ['Start Position', 'End Position'])
        rows = dataframe.iloc[0].tolist()
        i = 0
        current_start = rows[0]
        current_end = rows[1]
        temp = []
        while(i < len(dataframe)):
            next_rows = dataframe.iloc[i]
            next_start = next_rows[0]
            next_end  = next_rows[1]
            if current_end !=  next_end:
                if next_start - current_end > filter_value and current_start in temp:
                    temp_df = pd.DataFrame(columns = ['Start Position', 'End Position'])
                    temp_df.loc[len(temp_df)] = temp
                    dataframe_refined = pd.concat([dataframe_refined, temp_df], axis = 0)
                    current_start = next_start
                    
                    current_end = next_end
            temp = [current_start, next_end]      
            i += 1
        
        temp_df = pd.DataFrame(columns = ['Start Position', 'End Position'])
        temp_df.loc[len(temp_df)] = temp
        dataframe_refined = pd.concat([dataframe_refined, temp_df], axis = 0)
        dataframe_refined.index = dataframe_refined.reset_index(drop = True).index    

        return dataframe_refined
      
      else: 
              
        pass 
        return dataframe
        


            
    def filter_between_start_end(dataframe): 
            
            for i, df_row in enumerate(dataframe.values): 
                if df_row[1]  - df_row[0] < 100: 
                     dataframe = dataframe.drop(i)
            dataframe.index = dataframe.reset_index(drop = True).index + 1
            if not dataframe.empty:
                   return dataframe
            else: 
                   dataframe= pd.DataFrame()

                   return dataframe 

    def filter_accending_dataframe_values(dataframe): 
                    dataframe_refined_sorted = dataframe.values
                    dataframe_organized_min_order = np.sort(dataframe_refined_sorted, axis= None)
                    dataframe_organized_min_order = dataframe_organized_min_order.reshape(-1, 2)
                    dataframe_refined_sorted = pd.DataFrame(dataframe_organized_min_order)
                    dataframe_refined_sorted.index = dataframe_refined_sorted.reset_index(drop=True).index+1
                    return dataframe_refined_sorted

    def smoothing_filter(dataframe):
            if not dataframe.empty: 
                if len(dataframe) > 5:
                    i=0
                    elements = []
                    for i, df_row in  enumerate(dataframe.values): 
                            if i < (len(dataframe)- len(dataframe)/2-2):
                                beginning =  dataframe['Start Position'].iloc[0::1].iloc[0]
                                end = dataframe['End Position'].iloc[::-1].iloc[0]
                                current_start = dataframe['Start Position'].iloc[2::2].iloc[i]
                                current_end = dataframe['End Position'].iloc[2::2].iloc[i]
                                next_start = dataframe['Start Position'].iloc[3::2].iloc[i]
                                next_end = dataframe['End Position'].iloc[3::2].iloc[i]
 
                                if not current_end - current_start < 100 : 
                                     if not next_end - next_start < 100:
                                         elements.append(current_start)
                                         elements.append(current_end)
                                         elements.append(next_start)
                                         elements.append(next_end)

                    elements.append(beginning)
                    elements.append(end)
                    elements = np.array(elements)                    
                    elements = np.sort(elements, axis=None)
                    elements = elements.reshape(-1,2)
                    elements = pd.DataFrame(elements)
                    elements.index = elements.reset_index(drop=True).index         
                    if elements.empty:
                         pass
                    else: 
                         elements.columns = ['Start Position', 'End Position']
                    return elements
                else:
                    i=0
                    elements = []
                    for i, df_row in  enumerate(dataframe.values): 
                                beginning =  dataframe['Start Position'].iloc[0]
                                end = dataframe['End Position'].iloc[::-1].iloc[0] 
                    elements.append(beginning)
                    elements.append(end)
                    elements = np.array(elements)                    
                    elements = np.sort(elements, axis=None)
                    elements = elements.reshape(-1,2)
                    elements = pd.DataFrame(elements)
                    elements.index = elements.reset_index(drop=True).index         
                    if elements.empty:
                          
                         return dataframe
                    else: 
                         elements.columns = ['Start Position', 'End Position']
                    return elements                                                       
            else: 
                    dataframe = dataframe.iloc[0:0]
                    return dataframe                 

    def warning_positions_extractor(mov_avg_df, column):
            temp = pd.DataFrame()
            warning_groups_minus = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] <= -10)].groupby((mov_avg_df[str(column)] > -10 ).cumsum()):
            
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                warning_groups_minus = pd.concat([warning_groups_minus, temp])
            if warning_groups_minus.empty:
                print('There are no warning with the selected distance!')
            else:
                warning_groups_minus.columns = ['Start Position', 'End Position']
                warning_groups_minus.index = warning_groups_minus.reset_index(drop = True).index 
            temp = pd.DataFrame()
            warning_groups_positive = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] >= 10)].groupby((mov_avg_df[str(column)] < 10 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                warning_groups_positive = pd.concat([warning_groups_positive, temp])
            if warning_groups_positive.empty:
                print('There are no warning with the selected distance!')
            else:
                warning_groups_positive.columns = ['Start Position', 'End Position']
                warning_groups_positive.index = warning_groups_positive.reset_index(drop = True).index 
            groups_refined = pd.concat([warning_groups_minus, warning_groups_positive], axis = 0)
            groups_refined.index = groups_refined.reset_index(drop = True).index 

            return groups_refined


    def anomalies_extractor(mov_avg_df, column): 
            
            temp = pd.DataFrame()
            anomalies_dataframe = pd.DataFrame()
            for k, v in mov_avg_df[mov_avg_df[str(column)] > 0].groupby((mov_avg_df[str(column)] == 0).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1)
                anomalies_dataframe = pd.concat([anomalies_dataframe, temp])
            if anomalies_dataframe.empty:
                print('There are no anomalies with the selected distance!')
            else:
                anomalies_dataframe.columns = ['Start Position', 'End Position']
                anomalies_dataframe.index = anomalies_dataframe.reset_index(drop = True).index  
            return anomalies_dataframe   
    
    
    def failure_positions_extractor(mov_avg_df, column):
            temp = pd.DataFrame()
            failure_groups_positive = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] >= 15)].groupby((mov_avg_df[str(column)] < 15 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                failure_groups_positive = pd.concat([failure_groups_positive, temp])
            if failure_groups_positive.empty:
                print('There are no warning with the selected distance!')
            else:
                failure_groups_positive.columns = ['Start Position', 'End Position']
                failure_groups_positive.index = failure_groups_positive.reset_index(drop = True).index 
            

            temp = pd.DataFrame()
            failure_groups_negative = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] <= -15)].groupby((mov_avg_df[str(column)] > -15 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                failure_groups_negative = pd.concat([failure_groups_negative, temp])
            if failure_groups_negative.empty:
                print('There are no warning with the selected distance!')
            else:
                failure_groups_negative.columns = ['Start Position', 'End Position']
                failure_groups_negative.index = failure_groups_negative.reset_index(drop = True).index 
            groups_refined = pd.concat([failure_groups_negative, failure_groups_positive], axis = 0)
            groups_refined.index = groups_refined.reset_index(drop = True).index 

            return groups_refined

    def KESL_warning_positions_extractor(mov_avg_df, column):
            temp = pd.DataFrame()
            warning_groups_negative = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] <= -20)].groupby((mov_avg_df[str(column)] > -20 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                warning_groups_negative = pd.concat([warning_groups_negative, temp])
            if warning_groups_negative.empty:
                print('There are no warning with the selected distance!')
            else:
                warning_groups_negative.columns = ['Start Position', 'End Position']
                warning_groups_negative.index = warning_groups_negative.reset_index(drop = True).index 
            
            temp = pd.DataFrame()
            warning_groups_positive = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] >= 20)].groupby((mov_avg_df[str(column)] < 20 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                warning_groups_positive = pd.concat([warning_groups_positive, temp])
            if warning_groups_positive.empty:
                print('There are no warning with the selected distance!')
            else:
                warning_groups_positive.columns = ['Start Position', 'End Position']
                warning_groups_positive.index = warning_groups_positive.reset_index(drop = True).index 
            groups_refined = pd.concat([warning_groups_negative, warning_groups_positive], axis = 0)
            return groups_refined

    def KESL_failure_positions_extractor(mov_avg_df, column):
            temp = pd.DataFrame()
            failure_groups_positive = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] >= 30)].groupby((mov_avg_df[str(column)] < 30 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                failure_groups_positive = pd.concat([failure_groups_positive, temp])
            if failure_groups_positive.empty:
                print('There are no warning with the selected distance!')
            else:
                failure_groups_positive.columns = ['Start Position', 'End Position']
                failure_groups_positive.index = failure_groups_positive.reset_index(drop = True).index 
            temp = pd.DataFrame()
            failure_groups_negative = pd.DataFrame()
            for k, v in mov_avg_df.loc[(mov_avg_df[str(column)] <= -30)].groupby((mov_avg_df[str(column)] > -30 ).cumsum()):
                selected_rows = v[['Position']]
                temp = pd.concat([selected_rows.head(1).reset_index(drop = True), selected_rows.tail(1).reset_index(drop = True)], axis = 1) 
                failure_groups_negative = pd.concat([failure_groups_negative, temp])
            if failure_groups_negative.empty:
                print('There are no warning with the selected distance!')
            else:
                failure_groups_negative.columns = ['Start Position', 'End Position']
                failure_groups_negative.index = failure_groups_negative.reset_index(drop = True).index 

            groups_refined = pd.concat([failure_groups_positive, failure_groups_negative], axis = 0)
            groups_refined.index = groups_refined.reset_index(drop = True).index 
            return groups_refined
    
    def plot_general_view(moving_average_dataframe, directions): 
            
            dir = 'images'
            working_directory = os.path.abspath(dir)
            hub_general_view_path_DE = working_directory +'/Plot_Hub_DE'+ '.jpeg'
            hub_general_view_path_EN = working_directory +'/Plot_Hub_EN'+ '.jpeg'
            auslenkung_general_view_path_DE = working_directory+'/Plot_Auslenkung_DE'+'.jpeg' 
            auslenkung_general_view_path_EN = working_directory+'/Plot_Auslenkung_EN'+'.jpeg'    

            abstand_str = 'Abstand'
            auslenkung_str = 'Auslenkung'
            seaborn.set(rc={'figure.figsize':(8,4)})    
            if str(directions) == 'Abstand': 
                    
                    filter_cols_A = moving_average_dataframe.filter(like = abstand_str).iloc[:,0:4]
                    filter_cols = moving_average_dataframe[[col for col in moving_average_dataframe.columns if (abstand_str  in col or 'Position' in col)]]
                    for column in filter_cols_A:
                        figu = plt.figure()
                        subset = filter_cols
                        subset_MA = subset.drop(['Abstand_Error',  'Abstand_Normal', 'Abstand_Diff'],  axis = 1)
                        subsetm = subset_MA.melt('Position', var_name='', value_name='Mittelwert')
                        seaborn.set_style("darkgrid")
                        seaborn.color_palette("bright")            
                        ax1 = seaborn.scatterplot(x="Position", y="Mittelwert", s=7, hue='', data=subsetm,  edgecolor="none")
                        seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                        plt.tight_layout() 
                        plt.title('Hub', fontsize=16, loc='center', pad=15)
                        file_name1 =  os.path.abspath(hub_general_view_path_DE)
                        plt.switch_backend('agg')
                        figu.savefig(file_name1)
                        plt.close()
            elif str(directions) == 'Auslenkung': 
                    filter_cols_B = moving_average_dataframe.filter(like = auslenkung_str).iloc[:,0:4]
                    filter_cols = moving_average_dataframe[[col for col in moving_average_dataframe.columns if (auslenkung_str  in col or 'Position' in col)]]
                    seaborn.set(rc={'figure.figsize':(8,4)})    
                    for column in filter_cols_B:
                        figu = plt.figure()
                        subset = filter_cols
                        subset_MA = subset.drop(['Auslenkung_Error',  'Auslenkung_Normal', 'Auslenkung_Diff'],  axis = 1)
                        subsetm = subset_MA.melt('Position', var_name='', value_name='Mittelwert')
                        seaborn.set_style("darkgrid")
                        seaborn.color_palette("bright")            
                        ax1 = seaborn.scatterplot(x="Position", y="Mittelwert", s=7, hue='', data=subsetm,  edgecolor="none")
                        seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                        plt.tight_layout() 
                        plt.title('Auslenkung', fontsize=16, loc='center', pad=15)
                        file_name2 =  os.path.abspath(auslenkung_general_view_path_DE)
                        plt.switch_backend('agg')
                        figu.savefig(file_name2)
                        plt.close()
            
            abstand_str = 'Lift'
            auslenkung_str = 'Deflection'        
            if str(directions) == 'Lift': 
                   filter_cols = moving_average_dataframe.filter(like = abstand_str).iloc[:,0:4]
                   seaborn.set(rc={'figure.figsize':(8,4)})
                   for column in filter_cols:
                           figu = plt.figure()
                           subset = moving_average_dataframe
                           subset_MA = subset.drop(['Deflection-L1 [mm]', 'Deflection-L2 [mm]', 'Deflection-L3 [mm]', 'Deflection-PE [mm]'],  axis = 1)
                           subsetm = subset_MA.melt('Position', var_name='', value_name='Moving Average')
                           seaborn.set_style("darkgrid")
                           seaborn.color_palette("bright")            
                           ax1 = seaborn.scatterplot(x="Position", y="Moving Average", s=7, hue='', data=subsetm,  edgecolor="none")
                           seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                           plt.tight_layout() 
                           plt.title('Lift', fontsize=16, loc='center', pad=15)
                           file_name3 =  os.path.abspath(hub_general_view_path_EN)
                           plt.switch_backend('agg')
                           figu.savefig(file_name3)
                           plt.close()           
            elif str(directions) == 'Deflection': 
                    filter_cols = moving_average_dataframe.filter(like = auslenkung_str).iloc[:,0:4]
                    seaborn.set(rc={'figure.figsize':(8,4)})
                    for column in filter_cols:
                          
                            figu = plt.figure()
                            subset = moving_average_dataframe
                            subset_MA = subset.drop(['Lift-L1 [mm]', 'Lift-L2 [mm]', 'Lift-L3 [mm]', 'Lift-PE [mm]'],  axis = 1)
                            subsetm = subset_MA.melt('Position', var_name='', value_name='Moving Average')
                            seaborn.set_style("darkgrid")
                            seaborn.color_palette("bright")            
                            ax1 = seaborn.scatterplot(x="Position", y="Moving Average", s=7, hue='', data=subsetm,  edgecolor="none")
                            seaborn.move_legend(ax1, "center left", bbox_to_anchor=(1.02, 1), borderaxespad=5, fontsize = '8')
                            plt.tight_layout() 
                            plt.title('Deflection', fontsize=16, loc='center', pad=15)
                            file_name4 =  os.path.abspath(auslenkung_general_view_path_EN)
                            plt.switch_backend('agg')
                            figu.savefig(file_name4)
                            plt.close()


class Rauto():

    def __init__(self):
         self.customer_company_logo = None
         self.excel_file_path = None
         self.smart_collector_components_pic = None
         self.smart_collector_with_3d_sensor_pic = None
         self.save_directory = None
         self.customer_company_name = None
         self.name_of_the_Stromabnehmer_series = None
         self.armes_order_extra_section = None
         self.link_to_customer_company_dashboard = None
         self.armes_order_extra_section_EN = None
    
    def widget(self):
        self.customer_company_logo, self.excel_file_path, self.smart_collector_components_pic, self.smart_collector_with_3d_sensor_pic, self.save_directory, self.customer_company_name, self.name_of_the_Stromabnehmer_series, self.armes_order_extra_section, self.link_to_customer_company_dashboard, self.armes_order_extra_section_EN = entries_extractor()

    def generate(self):                
            
            dir = 'images'
            if os.path.exists(dir):
              shutil.rmtree(dir)
              os.makedirs(dir)
            else:
              os.makedirs(dir)
            
            working_directory = os.path.abspath('images')
            hub_general_view_path_DE = working_directory +'/Plot_Hub_DE'+ '.jpeg'
            hub_general_view_path_EN = working_directory +'/Plot_Hub_EN'+ '.jpeg'
            auslenkung_general_view_path_DE = working_directory+'/Plot_Auslenkung_DE'+'.jpeg' 
            auslenkung_general_view_path_EN = working_directory+'/Plot_Auslenkung_EN'+'.jpeg'
            Excel_reference_raw_data =  pd.read_excel(self.excel_file_path)
            Excel_reference_raw_data.drop(Excel_reference_raw_data[Excel_reference_raw_data['Position'] == 0].index, inplace=True)
            Excel_reference_raw_data = Excel_reference_raw_data.drop(Excel_reference_raw_data.columns[0], axis = 1)
            Excel_reference_raw_data = Excel_reference_raw_data.set_index('Position')
            mean_window_size = 40
            var_window_size = 100
            mov_avg_df_nor = Excel_reference_raw_data[::-1].rolling(mean_window_size, min_periods = 1).mean()[::-1]
            total_var = mov_avg_df_nor.var()
            var_df = mov_avg_df_nor[::-1].rolling(var_window_size, min_periods = 1).var()[::-1]
            mov_avg_df_diff = mov_avg_df_nor.copy()
            total_var = var_df.mean()
            total_var =total_var.to_dict()
            mov_avg_eng = mov_avg_df_nor.copy()
            mov_avg_eng.rename(columns={mov_avg_eng.columns[0]: 'Lift-L1 [mm]', mov_avg_eng.columns[1]: 'Lift-L2 [mm]',mov_avg_eng.columns[2]: 'Lift-L3 [mm]', mov_avg_eng.columns[3]: 'Lift-PE [mm]', mov_avg_eng.columns[4]: 'Deflection-L1 [mm]', mov_avg_eng.columns[5]: 'Deflection-L2 [mm]', mov_avg_eng.columns[6]: 'Deflection-L3 [mm]', mov_avg_eng.columns[7]: 'Deflection-PE [mm]'},inplace=True)
            mov_avg_eng = mov_avg_eng.round(1)
            mov_avg_eng= mov_avg_eng.reset_index()
            min_abstand = min([value for key, value in total_var.items() if 'abstand' in key.lower()]) + 0.16
            min_auslenkung = min([value for key, value in total_var.items() if 'auslenkung' in key.lower()]) + 0.16
            
            abstand_cols = var_df.loc[:,  (['Abstand' in col for col in var_df.columns])]
            
            auslenkung_cols = var_df.loc[:,  (['Auslenkung' in col for col in var_df.columns])]
            for i in range(len(abstand_cols)):
                mov_avg_df_nor['Abstand_Normal'] = abstand_cols.apply(lambda x: 5 if (x[col]> min_abstand for col in abstand_cols.columns) else 0, axis=0)
            
            for i in abstand_cols.index:
                if((abstand_cols.loc[i, :] > min_abstand).any()):
                    mov_avg_df_nor.loc[i,'Abstand_Normal'] = 5
                else:
                    mov_avg_df_nor.loc[i,'Abstand_Normal'] = 0 
            for i in auslenkung_cols.index:
                if((auslenkung_cols.loc[i, :] > min_auslenkung).any()):
                    mov_avg_df_nor.loc[i,'Auslenkung_Normal'] = 5
                else:
                    mov_avg_df_nor.loc[i,'Auslenkung_Normal'] = 0
            pd.reset_option('^display.', silent=True)
            
            comb_df = pd.DataFrame(index=mov_avg_df_diff.index)
            for column in mov_avg_df_diff:
                if 'Abstand' in column and 'Normal' not in column:
                        subset_columns = mov_avg_df_diff.loc[:, (mov_avg_df_diff.columns != column) & (['Abstand' in col for col in mov_avg_df_diff.columns]) & ['Normal' not in col for col in mov_avg_df_diff.columns]]
                        comb_df[column] = np.mean(subset_columns, axis = 1)
                elif 'Auslenkung' in column and 'Normal' not in column:
                        subset_columns = mov_avg_df_diff.loc[:, (mov_avg_df_diff.columns != column) & (['Auslenkung' in col for col in mov_avg_df_diff.columns]) & ['Normal' not in col for col in mov_avg_df_diff.columns]]
                        comb_df[column] = np.mean(subset_columns, axis = 1)
            diff_df = pd.DataFrame(index=mov_avg_df_diff.index)
            for column in comb_df:
                diff_df[column + '_Diff'] = mov_avg_df_diff[column] - comb_df[column]
            var_diff = diff_df[::-1].rolling(var_window_size, min_periods = 1).var()[::-1]
            total_var_diff = var_diff.mean()
            
            total_var_diff =total_var_diff.to_dict()
            min_abstand_diff = min([value for key, value in total_var_diff.items() if 'abstand' in key.lower()]) + 0.16
            min_auslenkung_diff = min([value for key, value in total_var_diff.items() if 'auslenkung' in key.lower()]) + 0.16
            abstand_cols = var_diff.loc[:,  (['Abstand' in col for col in var_diff.columns])]
            auslenkung_cols = var_diff.loc[:,  (['Auslenkung' in col for col in var_diff.columns])]
            
            for i in abstand_cols.index:
                if((abstand_cols.loc[i, :] > min_abstand_diff).any()):
                    mov_avg_df_nor.loc[i,'Abstand_Diff'] = 10
                else:
                    mov_avg_df_nor.loc[i,'Abstand_Diff'] = 0
            for i in auslenkung_cols.index:
                if((auslenkung_cols.loc[i, :] > min_auslenkung_diff).any()):
                    mov_avg_df_nor.loc[i,'Auslenkung_Diff'] = 10
                else:
                    mov_avg_df_nor.loc[i,'Auslenkung_Diff'] = 0
            sum_df = pd.DataFrame(index=mov_avg_df_nor.index)
            sum_df['Abstand_Error'] = mov_avg_df_nor['Abstand_Normal'] + mov_avg_df_nor['Abstand_Diff']
            sum_df['Auslenkung_Error'] = mov_avg_df_nor['Auslenkung_Normal'] + mov_avg_df_nor['Auslenkung_Diff']
            for i in sum_df.index:
                if(sum_df.loc[i,'Abstand_Error'] > 0):
                    mov_avg_df_nor.loc[i,'Abstand_Error'] = 15
                else:
                    mov_avg_df_nor.loc[i,'Abstand_Error'] = 0
                if(sum_df.loc[i,'Auslenkung_Error'] > 0):
                    mov_avg_df_nor.loc[i,'Auslenkung_Error'] = 15
                else:
                    mov_avg_df_nor.loc[i,'Auslenkung_Error'] = 0
            mov_avg_df_nor = mov_avg_df_nor.reset_index()
           
            Tools.plot_general_view(mov_avg_df_nor, 'Abstand')
            Tools.plot_general_view(mov_avg_df_nor, 'Auslenkung')
            Tools.plot_general_view(mov_avg_eng, 'Lift')
            Tools.plot_general_view(mov_avg_eng, 'Deflection')
            
            
            
            abstand_str = 'Lift'
            auslenkung_str = 'Deflection'
            filter_cols = mov_avg_eng.filter(like = abstand_str).iloc[:,0:4]
            max_general_hub = np.max(filter_cols.iloc[:,0:4].values)
            min_general_hub = np.min(filter_cols.iloc[:,0:4].values)
            average_general__hub = np.mean(filter_cols.iloc[:,0:4].values)

            abstand_str = 'Lift'
            auslenkung_str = 'Deflection'
            filter_cols = mov_avg_eng.filter(like = auslenkung_str).iloc[:,0:4]
            max_general_auslenkung = np.max(filter_cols.iloc[:,0:4].values)
            min_general_auslenkung = np.min(filter_cols.iloc[:,0:4].values)
            spring_constant=0
            contact_pressure=7 
            spring_position_constant=0
            if self.name_of_the_Stromabnehmer_series == 'KDS2/40':
               spring_constant= 1.53
               spring_position_constant = 16/70
            elif self.name_of_the_Stromabnehmer_series == 'KUFR2/40':
               spring_constant= 1.53
               spring_position_constant = 16/70
            elif self.name_of_the_Stromabnehmer_series == 'KESR':
                spring_constant= 1.14
                spring_position_constant = 23/75
            elif self.name_of_the_Stromabnehmer_series == 'KESL':
                 spring_constant= 1.14
                 spring_position_constant = 23/150
            max_general_hub_in_meter = round(max_general_hub,8)
            min_general_hub_in_meter = round(min_general_hub,8)
            
            average_general__hub = round(average_general__hub,8)
            minimum_press_pressure = round(- max_general_hub_in_meter * spring_constant * spring_position_constant + contact_pressure, 2)
            maximum_press_pressure = round(- min_general_hub_in_meter * spring_constant * spring_position_constant + contact_pressure, 2)
            average_press_preasure = round(- average_general__hub * spring_constant * spring_position_constant + contact_pressure,2)
            
            groups1 = Tools.anomalies_extractor(mov_avg_df_nor, 'Abstand_Diff')
            groups2 = Tools.anomalies_extractor(mov_avg_df_nor, 'Auslenkung_Diff')
            groups3 = Tools.anomalies_extractor(mov_avg_df_nor, 'Abstand_Normal')
            groups4 = Tools.anomalies_extractor(mov_avg_df_nor, 'Auslenkung_Normal')
            groups_refined = pd.concat([groups1, groups2, groups3, groups4], axis = 0)
            if not groups_refined.empty:            
                         organized_min_order = np.sort(groups_refined, axis=None)
                         organized_min_order = organized_min_order.reshape(-1,2)
                         refined_values = pd.DataFrame(organized_min_order)
                         refined_values.index = refined_values.reset_index(drop=True).index
                         if refined_values.empty: 
                             pass
                         else: 
                             refined_values.columns = ['Start Position', 'End Position']
                         
             
             
                         refined_anomalies_values = Tools.dataframe_filter(refined_values, 200) 
                         refined_anomalies_values = Tools.smoothing_filter(refined_anomalies_values)
                         refined_anomalies_values = Tools.filter_between_start_end(refined_anomalies_values)
            
                         Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, refined_anomalies_values, 'Abstand', 'anomalie')
                         Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, refined_anomalies_values, 'Auslenkung', 'anomalie')
                         Tools.anomalies_warning_failure_plotter(mov_avg_eng, refined_anomalies_values, 'Lift', 'anomalie')
                         Tools.anomalies_warning_failure_plotter(mov_avg_eng, refined_anomalies_values, 'Deflection', 'anomalie')
            else: 
                    refined_anomalies_values = pd.DataFrame          
            
            if self.name_of_the_Stromabnehmer_series == 'KDS2/40' or self.name_of_the_Stromabnehmer_series == 'KUFR2/40' or self.name_of_the_Stromabnehmer_series == 'KESR':  

                    groups1 = Tools.warning_positions_extractor(mov_avg_eng, 'Deflection-PE [mm]')
                    groups2 = Tools.warning_positions_extractor(mov_avg_eng, 'Deflection-L1 [mm]')
                    groups3 = Tools.warning_positions_extractor(mov_avg_eng, 'Deflection-L2 [mm]')
                    groups4 = Tools.warning_positions_extractor(mov_avg_eng, 'Deflection-L3 [mm]')
                    groups5 = Tools.warning_positions_extractor(mov_avg_eng, 'Lift-L1 [mm]')
                    groups6 = Tools.warning_positions_extractor(mov_avg_eng, 'Lift-L2 [mm]')
                    groups7 = Tools.warning_positions_extractor(mov_avg_eng, 'Lift-L3 [mm]')
                    groups8 = Tools.warning_positions_extractor(mov_avg_eng, 'Lift-PE [mm]')

        

                    deflection_groups_refined = pd.concat([groups1, groups2, groups3, groups4], axis = 0)
                    deflection_groups_refined.index = deflection_groups_refined.reset_index(drop = True).index #+ 1
                    deflection_warning_groups_refined_sorted = deflection_groups_refined.values
                    deflection_organized_min_order = np.sort(deflection_warning_groups_refined_sorted, axis = None)
                    deflection_organized_min_order = deflection_organized_min_order.reshape(-1, 2)
                    deflection_warning_groups_refined_sorted = pd.DataFrame(deflection_organized_min_order)
                    deflection_warning_groups_refined_sorted.index = deflection_warning_groups_refined_sorted.reset_index(drop=True).index#+1
                    if not deflection_warning_groups_refined_sorted.empty:
                          
                          deflection_warning_groups_refined_sorted.columns = ['Start Position', 'End Position']
                          
                    else: 
                          print('deflection_warning_groups_refined_sorted')


                    lift_groups_refined = pd.concat([groups5, groups6, groups7, groups8], axis = 0)
                    lift_groups_refined.index = lift_groups_refined.reset_index(drop = True).index #+ 1
                    lift_warning_groups_refined_sorted = lift_groups_refined.values
                    lift_organized_min_order = np.sort(lift_warning_groups_refined_sorted, axis = None)
                    lift_organized_min_order = lift_organized_min_order.reshape(-1, 2)
                    lift_warning_groups_refined_sorted = pd.DataFrame(lift_organized_min_order)
                    lift_warning_groups_refined_sorted.index = lift_warning_groups_refined_sorted.reset_index(drop=True).index#+1
                    if not lift_warning_groups_refined_sorted.empty:
                            lift_warning_groups_refined_sorted.columns = ['Start Position', 'End Position']
                    else:   
                            print('lift_warning_groups_refined_sorted empty')
                    print('lift_warning_groups_refined_sorted: ', lift_warning_groups_refined_sorted, '/n')
                    print('deflection_warning_groups_refined_sorted: ', deflection_warning_groups_refined_sorted, '/n')
                    deflection_warning_groups_refined_sorted = Tools.dataframe_filter(deflection_warning_groups_refined_sorted, 200)        
                    print('deflection_warning_groups_refined_sorted: ', deflection_warning_groups_refined_sorted, '/n')
                    deflection_warning_groups_refined_sorted = Tools.smoothing_filter(deflection_warning_groups_refined_sorted)
                    print('deflection_warning_groups_refined_sorted: ', deflection_warning_groups_refined_sorted, '/n')
                    deflection_warning_groups_refined_sorted = Tools.filter_between_start_end(deflection_warning_groups_refined_sorted)
                    print('deflection_warning_groups_refined_sorted: ', deflection_warning_groups_refined_sorted, '/n')
                    
                    lift_warning_groups_refined_sorted = Tools.dataframe_filter(lift_warning_groups_refined_sorted, 200)
                    print('lift_warning_groups_refined_sorted: ', lift_warning_groups_refined_sorted, '/n')
                    lift_warning_groups_refined_sorted = Tools.smoothing_filter(lift_warning_groups_refined_sorted)
                    print('lift_warning_groups_refined_sorted: ', lift_warning_groups_refined_sorted, '/n')
                    lift_warning_groups_refined_sorted = Tools.filter_between_start_end(lift_warning_groups_refined_sorted)
                    print('lift_warning_groups_refined_sorted: ', lift_warning_groups_refined_sorted, '/n')
                    print('groups1: ', groups1, '/n')
                    print('groups2: ', groups2, '/n')
                    print('groups3: ', groups3, '/n')
                    print('groups4: ', groups4, '/n')
                    print('groups5: ', groups5, '/n')
                    print('groups6: ', groups6, '/n')
                    print('groups7: ', groups7, '/n')
                    print('groups8: ', groups8, '/n')
                    
                    Tools.anomalies_warning_failure_plotter(mov_avg_eng, lift_warning_groups_refined_sorted, 'Lift', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_eng, lift_warning_groups_refined_sorted, 'Deflection', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_eng, deflection_warning_groups_refined_sorted, 'Deflection', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_eng, deflection_warning_groups_refined_sorted, 'Lift', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, lift_warning_groups_refined_sorted, 'Abstand', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, lift_warning_groups_refined_sorted, 'Auslenkung', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, deflection_warning_groups_refined_sorted, 'Auslenkung', 'warning')
                    Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, deflection_warning_groups_refined_sorted, 'Abstand', 'warning')                    
                    
                    

                    groups1 = Tools.failure_positions_extractor(mov_avg_eng, 'Deflection-PE [mm]')
                    groups2 = Tools.failure_positions_extractor(mov_avg_eng, 'Deflection-L1 [mm]')
                    groups3 = Tools.failure_positions_extractor(mov_avg_eng, 'Deflection-L2 [mm]')
                    groups4 = Tools.failure_positions_extractor(mov_avg_eng, 'Deflection-L3 [mm]')
                    groups5 = Tools.failure_positions_extractor(mov_avg_eng, 'Lift-L1 [mm]')
                    groups6 = Tools.failure_positions_extractor(mov_avg_eng, 'Lift-L2 [mm]')
                    groups7 = Tools.failure_positions_extractor(mov_avg_eng, 'Lift-L3 [mm]')
                    groups8 = Tools.failure_positions_extractor(mov_avg_eng, 'Lift-PE [mm]')
                    
                    deflection_groups_refined_failure = pd.concat([groups1, groups2, groups3, groups4], axis = 0)
                    deflection_groups_refined_failure.index = deflection_groups_refined_failure.reset_index(drop = True).index 
                    deflection_failure_groups_refined_sorted = deflection_groups_refined_failure.values
                    deflection_organized_min_order_failure = np.sort(deflection_failure_groups_refined_sorted, axis= None)
                    deflection_organized_min_order_failure = deflection_organized_min_order_failure.reshape(-1, 2)
                    deflection_failure_groups_refined_sorted = pd.DataFrame(deflection_organized_min_order_failure)
                    deflection_failure_groups_refined_sorted.index = deflection_failure_groups_refined_sorted.reset_index(drop=True).index
                    
                    if deflection_failure_groups_refined_sorted.empty:
                       pass
                    else: 
                         deflection_failure_groups_refined_sorted.columns = ['Start Position', 'End Position']
                    
                    lift_groups_refined_failure = pd.concat([groups5, groups6, groups7, groups8], axis = 0)
                    lift_groups_refined_failure.index = lift_groups_refined_failure.reset_index(drop = True).index
                    lift_failure_groups_refined_sorted = lift_groups_refined_failure.values
                    lift_organized_min_order_failure = np.sort(lift_failure_groups_refined_sorted, axis=None)
                    lift_organized_min_order_failure = lift_organized_min_order_failure.reshape(-1,2)
                    lift_failure_groups_refined_sorted = pd.DataFrame(lift_organized_min_order_failure)
                    lift_failure_groups_refined_sorted.index = lift_failure_groups_refined_sorted.reset_index(drop=True).index
                    
                    if lift_failure_groups_refined_sorted.empty:
                       pass
                    else: 
                       lift_failure_groups_refined_sorted.columns = ['Start Position', 'End Position']
                    
                    deflection_failure_groups_refined_sorted = Tools.dataframe_filter(deflection_failure_groups_refined_sorted, 200)        
                    print('deflection_failure_groups_refined_sorted: ', deflection_failure_groups_refined_sorted, '/n')
                    deflection_failure_groups_refined_sorted = Tools.smoothing_filter(deflection_failure_groups_refined_sorted)
                    print('deflection_failure_groups_refined_sorted: ', deflection_failure_groups_refined_sorted, '/n')
                    deflection_failure_groups_refined_sorted = Tools.filter_between_start_end(deflection_failure_groups_refined_sorted)
                    print('deflection_failure_groups_refined_sorted: ', deflection_failure_groups_refined_sorted, '/n')
                    
                    lift_failure_groups_refined_sorted = Tools.dataframe_filter(lift_failure_groups_refined_sorted, 200)
                    print('lift_failure_groups_refined_sorted: ', lift_failure_groups_refined_sorted, '/n')
                    lift_failure_groups_refined_sorted = Tools.smoothing_filter(lift_failure_groups_refined_sorted)
                    print('lift_failure_groups_refined_sorted: ', lift_failure_groups_refined_sorted, '/n')
                    lift_failure_groups_refined_sorted = Tools.filter_between_start_end(lift_failure_groups_refined_sorted)
                    print('lift_failure_groups_refined_sorted: ', lift_failure_groups_refined_sorted, '/n')
                    
                    if not lift_failure_groups_refined_sorted.empty: 

                              Tools.anomalies_warning_failure_plotter(mov_avg_eng, lift_failure_groups_refined_sorted, 'Lift', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_eng, lift_failure_groups_refined_sorted, 'Deflection', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, lift_failure_groups_refined_sorted, 'Abstand', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, lift_failure_groups_refined_sorted, 'Auslenkung', 'failure')
                    
                    if not deflection_failure_groups_refined_sorted.empty: 
                              
                              Tools.anomalies_warning_failure_plotter(mov_avg_eng, deflection_failure_groups_refined_sorted, 'Deflection', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_eng, deflection_failure_groups_refined_sorted, 'Lift', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, deflection_failure_groups_refined_sorted, 'Auslenkung', 'failure')
                              Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, deflection_failure_groups_refined_sorted, 'Abstand', 'failure')

                    

                    pdf = FPDF('P', 'mm', 'A4')
                    pdf.add_page()
                    pdf.image(str(glob.glob(r"vorlage/cover_page.jpg")[0]), x=0,y=0, w=210, h=297)
                    pdf.image(self.customer_company_logo, x=165, y= 23, w=30, h=20)
                    pdf.set_font('helvetica','', 12)
                    pdf.set_xy(x= 15, y= 40)
                    pdf.set_text_color(248,248,255)
                    pdf.multi_cell(w =500, h = 10, txt = 'X Group', border = 0 ,align = 'L', fill = False)
                    pdf.set_font('helvetica','B', 20)
                    pdf.set_xy(x=70, y= 115)
                    pdf.set_text_color(25,25,112) 
                    pdf.multi_cell(w =500, h = 10, txt = f'{self.customer_company_name}', border = 0 ,align = 'L', fill = False)
                    pdf.set_xy(x=70, y=125)
                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    pdf.multi_cell(w =160, h = 10, txt = str(date_time), border = 0 ,align = 'L', fill = False)
                    pdf.add_page()
                    pdf.set_xy(10, 25)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,0)
                    pdf.cell(w =190, h = 7, txt = str('Inhaltsverzeichnis ') , border = 0,
                              align = 'L', fill = False)
                    pdf.set_font('helvetica','', 8)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,0)
                    pdf.set_xy(10, 45)
                    title_name = f'Aktueller Status des Systems in der  ' + f'{self.customer_company_name}'
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                    pdf.ln()
                    title_name = f"{self.customer_company_name}"+ "/nErgebnisse der Inspektionsfahrt"
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                    pdf.ln()
                    title_name= "Überschreiten des Absolutwerts"
                    title_string_length_uberschreiten = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y_uberschreiten = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length_uberschreiten+13 , title_padding_y_uberschreiten+2.5, 193, title_padding_y_uberschreiten+2.5)
                    pdf.ln()
                    pdf.set_text_color(0,0,0)
                    pdf.set_font('helvetica','', 8)
                    pdf.set_top_margin(37)
                              
                    if not refined_anomalies_values.empty: 
                              
                              for idx, df_row in enumerate(refined_anomalies_values.values): 
                                  title_padding_y= pdf.get_y()
                                  title_name= 'Mögliche Anomalie bei Position ' + str(df_row[0]) +" bis " + str(df_row[1])
                                  threading.Thread(target=pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT))
                                  title_string_length = pdf.get_string_width(title_name)
                                  last_anomalie_padding_y= pdf.get_y()
                                  threading.Thread(target=pdf.dashed_line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5, dash_length=1, space_length=1))
                                  pdf.set_y(last_anomalie_padding_y)

                    else:   
                            title_name = 'Mögliche Anomalie'
                            pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            last_anomalie_padding_y_noanomalies= pdf.get_y()
                            title_string_length = pdf.get_string_width(title_name)
                            pdf.set_dash_pattern(dash=1, gap=1)
                            pdf.line(title_string_length+13 , last_anomalie_padding_y_noanomalies-2.5, 193, last_anomalie_padding_y_noanomalies-2.5)
                            pdf.set_y(last_anomalie_padding_y_noanomalies)

                    title_name = f'Einstieg ins Dashboard ' 
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name , border = 0,align = 'L', fill = False)
                    title_padding_y_Einstieg = pdf.get_y()
                    pdf.dashed_line(title_string_length+13 , title_padding_y_Einstieg+2.5, 193, title_padding_y_Einstieg+2.5, dash_length=1, space_length=1)
                    pdf.ln()
                    title_name = "Mögliche erkennbare Fehlerfälle"
                    title_string_length = pdf.get_string_width(title_name) 
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y_Mogliche = pdf.get_y()
                    pdf.dashed_line(title_string_length+13 , title_padding_y_Mogliche+2.5, 193, title_padding_y_Mogliche+2.5, dash_length=1, space_length=1)

                    
                    content_page_nu = pdf.page_no()
                    pdf.set_font('helvetica','', 8)
                    pdf.set_text_color(0,0,0)
                    pdf.page = 2 
                    pdf.set_xy(190, 45)
                    pdf.set_right_margin(20)
                    pdf.set_top_margin(35)
                    pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+1}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+3}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.cell(w =10, h = 5, txt = f"{content_page_nu+5}", border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.set_right_margin(20)
                    pdf.set_top_margin(35)
                    
                    if not refined_anomalies_values.empty:  
                          if not  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
                                for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+5+len(lift_warning_groups_refined_sorted)+len(deflection_warning_groups_refined_sorted)+len(lift_failure_groups_refined_sorted)+len(deflection_failure_groups_refined_sorted)): 
                                    threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))

                                    if pdf.page in range(2, content_page_nu+1): 
                                       pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                       pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                       pdf.set_top_margin(35)
                              
                                Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 5 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                pdf.set_xy(190, title_padding_y_Einstieg)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                pdf.ln()
                                pdf.set_xy(190, title_padding_y_Mogliche)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                          else:
                                for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+6+len(lift_warning_groups_refined_sorted)+len(deflection_warning_groups_refined_sorted)+len(lift_failure_groups_refined_sorted)+len(deflection_failure_groups_refined_sorted)): 
                                    threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                              
                                    if pdf.page in range(2, content_page_nu+1): 
                                       pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                       pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                       pdf.set_top_margin(35)
                              
                                Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                pdf.set_xy(190, title_padding_y_Einstieg)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                pdf.ln()
                                pdf.set_xy(190, title_padding_y_Mogliche)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                    
                    else: 
                          if not  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
        
                                  first_anomalie_page_number = content_page_nu + 5 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                  #if content_page_nu == 2:
                                  pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                  pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                  pdf.set_top_margin(35)

                                  Einsteug_page_nu=  content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.set_xy(190, title_padding_y_Einstieg)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                  pdf.ln()
                                  pdf.set_xy(190, title_padding_y_Mogliche)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                          else:         
                                  first_anomalie_page_number = content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                  #if content_page_nu == 2:
                                  pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                  pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                  pdf.set_top_margin(35)

                                  Einsteug_page_nu=  content_page_nu + 7 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.set_xy(190, title_padding_y_Einstieg)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                  pdf.ln()
                                  pdf.set_xy(190, title_padding_y_Mogliche)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
            
                    
                    
                    pdf.set_page_background(glob.glob(r"vorlage/background_seite.jpg")[0])
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Aktueller Status des Systems in der '+ f'{self.customer_company_name}') , border = 0,
                              align = 'L', fill = False)
                    pdf.image(self.smart_collector_components_pic,x=25, y=125,w=160, h=130,type='' )
                    pdf.set_xy(65, 255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 10, txt = 'Abbildung 1: Die Komponenten an der Ofenklappe', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 50)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = 'In der ' +f'{self.customer_company_name}' + ''' wurde der Smart Collector an einem Fahrwerk installiert. Das System wurde am Nachläufer eingereichtet und besteht aus den Komponenten: /n/n - Kompaktstromabnehmer mit 3D-Unit /n - Positionierungssystem  /n - Main-Unit /n - Industrierouter /n/n Folgend die Darstellung des Systems und der Komponenten bei '''+ f'{self.customer_company_name}'+ '.' ,
                                         border = 0,align = 'L', fill = False)
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(self.smart_collector_with_3d_sensor_pic,x=25, y=45,w=160, h=110,type='' )
                    pdf.set_xy(65, 155)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 10, txt = 'Abbildung 2: Stromabnehmer '+ str(self.name_of_the_Stromabnehmer_series)+ ' mit 3D-Sensor', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 170)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    
                    if not self.armes_order_extra_section:
                         pdf.multi_cell(w =190, h = 7, txt = f'''Die Software des Smart Collectors lässt es zu, die Anlage Komplett abzufahren und Bewegungswerte der Stromabnehmerarme den Positionswerten des Fahrzeugs zuzuordnen. Es ist auch möglich, Rferenzdaten zu hinterlegen und im weiteren Verlauf Fehler in der Anlage durch vergleich der aktuellen Werte und der Referenzwerte aufzudecken. 
                        /nIn den vergangenen Tagen wurden über mehrere Studen Anlagenwerte gesammelt, um zunächst zu bewerten, ob sich der aktuelle Anlagenzustand der ''' + str(self.customer_company_name)+ f" für eine Referenzfahrt eignet bzw. ob schon im Vorfeld Montage oder Verlegeprobleme erkennbar sind. Auf den folgenden Seiten werden nun die Ergebnisse dargestellt.",
                        
                                        border = 0,align = 'L', fill = False)
                    else:
                        pdf.multi_cell(w =190, h = 7, txt = f'''Die Software des Smart Collectors lässt es zu, die Anlage Komplett abzufahren und Bewegungswerte der Stromabnehmerarme den Positionswerten des Fahrzeugs zuzuordnen. Es ist auch möglich, Rferenzdaten zu hinterlegen und im weiteren Verlauf Fehler in der Anlage durch vergleich der aktuellen Werte und der Referenzwerte aufzudecken. 
                        /nIn den vergangenen Tagen wurden über mehrere Studen Anlagenwerte gesammelt, um zunächst zu bewerten, ob sich der aktuelle Anlagenzustand der ''' + str(self.customer_company_name)+ f" für eine Referenzfahrt eignet bzw. ob schon im Vorfeld Montage oder Verlegeprobleme erkennbar sind. Auf den folgenden Seiten werden nun die Ergebnisse dargestellt./n/n" + str(self.armes_order_extra_section),
                        
                                        border = 0,align = 'L', fill = False)

                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =160, h = 10, txt = str('Ergebnisse der Inspektionsfahr '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                    pdf.image(hub_general_view_path_DE,x=25, y=45,w=180, h=95,type='' )
                    pdf.image(auslenkung_general_view_path_DE, x = 25,y= 150, w=180, h = 95, type='' )
                    pdf.set_xy(50, 137)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 5, txt = 'Abbildung 3: Daten der gesamten Hub Anlagenstrecke', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(50, 242)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 5, txt = 'Abbildung 4: Daten der gesamten Auslenkung Anlagenstrecke', border = 0,
                              align = 'L', fill = False)
                    length_of_the_whole_route = np.max(Excel_reference_raw_data.index.values) - np.min(Excel_reference_raw_data.index.values)
                    pdf.set_xy(10, 250)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = '''Wie in der obigen Darstellung zu sehen ist, wurden der Hubverlauf und der Auslenkungsverlauf der gesamten Anlagenstrecke von ca. ''' + str(length_of_the_whole_route) + ' cm ' + '''Länge ermittelt.'''                             
                                    ,border = 0,align = 'L', fill = False )
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_xy(10, 40)
                    pdf.multi_cell(w =190, h = 7, txt = '''Der Stromabnehmer bewegt sich im Bereich von ''' + str(max_general_hub) + ' mm bis '+ str(min_general_hub) + ' mm in Hub und im Bereich von ' + str(max_general_auslenkung) + ' mm bis ' + str(min_general_auslenkung) + ''' mm in Auslenkung und damit im Gesamten in seinem zulässigen Bereich. Die erkennbaren Lücken in der Darstellung entstehen dadurch, dass der Stromabnehmer nicht alle Bereiche der Anlage in der Auzeichnungszeit befahren hat.
                                                             /nDas installierte System sowie die geprüfte Anlage weisen folgende Merkmale auf: /n/n - 4 Arme werden über den 3D-Unit Motion Sensor überwacht. /n/n - Während das Fahrzeug auf der Strecke fährt, werden die Hub und                                Auslenkungswerte von jedem Zentimeter der Strecke erfasst./n/n - Der Anpressdruck der Abnehmer variiert von '''+ str(maximum_press_pressure) + ' N bis '+ str(minimum_press_pressure) + f''' N./n   Der durchschnittliche Pressdruck beträgt {average_press_preasure} N.'''                              
                                    ,border = 0,align = 'L', fill = False )
                    
                    first_warnging_failure_page_number =   pdf.page_no()

                    if not lift_warning_groups_refined_sorted.empty:
                        for idx, df_row in enumerate(lift_warning_groups_refined_sorted.values[0:1]):    
                            pdf.add_page()
                            pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                            pdf.set_font('helvetica','', 16)
                            pdf.set_xy(10, 35)
                            pdf.set_text_color(0,0,255)
                            pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                            pdf.set_xy(10, 45)
                            pdf.set_font('helvetica','', 14)
                            pdf.set_text_color(0,0,0)        
                            pdf.multi_cell(w =190, h = 7, txt = f'Die Warngrenze in {len(lift_warning_groups_refined_sorted)} Bereichen in Hub überschritten (± 10 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]}/n' ,
                                                 border = 0,align = 'L', fill = False)
                            y = pdf.get_y()
                            pdf.set_xy(10, y)        
                            pdf.set_font('helvetica','', 14)
                            pdf.set_xy(10, 60)
                            pdf.set_text_color(0,0,0)
                            file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                            
                            pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                            pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    if  len(lift_warning_groups_refined_sorted) > 1:        

                            for idx, df_row in enumerate(lift_warning_groups_refined_sorted.values[1:]):
                                
                                pdf.add_page()
                                pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                pdf.set_font('helvetica','', 14)
                                pdf.set_xy(10, 40)
                                pdf.set_text_color(0,0,0)
                                pdf.multi_cell(w = 190, h = 7, txt=f'Warnwerte im Hub Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                    if not deflection_warning_groups_refined_sorted.empty:
                                for idx, df_row in enumerate(deflection_warning_groups_refined_sorted.values[0:1]):    
                    
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)           
                                    pdf.multi_cell(w =190, h = 7, txt = f'Die Warngrenze in {len(deflection_warning_groups_refined_sorted)} Bereichen in Auslenkung überschritten (± 10 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]} /n' ,
                                                     border = 0,align = 'L', fill = False)                
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 60)
                                    pdf.set_text_color(0,0,0)
                                    file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                    pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                    pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    if  len(deflection_warning_groups_refined_sorted) > 1:        

                                for idx, df_row in enumerate(deflection_warning_groups_refined_sorted.values[1:]):
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,0)
                                    pdf.multi_cell(w = 190, h = 7, txt=f'Warnwerte im Auslenkung Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                    file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '') 
                    if not lift_failure_groups_refined_sorted.empty:

                        for idx, df_row in enumerate(lift_failure_groups_refined_sorted.values[0:1]):    
                            pdf.add_page()
                            pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                            pdf.set_font('helvetica','', 16)
                            pdf.set_xy(10, 35)
                            pdf.set_text_color(0,0,255)
                            pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                            pdf.set_xy(10, 45)
                            pdf.set_font('helvetica','', 14)
                            pdf.set_text_color(0,0,0)        
                            pdf.multi_cell(w =190, h = 7, txt = f'Die Fehlergrenzen in {len(lift_failure_groups_refined_sorted)} Bereichen in Hub überschritten (± 15 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]}/n' ,
                                                 border = 0,align = 'L', fill = False)
                            y = pdf.get_y()
                            pdf.set_xy(10, y)        
                            pdf.set_font('helvetica','', 14)
                            pdf.set_xy(10, 60)
                            pdf.set_text_color(0,0,0)
                            file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                            pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                            pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    if  len(lift_failure_groups_refined_sorted) > 1:        

                            for idx, df_row in enumerate(lift_failure_groups_refined_sorted.values[1:]):
                                
                                pdf.add_page()
                                pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                pdf.set_font('helvetica','', 14)
                                pdf.set_xy(10, 40)
                                pdf.set_text_color(0,0,0)
                                pdf.multi_cell(w = 190, h = 7, txt=f'Fehlerwerte im Hub Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                    if not deflection_failure_groups_refined_sorted.empty:
                                for idx, df_row in enumerate(deflection_failure_groups_refined_sorted.values[0:1]):    
                    
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)           
                                    pdf.multi_cell(w =190, h = 7, txt = f'Die Fehlergrenzen in {len(deflection_failure_groups_refined_sorted)} Bereichen in Auslenkung überschritten (± 15 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]} /n' ,
                                                     border = 0,align = 'L', fill = False)                
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 60)
                                    pdf.set_text_color(0,0,0)
                                    file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                    pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                    pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    if  len(deflection_failure_groups_refined_sorted) > 1:        

                                for idx, df_row in enumerate(deflection_failure_groups_refined_sorted.values[1:]):
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,0)
                                    pdf.multi_cell(w = 190, h = 7, txt=f'Fehlerwerte im Auslenkung Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                    file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')

                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub und Auslenkung überschritten (± 15 mm) oder (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten (± 15 mm) oder (± 10 mm) und keine warnwerte in Hub überschritten (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty:

                              pdf.add_page()
                              pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                              pdf.set_font('helvetica','', 16)
                              pdf.set_xy(10, 35)
                              pdf.set_text_color(0,0,255)
                              pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                align = 'L', fill = False)
                              pdf.set_xy(10, 45)
                              pdf.set_font('helvetica','', 14)
                              pdf.set_text_color(0,0,0)                
                              pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub und Auslenkung überschritten (± 15 mm) oder (± 10 mm) und keine Warnwerte in Auslenkung überschritten (± 10 mm)' ,
                                               border = 0,align = 'L', fill = False)
                    
                    if deflection_warning_groups_refined_sorted.empty  and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty:

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten (± 15 mm) oder (± 10 mm) und keine Fehlerwerte in Hub überschritten (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    if  lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty:

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub überschritten (± 15 mm) oder (± 10 mm) und keine Fehlerwerte in Auslenkung überschritten (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)
    
                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                    
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub und Auslenkung überschritten (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty: 
                                    pdf.add_page()
                    
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Hub und Auslenkung überschritten (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if lift_warning_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty: 

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub überschritten (± 15 mm) oder (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    if deflection_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty:

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten (± 15 mm) oder (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    if  lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty:

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub überschritten (± 10 mm) und keine Fehlerwerte in Auslenkung überschritten (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    if deflection_warning_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty:

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Auslenkung überschritten (± 10 mm) oder Fehlerwerte in Hub überschritten (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                    
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)               
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub überschritten (± 10 mm)' ,
                                                 border = 0,align = 'L', fill = False)         
                    if deflection_warning_groups_refined_sorted.empty and not  lift_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Auslenkung überschritten (± 10 mm)' ,
                                                 border = 0,align = 'L', fill = False)                
                    if  lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty: 
                                    pdf.add_page()
                    
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)               
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Hub überschritten (± 15 mm)' ,
                                                 border = 0,align = 'L', fill = False)         
                    if deflection_failure_groups_refined_sorted.empty and not  lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty: 

                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Auslenkung überschritten (± 15 mm)' ,
                                                 border = 0,align = 'L', fill = False)
                    
                    
                    if not refined_anomalies_values.empty:
                      
                            for idx, df_row in enumerate(refined_anomalies_values.values):
        
                                    pdf.add_page()
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =190, h = 7, txt = str('Mögliche Anomalien zwischen den Positionen: ' + str(df_row[0]) +" und " + str(df_row[1])), border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_text_color(0,0,0)
                                    pdf.set_xy(30, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(40, 52)
                                    pdf.cell(w=10,h=5, txt='I.O', border = 0, align = 'L', fill = False)
                                    pdf.set_xy(75, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(85, 52)
                                    pdf.cell(w=10,h=5, txt='N.I.O', border = 0,align = 'L', fill = False)
                                    pdf.set_xy(120, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(130, 52)
                                    pdf.cell(w=10,h=5, txt='Ist.Korr', border = 0,align = 'L', fill = False)
                                    file_name1 = os.path.abspath(working_directory+'/Anomalie_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Anomalie_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                    else: 
                                    pdf.add_page()
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =190, h = 7, txt = str('Gibt es keine Anomalien in Hub und Auslenkung Bereichen'), border = 0,
                                      align = 'L', fill = False)
                    
           

                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Einstieg ins Dashboard ') , border = 0,
                              align = 'L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Einsteig_ins_Dashboard.jpg")[0], x=15, y= 45, w=180, h=100)
                    pdf.image(glob.glob(r"vorlage/Maintenance_Center.png")[0], x=15, y= 150, w=180, h=100)
                    pdf.set_xy(10, 260)
                    pdf.cell( w=160, h=5, txt= self.link_to_customer_company_dashboard ,link='', border=0, align=Align.L)
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Mögliche erkennbare Fehlerfälle ') , border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 50)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = 'Der Smart Collector ist in der Lage, eine beträchtliche Anzahl möglicher Fehler an der Stromschiene sowie am Stromabnehmer zu erkennen./nDie unten erwähnten Fehler wurden in der Vahle EHB-Testanlage in Rahmen eine Prüfung simuliert und die Ergebnisse analysiert und bearbeitet.' ,
                                         border = 0,align = 'L', fill = False)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_xy(10, 80)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Fehler in der Anlage ') , border = 0,
                              align = 'L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_1.png")[0], x=25, y= 95, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(40, 167)
                    pdf.cell(w = 50, h=5, txt='Kupfer zu Kurz in Trennstelle', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_2.png")[0], x=105, y= 95, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(110, 167)
                    pdf.cell(w = 50, h=5, txt='nicht Korrekt angeschraubter Festpunkt', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_3.png")[0], x=25, y= 175, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(35, 247)
                    pdf.cell(w = 50, h=5, txt='Kabel zwischen Schiene und Träger', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_4.png")[0], x=105, y= 175, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(120, 247)
                    pdf.cell(w = 50, h=5, txt='aufgebogene Schiene', border = 0, align='L', fill = False)
                    
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_5.png")[0], x=25, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(35, 112)
                    pdf.cell(w = 50, h=5, txt='Schiene nicht in Halter eingeclipst', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_6.png")[0], x=105, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(115, 112)
                    pdf.cell(w = 50, h=5, txt='Schiene zusammengedrückt', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_7.png")[0], x=25, y= 120, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(42, 192)
                    pdf.cell(w = 50, h=5, txt='Trennstelle Versatz', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_8.png")[0], x=105, y= 120, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(120, 192)
                    pdf.cell(w = 50, h=5, txt='Weichenübergang Versatz', border = 0, align='L', fill = False)
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_9.png")[0], x=25, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_10.png")[0], x=105, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(90, 115)
                    pdf.cell(w = 50, h=5, txt='eine fehlende Kohle', border = 0, align='L', fill = False)
                    pdf.set_text_color(0,0,0)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(10, 125)
                    pdf.cell(w = 190, h=5, txt='Zusätzlich kann der Smart Collector Anomalien wie Vibrationen und mechanische Auffälligkeiten detektieren.', border = 0, align='L', fill = False)
                    
                    pdf.output(r"./images/Final_Report_Deutsch.pdf")
                    
                    input_file = r'./images/Final_Report_Deutsch.pdf'
                    output_file = self.save_directory +r'/Final_Report_Deutsch.pdf'
                    
                    # Get pages
                    reader = PdfReader(input_file)
                    pages = [pagexobj(p) for p in reader.pages]
                    from reportlab.pdfgen import canvas 
                    # Compose new pdf
                    canvas =  canvas.Canvas(output_file)
                    for page_num, page in enumerate(pages, start=1):
                    
                        # Add page
                        canvas.setPageSize((page.BBox[2], page.BBox[3]))
                        canvas.doForm(makerl(canvas, page))
                        # Draw footer
                        footer_text = "Page %s of %s" % (page_num, len(pages))
                        x = 580
                        canvas.saveState()
                        canvas.setStrokeColorRGB(0, 0, 0)
                        canvas.setLineWidth(0.5)
                     
                        canvas.setFont('Helvetica-Bold', 10)
                        canvas.drawString(page.BBox[2]-x, 30, footer_text)
                        canvas.restoreState()
                        canvas.showPage()
                    
                    canvas.save()
                    
                    pdf = FPDF('P', 'mm', 'A4')
                    
                    pdf.add_page()
                    pdf.image(str(glob.glob(r"vorlage/cover_page.jpg")[0]), x=0,y=0, w=210, h=297)
                    pdf.image(self.customer_company_logo, x=165, y= 23, w=30, h=20)
                    pdf.set_font('helvetica','', 12)
                    pdf.set_xy(x= 15, y= 40)
                    pdf.set_text_color(248,248,255)
                    pdf.multi_cell(w =500, h = 10, txt = 'X Group', border = 0 ,align = 'L', fill = False)
                    pdf.set_font('helvetica','B', 20)
                    pdf.set_xy(x=70, y= 115)
                    pdf.set_text_color(25,25,112) 
                    pdf.multi_cell(w =500, h = 10, txt = f'{self.customer_company_name}', border = 0 ,align = 'L', fill = False)
                    pdf.set_xy(x=70, y=125)
                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    pdf.multi_cell(w =160, h = 10, txt = str(date_time), border = 0 ,align = 'L', fill = False)
                    pdf.add_page()
                    pdf.set_xy(10, 25)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,0)
                    pdf.cell(w =190, h = 7, txt = str('Table of contents') , border = 0,
                              align = 'L', fill = False)
                    pdf.set_font('helvetica','', 8)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,0)
                    pdf.set_xy(10, 45)
                    title_name = f'Current status of the system in ' + f'{self.customer_company_name}'
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                    pdf.ln()
                    title_name = f"{self.customer_company_name}"+ "/nResults of the inspection trip"
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                    pdf.ln()
                    title_name= "Exceeding absolute values"
                    title_string_length_uberschreiten = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y_uberschreiten = pdf.get_y()
                    pdf.set_dash_pattern(dash=1, gap=1)
                    pdf.line(title_string_length_uberschreiten+13 , title_padding_y_uberschreiten+2.5, 193, title_padding_y_uberschreiten+2.5)
                    pdf.ln()
                    pdf.set_text_color(0,0,0)
                    pdf.set_font('helvetica','', 8)
                    pdf.set_top_margin(37)
                    
                    if not refined_anomalies_values.empty: 
                              
                              for idx, df_row in enumerate(refined_anomalies_values.values): 
                                  title_padding_y= pdf.get_y()
                                  title_name= 'Possible anomalies between positions ' + str(df_row[0]) +" bis " + str(df_row[1])
                                  threading.Thread(target=pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT))
                                  title_string_length = pdf.get_string_width(title_name)
                                  last_anomalie_padding_y= pdf.get_y()
                                  threading.Thread(target=pdf.dashed_line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5, dash_length=1, space_length=1))
                                  pdf.set_y(last_anomalie_padding_y)

                    else:   
                            title_name = 'possible anomalies'
                            pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            last_anomalie_padding_y_noanomalies= pdf.get_y()
                            title_string_length = pdf.get_string_width(title_name)
                            pdf.set_dash_pattern(dash=1, gap=1)
                            pdf.line(title_string_length+13 , last_anomalie_padding_y_noanomalies-2.5, 193, last_anomalie_padding_y_noanomalies-2.5)
                            pdf.set_y(last_anomalie_padding_y_noanomalies)

                    title_name = f'Entrance to Dashboard ' 
                    title_string_length = pdf.get_string_width(title_name)
                    pdf.cell(w =190, h = 5, txt = title_name , border = 0,align = 'L', fill = False)
                    title_padding_y_Einstieg = pdf.get_y()
                    pdf.dashed_line(title_string_length+13 , title_padding_y_Einstieg+2.5, 193, title_padding_y_Einstieg+2.5, dash_length=1, space_length=1)
                    pdf.ln()
                    title_name = "Possible recognizable error cases"
                    title_string_length = pdf.get_string_width(title_name) 
                    pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                    title_padding_y_Mogliche = pdf.get_y()
                    pdf.dashed_line(title_string_length+13 , title_padding_y_Mogliche+2.5, 193, title_padding_y_Mogliche+2.5, dash_length=1, space_length=1)

                    
                    content_page_nu = pdf.page_no()
                    pdf.set_font('helvetica','', 8)
                    pdf.set_text_color(0,0,0)
                    pdf.page = 2 
                    pdf.set_xy(190, 45)
                    pdf.set_right_margin(20)
                    pdf.set_top_margin(35)
                    pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+1}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+3}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.cell(w =10, h = 5, txt = f"{content_page_nu+5}", border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                    pdf.set_right_margin(20)
                    pdf.set_top_margin(35)
                    
                    if not refined_anomalies_values.empty:  
                          if not  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
                                for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+5+len(lift_warning_groups_refined_sorted)+len(deflection_warning_groups_refined_sorted)+len(lift_failure_groups_refined_sorted)+len(deflection_failure_groups_refined_sorted)): 
                                    threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))

                                    if pdf.page in range(2, content_page_nu+1): 
                                       pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                       pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                       pdf.set_top_margin(35)
                              
                                Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 5 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                pdf.set_xy(190, title_padding_y_Einstieg)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                pdf.ln()
                                pdf.set_xy(190, title_padding_y_Mogliche)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                          else:
                                for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+6+len(lift_warning_groups_refined_sorted)+len(deflection_warning_groups_refined_sorted)+len(lift_failure_groups_refined_sorted)+len(deflection_failure_groups_refined_sorted)): 
                                    threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                              
                                    if pdf.page in range(2, content_page_nu+1): 
                                       pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                       pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                       pdf.set_top_margin(35)
                              
                                Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                pdf.set_xy(190, title_padding_y_Einstieg)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                pdf.ln()
                                pdf.set_xy(190, title_padding_y_Mogliche)
                                pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                    
                    else: 
                          if not  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
        
                                  first_anomalie_page_number = content_page_nu + 5 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                  #if content_page_nu == 2:
                                  pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                  pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                  pdf.set_top_margin(35)

                                  Einsteug_page_nu=  content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.set_xy(190, title_padding_y_Einstieg)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                  pdf.ln()
                                  pdf.set_xy(190, title_padding_y_Mogliche)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                          else:         
                                  first_anomalie_page_number = content_page_nu + 6 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                  #if content_page_nu == 2:
                                  pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                  pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                  pdf.set_top_margin(35)

                                  Einsteug_page_nu=  content_page_nu + 7 + len(lift_warning_groups_refined_sorted) + len(deflection_warning_groups_refined_sorted)+ len(lift_failure_groups_refined_sorted) + len(deflection_failure_groups_refined_sorted)
                                  pdf.set_xy(190, title_padding_y_Einstieg)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                  pdf.ln()
                                  pdf.set_xy(190, title_padding_y_Mogliche)
                                  pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)


                    
                    
                    pdf.set_page_background(glob.glob(r"vorlage/background_seite.jpg")[0])
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Current status of the system in '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                    pdf.image(self.smart_collector_components_pic,x=25, y=125,w=160, h=130,type='' )
                    pdf.set_xy(65, 255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 10, txt = 'Figure 1: The components on the (Ofenklappe)', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 50)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = 'In ' + str(self.customer_company_name) + ''' the Smart Collector was installed on a landing gear. The system was submitted on the trailing unit and consists of the components: /n/n - Compact Current Collector   with 3D unit /n - Positioning system  /n - Main-Unit /n - Industrial router /n/n Following is the diagram of the system and components at '''+ str(self.customer_company_name)+ '.' ,
                                         border = 0,align = 'L', fill = False)
                    
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(self.smart_collector_with_3d_sensor_pic,x=25, y=45,w=160, h=110,type='' )
                    pdf.set_xy(70, 155)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 10, txt = 'Figure 2: Current Collector  '+ str(self.name_of_the_Stromabnehmer_series)+ ' with 3D-Sensor', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 170)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    if not self.armes_order_extra_section_EN:  
                            pdf.multi_cell(w =190, h = 7, txt = f'''The software of the Smart Collector allows the system to be completely scanned and the movement values of the Current Collector   to be assigned to the position values of the vehicle. It is also possible to store reference data and subsequently detect errors in the system by comparing the current values and the reference values. 
                            /nOver the past few days, data of the plant was collected over several hours to first assess whether the current plant's condition of ''' + str(self.customer_company_name)+ f" is suitable for a reference run or Whether assembly or installation problems can already be identified in advance. The results are now presented on the following pages.",
                                            border = 0,align = 'L', fill = False)
                    else: 
                    
                           pdf.multi_cell(w =190, h = 7, txt = f'''The software of the Smart Collector allows the system to be completely scanned and the movement values of the Current Collector   to be assigned to the position values of the vehicle. It is also possible to store reference data and subsequently detect errors in the system by comparing the current values and the reference values. 
                            /nOver the past few days, data of the plant was collected over several hours to first assess whether the current plant's condition of ''' + str(self.customer_company_name)+ f" is suitable for a reference run or Whether assembly or installation problems can already be identified in advance. The results are now presented on the following pages./n/n{self.armes_order_extra_section_EN}",
                                            border = 0,align = 'L', fill = False)

                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =160, h = 10, txt = str('Results of the inspection trip '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                    pdf.image(hub_general_view_path_EN,x=25, y=45,w=180, h=95,type='' )
                    pdf.image(auslenkung_general_view_path_EN, x = 25,y= 150, w=180, h = 95, type='' )
                    pdf.set_xy(55, 137)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 5, txt = 'Figure 3: Data of the entire Lift plant route', border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(55, 242)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =160, h = 5, txt = 'Figure 4: Data of the entire Deflection plant route', border = 0,
                              align = 'L', fill = False)
                    length_of_the_whole_route = np.max(Excel_reference_raw_data.index.values) - np.min(Excel_reference_raw_data.index.values)
                    pdf.set_xy(10, 250)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = '''As can be seen in the above illustration, the Lift path and the Deflection path of the entire plant section of ''' + str(length_of_the_whole_route) + ' cm ' + '''Length determined.'''                             
                                    ,border = 0,align = 'L', fill = False )

                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_xy(10, 40)
                    pdf.multi_cell(w =190, h = 7, txt = '''The Current Collector  moves in the range of ''' + str(max_general_hub) + ' mm to '+ str(min_general_hub) + ' mm in Lift and in range of ' + str(max_general_auslenkung) + ' mm to ' + str(min_general_auslenkung) + ''' mm in Deflection and thus in its permissible range overall. The visible gaps in the display are due to the fact that the Current Collector  did not travel through all the routes/areas of the system during the recording time.
                                                             /nThe installed system as well as the tested system have the following characteristics: /n/n- 4 Arms are monitored via the 3D Unit Motion Sensor. /n/n- As the vehicle travels along the track, the Lift and Deflection values of every                 centimeter of the track are recorded./n/n- The average contact pressure of the collectors varies from '''+ str(maximum_press_pressure) + ' N to ' + str(minimum_press_pressure) + f''' N./n  The average press preasure was measured at {average_press_preasure}'''                             
                                    ,border = 0,align = 'L', fill = False )
                    
                    first_warnging_failure_page_number =   pdf.page_no()
                  
                    
                    if not lift_warning_groups_refined_sorted.empty:
                        for idx, df_row in enumerate(lift_warning_groups_refined_sorted.values[0:1]):    
                            pdf.add_page()
                            pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                            pdf.set_font('helvetica','', 16)
                            pdf.set_xy(10, 35)
                            pdf.set_text_color(0,0,255)
                            pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                            pdf.set_xy(10, 45)
                            pdf.set_font('helvetica','', 14)
                            pdf.set_text_color(0,0,0)        
                            pdf.multi_cell(w =190, h = 7, txt = f'The warning values exceeded (± 10 mm) {len(lift_warning_groups_refined_sorted)} in the Lift field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                 border = 0,align = 'L', fill = False)
                            y = pdf.get_y()
                            pdf.set_xy(10, y)        
                            pdf.set_font('helvetica','', 14)
                            pdf.set_xy(10, 60)
                            pdf.set_text_color(0,0,0)
                            file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                            pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                            pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    
                    if  len(lift_warning_groups_refined_sorted) > 1:        
                            for idx, df_row in enumerate(lift_warning_groups_refined_sorted.values[1:]):
                                pdf.add_page()
                                pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                pdf.set_font('helvetica','', 14)
                                pdf.set_xy(10, 35)
                                pdf.set_text_color(0,0,0)
                                pdf.multi_cell(w = 190, h = 7, txt=f'Warning values in Lift field between positions: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                    
                    if not deflection_warning_groups_refined_sorted.empty:
                                for idx, df_row in enumerate(deflection_warning_groups_refined_sorted.values[0:1]):    
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)           
                                    pdf.multi_cell(w =190, h = 7, txt = f'The warning values exceeded (± 10 mm) {len(deflection_warning_groups_refined_sorted)} in the Deflection field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                     border = 0,align = 'L', fill = False)                
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 60)
                                    pdf.set_text_color(0,0,0)
                                    file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                    pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                    pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    
                    if  len(deflection_warning_groups_refined_sorted) > 1:        
                                for idx, df_row in enumerate(deflection_warning_groups_refined_sorted.values[1:]):
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,0)
                                    pdf.multi_cell(w = 190, h = 7, txt=f'Warning values in Deflection field between positions: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                    file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')

                    if not lift_failure_groups_refined_sorted.empty:
                        for idx, df_row in enumerate(lift_failure_groups_refined_sorted.values[0:1]):    
                            pdf.add_page()
                            pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                            pdf.set_font('helvetica','', 16)
                            pdf.set_xy(10, 35)
                            pdf.set_text_color(0,0,255)
                            pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                              align = 'L', fill = False)
                            pdf.set_xy(10, 45)
                            pdf.set_font('helvetica','', 14)
                            pdf.set_text_color(0,0,0)        
                            pdf.multi_cell(w =190, h = 7, txt = f'The failure values exceeded (± 15 mm) {len(lift_failure_groups_refined_sorted)} times in the Lift field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                 border = 0,align = 'L', fill = False)
                            y = pdf.get_y()
                            pdf.set_xy(10, y)        
                            pdf.set_font('helvetica','', 14)
                            pdf.set_xy(10, 60)
                            pdf.set_text_color(0,0,0)
                            file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                            file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                            pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                            pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    
                    if  len(lift_failure_groups_refined_sorted) > 1:        
                            for idx, df_row in enumerate(lift_failure_groups_refined_sorted.values[1:]):
                                pdf.add_page()
                                pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                pdf.set_font('helvetica','', 14)
                                pdf.set_xy(10, 35)
                                pdf.set_text_color(0,0,0)
                                pdf.multi_cell(w = 190, h = 7, txt=f'Failure values in Lift field between positions: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')

                    if not deflection_failure_groups_refined_sorted.empty:
                                for idx, df_row in enumerate(deflection_failure_groups_refined_sorted.values[0:1]):    
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)           
                                    pdf.multi_cell(w =190, h = 7, txt = f'Failure values exceeded (± 15 mm) {len(deflection_failure_groups_refined_sorted)} times in the Deflection field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                     border = 0,align = 'L', fill = False)                
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 60)
                                    pdf.set_text_color(0,0,0)
                                    file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                    pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                    pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                    
                    if  len(deflection_failure_groups_refined_sorted) > 1:        
                                for idx, df_row in enumerate(deflection_failure_groups_refined_sorted.values[1:]):
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,0)
                                    pdf.multi_cell(w = 190, h = 7, txt=f'Failure values in Deflection field between positions: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                    file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')

                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Lift and Deflection fields exceeded (± 10 mm) and no failure values in Lift and Deflection fields exceeded (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection field exceeded (± 15 mm) and no warning values in Lift and Deflection fields exceeded (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty  and lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift field exceeded (± 15 mm) and no warning values in Lift and Deflection fields exceeded (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)

                    if deflection_warning_groups_refined_sorted.empty  and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty : 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift and Deflection fields exceeded (± 15 mm) and no failure values in Deflection field exceeded (± 15 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    
                    if lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift and Deflection fields exceeded (± 15 mm) and no warning values in Lift field exceeded (± 10 mm)' ,
                                              border = 0,align = 'L', fill = False)

                    if deflection_warning_groups_refined_sorted.empty and lift_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values both in Lift and Deflection fields exceeded (± 10 mm)',
                                                     border = 0,align = 'L', fill = False)
                    
                    if deflection_failure_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty:
                                   pdf.add_page()
                                   pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                   pdf.set_font('helvetica','', 16)
                                   pdf.set_xy(10, 35)
                                   pdf.set_text_color(0,0,255)
                                   pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                     align = 'L', fill = False)
                                   pdf.set_xy(10, 45)
                                   pdf.set_font('helvetica','', 14)
                                   pdf.set_text_color(0,0,0)               
                                   pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in both Lift and Deflection fields exceeded (± 15 mm)',
                                                border = 0,align = 'L', fill = False)

                    if lift_warning_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure or warning values in Lift field exceeded (± 15 mm) or (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    
                    if deflection_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure or warning values in Deflection field exceeded (± 15 mm) or (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    
                    if lift_warning_groups_refined_sorted.empty and deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection exceeded (± 15 mm) or warning values in Lift field exceeded (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                    
                    
                    if deflection_warning_groups_refined_sorted.empty and lift_failure_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift exceeded (± 15 mm) or warning values in Deflection field exceeded (± 10 mm)' ,
                                                     border = 0,align = 'L', fill = False)
                                    
                    if  lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)               
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Lift field exceeded (± 10 mm)' ,
                                                 border = 0,align = 'L', fill = False)         
                    
                    if deflection_warning_groups_refined_sorted.empty and not  lift_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty: 
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Deflection field exceeded (± 10 mm)' ,
                                                 border = 0,align = 'L', fill = False)                
                    
                    
                    if lift_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not deflection_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)               
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift field exceeded (± 15 mm)' ,
                                                 border = 0,align = 'L', fill = False)         
                    
                    
                    if deflection_failure_groups_refined_sorted.empty and not lift_warning_groups_refined_sorted.empty and not deflection_warning_groups_refined_sorted.empty and not lift_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)               
                                    pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection field exceeded (± 15 mm)' ,
                                                 border = 0,align = 'L', fill = False)         
                    
                    

                    if not refined_anomalies_values.empty:
                      
                            for idx, df_row in enumerate(refined_anomalies_values.values):
        
                                    pdf.add_page()
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =190, h = 7, txt = str('possible anomalies between positions: ' + str(df_row[0]) +" and " + str(df_row[1])), border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_text_color(0,0,0)
                                    pdf.set_xy(30, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(40, 52)
                                    pdf.cell(w=10,h=5, txt='I.O', border = 0, align = 'L', fill = False)
                                    pdf.set_xy(75, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(85, 52)
                                    pdf.cell(w=10,h=5, txt='N.I.O', border = 0,align = 'L', fill = False)
                                    pdf.set_xy(120, 52)
                                    pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                    pdf.set_xy(130, 52)
                                    pdf.cell(w=10,h=5, txt='Ist.Korr', border = 0,align = 'L', fill = False)
                                    file_name1 = os.path.abspath(working_directory+'/Anomalie_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                    file_name2 = os.path.abspath(working_directory+'/Anomalie_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                    pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                    else: 
                                    pdf.add_page()
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 40)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =190, h = 7, txt = str('There are no anomalies in Lift and deflection fields'), border = 0,
                                      align = 'L', fill = False)

                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Entrance to Dashboard ') , border = 0,
                              align = 'L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Einsteig_ins_Dashboard.jpg")[0], x=15, y= 45, w=180, h=100)
                    pdf.image(glob.glob(r"vorlage/Maintenance_Center.png")[0], x=15, y= 150, w=180, h=100)
                    pdf.set_xy(10, 260)
                    if not self.link_to_customer_company_dashboard:
                       pdf.cell( w=160, h=5, txt='' ,link='', border=0, align=Align.L)
                    else: 
                       pdf.cell( w=160, h=5, txt=self.link_to_customer_company_dashboard ,link='', border=0, align=Align.L)
            
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.set_font('helvetica','', 16)
                    pdf.set_xy(10, 35)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Possible recognizable error cases ') , border = 0,
                              align = 'L', fill = False)
                    pdf.set_xy(10, 50)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_text_color(0,0,0)
                    pdf.multi_cell(w =190, h = 7, txt = 'The Smart Collector is able to detect a considerable number of possible faults on the Electric rail as well as on the Current Collector ./nThe defects mentioned below were simulated in the Vahle EHB test facility as part of a test and the results were analyzed and processed.' ,
                                         border = 0,align = 'L', fill = False)
                    pdf.set_font('helvetica','', 14)
                    pdf.set_xy(10, 80)
                    pdf.set_text_color(0,0,255)
                    pdf.multi_cell(w =190, h = 10, txt = str('Error in the plant ') , border = 0,
                              align = 'L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_1.png")[0], x=25, y= 95, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(33, 167)
                    pdf.cell(w = 50, h=5, txt='Copper too short in separation point', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_2.png")[0], x=105, y= 95, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(110, 167)
                    pdf.cell(w = 50, h=5, txt='Fixed point not screwed on correctly', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_3.png")[0], x=25, y= 175, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(35, 247)
                    pdf.cell(w = 50, h=5, txt='Cable between rail and carrier', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_4.png")[0], x=105, y= 175, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(125, 247)
                    pdf.cell(w = 50, h=5, txt='bent up rail', border = 0, align='L', fill = False)
                    
                    
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_5.png")[0], x=25, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(35, 112)
                    pdf.cell(w = 50, h=5, txt='Rail not clipped into holder', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_6.png")[0], x=105, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(120, 112)
                    pdf.cell(w = 55, h=5, txt='Rail compressed', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_7.png")[0], x=25, y= 120, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(42, 192)
                    pdf.cell(w = 50, h=5, txt='Separation point Offset', border = 0, align='L', fill = False)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_8.png")[0], x=105, y= 120, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(120, 192)
                    pdf.cell(w = 50, h=5, txt='Switch transition Offset', border = 0, align='L', fill = False)
                    
                    pdf.add_page()
                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_9.png")[0], x=25, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_10.png")[0], x=105, y= 40, w=70, h=70)
                    pdf.set_text_color(0,0,255)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(87, 115)
                    pdf.cell(w = 50, h=5, txt='A missing coal brush', border = 0, align='L', fill = False)
                    pdf.set_text_color(0,0,0)
                    pdf.set_font('helvetica','', 10)
                    pdf.set_xy(10, 125)
                    pdf.cell(w = 190, h=5, txt='In addition, the Smart Collector can detect anomalies such as vibrations and mechanical abnormalities.', border = 0, align='L', fill = False)
                    
                    
                    pdf.output(r"./images/Final_Report_English.pdf")
                    input_file = r'./images/Final_Report_English.pdf'
                    output_file = self.save_directory +r'/Final_Report_English.pdf'
                    from reportlab.pdfgen import canvas
        
                    # Get pages
                    reader = PdfReader(input_file)
                    pages = [pagexobj(p) for p in reader.pages]
                    # Compose new pdf
                    canvas = canvas.Canvas(output_file)
                    for page_num, page in enumerate(pages, start=1):
                        # Add page
                        canvas.setPageSize((page.BBox[2], page.BBox[3]))
                        canvas.doForm(makerl(canvas, page))
                        # Draw footer
                        footer_text = "Page %s of %s" % (page_num, len(pages))
                        x = 580
                        canvas.saveState()
                        canvas.setStrokeColorRGB(0, 0, 0)
                        canvas.setLineWidth(0.5)
                        
                        canvas.setFont('Helvetica-Bold', 10)
                        canvas.drawString(page.BBox[2]-x, 30, footer_text)
                        canvas.restoreState()
                        canvas.showPage()
                    canvas.save()

            if self.name_of_the_Stromabnehmer_series == 'KESL':

                          groups1 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Deflection-PE [mm]')
                          groups2 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Deflection-L1 [mm]')
                          groups3 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Deflection-L2 [mm]')
                          groups4 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Deflection-L3 [mm]')
                          groups5 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Lift-L1 [mm]')
                          groups6 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Lift-L2 [mm]')
                          groups7 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Lift-L3 [mm]')
                          groups8 = Tools.KESL_warning_positions_extractor(mov_avg_eng, 'Lift-PE [mm]')
                          
                          KESL_deflection_groups_refined = pd.concat([groups1, groups2, groups3, groups4], axis = 0)
                          KESL_deflection_groups_refined.index = KESL_deflection_groups_refined.reset_index(drop = True).index 
                          KESL_deflection_warning_groups_refined_sorted = KESL_deflection_groups_refined.values
                          deflection_organized_min_order = sorted(KESL_deflection_warning_groups_refined_sorted, key = min)
                          KESL_deflection_warning_groups_refined_sorted = pd.DataFrame(deflection_organized_min_order)
                          KESL_deflection_warning_groups_refined_sorted.index = KESL_deflection_warning_groups_refined_sorted.reset_index(drop=True).index
                          if KESL_deflection_warning_groups_refined_sorted.empty:
                             pass
                          
                              
                          else: 
                               KESL_deflection_warning_groups_refined_sorted.columns = ['Start Position', 'End Position']
                          
                          KESL_lift_groups_refined = pd.concat([groups5, groups6, groups7, groups8], axis = 0)
                          KESL_lift_groups_refined.index = KESL_lift_groups_refined.reset_index(drop = True).index 
                          KESL_lift_warning_groups_refined_sorted = KESL_lift_groups_refined.values
                          KESL_lift_organized_min_order = sorted(KESL_lift_warning_groups_refined_sorted, key = min)
                          KESL_lift_warning_groups_refined_sorted = pd.DataFrame(KESL_lift_organized_min_order)
                          KESL_lift_warning_groups_refined_sorted.index = KESL_lift_warning_groups_refined_sorted.reset_index(drop=True).index
                          
                          if KESL_lift_warning_groups_refined_sorted.empty:
                             
                          
                             pass
                          else: 
                             KESL_lift_warning_groups_refined_sorted.columns = ['Start Position', 'End Position']
                          

                          KESL_deflection_warning_groups_refined_sorted = Tools.dataframe_filter(KESL_deflection_warning_groups_refined_sorted, 200)        
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_warning_groups_refined_sorted, '/n')
                          KESL_deflection_warning_groups_refined_sorted = Tools.smoothing_filter(KESL_deflection_warning_groups_refined_sorted)
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_warning_groups_refined_sorted, '/n')
                          KESL_deflection_warning_groups_refined_sorted = Tools.filter_between_start_end(KESL_deflection_warning_groups_refined_sorted)
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_warning_groups_refined_sorted, '/n')
                          
                          KESL_lift_warning_groups_refined_sorted = Tools.dataframe_filter(KESL_lift_warning_groups_refined_sorted, 200)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_warning_groups_refined_sorted, '/n')
                          KESL_lift_warning_groups_refined_sorted = Tools.smoothing_filter(KESL_lift_warning_groups_refined_sorted)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_warning_groups_refined_sorted, '/n')
                          KESL_lift_warning_groups_refined_sorted = Tools.filter_between_start_end(KESL_lift_warning_groups_refined_sorted)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_warning_groups_refined_sorted, '/n')

                          groups1 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Deflection-PE [mm]')
                          groups2 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Deflection-L1 [mm]')
                          groups3 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Deflection-L2 [mm]')
                          groups4 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Deflection-L3 [mm]')
                          groups5 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Lift-L1 [mm]')
                          groups6 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Lift-L2 [mm]')
                          groups7 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Lift-L3 [mm]')
                          groups8 = Tools.KESL_failure_positions_extractor(mov_avg_eng, 'Lift-PE [mm]')
                          
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_lift_warning_groups_refined_sorted, 'Lift', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_lift_warning_groups_refined_sorted, 'Deflection', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_deflection_warning_groups_refined_sorted, 'Deflection', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_deflection_warning_groups_refined_sorted, 'Lift', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_lift_warning_groups_refined_sorted, 'Abstand', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_lift_warning_groups_refined_sorted, 'Auslenkung', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_deflection_warning_groups_refined_sorted, 'Auslenkung', 'warning')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_deflection_warning_groups_refined_sorted, 'Abstand', 'warning')

                          KESL_deflection_groups_refined_failure = pd.concat([groups1, groups2, groups3, groups4], axis = 0)
                          KESL_deflection_groups_refined_failure.index = KESL_deflection_groups_refined_failure.reset_index(drop = True).index 
                          KESL_deflection_failure_groups_refined_sorted = KESL_deflection_groups_refined_failure.values
                          KESL_deflection_organized_min_order_failure = np.sort(KESL_deflection_failure_groups_refined_sorted, axis=None)
                          KESL_deflection_organized_min_order_failure = KESL_deflection_organized_min_order_failure.reshape(-1,2)
                          KESL_deflection_failure_groups_refined_sorted = pd.DataFrame(KESL_deflection_organized_min_order_failure)
                          KESL_deflection_failure_groups_refined_sorted.index = KESL_deflection_failure_groups_refined_sorted.reset_index(drop=True).index
                          
                          if KESL_deflection_failure_groups_refined_sorted.empty:
                             pass

                          else: 
                               KESL_deflection_failure_groups_refined_sorted.columns = ['Start Position', 'End Position']
                          
                          KESL_lift_groups_refined_failure = pd.concat([groups5, groups6, groups7, groups8], axis = 0)
                          KESL_lift_groups_refined_failure.index = KESL_lift_groups_refined_failure.reset_index(drop = True).index 
                          KESL_lift_failure_groups_refined_sorted = KESL_lift_groups_refined_failure.values
                          KESL_lift_organized_min_order_failure = np.sort(KESL_lift_failure_groups_refined_sorted, axis=None)
                          KESL_lift_organized_min_order_failure = KESL_lift_organized_min_order_failure.reshape(-1,2)
                          KESL_lift_failure_groups_refined_sorted = pd.DataFrame(KESL_lift_organized_min_order_failure)
                          KESL_lift_failure_groups_refined_sorted.index = KESL_lift_failure_groups_refined_sorted.reset_index(drop=True).index
                          if KESL_lift_failure_groups_refined_sorted.empty:

                             pass
                          else: 
                             KESL_lift_failure_groups_refined_sorted.columns = ['Start Position', 'End Position'] 
                          
                          KESL_deflection_failure_groups_refined_sorted = Tools.dataframe_filter(KESL_deflection_failure_groups_refined_sorted, 200)        
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_failure_groups_refined_sorted, '/n')
                          KESL_deflection_failure_groups_refined_sorted = Tools.smoothing_filter(KESL_deflection_failure_groups_refined_sorted)
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_failure_groups_refined_sorted, '/n')
                          KESL_deflection_failure_groups_refined_sorted = Tools.filter_between_start_end(KESL_deflection_failure_groups_refined_sorted)
                          print('deflection_failure_groups_refined_sorted: ', KESL_deflection_failure_groups_refined_sorted, '/n')
                          
                          KESL_lift_failure_groups_refined_sorted = Tools.dataframe_filter(KESL_lift_failure_groups_refined_sorted, 200)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_failure_groups_refined_sorted, '/n')
                          KESL_lift_failure_groups_refined_sorted = Tools.smoothing_filter(KESL_lift_failure_groups_refined_sorted)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_failure_groups_refined_sorted, '/n')
                          KESL_lift_failure_groups_refined_sorted = Tools.filter_between_start_end(KESL_lift_failure_groups_refined_sorted)
                          print('lift_failure_groups_refined_sorted: ', KESL_lift_failure_groups_refined_sorted, '/n')

                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_lift_failure_groups_refined_sorted, 'Lift', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_lift_failure_groups_refined_sorted, 'Deflection', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_deflection_failure_groups_refined_sorted, 'Deflection', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_eng, KESL_deflection_failure_groups_refined_sorted, 'Lift', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_lift_failure_groups_refined_sorted, 'Abstand', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_lift_failure_groups_refined_sorted, 'Auslenkung', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_deflection_failure_groups_refined_sorted, 'Auslenkung', 'failure')
                          Tools.anomalies_warning_failure_plotter(mov_avg_df_nor, KESL_deflection_failure_groups_refined_sorted, 'Abstand', 'failure')    

                          pdf = FPDF('P', 'mm', 'A4')
                          
                          pdf.add_page()
                          pdf.image(str(glob.glob(r"vorlage/cover_page.jpg")[0]), x=0,y=0, w=210, h=297)
                          pdf.image(self.customer_company_logo, x=165, y= 23, w=30, h=20)
                          pdf.set_font('helvetica','', 12)
                          pdf.set_xy(x= 15, y= 40)
                          pdf.set_text_color(248,248,255)
                          pdf.multi_cell(w =500, h = 10, txt = 'X Group', border = 0 ,align = 'L', fill = False)
                          pdf.set_font('helvetica','B', 20)
                          pdf.set_xy(x=70, y= 115)
                          pdf.set_text_color(25,25,112) 
                          pdf.multi_cell(w =500, h = 10, txt = f'{self.customer_company_name}', border = 0 ,align = 'L', fill = False)
                          pdf.set_xy(x=70, y=125)
                          now = datetime.now()
                          date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                          pdf.multi_cell(w =160, h = 10, txt = str(date_time), border = 0 ,align = 'L', fill = False)
                          pdf.add_page()
                          pdf.set_xy(10, 25)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,0)
                          pdf.cell(w =190, h = 7, txt = str('Inhaltsverzeichnis ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.set_font('helvetica','', 8)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,0)
                          pdf.set_xy(10, 45)
                          title_name = f'Aktueller Status des Systems in der  ' + f'{self.customer_company_name}'
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                          pdf.ln()
                          title_name = f"{self.customer_company_name}"+ "/nErgebnisse der Inspektionsfahrt"
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                          pdf.ln()
                          title_name= "Überschreiten des Absolutwerts"
                          title_string_length_uberschreiten = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y_uberschreiten = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length_uberschreiten+13 , title_padding_y_uberschreiten+2.5, 193, title_padding_y_uberschreiten+2.5)
                          pdf.ln()
                          pdf.set_text_color(0,0,0)
                          pdf.set_font('helvetica','', 8)
                          pdf.set_top_margin(37)
                          
                          if not refined_anomalies_values.empty: 
                                    
                                    for idx, df_row in enumerate(refined_anomalies_values.values): 
                                        title_padding_y= pdf.get_y()
                                        title_name= 'Mögliche Anomalie bei Position ' + str(df_row[0]) +" bis " + str(df_row[1])
                                        threading.Thread(target=pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT))
                                        title_string_length = pdf.get_string_width(title_name)
                                        last_anomalie_padding_y= pdf.get_y()
                                        threading.Thread(target=pdf.dashed_line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5, dash_length=1, space_length=1))
                                        pdf.set_y(last_anomalie_padding_y)
      
                          else:   
                                  title_name = 'Mögliche Anomalie'
                                  pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                                  last_anomalie_padding_y_noanomalies= pdf.get_y()
                                  title_string_length = pdf.get_string_width(title_name)
                                  pdf.set_dash_pattern(dash=1, gap=1)
                                  pdf.line(title_string_length+13 , last_anomalie_padding_y_noanomalies-2.5, 193, last_anomalie_padding_y_noanomalies-2.5)
                                  pdf.set_y(last_anomalie_padding_y_noanomalies)
      
                          title_name = f'Einstieg ins Dashboard ' 
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name , border = 0,align = 'L', fill = False)
                          title_padding_y_Einstieg = pdf.get_y()
                          pdf.dashed_line(title_string_length+13 , title_padding_y_Einstieg+2.5, 193, title_padding_y_Einstieg+2.5, dash_length=1, space_length=1)
                          pdf.ln()
                          title_name = "Mögliche erkennbare Fehlerfälle"
                          title_string_length = pdf.get_string_width(title_name) 
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y_Mogliche = pdf.get_y()
                          pdf.dashed_line(title_string_length+13 , title_padding_y_Mogliche+2.5, 193, title_padding_y_Mogliche+2.5, dash_length=1, space_length=1)
      
                          
                          content_page_nu = pdf.page_no()
                          pdf.set_font('helvetica','', 8)
                          pdf.set_text_color(0,0,0)
                          pdf.page = 2 
                          pdf.set_xy(190, 45)
                          pdf.set_right_margin(20)
                          pdf.set_top_margin(35)
                          pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+1}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+3}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.cell(w =10, h = 5, txt = f"{content_page_nu+5}", border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.set_right_margin(20)
                          pdf.set_top_margin(35)
                          
                          if not refined_anomalies_values.empty:  
                                if not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                    for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+5+len(KESL_lift_warning_groups_refined_sorted)+len(KESL_deflection_warning_groups_refined_sorted)+len(KESL_lift_failure_groups_refined_sorted)+len(KESL_deflection_failure_groups_refined_sorted)): 
                                          threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                                    
                                          if pdf.page in range(2, content_page_nu+1): 
                                            pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                            pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                            pdf.set_top_margin(35)
                                    
                                    Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 5 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                    pdf.set_xy(190, title_padding_y_Einstieg)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                    pdf.ln()
                                    pdf.set_xy(190, title_padding_y_Mogliche)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                                
                                else: 
                                    
                                    for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+6+len(KESL_lift_warning_groups_refined_sorted)+len(KESL_deflection_warning_groups_refined_sorted)+len(KESL_lift_failure_groups_refined_sorted)+len(KESL_deflection_failure_groups_refined_sorted)): 
                                          threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                                    
                                          if pdf.page in range(2, content_page_nu+1): 
                                            pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                            pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                            pdf.set_top_margin(35)
                                    
                                    Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                    pdf.set_xy(190, title_padding_y_Einstieg)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                    pdf.ln()
                                    pdf.set_xy(190, title_padding_y_Mogliche)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)

                          else: 
                                  if not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                        
                                        first_anomalie_page_number = content_page_nu + 5 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                        #if content_page_nu == 2:
                                        pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                        pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                        pdf.set_top_margin(35)
      
                                        Einsteug_page_nu=  content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.set_xy(190, title_padding_y_Einstieg)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                        pdf.ln()
                                        pdf.set_xy(190, title_padding_y_Mogliche)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                                  
                                  else:      
                                        first_anomalie_page_number = content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                        #if content_page_nu == 2:
                                        pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                        pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                        pdf.set_top_margin(35)
      
                                        Einsteug_page_nu=  content_page_nu + 7 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.set_xy(190, title_padding_y_Einstieg)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                        pdf.ln()
                                        pdf.set_xy(190, title_padding_y_Mogliche)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                                      
                          
                          pdf.set_page_background(glob.glob(r"vorlage/background_seite.jpg")[0])
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Aktueller Status des Systems in der '+ f'{self.customer_company_name}') , border = 0,
                                    align = 'L', fill = False)
                          
                          pdf.image(self.smart_collector_components_pic,x=25, y=125,w=160, h=130,type='' )
                          pdf.set_xy(65, 255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 10, txt = 'Abbildung 1: Die Komponenten an der Ofenklappe', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 50)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = 'In der ' +f'{self.customer_company_name}' + ''' wurde der Smart Collector an einem Fahrwerk installiert. Das System wurde am Nachläufer eingereichtet und besteht aus den Komponenten: /n/n - Kompaktstromabnehmer mit 3D-Unit /n - Positionierungssystem  /n - Main-Unit /n - Industrierouter /n/n Folgend die Darstellung des Systems und der Komponenten bei '''+ f'{self.customer_company_name}'+ '.' ,
                                              border = 0,align = 'L', fill = False)
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(self.smart_collector_with_3d_sensor_pic,x=25, y=45,w=160, h=110,type='' )
                          pdf.set_xy(65, 155)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 10, txt = 'Abbildung 2: Stromabnehmer '+ str(self.name_of_the_Stromabnehmer_series)+ ' mit 3D-Sensor', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 170)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          
                          if not self.armes_order_extra_section:
                              pdf.multi_cell(w =190, h = 7, txt = f'''Die Software des Smart Collectors lässt es zu, die Anlage Komplett abzufahren und Bewegungswerte der Stromabnehmerarme den Positionswerten des Fahrzeugs zuzuordnen. Es ist auch möglich, Rferenzdaten zu hinterlegen und im weiteren Verlauf Fehler in der Anlage durch vergleich der aktuellen Werte und der Referenzwerte aufzudecken. 
                              /nIn den vergangenen Tagen wurden über mehrere Studen Anlagenwerte gesammelt, um zunächst zu bewerten, ob sich der aktuelle Anlagenzustand der ''' + str(self.customer_company_name)+ f" für eine Referenzfahrt eignet bzw. ob schon im Vorfeld Montage oder Verlegeprobleme erkennbar sind. Auf den folgenden Seiten werden nun die Ergebnisse dargestellt.",
                              
                                              border = 0,align = 'L', fill = False)
                          else:
                              pdf.multi_cell(w =190, h = 7, txt = f'''Die Software des Smart Collectors lässt es zu, die Anlage Komplett abzufahren und Bewegungswerte der Stromabnehmerarme den Positionswerten des Fahrzeugs zuzuordnen. Es ist auch möglich, Rferenzdaten zu hinterlegen und im weiteren Verlauf Fehler in der Anlage durch vergleich der aktuellen Werte und der Referenzwerte aufzudecken. 
                              /nIn den vergangenen Tagen wurden über mehrere Studen Anlagenwerte gesammelt, um zunächst zu bewerten, ob sich der aktuelle Anlagenzustand der ''' + str(self.customer_company_name)+ f" für eine Referenzfahrt eignet bzw. ob schon im Vorfeld Montage oder Verlegeprobleme erkennbar sind. Auf den folgenden Seiten werden nun die Ergebnisse dargestellt./n/n" + str(self.armes_order_extra_section),
                              
                                              border = 0,align = 'L', fill = False)

                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =160, h = 10, txt = str('Ergebnisse der Inspektionsfahr '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(hub_general_view_path_DE,x=25, y=45,w=180, h=95,type='' )
                          pdf.image(auslenkung_general_view_path_DE, x = 25,y= 150, w = 180, h = 95, type='' )
                          pdf.set_xy(50, 137)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 5, txt = 'Abbildung 3: Daten der gesamten Hub Anlagenstrecke', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(50, 242)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 5, txt = 'Abbildung 4: Daten der gesamten Auslenkung Anlagenstrecke', border = 0,
                                    align = 'L', fill = False)
                          length_of_the_whole_route = np.max(Excel_reference_raw_data.index.values) - np.min(Excel_reference_raw_data.index.values)
                          pdf.set_xy(10, 250)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = '''Wie in der obigen Darstellung zu sehen ist, wurden der Hubverlauf und der Auslenkungsverlauf der gesamten Anlagenstrecke von ca. ''' + str(length_of_the_whole_route) + ' cm ' + '''Länge ermittelt.'''                             
                                          ,border = 0,align = 'L', fill = False )
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_xy(10, 40)
                          pdf.multi_cell(w =190, h = 7, txt = '''Der Stromabnehmer bewegt sich im Bereich von ''' + str(max_general_hub) + ' mm bis '+ str(min_general_hub) + ' mm in Hub und im Bereich von ' + str(max_general_auslenkung) + ' mm bis ' + str(min_general_auslenkung) + ''' mm in Auslenkung und damit im Gesamten in seinem zulässigen Bereich. Die erkennbaren Lücken in der Darstellung entstehen dadurch, dass der Stromabnehmer nicht alle Bereiche der Anlage in der Auzeichnungszeit befahren hat.
                                                                  /nDas installierte System sowie die geprüfte Anlage weisen folgende Merkmale auf: /n/n - 4 Arme werden über den 3D-Unit Motion Sensor überwacht. /n/n - Während das Fahrzeug auf der Strecke fährt, werden die Hub und                                Auslenkungswerte von jedem Zentimeter der Strecke erfasst./n/n - Der Anpressdruck der Abnehmer variiert von '''+ str(maximum_press_pressure) + ' N bis '+ str(minimum_press_pressure) + f''' N./n   Der durchschnittliche Pressdruck beträgt {average_press_preasure} N.'''                              
                                          ,border = 0,align = 'L', fill = False )
                          
                          
                          if not KESL_lift_warning_groups_refined_sorted.empty:

                              for idx, df_row in enumerate(KESL_lift_warning_groups_refined_sorted.values[0:1]):    
                                  pdf.add_page()
                                  pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                  pdf.set_font('helvetica','', 16)
                                  pdf.set_xy(10, 35)
                                  pdf.set_text_color(0,0,255)
                                  pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                                  pdf.set_xy(10, 45)
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_text_color(0,0,0)        
                                  pdf.multi_cell(w =190, h = 7, txt = f'Die Warngrenze in {len(KESL_lift_warning_groups_refined_sorted)} Bereichen in Hub überschritten (± 20 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]}/n' ,
                                                      border = 0,align = 'L', fill = False)
                                  y = pdf.get_y()
                                  pdf.set_xy(10, y)        
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_xy(10, 60)
                                  pdf.set_text_color(0,0,0)
                                  file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                  file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                  
                                  pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                  pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_lift_warning_groups_refined_sorted) > 1:        

                                  for idx, df_row in enumerate(KESL_lift_warning_groups_refined_sorted.values[1:]):
                                      
                                      pdf.add_page()
                                      pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                      pdf.set_font('helvetica','', 14)
                                      pdf.set_xy(10, 40)
                                      pdf.set_text_color(0,0,0)
                                      pdf.multi_cell(w = 190, h = 7, txt=f'Warnwerte im Hub Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                      file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                      file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                      pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                      pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if not KESL_deflection_warning_groups_refined_sorted.empty:
                                      for idx, df_row in enumerate(KESL_deflection_warning_groups_refined_sorted.values[0:1]):    
                          
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)           
                                          pdf.multi_cell(w =190, h = 7, txt = f'Die Warngrenze in {len(KESL_deflection_warning_groups_refined_sorted)} Bereichen in Auslenkung überschritten (± 20 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]} /n' ,
                                                          border = 0,align = 'L', fill = False)                
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 60)
                                          pdf.set_text_color(0,0,0)
                                          file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                          pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                          pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_deflection_warning_groups_refined_sorted) > 1:        

                                      for idx, df_row in enumerate(KESL_deflection_warning_groups_refined_sorted.values[1:]):
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,0)
                                          pdf.multi_cell(w = 190, h = 7, txt=f'Warnwerte im Auslenkung Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                          file_name1 = os.path.abspath(working_directory+'/Warning_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
      
                          if not KESL_lift_failure_groups_refined_sorted.empty:

                              for idx, df_row in enumerate(KESL_lift_failure_groups_refined_sorted.values[0:1]):    
                                  pdf.add_page()
                                  pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                  pdf.set_font('helvetica','', 16)
                                  pdf.set_xy(10, 35)
                                  pdf.set_text_color(0,0,255)
                                  pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                                  pdf.set_xy(10, 45)
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_text_color(0,0,0)        
                                  pdf.multi_cell(w =190, h = 7, txt = f'Die Fehlergrenzen in {len(KESL_lift_failure_groups_refined_sorted)} Bereichen in Hub überschritten (± 30 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]}/n' ,
                                                      border = 0,align = 'L', fill = False)
                                  y = pdf.get_y()
                                  pdf.set_xy(10, y)        
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_xy(10, 60)
                                  pdf.set_text_color(0,0,0)
                                  file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                  file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                  
                                  pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                  pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_lift_failure_groups_refined_sorted) > 1:        

                                  for idx, df_row in enumerate(KESL_lift_failure_groups_refined_sorted.values[1:]):
                                      
                                      pdf.add_page()
                                      pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                      pdf.set_font('helvetica','', 14)
                                      pdf.set_xy(10, 40)
                                      pdf.set_text_color(0,0,0)
                                      pdf.multi_cell(w = 190, h = 7, txt=f'Fehlerwerte im Hub Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                      file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                      file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                      pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                      pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if not KESL_deflection_failure_groups_refined_sorted.empty:
                                      for idx, df_row in enumerate(KESL_deflection_failure_groups_refined_sorted.values[0:1]):    
                          
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)           
                                          pdf.multi_cell(w =190, h = 7, txt = f'Die Fehlergrenzen in {len(KESL_deflection_failure_groups_refined_sorted)} Bereichen in Auslenkung überschritten (± 30 mm), in den folgenden Positionen: {df_row[0]} und {df_row[1]} /n' ,
                                                          border = 0,align = 'L', fill = False)                
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 60)
                                          pdf.set_text_color(0,0,0)
                                          file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                          pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                          pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_deflection_failure_groups_refined_sorted) > 1:        

                                      for idx, df_row in enumerate(KESL_deflection_failure_groups_refined_sorted.values[1:]):
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,0)
                                          pdf.multi_cell(w = 190, h = 7, txt=f'Fehlerwerte im Auslenkung Bereich zwischen den Positionen: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                          file_name1 = os.path.abspath(working_directory+'/Failure_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')

                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub und Auslenkung überschritten (± 30 mm) oder (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten (± 30 mm) oder (± 20 mm) und keine warnwerte in Hub überschritten (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                    pdf.add_page()
                                    pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                    pdf.set_font('helvetica','', 16)
                                    pdf.set_xy(10, 35)
                                    pdf.set_text_color(0,0,255)
                                    pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                      align = 'L', fill = False)
                                    pdf.set_xy(10, 45)
                                    pdf.set_font('helvetica','', 14)
                                    pdf.set_text_color(0,0,0)                
                                    pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub und Auslenkung überschritten  (± 30 mm) oder  (± 20 mm) und keine Warnwerte in Auslenkung überschritten  (± 20 mm)' ,
                                                    border = 0,align = 'L', fill = False)
                          
                          if KESL_deflection_warning_groups_refined_sorted.empty  and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten   (± 30 mm) oder  (± 20 mm) und keine Fehlerwerte in Hub überschritten   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          
                          if  KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub überschritten   (± 30 mm) oder  (± 20 mm) und keine Fehlerwerte in Auslenkung überschritten   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)
          
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub und Auslenkung überschritten  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)

                          if KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Hub und Auslenkung überschritten   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)

                          if KESL_lift_warning_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty: 
 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Hub überschritten   (± 30 mm) oder  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty:

                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehler oder Warnwerte in Auslenkung überschritten   (± 30 mm) oder  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if  KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty:

                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub überschritten  (± 20 mm) und keine Fehlerwerte in Auslenkung überschritten   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty:

                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Auslenkung überschritten  (± 20 mm) oder Fehlerwerte in Hub überschritten   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)

                          if  KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)               
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Hub überschritten  (± 20 mm)' ,
                                                      border = 0,align = 'L', fill = False)         
                          if KESL_deflection_warning_groups_refined_sorted.empty and not  KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 

                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Warnwerte in Auslenkung überschritten  (± 20 mm)' ,
                                                      border = 0,align = 'L', fill = False)                
                          if  KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)               
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Hub überschritten   (± 30 mm)' ,
                                                      border = 0,align = 'L', fill = False)         
                          if KESL_deflection_failure_groups_refined_sorted.empty and not  KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty: 

                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'Gibt es keine Fehlerwerte in Auslenkung überschritten   (± 30 mm)' ,
                                                      border = 0,align = 'L', fill = False)
 
                          if not refined_anomalies_values.empty:
                            
                                  for idx, df_row in enumerate(refined_anomalies_values.values):
              
                                          pdf.add_page()
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =190, h = 7, txt = str('Mögliche Anomalien zwischen den Positionen: ' + str(df_row[0]) +" und " + str(df_row[1])), border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_text_color(0,0,0)
                                          pdf.set_xy(30, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(40, 52)
                                          pdf.cell(w=10,h=5, txt='I.O', border = 0, align = 'L', fill = False)
                                          pdf.set_xy(75, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(85, 52)
                                          pdf.cell(w=10,h=5, txt='N.I.O', border = 0,align = 'L', fill = False)
                                          pdf.set_xy(120, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(130, 52)
                                          pdf.cell(w=10,h=5, txt='Ist.Korr', border = 0,align = 'L', fill = False)
                                          file_name1 = os.path.abspath(working_directory+'/Anomalie_Hub_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Anomalie_Auslenkung_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          else: 
                                          pdf.add_page()
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =190, h = 7, txt = str('Gibt es keine Anomalien in Hub und Auslenkung Bereichen'), border = 0,
                                            align = 'L', fill = False)
      
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Einstieg ins Dashboard ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Einsteig_ins_Dashboard.jpg")[0], x=15, y= 45, w=180, h=100)
                          pdf.image(glob.glob(r"vorlage/Maintenance_Center.png")[0], x=15, y= 150, w=180, h=100)
                          pdf.set_xy(10, 260)
                          pdf.cell( w=160, h=5, txt= self.link_to_customer_company_dashboard ,link='', border=0, align=Align.L)
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Mögliche erkennbare Fehlerfälle ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 50)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = 'Der Smart Collector ist in der Lage, eine beträchtliche Anzahl möglicher Fehler an der Stromschiene sowie am Stromabnehmer zu erkennen./nDie unten erwähnten Fehler wurden in der Vahle EHB-Testanlage in Rahmen eine Prüfung simuliert und die Ergebnisse analysiert und bearbeitet.' ,
                                              border = 0,align = 'L', fill = False)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_xy(10, 80)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Fehler in der Anlage ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_1.png")[0], x=25, y= 95, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(40, 167)
                          pdf.cell(w = 50, h=5, txt='Kupfer zu Kurz in Trennstelle', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_2.png")[0], x=105, y= 95, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(110, 167)
                          pdf.cell(w = 50, h=5, txt='nicht Korrekt angeschraubter Festpunkt', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_3.png")[0], x=25, y= 175, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(35, 247)
                          pdf.cell(w = 50, h=5, txt='Kabel zwischen Schiene und Träger', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_4.png")[0], x=105, y= 175, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(120, 247)
                          pdf.cell(w = 50, h=5, txt='aufgebogene Schiene', border = 0, align='L', fill = False)
                          
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_5.png")[0], x=25, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(35, 112)
                          pdf.cell(w = 50, h=5, txt='Schiene nicht in Halter eingeclipst', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_6.png")[0], x=105, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(115, 112)
                          pdf.cell(w = 50, h=5, txt='Schiene zusammengedrückt', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_7.png")[0], x=25, y= 120, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(42, 192)
                          pdf.cell(w = 50, h=5, txt='Trennstelle Versatz', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_8.png")[0], x=105, y= 120, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(120, 192)
                          pdf.cell(w = 50, h=5, txt='Weichenübergang Versatz', border = 0, align='L', fill = False)
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_9.png")[0], x=25, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_10.png")[0], x=105, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(90, 115)
                          pdf.cell(w = 50, h=5, txt='eine fehlende Kohle', border = 0, align='L', fill = False)
                          pdf.set_text_color(0,0,0)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(10, 125)
                          pdf.cell(w = 190, h=5, txt='Zusätzlich kann der Smart Collector Anomalien wie Vibrationen und mechanische Auffälligkeiten detektieren.', border = 0, align='L', fill = False)
                          
                          pdf.output(r"./images/Final_Report_Deutsch.pdf")
                          
                          input_file = r'./images/Final_Report_Deutsch.pdf'
                          output_file = self.save_directory +r'/Final_Report_Deutsch.pdf'
                          
                          # Get pages
                          reader = PdfReader(input_file)
                          pages = [pagexobj(p) for p in reader.pages]
                          from reportlab.pdfgen import canvas  
                          # Compose new pdf
                          canvas =  canvas.Canvas(output_file)
                          for page_num, page in enumerate(pages, start=1):
                          
                              # Add page
                              canvas.setPageSize((page.BBox[2], page.BBox[3]))
                              canvas.doForm(makerl(canvas, page))
                          
                              # Draw footer
                              footer_text = "Page %s of %s" % (page_num, len(pages))
                              x = 580
                              canvas.saveState()
                              canvas.setStrokeColorRGB(0, 0, 0)
                              canvas.setLineWidth(0.5)
                          
                              canvas.setFont('Helvetica-Bold', 10)
                              canvas.drawString(page.BBox[2]-x, 30, footer_text)
                              canvas.restoreState()
                              canvas.showPage()
                          canvas.save()
                          
                          pdf = FPDF('P', 'mm', 'A4')
                          
                          pdf.add_page()
                          pdf.image(str(glob.glob(r"vorlage/cover_page.jpg")[0]), x=0,y=0, w=210, h=297)
                          pdf.image(self.customer_company_logo, x=165, y= 23, w=30, h=20)
                          pdf.set_font('helvetica','', 12)
                          pdf.set_xy(x= 15, y= 40)
                          pdf.set_text_color(248,248,255)
                          pdf.multi_cell(w =500, h = 10, txt = 'X Group', border = 0 ,align = 'L', fill = False)
                          pdf.set_font('helvetica','B', 20)
                          pdf.set_xy(x=70, y= 115)
                          pdf.set_text_color(25,25,112) 
                          pdf.multi_cell(w =500, h = 10, txt = f'{self.customer_company_name}', border = 0 ,align = 'L', fill = False)
                          pdf.set_xy(x=70, y=125)
                          now = datetime.now()
                          date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                          pdf.multi_cell(w =160, h = 10, txt = str(date_time), border = 0 ,align = 'L', fill = False)
                          pdf.add_page()
                          pdf.set_xy(10, 25)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,0)
                          pdf.cell(w =190, h = 7, txt = str('Table of contents') , border = 0,
                                    align = 'L', fill = False)
                          pdf.set_font('helvetica','', 8)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,0)
                          pdf.set_xy(10, 45)
                          title_name = f'Current status of the system in ' + f'{self.customer_company_name}'
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                          pdf.ln()
                          title_name = f"{self.customer_company_name}"+ "/nResults of the inspection trip"
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5)
                          pdf.ln()
                          title_name= "Exceeding absolute values"
                          title_string_length_uberschreiten = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y_uberschreiten = pdf.get_y()
                          pdf.set_dash_pattern(dash=1, gap=1)
                          pdf.line(title_string_length_uberschreiten+13 , title_padding_y_uberschreiten+2.5, 193, title_padding_y_uberschreiten+2.5)
                          pdf.ln()
                          pdf.set_text_color(0,0,0)
                          pdf.set_font('helvetica','', 8)
                          pdf.set_top_margin(37)
                          
                          if not refined_anomalies_values.empty: 
                                    
                                    for idx, df_row in enumerate(refined_anomalies_values.values): 
                                        title_padding_y= pdf.get_y()
                                        title_name= 'Possible anomalies between positions ' + str(df_row[0]) +" bis " + str(df_row[1])
                                        threading.Thread(target=pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT))
                                        title_string_length = pdf.get_string_width(title_name)
                                        last_anomalie_padding_y= pdf.get_y()
                                        threading.Thread(target=pdf.dashed_line(title_string_length+13 , title_padding_y+2.5, 193, title_padding_y+2.5, dash_length=1, space_length=1))
                                        pdf.set_y(last_anomalie_padding_y)
      
                          else:   
                                  title_name = 'possible anomalies'
                                  pdf.multi_cell( w = 190, h = 5, txt = title_name , border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                                  last_anomalie_padding_y_noanomalies= pdf.get_y()
                                  title_string_length = pdf.get_string_width(title_name)
                                  pdf.set_dash_pattern(dash=1, gap=1)
                                  pdf.line(title_string_length+13 , last_anomalie_padding_y_noanomalies-2.5, 193, last_anomalie_padding_y_noanomalies-2.5)
                                  pdf.set_y(last_anomalie_padding_y_noanomalies)
      
                          title_name = f'Entrance to Dashboard ' 
                          title_string_length = pdf.get_string_width(title_name)
                          pdf.cell(w =190, h = 5, txt = title_name , border = 0,align = 'L', fill = False)
                          title_padding_y_Einstieg = pdf.get_y()
                          pdf.dashed_line(title_string_length+13 , title_padding_y_Einstieg+2.5, 193, title_padding_y_Einstieg+2.5, dash_length=1, space_length=1)
                          pdf.ln()
                          title_name = "Possible recognizable error cases"
                          title_string_length = pdf.get_string_width(title_name) 
                          pdf.cell(w =190, h = 5, txt = title_name, border = 0,align = 'L', fill = False)
                          title_padding_y_Mogliche = pdf.get_y()
                          pdf.dashed_line(title_string_length+13 , title_padding_y_Mogliche+2.5, 193, title_padding_y_Mogliche+2.5, dash_length=1, space_length=1)
      
                          
                          content_page_nu = pdf.page_no()
                          pdf.set_font('helvetica','', 8)
                          pdf.set_text_color(0,0,0)
                          pdf.page = 2 
                          pdf.set_xy(190, 45)
                          pdf.set_right_margin(20)
                          pdf.set_top_margin(35)
                          pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+1}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.cell(w=10, h = 5,  txt = f"{content_page_nu+3}",  border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.cell(w =10, h = 5, txt = f"{content_page_nu+5}", border = 0,align = Align.R, new_x=XPos.RMARGIN, new_y=YPos.NEXT, fill = False)
                          pdf.set_right_margin(20)
                          pdf.set_top_margin(35)
                          
                          if not refined_anomalies_values.empty:  
                                if not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                    for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+5+len(KESL_lift_warning_groups_refined_sorted)+len(KESL_deflection_warning_groups_refined_sorted)+len(KESL_lift_failure_groups_refined_sorted)+len(KESL_deflection_failure_groups_refined_sorted)): 
                                          threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                                    
                                          if pdf.page in range(2, content_page_nu+1): 
                                            pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                            pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                            pdf.set_top_margin(35)
                                    
                                    Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 5 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                    pdf.set_xy(190, title_padding_y_Einstieg)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                    pdf.ln()
                                    pdf.set_xy(190, title_padding_y_Mogliche)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                                
                                else: 
                                    
                                    for idx, df_row in enumerate(refined_anomalies_values.values,content_page_nu+6+len(KESL_lift_warning_groups_refined_sorted)+len(KESL_deflection_warning_groups_refined_sorted)+len(KESL_lift_failure_groups_refined_sorted)+len(KESL_deflection_failure_groups_refined_sorted)): 
                                          threading.Thread(target=pdf.multi_cell(w=10, h = 5, txt = str(idx), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT ))
                                    
                                          if pdf.page in range(2, content_page_nu+1): 
                                            pdf.image(self.customer_company_logo, x=165, y= 10, w=30, h=20)
                                            pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                            pdf.set_top_margin(35)
                                    
                                    Einsteug_page_nu= len(refined_anomalies_values.values) + content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                    pdf.set_xy(190, title_padding_y_Einstieg)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                    pdf.ln()
                                    pdf.set_xy(190, title_padding_y_Mogliche)
                                    pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)

                          else: 
                                  if not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                        
                                        first_anomalie_page_number = content_page_nu + 5 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                        #if content_page_nu == 2:
                                        pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                        pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                        pdf.set_top_margin(35)
      
                                        Einsteug_page_nu=  content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.set_xy(190, title_padding_y_Einstieg)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                        pdf.ln()
                                        pdf.set_xy(190, title_padding_y_Mogliche)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                                  
                                  else:      
                                        first_anomalie_page_number = content_page_nu + 6 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.multi_cell(w=10, h = 5, txt = str(first_anomalie_page_number), align = Align.R, border = 0,new_x=XPos.RMARGIN, new_y=YPos.NEXT )
                                        #if content_page_nu == 2:
                                        pdf.image(self.customer_company_logo , x=165, y= 10, w=30, h=20)
                                        pdf.image(glob.glob(r"vorlage/Vahle_Logo.png")[0], x= 15, y=15, w= 50, h = 0, type='' )
                                        pdf.set_top_margin(35)
      
                                        Einsteug_page_nu=  content_page_nu + 7 + len(KESL_lift_warning_groups_refined_sorted) + len(KESL_deflection_warning_groups_refined_sorted)+ len(KESL_lift_failure_groups_refined_sorted) + len(KESL_deflection_failure_groups_refined_sorted)
                                        pdf.set_xy(190, title_padding_y_Einstieg)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu}", border = 0,align = Align.R, fill = False)
                                        pdf.ln()
                                        pdf.set_xy(190, title_padding_y_Mogliche)
                                        pdf.cell(w=10, h = 5, txt = f"{Einsteug_page_nu+1}", border = 0,align = Align.R, fill = False)
                          
                                      
                          pdf.set_page_background(glob.glob(r"vorlage/background_seite.jpg")[0])
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Current status of the system in '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(self.smart_collector_components_pic,x=25, y=125,w=160, h=130,type='' )
                          pdf.set_xy(65, 255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 10, txt = 'Figure 1: The components on the (Ofenklappe)', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 50)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = 'In ' + str(self.customer_company_name) + ''' the Smart Collector was installed on a landing gear. The system was submitted on the trailing unit and consists of the components: /n/n - Compact Current Collector   with 3D unit /n - Positioning system  /n - Main-Unit /n - Industrial router /n/n Following is the diagram of the system and components at '''+ str(self.customer_company_name)+ '.' ,
                                              border = 0,align = 'L', fill = False)
                          
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(self.smart_collector_with_3d_sensor_pic,x=25, y=45,w=160, h=110,type='' )
                          pdf.set_xy(70, 155)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 10, txt = 'Figure 2: Current Collector  '+ str(self.name_of_the_Stromabnehmer_series)+ ' with 3D-Sensor', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 170)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          
                          if not self.armes_order_extra_section_EN:  
                                  pdf.multi_cell(w =190, h = 7, txt = f'''The software of the Smart Collector allows the system to be completely scanned and the movement values of the Current Collector   to be assigned to the position values of the vehicle. It is also possible to store reference data and subsequently detect errors in the system by comparing the current values and the reference values. 
                                  /nOver the past few days, data of the plant was collected over several hours to first assess whether the current plant's condition of ''' + str(self.customer_company_name)+ f" is suitable for a reference run or Whether assembly or installation problems can already be identified in advance. The results are now presented on the following pages.",
                                                  border = 0,align = 'L', fill = False)
                          else: 
                                pdf.multi_cell(w =190, h = 7, txt = f'''The software of the Smart Collector allows the system to be completely scanned and the movement values of the Current Collector   to be assigned to the position values of the vehicle. It is also possible to store reference data and subsequently detect errors in the system by comparing the current values and the reference values. 
                                  /nOver the past few days, data of the plant was collected over several hours to first assess whether the current plant's condition of ''' + str(self.customer_company_name)+ f" is suitable for a reference run or Whether assembly or installation problems can already be identified in advance. The results are now presented on the following pages./n/n{self.armes_order_extra_section_EN}",
                                                  border = 0,align = 'L', fill = False)
                          
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =160, h = 10, txt = str('Results of the inspection trip '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(hub_general_view_path_EN,x=25, y=45,w=180, h=95,type='' )
                          pdf.image(auslenkung_general_view_path_EN, x = 25,y= 150, w = 190, h = 95, type='' )
                          pdf.set_xy(55, 137)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 5, txt = 'Figure 3: Data of the entire Lift plant route', border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(55, 242)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =160, h = 5, txt = 'Figure 4: Data of the entire Deflection plant route', border = 0,
                                    align = 'L', fill = False)
                          length_of_the_whole_route = np.max(Excel_reference_raw_data.index.values) - np.min(Excel_reference_raw_data.index.values)
                          pdf.set_xy(10, 250)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = '''As can be seen in the above illustration, the Lift path and the Deflection path of the entire plant section of ''' + str(length_of_the_whole_route) + ' cm ' + '''Length determined.'''                             
                                          ,border = 0,align = 'L', fill = False )
                          
                          
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_xy(10, 40)
                          pdf.multi_cell(w =190, h = 7, txt = '''The Current Collector  moves in the range of ''' + str(max_general_hub) + ' mm to '+ str(min_general_hub) + ' mm in Lift and in range of ' + str(max_general_auslenkung) + ' mm to ' + str(min_general_auslenkung) + ''' mm in Deflection and thus in its permissible range overall. The visible gaps in the display are due to the fact that the Current Collector  did not travel through all the routes/areas of the system during the recording time.
                                                                  /nThe installed system as well as the tested system have the following characteristics: /n/n- 4 Arms are monitored via the 3D Unit Motion Sensor. /n/n- As the vehicle travels along the track, the Lift and Deflection values of every                 centimeter of the track are recorded./n/n- The average contact pressure of the collectors varies from '''+ str(maximum_press_pressure) + ' N to ' + str(minimum_press_pressure) + f''' N./n  The average press preasure was measured at {average_press_preasure}'''                             
                                          ,border = 0,align = 'L', fill = False )
                          if not KESL_lift_warning_groups_refined_sorted.empty:
                              for idx, df_row in enumerate(KESL_lift_warning_groups_refined_sorted.values[0:1]):    
                                  pdf.add_page()
                                  pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                  pdf.set_font('helvetica','', 16)
                                  pdf.set_xy(10, 35)
                                  pdf.set_text_color(0,0,255)
                                  pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                                  pdf.set_xy(10, 45)
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_text_color(0,0,0)        
                                  pdf.multi_cell(w =190, h = 7, txt = f'The warning values exceeded  (± 20 mm) {len(KESL_lift_warning_groups_refined_sorted)} in the Lift field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                      border = 0,align = 'L', fill = False)
                                  y = pdf.get_y()
                                  pdf.set_xy(10, y)        
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_xy(10, 60)
                                  pdf.set_text_color(0,0,0)
                                  file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                  file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                  pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                  pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_lift_warning_groups_refined_sorted) > 1:        
                                  for idx, df_row in enumerate(KESL_lift_warning_groups_refined_sorted.values[1:]):
                                      pdf.add_page()
                                      pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                      pdf.set_font('helvetica','', 14)
                                      pdf.set_xy(10, 35)
                                      pdf.set_text_color(0,0,0)
                                      pdf.multi_cell(w = 190, h = 7, txt=f'Warning values in Lift field between positions: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                      file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                      file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                      pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                      pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if not KESL_deflection_warning_groups_refined_sorted.empty:
                                      for idx, df_row in enumerate(KESL_deflection_warning_groups_refined_sorted.values[0:1]):    
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)           
                                          pdf.multi_cell(w =190, h = 7, txt = f'The warning values exceeded  (± 20 mm) {len(KESL_deflection_warning_groups_refined_sorted)} in the Deflection field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                          border = 0,align = 'L', fill = False)                
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 60)
                                          pdf.set_text_color(0,0,0)
                                          file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                          pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                          pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_deflection_warning_groups_refined_sorted) > 1:        
                                      for idx, df_row in enumerate(KESL_deflection_warning_groups_refined_sorted.values[1:]):
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,0)
                                          pdf.multi_cell(w = 190, h = 7, txt=f'Warning values in Deflection field between positions: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                          file_name1 = os.path.abspath(working_directory+'/Warning_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Warning_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if not KESL_lift_failure_groups_refined_sorted.empty:
                              for idx, df_row in enumerate(KESL_lift_failure_groups_refined_sorted.values[0:1]):    
                                  pdf.add_page()
                                  pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                  pdf.set_font('helvetica','', 16)
                                  pdf.set_xy(10, 35)
                                  pdf.set_text_color(0,0,255)
                                  pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                    align = 'L', fill = False)
                                  pdf.set_xy(10, 45)
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_text_color(0,0,0)        
                                  pdf.multi_cell(w =190, h = 7, txt = f'The failure values exceeded (± 30 mm) {len(KESL_lift_failure_groups_refined_sorted)} times in the Lift field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                      border = 0,align = 'L', fill = False)
                                  y = pdf.get_y()
                                  pdf.set_xy(10, y)        
                                  pdf.set_font('helvetica','', 14)
                                  pdf.set_xy(10, 60)
                                  pdf.set_text_color(0,0,0)
                                  file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                  file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                  pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                  pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_lift_failure_groups_refined_sorted) > 1:        
                                  for idx, df_row in enumerate(KESL_lift_failure_groups_refined_sorted.values[1:]):
                                      pdf.add_page()
                                      pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20) 
                                      pdf.set_font('helvetica','', 14)
                                      pdf.set_xy(10, 35)
                                      pdf.set_text_color(0,0,0)
                                      pdf.multi_cell(w = 190, h = 7, txt=f'Failure values in Lift field between positions: {df_row[0]} und {df_row[1]}', align=Align.L, border = 0, fill = False) 
                                      file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                      file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')            
                                      pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                      pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if not KESL_deflection_failure_groups_refined_sorted.empty:
                                      for idx, df_row in enumerate(KESL_deflection_failure_groups_refined_sorted.values[0:1]):    
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)           
                                          pdf.multi_cell(w =190, h = 7, txt = f'Failure values exceeded (± 30 mm) {len(KESL_deflection_failure_groups_refined_sorted)} times in the Deflection field between positions: {df_row[0]} and {df_row[1]}/n' ,
                                                          border = 0,align = 'L', fill = False)                
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 60)
                                          pdf.set_text_color(0,0,0)
                                          file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')                
                                          pdf.image(file_name1, x = 0, y = 65, w = 200, h = 100, type = '')
                                          pdf.image(file_name2, x = 0, y = 175, w = 200, h = 100, type = '')
                          if  len(KESL_deflection_failure_groups_refined_sorted) > 1:        
                                      for idx, df_row in enumerate(KESL_deflection_failure_groups_refined_sorted.values[1:]):
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,0)
                                          pdf.multi_cell(w = 190, h = 7, txt=f'Failure values in Deflection field between positions: {df_row[0]} und {df_row[1]}', align= Align.L ,border = 0, fill = False) 
                                          file_name1 = os.path.abspath(working_directory+'/Failure_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Failure_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')         
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Lift and Deflection fields exceeded (± 20 mm) and no failure values in Lift and Deflection fields exceeded (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection field exceeded (± 30 mm) and no warning values in Lift and Deflection fields exceeded (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty  and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift field exceeded   (± 30 mm) and no warning values in Lift and Deflection fields exceeded  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty  and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty : 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift and Deflection fields exceeded   (± 30 mm) and no failure values in Deflection field exceeded   (± 30 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift and Deflection fields exceeded   (± 30 mm) and no warning values in Lift field exceeded  (± 20 mm)' ,
                                                    border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values both in Lift and Deflection fields exceeded  (± 20 mm)',
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_failure_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty:
                                        pdf.add_page()
                                        pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                        pdf.set_font('helvetica','', 16)
                                        pdf.set_xy(10, 35)
                                        pdf.set_text_color(0,0,255)
                                        pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                          align = 'L', fill = False)
                                        pdf.set_xy(10, 45)
                                        pdf.set_font('helvetica','', 14)
                                        pdf.set_text_color(0,0,0)               
                                        pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in both Lift and Deflection fields exceeded   (± 30 mm)',
                                                      border = 0,align = 'L', fill = False)
                          if KESL_lift_warning_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure or warning values in Lift field exceeded   (± 30 mm) or  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure or warning values in Deflection field exceeded (± 15 mm) or  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_lift_warning_groups_refined_sorted.empty and KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection exceeded (± 15 mm) or warning values in Lift field exceeded  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if KESL_deflection_warning_groups_refined_sorted.empty and KESL_lift_failure_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift exceeded (± 15 mm) or warning values in Deflection field exceeded  (± 20 mm)' ,
                                                          border = 0,align = 'L', fill = False)
                          if  KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)               
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Lift field exceeded  (± 20 mm)' ,
                                                      border = 0,align = 'L', fill = False)         
                          if KESL_deflection_warning_groups_refined_sorted.empty and not  KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty: 
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Überschreiten des Absolutwerts '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)                
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no warning values in Deflection field exceeded  (± 20 mm)' ,
                                                      border = 0,align = 'L', fill = False)                
                          if KESL_lift_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_deflection_failure_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)               
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Lift field exceeded (± 15 mm)' ,
                                                      border = 0,align = 'L', fill = False)         
                          if KESL_deflection_failure_groups_refined_sorted.empty and not KESL_lift_warning_groups_refined_sorted.empty and not KESL_deflection_warning_groups_refined_sorted.empty and not KESL_lift_failure_groups_refined_sorted.empty:
                                          pdf.add_page()
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 35)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =160, h = 10, txt = str('Exceeding absolute values '+ str(self.customer_company_name)) , border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_xy(10, 45)
                                          pdf.set_font('helvetica','', 14)
                                          pdf.set_text_color(0,0,0)               
                                          pdf.multi_cell(w =190, h = 7, txt = f'There are no failure values in Deflection field exceeded (± 15 mm)' ,
                                                      border = 0,align = 'L', fill = False)         
                          if not refined_anomalies_values.empty:
                            
                                  for idx, df_row in enumerate(refined_anomalies_values.values):
              
                                          pdf.add_page()
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =190, h = 7, txt = str('possible anomalies between positions: ' + str(df_row[0]) +" and " + str(df_row[1])), border = 0,
                                            align = 'L', fill = False)
                                          pdf.set_text_color(0,0,0)
                                          pdf.set_xy(30, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(40, 52)
                                          pdf.cell(w=10,h=5, txt='I.O', border = 0, align = 'L', fill = False)
                                          pdf.set_xy(75, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(85, 52)
                                          pdf.cell(w=10,h=5, txt='N.I.O', border = 0,align = 'L', fill = False)
                                          pdf.set_xy(120, 52)
                                          pdf.cell(w=10,h=5, txt='', border = 1,align = 'L', fill = False)
                                          pdf.set_xy(130, 52)
                                          pdf.cell(w=10,h=5, txt='Ist.Korr', border = 0,align = 'L', fill = False)
                                          file_name1 = os.path.abspath(working_directory+'/Anomalie_Hub_EN_'+str(df_row[0]) +'_' + str(df_row[1])+'.jpeg')
                                          file_name2 = os.path.abspath(working_directory+'/Anomalie_Auslenkung_EN_'+ str(df_row[0]) +'_'+ str(df_row[1])+'.jpeg')
                                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                                          pdf.image(file_name1, x = 0, y = 60, w = 200, h = 105, type = '')
                                          pdf.image(file_name2, x = 0, y = 170, w = 200, h = 105, type = '')
                          else: 
                                          pdf.add_page()
                                          pdf.set_font('helvetica','', 16)
                                          pdf.set_xy(10, 40)
                                          pdf.set_text_color(0,0,255)
                                          pdf.multi_cell(w =190, h = 7, txt = str('There are no anomalies in Lift and deflection fields'), border = 0,
                                            align = 'L', fill = False)
                                
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Entrance to Dashboard ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Einsteig_ins_Dashboard.jpg")[0], x=15, y= 45, w=180, h=100)
                          pdf.image(glob.glob(r"vorlage/Maintenance_Center.png")[0], x=15, y= 150, w=180, h=100)
                          pdf.set_xy(10, 260)
                          if not self.link_to_customer_company_dashboard:
                            pdf.cell( w=160, h=5, txt='' ,link='', border=0, align=Align.L)
                          else: 
                            pdf.cell( w=160, h=5, txt=self.link_to_customer_company_dashboard ,link='', border=0, align=Align.L)
                  
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.set_font('helvetica','', 16)
                          pdf.set_xy(10, 35)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Possible recognizable error cases ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.set_xy(10, 50)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_text_color(0,0,0)
                          pdf.multi_cell(w =190, h = 7, txt = 'The Smart Collector is able to detect a considerable number of possible faults on the Electric rail as well as on the Current Collector ./nThe defects mentioned below were simulated in the Vahle EHB test facility as part of a test and the results were analyzed and processed.' ,
                                              border = 0,align = 'L', fill = False)
                          pdf.set_font('helvetica','', 14)
                          pdf.set_xy(10, 80)
                          pdf.set_text_color(0,0,255)
                          pdf.multi_cell(w =190, h = 10, txt = str('Error in the plant ') , border = 0,
                                    align = 'L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_1.png")[0], x=25, y= 95, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(33, 167)
                          pdf.cell(w = 50, h=5, txt='Copper too short in separation point', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_2.png")[0], x=105, y= 95, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(110, 167)
                          pdf.cell(w = 50, h=5, txt='Fixed point not screwed on correctly', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_3.png")[0], x=25, y= 175, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(35, 247)
                          pdf.cell(w = 50, h=5, txt='Cable between rail and carrier', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_4.png")[0], x=105, y= 175, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(125, 247)
                          pdf.cell(w = 50, h=5, txt='bent up rail', border = 0, align='L', fill = False)

                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_5.png")[0], x=25, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(35, 112)
                          pdf.cell(w = 50, h=5, txt='Rail not clipped into holder', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_6.png")[0], x=105, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(120, 112)
                          pdf.cell(w = 55, h=5, txt='Rail compressed', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_7.png")[0], x=25, y= 120, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(42, 192)
                          pdf.cell(w = 50, h=5, txt='Separation point Offset', border = 0, align='L', fill = False)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_8.png")[0], x=105, y= 120, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(120, 192)
                          pdf.cell(w = 50, h=5, txt='Switch transition Offset', border = 0, align='L', fill = False)
                          pdf.add_page()
                          pdf.image(self.customer_company_logo, x=165, y= 15, w=30, h=20)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_9.png")[0], x=25, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.image(glob.glob(r"vorlage/Fehler_in_der_Anlage_10.png")[0], x=105, y= 40, w=70, h=70)
                          pdf.set_text_color(0,0,255)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(87, 115)
                          pdf.cell(w = 50, h=5, txt='A missing coal brush', border = 0, align='L', fill = False)
                          pdf.set_text_color(0,0,0)
                          pdf.set_font('helvetica','', 10)
                          pdf.set_xy(10, 125)
                          pdf.cell(w = 190, h=5, txt='In addition, the Smart Collector can detect anomalies such as vibrations and mechanical abnormalities.', border = 0, align='L', fill = False)
                          pdf.output(r"./images/Final_Report_English.pdf")
                          input_file = r'./images/Final_Report_English.pdf'
                          output_file = self.save_directory +r'/Final_Report_English.pdf'
                          from reportlab.pdfgen import canvas
              
                          # Get pages
                          reader = PdfReader(input_file)
                          pages = [pagexobj(p) for p in reader.pages]
                          # Compose new pdf
                          canvas = canvas.Canvas(output_file)
                          for page_num, page in enumerate(pages, start=1):
                              # Add page
                              canvas.setPageSize((page.BBox[2], page.BBox[3]))
                              canvas.doForm(makerl(canvas, page))
                              # Draw footer
                              footer_text = "Page %s of %s" % (page_num, len(pages))
                              x = 580
                              canvas.saveState()
                              canvas.setStrokeColorRGB(0, 0, 0)
                              canvas.setLineWidth(0.5)
                              
                              canvas.setFont('Helvetica-Bold', 10)
                              canvas.drawString(page.BBox[2]-x, 30, footer_text)
                              canvas.restoreState()
                              canvas.showPage()
                          canvas.save() 
    def load(self):    
                root = Toplevel()
                image = PhotoImage(file= r'vorlage/Vahle_Logo_gui.png')
                root.title("VTC - Smart Collector")
                root.minsize(530, 430)
               
                root.config(background='#000080')
                bg_label = Label(root,  bg = "#000080", image=image)
                bg_label.place(x= 30, y=45)
                root.resizable(False,False)
                root.update()
                progress_label = Label(root,  text="Loading... ", font=("Trebuchet Ms", 15, "bold"), fg="#FFFFFF", bg = "#000080")
                progress_label.place(x=210, y=330)
                root.update()
                root.resizable(False,False)
                root.update()
                bg_label = Label(root,  bg = "#000080", image=image)
                root.update()
                root.resizable(False,False)
                root.update()
                time.sleep(3)
                root.resizable(False,False)
                root.update()
                root.quit()
                        
    def done(self): 
                root = Toplevel()
                image = PhotoImage(file= r'vorlage/Vahle_Logo_gui.png')
                root.title("VTC - Smart Collector")
                root.minsize(530, 430)
              
                root.config(background='#000080')
                bg_label = Label(root,  bg = "#000080", image=image)
                bg_label.place(x= 30, y=65)          
                progress_label = Label(root,  text=" ", font=("Trebuchet Ms", 15, "bold"), fg="#FFFFFF", bg = "#000080")
                progress_label.place(x=210, y=330)
                root.update()
                txt = 'Done'          
                progress_label.config(text=txt)
                root.update()
                time.sleep(5)
                root.resizable(False,False)
                root.quit()


if __name__ == '__main__':
        
    rauto = Rauto()
    rauto.widget()
    rauto.load()
    rauto.generate()   
    rauto.done()   




