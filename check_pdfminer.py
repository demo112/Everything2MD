
try:
    import pdfminer
    print(f"pdfminer imported: {pdfminer.__file__}")
    from pdfminer.high_level import extract_text
    print("pdfminer.high_level.extract_text imported")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
