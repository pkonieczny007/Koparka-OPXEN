import subprocess
import time
import os
import signal

SCRIPT = "minter.py"
INTERVAL = 10  # sekundy

while True:
    # 1️⃣ Start procesu
    process = subprocess.Popen(["python", SCRIPT])
    print(f"[LOOPER] Uruchomiono {SCRIPT} (PID: {process.pid})")

    # 2️⃣ Czekaj 30 sek
    time.sleep(INTERVAL)

    # 3️⃣ Zabij proces
    print(f"[LOOPER] Zatrzymuję proces PID: {process.pid}")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.kill(process.pid, signal.SIGKILL)
        print(f"[LOOPER] Proces {process.pid} zabity siłą.")

    # 4️⃣ Pętla ponawia uruchomienie
