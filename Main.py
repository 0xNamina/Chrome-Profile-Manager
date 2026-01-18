import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path

APP_NAME = "Chrome Profile Manager"
DATA_FILE = "data.json"
DEFAULT_DATA = {
    "language": "id",
    "user_mode": None,
    "user_data_dir": "ChromeProfiles",
    "last_account_number": 0,
    "last_profile_number": 0,
    "global_file": None,
    "folders": {
        "Public": []
    }
}

class Colors:
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def color(text, color_code):
    return color_code + text + Colors.RESET

def print_header(title):
    clear()
    print(color(f"\n{'='*50}", Colors.CYAN))
    print(color(f"  {title}", Colors.BOLD + Colors.CYAN))
    print(color(f"{'='*50}", Colors.CYAN))

def pause_basic():
    input(color("\n⏎ Tekan Enter untuk melanjutkan... ", Colors.GRAY))

def pause_beginner(message="Lanjut?"):
    input(color(f"\n⏎ {message} Tekan Enter untuk melanjutkan... ", Colors.GRAY))

def yesno(msg):
    while True:
        response = input(f"{msg} (y/n): ").lower().strip()
        if response in ['y', 'n']:
            return response == 'y'

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        print(color("Data rusak, menggunakan default...", Colors.YELLOW))
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    
    fixed = False
    for k, v in DEFAULT_DATA.items():
        if k not in data:
            data[k] = v
            fixed = True
    
    if "folders" not in data or not isinstance(data["folders"], dict):
        data["folders"] = {"Public": []}
        fixed = True
    
    if "Public" not in data["folders"]:
        data["folders"]["Public"] = []
        fixed = True
    
    if fixed:
        save_data(data)
        print(color("Data diperbaiki otomatis.", Colors.YELLOW))
    
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_chrome():
    paths = [
        os.environ.get("CHROME_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    for p in paths:
        if p:
            expanded = os.path.expandvars(p)
            if os.path.exists(expanded):
                return expanded
    return None

CHROME_EXE = find_chrome()

def startup(data):
    # Selalu tanyakan mode pengguna setiap kali program dibuka
    print_header("MODE PENGGUNA")
    print("\nApakah kamu sudah pernah menggunakan tool ini?")
    print("y = Sudah mengerti (Advanced)")
    print("n = Belum pernah (Pemula)")
    
    while True:
        choice = input("(y/n): ").lower().strip()
        if choice in ['y', 'n']:
            data["user_mode"] = "advanced" if choice == "y" else "beginner"
            # TIDAK menyimpan ke file, hanya untuk sesi ini
            break

def tutorial(message, user_mode):
    if user_mode == "beginner":
        print(color(f"\nℹ️  {message}", Colors.BLUE))
        pause_beginner()

def menu_global_file(data):
    user_mode = data["user_mode"]
    
    # TUTORIAL untuk pemula
    if user_mode == "beginner":
        print_header("FILE GLOBAL - TUTORIAL")
        print("\n" + color("📚 APA ITU FILE GLOBAL?", Colors.CYAN))
        print("File Global adalah file (seperti .html, .txt, dll) yang akan")
        print("dibuka otomatis setiap kali Anda membuka akun Chrome.")
        print("\n" + color("🎯 CONTOH PENGGUNAAN:", Colors.YELLOW))
        print("1. File index.html dengan bookmark favorit")
        print("2. File note.txt dengan catatan penting")
        print("3. File todo.html dengan daftar tugas")
        print("\n" + color("📍 CARA KERJA:", Colors.GREEN))
        print("1. Pilih file di komputer Anda")
        print("2. Setiap akun Chrome yang dibuka akan otomatis")
        print("   membuka file tersebut")
        print("3. Bisa dihapus kapan saja")
        pause_beginner("Paham?")
    
    while True:
        print_header("FILE GLOBAL")
        current_file = data.get("global_file")
        
        # Tampilkan status dengan lebih jelas
        if current_file and os.path.exists(current_file):
            file_status = color("✓ ADA", Colors.GREEN)
            file_display = color(current_file, Colors.GREEN)
        elif current_file:
            file_status = color("✗ TIDAK DITEMUKAN", Colors.RED)
            file_display = color(current_file, Colors.RED)
        else:
            file_status = color("✗ BELUM DIATUR", Colors.YELLOW)
            file_display = color("Tidak ada file global", Colors.YELLOW)
        
        print(f"\nStatus: {file_status}")
        print(f"File: {file_display}")
        
        print(f"\n{color('1.', Colors.CYAN)} Input File Global")
        print(f"{color('2.', Colors.CYAN)} Hapus File Global")
        print(f"{color('3.', Colors.CYAN)} Test Buka File Global")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "1":
            print("\n" + color("📁 CONTOH PATH FILE:", Colors.YELLOW))
            print("C:\\Users\\Nama\\Documents\\index.html")
            print("D:\\bookmark.html")
            print("C:\\project\\todo.txt")
            
            path = input("\nMasukkan path lengkap file: ").strip('"').strip()
            
            if os.path.exists(path):
                data["global_file"] = path
                save_data(data)
                print(color("✓ File global berhasil disimpan!", Colors.GREEN))
                print(color("File ini akan otomatis terbuka saat membuka akun.", Colors.BLUE))
                pause_basic()
            else:
                print(color("✗ File tidak ditemukan!", Colors.RED))
                print(color("Pastikan path file benar dan file ada.", Colors.YELLOW))
                pause_basic()
                
        elif choice == "2":
            if current_file:
                confirm = yesno(f"Yakin hapus file global?\nFile: {current_file}")
                if confirm:
                    data["global_file"] = None
                    save_data(data)
                    print(color("✓ File global dihapus!", Colors.GREEN))
            else:
                print(color("✗ Tidak ada file global yang diatur!", Colors.YELLOW))
            pause_basic()
            
        elif choice == "3":
            # Fitur baru: Test buka file global
            if current_file and os.path.exists(current_file):
                try:
                    os.startfile(current_file)
                    print(color("✓ File global berhasil dibuka!", Colors.GREEN))
                    print(color("Seperti inilah yang akan muncul saat membuka akun.", Colors.BLUE))
                except Exception as e:
                    print(color(f"✗ Gagal membuka file: {e}", Colors.RED))
            elif current_file:
                print(color("✗ File tidak ditemukan di lokasi tersebut!", Colors.RED))
            else:
                print(color("✗ Belum ada file global yang diatur!", Colors.YELLOW))
            pause_basic()
            
        elif choice == "x":
            return

def open_account(account, data):
    if not CHROME_EXE:
        print(color("✗ Chrome.exe tidak ditemukan!", Colors.RED))
        pause_basic()
        return
    
    try:
        cmd = account["command"]
        subprocess.Popen(cmd, shell=True)
        
        # PERBAIKAN: Cek apakah global_file tidak None dan ada
        global_file = data.get("global_file")
        if global_file and os.path.exists(global_file):
            os.startfile(global_file)
        
        account["opened_this_session"] = True
        print(color(f"✓ Membuka akun: {account['name']}", Colors.GREEN))
        time.sleep(1)
    except Exception as e:
        print(color(f"✗ Gagal membuka akun: {e}", Colors.RED))
        pause_basic()

def select_accounts_menu(accounts, selected_indices):
    while True:
        print_header("PILIH AKUN (MULTI SELECT)")
        print(f"\nPilih akun (1-{len(accounts)}), ketik lagi untuk batal pilih")
        print(f"Terpilih: {len(selected_indices)} akun")
        print(f"\n{color('y.', Colors.GREEN)} Selesai Pilih")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        for i, acc in enumerate(accounts, 1):
            status = color("✓", Colors.GREEN) if i in selected_indices else " "
            name_color = Colors.GREEN if acc.get("opened_this_session") else Colors.WHITE
            print(f"  {status} {color(str(i), Colors.CYAN)}. {color(acc['name'], name_color)}")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "y":
            return selected_indices
        elif choice == "x":
            return None
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(accounts):
                if idx in selected_indices:
                    selected_indices.remove(idx)
                else:
                    selected_indices.add(idx)

def account_actions_menu(data, folder, account_indices, page_accounts):
    if not account_indices:
        print(color("✗ Tidak ada akun terpilih!", Colors.YELLOW))
        pause_basic()
        return
    
    while True:
        print_header("AKSI AKUN TERPILIH")
        print(f"\n{len(account_indices)} akun terpilih")
        print(f"\n{color('1.', Colors.CYAN)} Rename Akun")
        print(f"{color('2.', Colors.CYAN)} Hapus Akun")
        print(f"{color('3.', Colors.CYAN)} Pindahkan ke Folder")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "1":
            for idx in sorted(account_indices):
                acc = page_accounts[idx-1]
                new_name = input(f"\nNama baru untuk '{acc['name']}': ").strip()
                if new_name:
                    if yesno("Tambahkan nomor urut?"):
                        acc["name"] = f"{new_name}_{idx}"
                    else:
                        acc["name"] = new_name
            save_data(data)
            print(color("✓ Nama diubah!", Colors.GREEN))
            pause_basic()
            return
            
        elif choice == "2":
            confirm = yesno("Yakin menghapus akun terpilih?")
            if confirm:
                # Perbaikan di sini: Hapus dari data asli bukan hanya dari page_accounts
                accounts = data["folders"][folder]
                
                # Dapatkan indeks global dari akun yang dipilih
                global_indices = []
                for idx in account_indices:
                    # Cari akun di page_accounts dalam accounts
                    page_acc = page_accounts[idx-1]
                    for i, acc in enumerate(accounts):
                        if acc["name"] == page_acc["name"] and acc["command"] == page_acc["command"]:
                            global_indices.append(i)
                            break
                
                # Hapus dari belakang agar indeks tidak berubah
                for i in sorted(global_indices, reverse=True):
                    accounts.pop(i)
                
                save_data(data)
                print(color("✓ Akun dihapus!", Colors.GREEN))
                pause_basic()
                return
        
        elif choice == "3":
            folders = [f for f in data["folders"].keys() if f != folder]
            if not folders:
                print(color("✗ Tidak ada folder lain!", Colors.YELLOW))
                pause_basic()
                continue
            
            print("\nPilih folder tujuan:")
            for i, f in enumerate(folders, 1):
                print(f"{color(str(i), Colors.CYAN)}. {f}")
            
            try:
                folder_idx = int(input(f"\n{color('>', Colors.GREEN)} ")) - 1
                target_folder = folders[folder_idx]
                
                # Perbaikan di sini: Pindahkan dari data asli
                accounts = data["folders"][folder]
                target_accounts = data["folders"][target_folder]
                
                # Dapatkan akun yang akan dipindahkan
                accounts_to_move = []
                for idx in account_indices:
                    page_acc = page_accounts[idx-1]
                    for i, acc in enumerate(accounts):
                        if acc["name"] == page_acc["name"] and acc["command"] == page_acc["command"]:
                            accounts_to_move.append((i, acc))
                            break
                
                # Pindahkan dari belakang agar indeks tidak berubah
                for i, acc in sorted(accounts_to_move, key=lambda x: x[0], reverse=True):
                    accounts.pop(i)
                    target_accounts.append(acc)
                
                save_data(data)
                print(color(f"✓ Akun dipindahkan ke {target_folder}!", Colors.GREEN))
                pause_basic()
                return
            except:
                print(color("✗ Pilihan tidak valid!", Colors.RED))
                pause_basic()
        
        elif choice == "x":
            return

def list_accounts(data):
    user_mode = data["user_mode"]
    
    if user_mode == "beginner":
        tutorial("Daftar Akun: Lihat dan kelola akun Chrome yang sudah dibuat. Akun hijau = sudah dibuka sesi ini.", user_mode)
    
    folders = list(data["folders"].keys())
    
    while True:
        print_header("PILIH FOLDER")
        print("\nFolder:")
        for i, folder in enumerate(folders, 1):
            count = len(data["folders"][folder])
            print(f"{color(str(i), Colors.CYAN)}. {folder} ({count} akun)")
        print(f"{color('n.', Colors.GREEN)} Buat Folder Baru")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "x":
            return
        elif choice == "n":
            new_folder = input("Nama folder baru: ").strip()
            if new_folder and new_folder not in data["folders"]:
                data["folders"][new_folder] = []
                save_data(data)
                folders.append(new_folder)
                print(color(f"✓ Folder '{new_folder}' dibuat!", Colors.GREEN))
                pause_basic()
            continue
        
        try:
            folder_idx = int(choice) - 1
            if 0 <= folder_idx < len(folders):
                selected_folder = folders[folder_idx]
                break
        except:
            continue
    
    accounts = data["folders"][selected_folder]
    page = 0
    selected_indices = set()
    
    while True:
        print_header(f"DAFTAR AKUN - {selected_folder}")
        print(f"\nTotal: {len(accounts)} akun | Halaman: {page+1}/{(len(accounts)-1)//10 + 1}")
        
        start_idx = page * 10
        end_idx = start_idx + 10
        page_accounts = accounts[start_idx:end_idx]
        
        if not page_accounts:
            print(color("\nTidak ada akun di halaman ini.", Colors.YELLOW))
        else:
            for i, acc in enumerate(page_accounts, 1):
                global_i = start_idx + i
                status = color("✓", Colors.GREEN) if global_i-1 in selected_indices else " "
                name_color = Colors.GREEN if acc.get("opened_this_session") else Colors.WHITE
                print(f"{status} {color(str(i), Colors.CYAN)}. {color(acc['name'], name_color)}")
                if acc.get("command"):
                    print(f"     {color(acc['command'][:80], Colors.GRAY)}")
        
        print(f"\n{color('1-10', Colors.YELLOW)} buka akun | {color('c', Colors.YELLOW)} pilih multi | {color('n', Colors.YELLOW)} next")
        print(f"{color('p', Colors.YELLOW)} previous | {color('g', Colors.YELLOW)} go to | {color('x', Colors.RED)} kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(page_accounts):
                open_account(page_accounts[idx-1], data)
                save_data(data)
        
        elif choice == "c":
            selected = select_accounts_menu(page_accounts, set())
            if selected is not None:
                account_actions_menu(data, selected_folder, selected, page_accounts)
                accounts = data["folders"][selected_folder]
                selected_indices.clear()
        
        elif choice == "n":
            if (page + 1) * 10 < len(accounts):
                page += 1
        
        elif choice == "p":
            if page > 0:
                page -= 1
        
        elif choice == "g":
            try:
                new_page = int(input("Halaman ke: ")) - 1
                if 0 <= new_page <= (len(accounts)-1)//10:
                    page = new_page
            except:
                pass
        
        elif choice == "x":
            return

def add_account(data):
    user_mode = data["user_mode"]
    
    if user_mode == "beginner":
        tutorial("Tambahkan Akun: Menambahkan akun Chrome yang sudah ada. Masukkan command Chrome dengan profile directory.", user_mode)
    
    folders = list(data["folders"].keys())
    
    while True:
        print_header("PILIH FOLDER")
        print("\nFolder tujuan:")
        for i, folder in enumerate(folders, 1):
            count = len(data["folders"][folder])
            print(f"{color(str(i), Colors.CYAN)}. {folder} ({count} akun)")
        print(f"{color('n.', Colors.GREEN)} Buat Folder Baru")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "x":
            return
        elif choice == "n":
            new_folder = input("Nama folder baru: ").strip()
            if new_folder and new_folder not in data["folders"]:
                data["folders"][new_folder] = []
                save_data(data)
                folders.append(new_folder)
                print(color(f"✓ Folder '{new_folder}' dibuat!", Colors.GREEN))
                pause_basic()
            continue
        
        try:
            folder_idx = int(choice) - 1
            if 0 <= folder_idx < len(folders):
                selected_folder = folders[folder_idx]
                break
        except:
            continue
    
    while True:
        print_header(f"TAMBAH AKUN - {selected_folder}")
        print(f"\n{color('1.', Colors.CYAN)} Tambah Akun (Satu)")
        print(f"{color('2.', Colors.CYAN)} Tambah Akun (Bulk)")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "1":
            print(color("\nContoh command Chrome:", Colors.YELLOW))
            print('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --profile-directory="Profile 1"')
            print('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --user-data-dir="C:\\ChromeProfiles\\profile1"\n')
            
            command = input("Command Chrome: ").strip()
            if not command:
                print(color("✗ Command tidak boleh kosong!", Colors.RED))
                pause_basic()
                continue
            
            default_name = f"Akun_{data['last_account_number'] + 1}"
            name = input(f"Nama akun [{default_name}]: ").strip()
            if not name:
                name = default_name
            
            data["last_account_number"] += 1
            account = {
                "name": name,
                "command": command,
                "profile_dir": None,
                "opened_this_session": False
            }
            
            data["folders"][selected_folder].append(account)
            save_data(data)
            print(color(f"✓ Akun '{name}' ditambahkan!", Colors.GREEN))
            pause_basic()
        
        elif choice == "2":
            print(color("\nMasukkan command Chrome, pisahkan dengan koma:", Colors.YELLOW))
            print('Contoh: "chrome.exe --profile=1", "chrome.exe --profile=2"\n')
            
            commands_input = input("Commands: ").strip()
            if not commands_input:
                print(color("✗ Input tidak boleh kosong!", Colors.RED))
                pause_basic()
                continue
            
            commands = [cmd.strip() for cmd in commands_input.split(",") if cmd.strip()]
            
            for i, cmd in enumerate(commands, 1):
                data["last_account_number"] += 1
                account = {
                    "name": f"Akun_{data['last_account_number']}",
                    "command": cmd,
                    "profile_dir": None,
                    "opened_this_session": False
                }
                data["folders"][selected_folder].append(account)
            
            save_data(data)
            print(color(f"✓ {len(commands)} akun ditambahkan!", Colors.GREEN))
            pause_basic()
        
        elif choice == "x":
            return

def create_profile(data):
    user_mode = data["user_mode"]
    
    if user_mode == "beginner":
        tutorial("Buat Profil Baru: Membuat profil Chrome baru yang fresh. Chrome akan terbuka sebentar lalu tertutup otomatis.", user_mode)
    
    if not CHROME_EXE:
        print(color("✗ Chrome.exe tidak ditemukan!", Colors.RED))
        pause_basic()
        return
    
    base_dir = os.path.abspath(data["user_data_dir"])
    os.makedirs(base_dir, exist_ok=True)
    
    while True:
        print_header("BUAT PROFIL BARU")
        print(f"\nFolder: {color('Public', Colors.YELLOW)} (default)")
        print(f"\n{color('1.', Colors.CYAN)} Buat 1 Profil")
        print(f"{color('2.', Colors.CYAN)} Buat Profil Bulk (max 10)")
        print(f"{color('x.', Colors.RED)} Kembali")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "1":
            count = 1
        elif choice == "2":
            try:
                count = int(input("Jumlah profil (max 10): "))
                count = max(1, min(10, count))
            except:
                print(color("✗ Input tidak valid!", Colors.RED))
                pause_basic()
                continue
        elif choice == "x":
            return
        else:
            continue
        
        print(f"\n{color('Membuat', Colors.YELLOW)} {count} profil baru...")
        
        for i in range(count):
            data["last_profile_number"] += 1
            profile_dir = os.path.join(base_dir, f"profile_{data['last_profile_number']}")
            
            cmd = f'"{CHROME_EXE}" --user-data-dir="{profile_dir}" --no-first-run --no-default-browser-check'
            
            print(f"\nProfil {i+1}: Membuka Chrome...")
            try:
                process = subprocess.Popen(cmd, shell=True)
                time.sleep(3)
                process.terminate()
                time.sleep(1)
                
                account = {
                    "name": f"Profil_{data['last_profile_number']}",
                    "command": cmd,
                    "profile_dir": profile_dir,
                    "opened_this_session": False
                }
                
                data["folders"]["Public"].append(account)
                print(color(f"✓ Profil {i+1} selesai", Colors.GREEN))
                
            except Exception as e:
                print(color(f"✗ Gagal membuat profil {i+1}: {e}", Colors.RED))
        
        save_data(data)
        print(color(f"\n✓ Selesai membuat {count} profil!", Colors.GREEN))
        pause_basic()

def main_menu(data):
    user_mode = data["user_mode"]
    
    while True:
        print_header(APP_NAME)
        print(f"Mode: {color(user_mode.capitalize(), Colors.YELLOW)}")
        print(f"\n{color('1.', Colors.CYAN)} File Global")
        print(f"{color('2.', Colors.CYAN)} Daftar Akun")
        print(f"{color('3.', Colors.CYAN)} Tambahkan Akun")
        print(f"{color('4.', Colors.CYAN)} Buat Profil Baru")
        print(f"{color('x.', Colors.RED)} Keluar")
        
        choice = input(f"\n{color('>', Colors.GREEN)} ").strip().lower()
        
        if choice == "1":
            menu_global_file(data)
        elif choice == "2":
            list_accounts(data)
        elif choice == "3":
            add_account(data)
        elif choice == "4":
            create_profile(data)
        elif choice == "x":
            print(color("\n✓ Menyimpan data...", Colors.GREEN))
            save_data(data)
            print(color("✓ Sampai jumpa!", Colors.CYAN))
            sys.exit(0)

def main():
    data = load_data()
    startup(data)
    main_menu(data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color("\n\n✗ Program dihentikan", Colors.RED))
        sys.exit(1)
    except Exception as e:
        print(color(f"\n✗ Error: {e}", Colors.RED))
        pause_basic()
        sys.exit(1)