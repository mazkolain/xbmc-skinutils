'''
Created on 09/08/2011

@author: mikel
'''
import os
import xbmc
import xml.etree.ElementTree as ET
from skinutils import SkinUtilsError, check_skin_writability, case_file_exists, DocumentCache



class IncludeXmlError(SkinUtilsError):
    pass



class IncludeManager:
    __installed_names = None
    __doc_cache = None
    
    
    def _list_skin_include_files(self):
        include_list = []
        skin_path = xbmc.translatePath("special://skin/")
        
        #Go into each dir. Could be 720, 1080...
        for dir_item in os.listdir(skin_path):
            dir_path = os.path.join(skin_path, dir_item)
            if os.path.isdir(dir_path):
                file = os.path.join(dir_path, "includes.xml")
                if case_file_exists(file):
                    include_list.append(file)
                
                file = os.path.join(dir_path, "Includes.xml")
                if case_file_exists(file):
                    include_list.append(file)
        
        return include_list
    
    
    def __init__(self):
        check_skin_writability()
        self.__installed_names = []
        
        #Initialize the doc cache with found files
        self.__doc_cache = DocumentCache()
        for file in self._list_skin_include_files():
            self.__doc_cache.add(file)
    
    
    def is_name_installed(self, name):
        return name in self.__installed_names
    
    
    def add_include(self, name, node):
        for file in self.__doc_cache.list_files():
            doc = self.__doc_cache.read(file)
            doc.getroot().append(node)
            self.__installed_names.append(name)
    
    
    def install_file(self, file, commit=True, clear=True):
        print "install include: %s" % file
        tree = ET.parse(file)
        
        #Handle all includes
        for item in tree.getroot().findall("include"):
            name = item.get("name")
            if name is None:
                xbmc.log("Only named includes are supported.", xbmc.LOGWARNING)
            
            elif self.is_name_installed(name):
                xbmc.log("Include name '%s' already installed" % name)
            
            else:
                self.add_include(name, item)
        
        #If a save was requested
        if commit:
            self.__doc_cache.write_all()
            
            #If we where requested to clear the cached docs
            if clear:
                self.__doc_cache.clear_all()
    
    
    def remove_installed_names(self):
        self.__doc_cache.rollback_all()
    
    
    def cleanup(self):
        self.remove_installed_names()
    
    
    def __del__(self):
        self.cleanup()
