from __future__ import annotations

import gui_data_type as gt_
import data_type as dt
import dearpygui.dearpygui as dpg
from snap7.util import *
from snap7.type import date 
from typing import Union

def set_char(bytearray_: bytearray, byte_index: int, chr_: str) -> Union[ValueError, bytearray]:
    if chr_.isascii():
        bytearray_[byte_index] = ord(chr_)
        return bytearray_
    raise ValueError(f"chr_ : {chr_} contains a None-Ascii value, but ASCII-only is allowed.")


def return_obj_by_type(element:dt.TiaElement,editor:str,pos:list,is_vis:bool,main_callback=None):
    
    if element._is_std:
        return gt_.GUI_STD(element,editor,pos,is_vis,main_callback)
    if element._is_udt:
        return gt_.GUI_UDT(element,editor,pos,is_vis,main_callback)
    if element._is_struct:
        return gt_.GUI_STRUCT(element,editor,pos,is_vis,main_callback)

def update_data(new_data:bytearray,element:gt_.GUI_STD|gt_.GUI_UDT|gt_.GUI_STRUCT):
    def set_result(data,element:gt_.GUI_STD):
        if data is None:
            return print("ERRORE")
        match element._type.lower():
            case 'byte':
                result = get_byte(data,element._offset[0])
            case 'word':
                result = get_word(data,element._offset[0])
            case 'bool':
                result = get_bool(data ,element._offset[0], element._offset[1])
            case 'int':
                result = get_int(data ,element._offset[0])
            case 'dint':
                result = get_dint(data ,element._offset[0])
            case 'float':
                result = get_real(data, element._offset[0])
            case 'string':
                result = get_string(data ,element._offset[0])
            case 'char':
                result =  get_char(data ,element._offset[0] )
            case 'time':
                result = get_time(data,element._offset[0])
        return result
    if type(element) is gt_.GUI_STD:
        if element._is_array:
            result =""
            for s in element._hangingObject:
                result += str(set_result(new_data,s)) 
        else:
            result = str(set_result(new_data,element))
        
        dpg.set_value(element.node_result,str(result))
        element._result = result
    else:  
        for s in  element._hangingObject:
            update_data(new_data,s)

    
def set_element(element:gt_.GUI_STD,old_data):
   
    match element._type.lower():
        case "bool":data_result= set_bool(old_data,element._offset[0],element._offset[1],bool(element._result))
        case "byte":data_result= set_byte(old_data,element._offset[0],int(element._result))
        case "date":return print("NOT IMPLEMENTED YET") # set_date(old_data,element._offset[0],date(element._result))
        case "dint":data_result= set_dint(old_data,element._offset[0],int(element._result))
        case "dword":data_result= set_dword(old_data,element._offset[0],int(element._result))
        case "fstring":data_result= set_fstring(old_data,element._offset[0],element._result)
        case "int":data_result= set_int(old_data,element._offset[0],element._result)
        case "lreal":data_result= set_lreal(old_data,element._offset[0],float(element._result))
        case "real":data_result= set_real(old_data,element._offset[0],int(element._result))
        case "sint":data_result= set_sint(old_data,element._offset[0],int(element._result))
        case "string":data_result= set_string(old_data,element._offset[0],element._result)
        case "time":data_result= set_time(old_data,element._offset[0],element._result)
        case "udint":data_result= set_udint(old_data,element._offset[0],int(element._result))
        case "uint:":data_result= set_uint(old_data,element._offset[0],int(element._result))
        case "usint":data_result= set_usint(old_data,element._offset[0],int(element._result))
        case "word":data_result= set_word(old_data,element._offset[0],int(element._result))
        case 'char':data_result= set_char(old_data,element._offset[0], element._result)
        case _: return print("Error in datatype")
    return data_result

def setup_modern_theme():
    with dpg.theme(tag="modern_theme") as theme:
        with dpg.theme_component(dpg.mvAll):

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 45), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (65, 65, 65), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 120, 200), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 140, 230), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 160, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230), category=dpg.mvThemeCat_Core)
            
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)
    
    dpg.bind_theme(theme)

def setup_editor_theme():
    with dpg.theme(tag="node_theme") as theme:
        with dpg.theme_component(dpg.mvNodeEditor):
            dpg.add_theme_color(dpg.mvNodeCol_GridBackground, (25, 25, 25), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_GridLine, (50, 50, 50), category=dpg.mvThemeCat_Nodes)

        with dpg.theme_component(dpg.mvNode):
            dpg.add_theme_color(dpg.mvNodeCol_TitleBar, (60, 120, 200, 255), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_TitleBarHovered, (80, 140, 230, 255), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_TitleBarSelected, (100, 160, 255, 255), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, (40, 40, 40, 255), category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4, category=dpg.mvThemeCat_Nodes)
      
    return theme