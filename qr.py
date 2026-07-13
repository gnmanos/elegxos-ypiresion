import qrcode


url = "http://192.168.1.130:5000"


img = qrcode.make(url)

img.save("QR_EGGRAFI.png")


print("Το QR δημιουργήθηκε")