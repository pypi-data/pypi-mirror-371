from langchain_community.document_loaders import TextLoader
from kion_vectorstore.file_loader import FileLoader


class KionTextFileLoader(FileLoader):    

    #Contructor to pass HTML file_path
    def __init__(self, file_path, chunk_size, chunk_overlap):
        super().__init__(file_path, chunk_size, chunk_overlap)

    #Load Text File
    def load_file(self):  
        loader = TextLoader(self.file_path, encoding = 'utf-8')
        documents = loader.load()
        
        #print(f"Number of Text Documents loaded = {len(documents)}")      
        
        return documents
   
    