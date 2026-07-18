import easyocr
import time
print("import easy ocr")
reader = easyocr.Reader(['en'])
print("made the reader")
s = time.time()
result = reader.readtext("./pokemon_images/prediction.png", detail=0)
e = time.time()
print(f"Total time taken to read the text: {e-s}")
print(result)
