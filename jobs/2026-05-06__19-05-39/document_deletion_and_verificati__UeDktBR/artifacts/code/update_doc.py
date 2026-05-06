def update_document(client, file_name, new_content):
    """
    Updates a document in Alchemyst AI by deleting the existing one with the same file_name
    and then adding the new content.
    """
    # Delete the existing document with the given file_name
    client.v1.context.delete(metadata={"file_name": file_name})

    # Add the new document with the new content and the same file_name
    client.v1.context.add(
        documents=[{"content": new_content, "metadata": {"file_name": file_name}}],
        context_type="resource",
        source="docs",
        scope="internal"
    )
