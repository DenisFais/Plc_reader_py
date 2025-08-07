import dearpygui.dearpygui as dpg
from file_links import files
import data_type as dt
import gui_data_type as gt
import gui_lib as gl
from db_parser import map_struct
from typing import List,Dict,Any,Optional
from pnio_dcp import*
import snap7 
import time



class GUI():
    def __init__(self):
        
        self.test=0

        self.db_list = self.get_dbs()

        self.ip_valid = False
        self.db_valid = False

        self._data = bytearray(0)
        
        self.ip_picked = None
        self.found_devices  = {}
        self.element_in_scene : Dict[dt.TiaElement]= {}
     
        self.obj_instance()

    def obj_instance(self):

        dpg.create_context()   
        gl.setup_modern_theme()
        gl.setup_editor_theme()
        with dpg.font_registry():
            default_font = dpg.add_font("Roboto-Regular.ttf", 16)
            
        with dpg.window(tag="PLC_GUI", width=1000, height=800):
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=5)
                dpg.add_combo(tag="ip_combo", label="IP", width=200,items=[], callback=self.ip_selected_callback)
                labels = list(self.db_list.keys())               
                dpg.add_combo(tag="db_combo", label="DB", width=200, items=labels,callback=self.db_selected_callback)
                dpg.add_input_text(tag="db_num",label="DB NR",width=90,callback=self.change_db_nr)
                dpg.add_button(tag="add_db", label="+",callback=lambda : self.add_db(),width=25,height=25)
                dpg.add_spacer(width=100)
                dpg.add_loading_indicator(tag="loader", radius=1.5, thickness=2.0, color=(200, 200, 255), secondary_color=(100, 100, 255))
                dpg.add_button(label="Scan Network", callback=lambda : self.scan_ips_callback(),height=25,width=100)
                dpg.add_button(tag="btn_connect", label="Get Data", callback=lambda :self.connect_callback(),height=25,width=100)
                dpg.add_button(tag="btn_upload", label="Set Data", callback=lambda :self.upload_data_callback(),height=25,width=100)
                dpg.hide_item("loader")
                dpg.hide_item("btn_connect")
                dpg.hide_item("btn_upload")
                
            dpg.add_spacer(height=10)

        dpg.bind_font(default_font)
        dpg.create_viewport(title='Plc-reader',width=1000, height=800,x_pos=0,y_pos=0)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("PLC_GUI",True)
        dpg.start_dearpygui()
        dpg.destroy_context()
      
    def change_data(self,element:gt.GUI_STD):
        self._data = gl.set_element(element,self._data)

    def change_db_nr(self,paret,appdata):
        self._db.number = appdata

    def scan_ips_callback(self):
        dpg.show_item("loader")
        ip = "10.94.248.221"
        self.dcp = pnio_dcp.DCP(ip)
        obj_list:List[Device] =self.dcp.identify_all()
        found_devices = {}
        for i in obj_list:
            if "S7" in i.family and "eth" in i.name_of_station : 
                name,x = i.name_of_station.split(".",1)
                found_devices[name] =i.IP,i.name_of_station
        
        keys = list(found_devices.keys())
        keys.sort()
        dpg.configure_item("ip_combo",items=keys)

        self.found_devices = found_devices
        dpg.hide_item("loader")

    def ip_selected_callback(self,sender, app_data, user_data):
        self.ip_picked = self.found_devices[app_data][0]
        dpg.show_item("btn_connect")
        dpg.show_item("btn_upload")

    def db_selected_callback(self,sender, app_data, user_data):
        dpg.show_item("loader")
        label = app_data
        info = self.db_list.get(label)
       
        db_parsed = map_struct.parseString(files.get_db_file(info["full_name"]))
        self._db = dt.db(db_parsed,info["number"])
        dpg.set_value("db_num",self._db.number)
        self.instantiate_db(self._db)

    def link(self):
        pass
    def delink(self):
        pass
 
    def instantiate_db(self,db_:dt.db)-> dict:    
        
        x_base, y_base = 50, 50
        padding = 10
        x,y = x_base,y_base
        w,h =0,0
        
        with dpg.node_editor(callback=self.link, delink_callback=self.delink, tag="editor",parent="PLC_GUI"):
            for _element in db_._body:
                element = gl.return_obj_by_type(_element,"editor",[x,y],True,self.change_data)
                time.sleep(0.01)
                while w == 0 and h == 0:
                    w,h =dpg.get_item_rect_size(element._self_node)
                y+= h+padding
                self.element_in_scene[_element._name]=element
                w,h =0,0

        dpg.hide_item("loader")

    def get_dbs(self)->dict:
        return files.get_db_list()
    
    def connect_callback(self):
        dpg.show_item("loader")
        
        self.client = snap7.client.Client()
        self.client.connect(str(self.ip_picked),0,0)
        if self.client.get_connected():
            pass
        else:
            return print("Error connecting to client")
        
        data = self.client.db_read(int(self._db.number),0,int(self._db._offset))        
        
        self._data = data
        if self.element_in_scene :
            for element in self.element_in_scene:
                
                gl.update_data(data,self.element_in_scene[element])
        else:
            print("ERRORE")
        dpg.hide_item("loader")

    def upload_data_callback(self):
        dpg.show_item("loader")
        
        self.client = snap7.client.Client()
        self.client.connect(str(self.ip_picked),0,0)
        if self.client.get_connected():
            pass
        else:
            return print("Error connecting to client")
         
        self.client.db_write(int(self._db.number),0,self._data)

        dpg.hide_item("loader")

        
if __name__ == "__main__":
  
    GUI()

