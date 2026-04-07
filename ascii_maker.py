import sys
import shutil
from PIL import Image

# Daftar karakter ASCII dari yang paling gelap (@) ke paling terang (.)
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def get_terminal_width():
    """Mendeteksi lebar layar terminal secara otomatis"""
    # Ambil lebar kolom, default 80 kalau misal gagal deteksi
    columns, _ = shutil.get_terminal_size(fallback=(80, 24))
    return columns

def resize_image(image, new_width):
    """Ngecilin ukuran gambar sesuai lebar terminal"""
    width, height = image.size
    ratio = height / width
    # Dikali 0.55 biar gambarnya nggak melar ke bawah (menyesuaikan bentuk font terminal)
    new_height = int(new_width * ratio * 0.55)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    """Ubah gambar jadi hitam putih (grayscale)"""
    return image.convert("L")

def pixels_to_ascii(image):
    """Ubah setiap piksel jadi karakter ASCII"""
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def main():
    if len(sys.argv) < 2:
        print("\n[!] Cara pakai: python ascii_maker.py <path_ke_gambar>")
        return

    image_path = sys.argv[1]
    
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"\n[!] Gagal ngebuka gambar: {image_path}")
        return

    print("\n[*] Sedang memproses gambar...\n")
    
    # Deteksi lebar layar dan kurangi 2 karakter buat margin biar aman
    target_width = get_terminal_width() - 2 
    
    # Eksekusi prosesnya
    new_image_data = pixels_to_ascii(grayify(resize_image(image, target_width)))
    
    # Format baris baru sesuai target lebar layar yang udah dideteksi
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index + target_width)] for index in range(0, pixel_count, target_width)])
    
    # Print hasilnya!
    print(ascii_image)
    
    with open("hasil_ascii.txt", "w") as f:
        f.write(ascii_image)
    
    print("\n[+] Selesai! Gambar ASCII juga sudah disimpan di hasil_ascii.txt\n")

if __name__ == '__main__':
    main()
