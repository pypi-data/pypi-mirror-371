from langchain_community.document_loaders import PyPDFLoader
from kion_vectorstore.file_loader import FileLoader

class KionPDFFileLoader(FileLoader):

    # Constructor to pass PDF file_path
    def __init__(self, file_path, chunk_size, chunk_overlap):
        super().__init__(file_path, chunk_size, chunk_overlap)
        print(f"Initialized KionPDFFileLoader with file_path: {file_path}, chunk_size: {chunk_size}, chunk_overlap: {chunk_overlap}")

    # Load PDF File
    def load_file(self):
        loader = PyPDFLoader(self.file_path)
        documents = loader.load()
        
        print(f"Number of PDF Documents loaded = {len(documents)}")
        
        return documents