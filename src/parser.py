def recursive_json_to_text(data, level=1) -> str:
    """
    Dynamically walks through ANY JSON structure and converts it into a flat,
    readable Markdown-like string for the LLM.
    """
    text = ""
    if isinstance(data, dict):
        for key, value in data.items():
            # Add headers for dictionary keys based on depth
            text += f"\n{'#' * level} {key}\n"
            text += recursive_json_to_text(value, level + 1)
    elif isinstance(data, list):
        for item in data:
            # Add bullet points for list items
            parsed_item = recursive_json_to_text(item, level).strip()
            if parsed_item:
                # If the item is a complex object, space it out. If it's a simple string, bullet it.
                if isinstance(item, dict):
                    text += f"\n{parsed_item}\n---"
                else:
                    text += f"- {parsed_item}\n"
    else:
        # Base case: it's a string, int, bool, etc.
        text += f"{data}\n"

    return text