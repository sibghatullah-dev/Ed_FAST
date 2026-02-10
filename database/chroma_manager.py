"""
ChromaDB manager module for EdFast application.
Handles ChromaDB initialization and management.
"""

import os
import time
import shutil
import streamlit as st
import chromadb
import psutil
from config.constants import CHROMADB_PATH, COLLECTION_NAME, CHROMADB_TIMEOUT


def is_chromadb_running():
    """Check if ChromaDB is already running."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'python' in proc.info['name'].lower():
                    for file in proc.open_files():
                        if 'chromadb' in file.path.lower():
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    except ImportError:
        st.warning("psutil not installed. Cannot check for running ChromaDB processes.")
        return False


def load_chroma_with_timeout(timeout=CHROMADB_TIMEOUT):
    """Load ChromaDB with timeout and error handling."""
    try:
        chromadb_path = os.path.join(os.getcwd(), CHROMADB_PATH)
        st.info(f"Connecting to database at: {chromadb_path}")
        
        # Ensure the directory exists and is empty
        if os.path.exists(chromadb_path):
            try:
                shutil.rmtree(chromadb_path)
                st.info("Removed existing ChromaDB directory")
            except Exception as e:
                st.error(f"Error removing existing ChromaDB directory: {str(e)}")
                return None
        
        # Create fresh directory
        try:
            os.makedirs(chromadb_path, exist_ok=True)
            st.info("Created new ChromaDB directory")
        except Exception as e:
            st.error(f"Error creating ChromaDB directory: {str(e)}")
            return None
        
        # Initialize client with settings
        try:
            client = chromadb.PersistentClient(
                path=chromadb_path,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            st.info("ChromaDB client created successfully")
        except Exception as e:
            st.error(f"Error creating ChromaDB client: {str(e)}")
            return None
        
        # Create collection with timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to create a new collection
                collection = client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                st.success("Successfully created new collection")
                return collection
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    try:
                        collection = client.get_collection(name=COLLECTION_NAME)
                        st.success("Successfully connected to existing collection")
                        return collection
                    except Exception as get_error:
                        st.error(f"Error getting existing collection: {str(get_error)}")
                        return None
                elif time.time() - start_time > timeout:
                    st.error(f"Timed out while creating collection: {error_msg}")
                    return None
                time.sleep(0.5)
                
    except Exception as e:
        st.error(f"Error loading ChromaDB: {str(e)}")
        st.info("Please ensure you have write permissions in the directory.")
        return None


def initialize_chromadb():
    """Initialize ChromaDB for the application."""
    try:
        # Create chromadb directory if it doesn't exist
        if not os.path.exists(CHROMADB_PATH):
            os.makedirs(CHROMADB_PATH)
        return True
    except Exception as e:
        st.error(f"Error initializing ChromaDB: {str(e)}")
        return False 