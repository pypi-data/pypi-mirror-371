#from abc import ABC#, abstractmethod
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

class FileLoader:

    #Contructor to pass a File path
    def __init__(self, file_path, chunk_size, chunk_overlap):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    #Create a method that will call the correct loader
    def call_file_loader(self):
        print(f"working directory: {os.getcwd()} - file_path: {self.file_path} ")
        print(f"Calling file loader for: {self.file_path}")
        return self.load_file()
    
    #Split Documents into chunks
    def split_data(self, loaded_documents, collection_name):           
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = self.chunk_size,
                chunk_overlap = self.chunk_overlap,
                length_function = len,
                is_separator_regex=False
            )
            chunks = text_splitter.split_documents(loaded_documents)

            file_name = os.path.basename(self.file_path)  # Extract file name from path
            print(f"File name for metadata: {file_name}")

            for chunk in chunks:
                custom_metadata= {
                    'file_name': os.path.basename(self.file_path),
                    'collection_name': collection_name
                }
                chunk.metadata.update(custom_metadata)

            print("Chunking done")    

            return chunks
    
    #Create a method to embed the chunks
    def embed_chunks(self, chunks):
        embeddings = OpenAIEmbeddings()
        embedded_chunks = embeddings.embed_documents([doc.page_content for doc in chunks])
        print(f"Number of embedded chunks = {len(embedded_chunks)}")
        # print(f"First chunk: {chunks[0].page_content if chunks else 'No chunks to embed'}")
        print(f"First embedded chunk: {embedded_chunks[0] if embedded_chunks else 'No chunks to embed'}")

        return embedded_chunks
    
    # Mutator methods for file_path, chunk_size, and chunk_overlap
    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_chunk_size(self, chunk_size):
        self.chunk_size = chunk_size

    def set_chunk_overlap(self, chunk_overlap):
        self.chunk_overlap = chunk_overlap