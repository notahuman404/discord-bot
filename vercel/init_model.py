import easyocr

print("Initializing EasyOCR reader (this downloads detection + recognition models)...")
reader = easyocr.Reader(['en'])
print("Model initialization complete.")
