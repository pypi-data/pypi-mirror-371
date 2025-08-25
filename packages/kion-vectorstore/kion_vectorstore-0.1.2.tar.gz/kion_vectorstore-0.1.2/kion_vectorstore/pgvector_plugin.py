from langchain_community.vectorstores import PGVector
from sqlalchemy import create_engine, text
from kion_vectorstore.config import Config

class PGVectorPlugin:
    # Accept 'embedding_model' as a required argument
    def __init__(self, embedding_model):
        # Ensure the configuration is loaded before proceeding
        if not Config._is_loaded:
            raise RuntimeError(
                "Configuration has not been initialized. "
                "Please call kion_vectorstore.initialize_config() at the start of your application."
            )

        # Check param: embedding_model provided
        if embedding_model is None:
            raise ValueError("An embedding_model instance must be provided to PGVectorPlugin.")
        
        # Store params as the instance variables
        self.embedding_model = embedding_model
        self.connection_string = Config.CONNECTION_STRING
        print(f"Using connection string: {self.connection_string}")

        if not self.connection_string:
            raise ValueError(
                "Database CONNECTION_STRING could not be built. "
                "Please ensure all database settings are defined in your .env file."
            )

        self.engine = create_engine(self.connection_string)


    def list_collections(self):
        with self.engine.connect() as conn:
            res = conn.execute(text("SELECT name FROM langchain_pg_collection ORDER BY name;"))
            return [row[0] for row in res.fetchall()]

    def add_documents(self, documents, collection_name):
        # documents: list of langchain Documents
        db = PGVector.from_documents(
            embedding=self.embedding_model,
            documents=documents,
            collection_name=collection_name,
            connection_string=self.connection_string
        )
        print(f"Added {len(documents)} documents to collection '{collection_name}'")

    def list_files(self, collection_name):
        with self.engine.connect() as conn:
            res = conn.execute(
                text("SELECT uuid FROM langchain_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                return []
            collection_uuid = res[0]
            files_res = conn.execute(
                text("""
                    SELECT DISTINCT cmetadata->>'file_name' AS file_name
                    FROM langchain_pg_embedding
                    WHERE collection_id = :uuid AND cmetadata->>'file_name' IS NOT NULL
                    ORDER BY file_name
                    """), {"uuid": str(collection_uuid)}
            )
            return [row[0] for row in files_res.fetchall()]

    def delete_file(self, collection_name, file_name):
        with self.engine.begin() as conn:
            res = conn.execute(
                text("SELECT uuid FROM langchain_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                raise ValueError(f"Collection '{collection_name}' not found.")
            collection_uuid = res[0]
            result = conn.execute(
                text("""
                    DELETE FROM langchain_pg_embedding
                    WHERE collection_id = :collection_uuid
                    AND cmetadata->>'file_name' = :file_name
                """),
                {"collection_uuid": str(collection_uuid), "file_name": file_name}
            )
            return result.rowcount

    def delete_collection(self, collection_name):
        with self.engine.begin() as conn:
            res = conn.execute(
                text("SELECT uuid FROM langchain_pg_collection WHERE name = :name"),
                {"name": collection_name}
            ).fetchone()
            if not res:
                raise ValueError(f"Collection '{collection_name}' not found.")
            collection_uuid = res[0]
            # Remove all embeddings first
            conn.execute(
                text("DELETE FROM langchain_pg_embedding WHERE collection_id = :uuid"),
                {"uuid": str(collection_uuid)}
            )
            # Remove the collection itself
            conn.execute(
                text("DELETE FROM langchain_pg_collection WHERE uuid = :uuid"),
                {"uuid": str(collection_uuid)}
            )
    
    def similarity_search_with_scores(self, collection_name, query, k=5):
        vector_store = PGVector(
            embedding_function=self.embedding_model,
            collection_name=collection_name,
            connection_string=self.connection_string
        )
        # Returns list of (Document, score)
        return vector_store.similarity_search_with_score(query, k=k)