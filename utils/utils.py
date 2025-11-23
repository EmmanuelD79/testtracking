def format_ref(ref):
    if isinstance(ref, int) or (isinstance(ref, str) and ref.isdigit()):
        return f"0{ref}"
    return ref
    