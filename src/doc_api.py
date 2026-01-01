from pathlib import Path
import json
from pdf_reader import PDFhandler

class API:
    def __init__(self, dict_path, searchterm):
        self.dictpath = dict_path
        self.searchterm = searchterm
        self.paths_to_files = []
        self.key_collector = []
        self.data = {}
        self.load_active_data()

    def lastpartextract(self):
        path = Path(self.dictpath)
        self.last_part = path.name
        return self.last_part

    def file_loader(self, dir_name):
        project_root = Path(__file__).resolve().parent.parent
        dirs = project_root / "dirs"
        js_path = dirs / f"{dir_name}.json"

        try:
            with open(js_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
                return self.data.get("data", {})
        except FileNotFoundError:
            return {}

    # checks if a key is anywhere to be found in self.data
    def key_exists_anywhere(self, data, key):
            if isinstance(data, dict):
                if key in data:
                    return True
                return any(
                    self.key_exists_anywhere(v, key)
                    for v in data.values()
                )
            return False

    # get the values if key is in dict (self.key_exists_anywhere checkes first)
    # and return a list with the values -> in the list is a dict!
    def get_values_from_key(self, data, key, results=None):
        if results is None:
                results = [] # create empty list in function
        if isinstance(data, dict): # check data is dict
            if key in data: # check if key is present directly in given dict (first layer)
                results.append(data[key])
            for v in data.values(): # check if key is present in deeper layers of the nested dict
                self.get_values_from_key(v, key, results) # recursivly call function, v is the new dict to search
                                                        # key is now searched in the new dict and function is called recursivly
                                                        # until the key is found (it will be found since the key comes from the dict)

        return results

    def load_active_data(self):
        """
        Loads the data from the json file corresponding to the active path
        set in the PathManager.
        """
        active_dir_name = 'default' # Default value

        # Get the active directory name
        try:
            active_path_file = Path(__file__).resolve().parent / "active_path.json"
            with open(active_path_file, "r", encoding="utf-8") as f:
                active_path_data = json.load(f)
                active_dir_name = active_path_data.get("active", 'default')
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        self.data = self.file_loader(active_dir_name)
        return self.data

    def key_finder(self):
        last = self.lastpartextract()
        if last.endswith(".pdf"): # append full path to key_collector if self.lastpartextract is pdf
            self.key_collector.append(str(self.dictpath))
        elif self.key_exists_anywhere(self.data, last): # check if key is present in dict (it is, since the key comes from the dict
            # but the if-statement toggles the extraction of the values of the given key ('last'))
                values = self.get_values_from_key(self.data, last) # call the function to extract values from the given key, function returns a list
                for dict in values: # extract the dict from the returned list
                    for key, value in dict.items(): # keys of the returned dict are the values we need
                        self.key_collector.append(str(self.dictpath)+f'/{key}') # append the given dictpath and combine it with the given key for full path to data

        else:
            pass

        for entry in self.key_collector:
            foundterm = PDFhandler(entry, self.searchterm)
            print(foundterm.searchterm_finder())
