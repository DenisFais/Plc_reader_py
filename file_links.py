import json
import os
import re

class files():
    def __init__(self):
        with open("file_dir.json","r") as f:
            self.directories = json.load(f)
        self.base = self.directories["base_dir"]
    
    def get_db_file(self,name):
        path=os.path.join(self.base,self.directories["DBs_folder"],name)
        with open(path, encoding="utf-8-sig") as f:
            DB = f.read()
            return DB

    def get_db_list(self):
        path= os.path.join(self.base,self.directories["DBs_folder"])
        dbs = os.listdir(path)
        db_list={}
        for db in dbs:
            match = re.search(r'\[(\d+)\]', db)
            if match:
                nr = (match.group(1))
                name= re.sub(".db", "", db)
                name= re.sub(r'\[\d+\]', "", name)

                db_list[name] = {
                    "name":name,
                    "full_name":db,
                    "number":nr
                    }
        
        return db_list
    
files = files()