from __future__ import annotations

from dataclasses import dataclass,field
from typing import List,Any,Optional,Dict

import copy


@dataclass
class UDT:
    _name:str=""
    _udt_struct: List['TiaElement']|List[UDT] = field(default_factory=list)
    
    @classmethod
    def from_pyparser(cls,parser,udts):        

        return cls(
            _name = parser["udt_name"],
            _udt_struct = [TiaElement.from_pyparser(s,udts) for s in parser["udt"]]

        )
    
@dataclass
class TiaElement:

    _name: str 
    _type: str 

    _is_std:bool
    _is_udt:bool
    _is_struct:bool
    _is_array:bool
    _is_in_array:Optional[bool] = None
    _array_max:Optional[int]=None

    _array_length: Optional[int] = None
    _hangingObject: Optional[List["TiaElement"]] = None
    _offset: Optional[tuple[int,int]] = None
    _result: Optional[Any]= None
    _array_nr: Optional[int]= None
    
    def debug_to_dict(self):
        return {
            "_name": self._name,
            "_type": self._type,
            
            "_isStandard": self._is_std,
            "_isUDt": self._is_udt,
            "_isStruct": self._is_struct,
            "_isArray": self._is_array,
            
            "_array_length": self._array_length,
            "_hangingObject": None if self._hangingObject is None else [s.debug_to_dict() for s in self._hangingObject],
            "_offset":self._offset,
        }
    
    @classmethod
    def from_pyparser(cls, parsed,udts:Dict[UDT]):
        
        name = parsed["name"]
        type_ = parsed["type"]
        
        is_std=type_ in standard_types_
        is_udt=type_ in udts
        is_struct = type_ == "Struct" 
        is_array="array_length" in parsed
        allowed = []
        
        if is_array:
            start,stop = int(parsed["array_length"]["start_array"]),int(parsed["array_length"]["end_array"])+1
            array_length = abs(start-stop)
            array_max = array_length
            hangingObject = []

        if is_std :
            if is_array:
                for i in range(start,stop):
                    instance = cls(_name=name+f" [{i}]",_array_nr=i,_type=type_,_is_std=True, _is_udt=False, _is_struct=False, _is_array=False,_is_in_array=True, _array_max=array_max)
                    hangingObject.append(instance)
            else:
                hangingObject= None
                array_length= None
                
        elif is_udt:
            udt:UDT = udts.get(type_)
            if is_array:
                elememnt_to_add=TiaElement.from_udt(udt,name) 
                
                for i in range(start,stop):
                    element_copy = copy.deepcopy(elememnt_to_add)
                    element_copy._name +=f" [{i}]"
                    element_copy._array_nr=i
                    
                    hangingObject.append(element_copy)
                    
            else:
                hangingObject = udt._udt_struct
                array_length= None

        elif is_struct:
            hangingObject = [cls.from_pyparser(child,udts) for child in parsed["element"]]
            array_length= None 

        instance = cls(_name=name,_type=type_,_array_length=array_length,_hangingObject=hangingObject,_is_std=is_std,_is_udt=is_udt,_is_array=is_array,_is_struct=is_struct)
        
        return instance
    
    @classmethod
    def from_udt(cls,udt:UDT,name:str):
        instance = cls(
            
            _name=name, 
            _type=udt._name, 

            _is_std=False,
            _is_udt=True,
            _is_struct=False,
            _is_array=False,

            _hangingObject=udt._udt_struct
            )
        
        return instance

    def set_offset(self, _offset):
        def add_padding(x_) :
             
            x = (x_[0] + 1, 0)        
            return x
        
        offset_from = _offset
        
        
        if self._is_struct and offset_from[0]%2 > 0:
            offset_from = add_padding(offset_from)
        
        if self._hangingObject :
            for elem in self._hangingObject:
                offset_from = elem.set_offset(offset_from)
           
            return offset_from
        else:
            if type_size_[self._type][0] >1 and offset_from[0]%2 > 0 :
                offset_from = add_padding(offset_from)
                
            self._offset = offset_from
            size = type_size_[self._type]
            next_offset = tuple(x + y for x, y in zip(offset_from, size))
   
            if self._type == "Bool" and offset_from[1] + size[1] > 7:
                byte_ = offset_from[0]+1
                next_offset = (byte_, 0)
                return next_offset
            
            return next_offset

class db:
    def __init__(self,db_parsed,db_nr):

        udt_list = {}
        self._offset : tuple[int,int] 
        for udt in db_parsed["udt_field"]: udt_list[udt["udt_name"]] = UDT.from_pyparser(udt,udt_list)
        
        pars_struct = db_parsed["struct_field"]
        elements = [TiaElement.from_pyparser(element,udt_list) for element in pars_struct]
        
        self._udts: List[TiaElement]=udt_list
        self._body: List[TiaElement]=elements
        self.number:int=db_nr
  
        self.set_offset()
    
    def set_offset(self):
        self._offset = (0,0)
        for _element in self._body : 
            self._offset =  _element.set_offset(self._offset)
        self._offset= self._offset[0] +1
    

standard_types_ :dict= {
    "Bool", 
    "Int", 
    "DInt", 
    "Real", 
    "Char", 
    "String", 
    "Byte", 
    "Word", 
    "Time",
    }

type_size_:dict = {
    "Bool": (0,1),  
    "Byte": (1,0), 
    "Char": (1,0),
    "Word": (2,0), 
    "Int": (2,0),
    "DInt": (4,0), 
    "Real": (4,0),
    "String": (256,0),
    "Struct" : (2,0)  
    }

numerical_type:list = ["int","dint","real","byte","word"]
    
string_type:list = ["char","string","time","bool"]
