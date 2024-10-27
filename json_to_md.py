def Convert(element, level=0, back_to_line='  \n', indentation=''):
    line = ''   # str to return

    # Case the element is a dictionnary
    if isinstance(element, dict):
        md = ''
        for key, value in element.items():      # For each of its elements
            if isinstance(value, (dict, list)): # If the value is iterable, we have a title
                md += f'{indentation * level}{'#' * (level+1)} {key}{back_to_line}{back_to_line}' # Define the title
                md += Convert(value, level+1, back_to_line, indentation)                          # Add recursively the next elements
            else:   # The the value is not iterable, the key is a keyword with a value
                md += f'{indentation * level} **{key}:** {value}{back_to_line}'
        return md + back_to_line

    # Case the element is a list
    elif isinstance(element, list):
        md = ''
        # Simply iterate it and concatenate the recursive results
        for e in element:
            md += Convert(e, level, back_to_line, indentation)
        return md + back_to_line

    # Case the element is not iterable, its a single element
    else:
        return f'{indentation * level}- {element}{back_to_line}'
