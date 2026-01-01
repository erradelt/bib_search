from PyPDF2 import PdfReader

class PDFhandler:
    def __init__(self, doc_path, searchterm):
        self.doc_path = doc_path
        self.searchterm = searchterm

    def read_doc(self):
        return(PdfReader(self.doc_path))

    def doc_dissector(self):
        self.page_dict = {}
        i=1
        for page in self.read_doc().pages:
            self.page_dict[f"seite {i}"]=page.extract_text()
            i += 1
        return self.page_dict

    def searchterm_finder(self):
        #key = page of document
        #value = text of corresponding page
        self.found_dict = {}
        for key, value in self.doc_dissector().items():
            found_word = value.find(self.searchterm)
            if found_word != - 1: # -1 means searchterm not found in value
                start = max(0, found_word-75)
                end = min(len(value), found_word+len(self.searchterm)+75)
                self.found_dict[key]=f'...{value[start:end]}...'.replace('\n','')
        return self.found_dict

found = PDFhandler("/home/robert/Downloads/polaris-family-br-DMC-109998-de-de-2410-1.pdf", "Leuchte")
print(found.searchterm_finder())
