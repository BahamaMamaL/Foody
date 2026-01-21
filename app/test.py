import torch
import ctypes

print(f"Torch Version: {torch.__version__}")

# Versuche, CUDA zu laden und Fehler abzufangen
try:
    if torch.cuda.is_available():
        print("CUDA ist verfügbar! (Wunder geschehen)")
    else:
        print("CUDA ist NICHT verfügbar.")

        # Warum? Tiefer graben.
        # 1. Prüfen ob die CUDA-DLLs überhaupt da sind
        try:
            # Versuche, die wichtigste CUDA-Bibliothek direkt zu laden
            ctypes.CDLL('nvcuda.dll')
            print("-> 'nvcuda.dll' wurde gefunden (Treiber scheint ok).")
        except OSError:
            print(
                "-> KRITISCH: 'nvcuda.dll' nicht gefunden! Dein Grafikkartentreiber ist kaputt oder nicht installiert.")

        # 2. Hat PyTorch überhaupt CUDA-Support mitkompiliert?
        if torch.backends.cuda.is_built():
            print("-> PyTorch wurde MIT CUDA-Support gebaut.")
        else:
            print("-> PyTorch wurde OHNE CUDA-Support gebaut (Du hast die CPU-Version).")

except Exception as e:
    print(f"Unbekannter Fehler: {e}")
