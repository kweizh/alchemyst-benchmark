import os
import sys
import pytest

PROJECT_DIR = "/home/user/alchemyst_project"
sys.path.append(PROJECT_DIR)

def test_update_doc_exists():
    assert os.path.isfile(os.path.join(PROJECT_DIR, "update_doc.py")), "update_doc.py not found in project directory"

def test_update_document():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        pytest.skip("ALCHEMYST_AI_API_KEY environment variable is not set")
    
    try:
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=api_key)
    except ImportError as e:
        pytest.fail(f"Failed to import AlchemystAI: {e}")

    try:
        from update_doc import update_document
    except ImportError as e:
        pytest.fail(f"Failed to import update_document from update_doc.py: {e}")

    file_name = "test_update_doc_123.txt"
    initial_content = "Initial content before update."
    new_content = "Updated content after deletion."

    # Clean up before test
    try:
        client.v1.context.delete(metadata={"file_name": file_name})
    except Exception:
        pass

    # Add initial document
    try:
        client.v1.context.add(
            documents=[{
                "content": initial_content,
                "metadata": {"file_name": file_name}
            }],
            context_type="resource",
            source="docs",
            scope="internal"
        )
    except Exception as e:
        pytest.fail(f"Failed to add initial document: {e}")

    # Call the user's function
    try:
        update_document(client, file_name, new_content)
    except Exception as e:
        pytest.fail(f"update_document failed with error: {e}")

    # Verify the document was updated
    try:
        result = client.v1.context.search(
            query="Updated content",
            similarity_threshold=0.5,
            scope="internal"
        )
        contexts = result.contexts or []
        assert len(contexts) > 0, "No context found after update"
        
        found = any(new_content in ctx.content for ctx in contexts)
        assert found, "The new content was not found in the search results"
    except Exception as e:
        pytest.fail(f"Failed to search and verify updated document: {e}")
    finally:
        # Clean up after test
        try:
            client.v1.context.delete(metadata={"file_name": file_name})
        except Exception:
            pass
