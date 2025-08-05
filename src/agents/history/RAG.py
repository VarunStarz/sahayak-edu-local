from langchain_objectbox.vectorstores import ObjectBox
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders import (
    WebBaseLoader, 
    PyPDFLoader, 
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain
from typing import List, Union
import os
from pathlib import Path

class EnhancedRAG:
    def __init__(self, model: str = "gemma2:7b", embedding_dimensions: int = 768):
        """
        Initialize the RAG pipeline with specified model and embedding dimensions.
        
        Args:
            model: Ollama model name
            embedding_dimensions: Dimensions for embeddings (default: 768)
        """
        self.llm = Ollama(model=model)
        self.embeddings = OllamaEmbeddings(model=model)
        self.embedding_dimensions = embedding_dimensions
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.vector_store = None
        self.retrieval_chain = None
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context. 
        If you cannot find the answer in the context, please say "I don't have enough information to answer this question."

        <context>
        {context}
        </context>

        Question: {input}
        
        Answer:""")
    
    def load_pdf_documents(self, pdf_paths: Union[str, List[str]]) -> List[Document]:
        """Load PDF documents."""
        if isinstance(pdf_paths, str):
            pdf_paths = [pdf_paths]
        
        documents = []
        for pdf_path in pdf_paths:
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded PDF: {pdf_path} ({len(docs)} pages)")
            except Exception as e:
                print(f"Error loading PDF {pdf_path}: {e}")
        
        return documents
    
    def load_word_documents(self, word_paths: Union[str, List[str]]) -> List[Document]:
        """Load Word documents (.docx)."""
        if isinstance(word_paths, str):
            word_paths = [word_paths]
        
        documents = []
        for word_path in word_paths:
            try:
                loader = Docx2txtLoader(word_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded Word document: {word_path}")
            except Exception as e:
                print(f"Error loading Word document {word_path}: {e}")
        
        return documents
    
    def load_text_documents(self, text_paths: Union[str, List[str]]) -> List[Document]:
        """Load plain text documents."""
        if isinstance(text_paths, str):
            text_paths = [text_paths]
        
        documents = []
        for text_path in text_paths:
            try:
                loader = TextLoader(text_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded text file: {text_path}")
            except Exception as e:
                print(f"Error loading text file {text_path}: {e}")
        
        return documents
    
    def load_csv_documents(self, csv_paths: Union[str, List[str]]) -> List[Document]:
        """Load CSV documents."""
        if isinstance(csv_paths, str):
            csv_paths = [csv_paths]
        
        documents = []
        for csv_path in csv_paths:
            try:
                loader = CSVLoader(csv_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded CSV file: {csv_path}")
            except Exception as e:
                print(f"Error loading CSV file {csv_path}: {e}")
        
        return documents
    
    def load_powerpoint_documents(self, ppt_paths: Union[str, List[str]]) -> List[Document]:
        """Load PowerPoint documents (.pptx)."""
        if isinstance(ppt_paths, str):
            ppt_paths = [ppt_paths]
        
        documents = []
        for ppt_path in ppt_paths:
            try:
                loader = UnstructuredPowerPointLoader(ppt_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded PowerPoint: {ppt_path}")
            except Exception as e:
                print(f"Error loading PowerPoint {ppt_path}: {e}")
        
        return documents
    
    def load_excel_documents(self, excel_paths: Union[str, List[str]]) -> List[Document]:
        """Load Excel documents (.xlsx)."""
        if isinstance(excel_paths, str):
            excel_paths = [excel_paths]
        
        documents = []
        for excel_path in excel_paths:
            try:
                loader = UnstructuredExcelLoader(excel_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded Excel file: {excel_path}")
            except Exception as e:
                print(f"Error loading Excel file {excel_path}: {e}")
        
        return documents
    
    def load_web_documents(self, urls: Union[str, List[str]]) -> List[Document]:
        """Load documents from web URLs."""
        if isinstance(urls, str):
            urls = [urls]
        
        documents = []
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded web content: {url}")
            except Exception as e:
                print(f"Error loading web content {url}: {e}")
        
        return documents
    
    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported documents from a directory."""
        directory = Path(directory_path)
        documents = []
        
        if not directory.exists():
            print(f"Directory {directory_path} does not exist")
            return documents
        
        # Define file extensions and their corresponding loaders
        file_loaders = {
            '.pdf': self.load_pdf_documents,
            '.docx': self.load_word_documents,
            '.txt': self.load_text_documents,
            '.csv': self.load_csv_documents,
            '.pptx': self.load_powerpoint_documents,
            '.xlsx': self.load_excel_documents
        }
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in file_loaders:
                loader_func = file_loaders[file_path.suffix.lower()]
                docs = loader_func(str(file_path))
                documents.extend(docs)
        
        print(f"Loaded {len(documents)} documents from directory: {directory_path}")
        return documents
    
    def create_vector_store(self, documents: List[Document]):
        """Create vector store from documents."""
        if not documents:
            print("No documents provided for vector store creation")
            return
        
        # Split documents into chunks
        split_documents = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(split_documents)} chunks")
        
        # Create vector store
        self.vector_store = ObjectBox.from_documents(
            split_documents, 
            self.embeddings, 
            embedding_dimensions=self.embedding_dimensions
        )
        print("Vector store created successfully")
    
    def setup_retrieval_chain(self):
        """Setup the retrieval chain for Q&A."""
        if self.vector_store is None:
            print("Vector store not created. Please create vector store first.")
            return
        
        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve top 5 similar chunks
        )
        
        # Create retrieval chain
        self.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        print("Retrieval chain setup completed")
    
    def query(self, question: str) -> dict:
        """Query the RAG system."""
        if self.retrieval_chain is None:
            return {"error": "Retrieval chain not setup. Please setup the chain first."}
        
        try:
            response = self.retrieval_chain.invoke({"input": question})
            return response
        except Exception as e:
            return {"error": f"Error during query: {e}"}
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vector store."""
        if self.vector_store is None:
            print("Creating new vector store...")
            self.create_vector_store(documents)
        else:
            print("Adding documents to existing vector store...")
            split_documents = self.text_splitter.split_documents(documents)
            self.vector_store.add_documents(split_documents)
            print(f"Added {len(split_documents)} document chunks to vector store")

# Example usage
def main():
    # Initialize RAG system
    rag = EnhancedRAG(model="gemma2:7b")
    
    # Load documents from various sources
    documents = []
    
    # Load web content
    web_docs = rag.load_web_documents("https://docs.smith.langchain.com/user_guide")
    documents.extend(web_docs)
    
    # Load PDF files (uncomment if you have PDF files)
    # pdf_docs = rag.load_pdf_documents(["path/to/your/file.pdf"])
    # documents.extend(pdf_docs)
    
    # Load Word documents (uncomment if you have Word files)
    # word_docs = rag.load_word_documents(["path/to/your/file.docx"])
    # documents.extend(word_docs)
    
    # Load entire directory (uncomment if you want to load a directory)
    # dir_docs = rag.load_directory("path/to/your/documents")
    # documents.extend(dir_docs)
    
    # Create vector store
    rag.create_vector_store(documents)
    
    # Setup retrieval chain
    rag.setup_retrieval_chain()
    
    # Query the system
    questions = [
        "How can LangSmith help with testing?",
        "What are the main features of LangSmith?",
        "How do I get started with LangSmith?"
    ]
    
    for question in questions:
        print(f"\n**Question:** {question}")
        response = rag.query(question)
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"**Answer:** {response['answer']}")
            print(f"**Sources:** {len(response.get('context', []))} documents used")

if __name__ == "__main__":
    main()
