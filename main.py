from constants.constants import *
from utils.folders import create_folders, folder_convert, folder2mp3
# from menu import menu

from constants.constants import *
from classes.Options import Options
from utils.cryptography import get_fernet, decrypt_content
from utils.ctxt import *
from utils.injection import inject_file, extract_file
from utils.input import get_path, get_bool
from utils.read_write import *

MOD_PREFIX = ""
MOD_SUFIX = "_mod"
STORE_RANDOM = False
TEST_MODE = False


create_folders(*PATHS)
folder_convert(BASE_IMAGES_PATH, ".png", IMAGE_EXTS)
folder2mp3(BASE_AUDIOS_PATH)

from pathlib import Path
import time



def get_out_path(base_path: str, file_type: str) -> str:
    base_stem = Path(base_path).stem
    if file_type == "image":
        out_path = f"{MOD_IMAGES_PATH}/{MOD_PREFIX}{base_stem}{MOD_SUFIX}.png"
    elif file_type == "audio":
        out_path = f"{MOD_AUDIOS_PATH}/{MOD_PREFIX}{base_stem}{MOD_SUFIX}.wav"
    return out_path



def menu():
    option = Options(["EXIT", "Inject file", "Extract file"]).get_choice()

    if option == 0: 
        exit()

    elif option == 1: 
        inject_file_func()

    elif option == 2:
        extract_file_func()



def inject_file_func():
    if TEST_MODE:
        file_path = f"{INPUT_PATH}/images.zip"
        # base_path = f"{BASE_AUDIOS_PATH}/winter-vivaldi.mp3"
        base_path = f"{BASE_IMAGES_PATH}/1'7MP.png"
    else:
        file_path = get_path([INPUT_PATH], "File to be stored: ")
        base_path = get_path([BASE_IMAGES_PATH,BASE_AUDIOS_PATH], "Filename of the base file: ", [IMAGE_EXTS,AUDIO_EXTS])

   
    do_encryption = get_bool("Encrypt the file?")
    file = read_file(file_path)
    
    base_file = read_base_file(base_path)
    arr = base_file["arr"]
    file_type = base_file["file_type"]
    filename = Path(file_path).name.encode()

    out_path = get_out_path(base_path, file_type)
    if do_encryption:
        fernet = get_fernet()
        file = fernet.encrypt(file)
        filename = fernet.encrypt(filename)

    t1 = time.time()
    try:
        new_arr = inject_file(arr, file, filename, STORE_RANDOM)

        if file_type == "image":
            write_image(new_arr, out_path)
        elif file_type == "audio":
            write_audio(new_arr, base_file["frame_rate"], base_file["num_channels"], out_path)

        print(ctxt(f"\nModified {file_type} saved in {ctxt(out_path)}"))

    except Exception as e:
        print(f"\n{ctxt('Error: ')}{e}")
        return
    print(f"\nDone in {ctxt(round(time.time() - t1, 4))} seconds")
  



def extract_file_func():
    if TEST_MODE:
        # mod_file_path = f"{MOD_AUDIOS_PATH}/winter-vivaldi_mod.wav"
        mod_file_path = f"{MOD_IMAGES_PATH}/1'7MP_mod.png"
    else:
        mod_file_path = get_path([MOD_IMAGES_PATH, MOD_AUDIOS_PATH], "Filename of the modified file: ", [IMAGE_EXTS,AUDIO_EXTS])
    t1 = time.time()
    if Path(mod_file_path).suffix in IMAGE_EXTS:
        mod_arr = read_image(mod_file_path)
    elif Path(mod_file_path).suffix in AUDIO_EXTS:
        mod_arr = read_audio(mod_file_path)["arr"]
    output = extract_file(mod_arr)
    file, filename = output["file"], output['filename']
    if file.startswith(b"gAAAAA") and filename.startswith(b"gAAAAA"):
        try:
            output_decrypted = decrypt_content(file, filename)
            file = output_decrypted["file"]
            filename = output_decrypted["filename"]
        except Exception as e:
            print(f"\n{ctxt('Error: ')}{e}")
            return
    filename = filename.decode("utf-8")

    out_path = f"{OUTPUT_PATH}/{filename}"
    write_file(file, out_path)
    print(ctxt(f"\nOutput file saved in {ctxt(out_path)}"))
    print(f"\nDone in {ctxt(round(time.time() - t1, 4))} seconds")

menu()