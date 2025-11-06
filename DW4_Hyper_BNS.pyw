import os, re, threading, tkinter as tk
from tkinter import ttk

# meta details
jpbns_file = "voice_jp.bns"
usbns_file = "voice_us.bns"
jp_ref = "voice_jp.ref"
us_ref = "voice_us.ref"
folder1 = "JP_Ogg_Files"
folder2 = "US_Ogg_Files"
folder3 = "New_BNS_Files"
SECTOR = 2048
ogg_header = b'\x4F\x67\x67\x53\x00\x02\x00\x00' # the correct header, always this for DW4 Hyper ogg files

# GUI

def GUI():
    """Main function to initialize the rest"""
    root = tk.Tk()
    root.title("Dynasty Warriors 4 Hyper BNS Unpacker")
    root.minsize(1000, 700)
    root.resizable(False, False)

    status_label = gui_stuff(root)  # return the label so we can pass it
    progress = init_progress(root)  # CAPTURE the progress object

    btn_unpack = tk.Button(
        root, text="Unpack BNS files",
        command=lambda: start_unpack_thread(root, progress, status_label, ()),
        height=5, width=25
    )
    btn_unpack.place(x=700, y=50)

    btn_repack = tk.Button(
        root, text="Repack BNS files",
        command=lambda: start_repack_thread(root, progress, status_label, ()),
        height=5, width=25
    )
    btn_repack.place(x=700, y=250)

    # stash buttons so we can disable/enable during work
    root._bns_buttons = (btn_unpack, btn_repack)
    
    root.mainloop()

def gui_stuff(root):
    """This function handles GUI display related functions"""
    tk.Label(
        root,
        text="To unpack the files, click the Unpack button and ensure the needed files are in the same directory."
    ).place(x=60, y=50)

    tk.Label(
        root,
        text=(
            f"To repack, place .ogg files into {folder1} and/or {folder2}.\n"
            f"Outputs will be written into {folder3}."
        )
    ).place(x=60, y=250)

    # Status label
    status_label = tk.Label(root, text="", fg="green")
    status_label.place(x=60, y=500)
    return status_label

# File Unpacking Function
        
def unpack_worker(notify):
    # JP then US. each: scan → write .ref → extract OGGs
    try:
        _bns_scan_to_ref(jpbns_file, jp_ref, notify)
        _bns_extract_from_ref(jpbns_file, jp_ref, folder1, notify)
        _bns_scan_to_ref(usbns_file, us_ref, notify)
        _bns_extract_from_ref(usbns_file, us_ref, folder2, notify)
        notify(("done", "Unpack complete."))
    except Exception as e:
        notify(("status", f"Unpack failed: {e}", "red"))
        notify(("done", "Error."))

def _bns_scan_to_ref(bns_path, ref_path, notify):
    notify(("status", f"Scanning {bns_path} → {ref_path}", "green"))
    os.makedirs(os.path.dirname(ref_path) or ".", exist_ok=True)
    with open(bns_path, "rb") as f1, open(ref_path, "wb") as f2:
        while True:
            offset = f1.tell()
            block = f1.read(16)
            if not block:
                break
            if ogg_header in block:
                f2.write(offset.to_bytes(4, "little"))
        f2.write(os.path.getsize(bns_path).to_bytes(4, "little"))

def _read_offsets(ref_path):
    offs = []
    with open(ref_path, "rb") as r:
        while True:
            b = r.read(4)
            if not b:
                break
            offs.append(int.from_bytes(b, "little"))
    return offs

def _bns_extract_from_ref(bns_path, ref_path, out_folder, notify):
    os.makedirs(out_folder, exist_ok=True)
    offsets = _read_offsets(ref_path)
    pairs = list(zip(offsets, offsets[1:]))
    total = len(pairs)
    notify(("progress", 0, max(1, total), "Unpacking…"))

    with open(bns_path, "rb") as bns:
        for i, (a, b) in enumerate(pairs, 1):
            bns.seek(a)
            data = bns.read(b - a)
            out_name = os.path.join(out_folder, f"File_{i}.ogg")
            with open(out_name, "wb") as out:
                out.write(data)
            if (i & 31) == 0 or i == total:
                notify(("progress", i, total, None))
    notify(("status", f"Unpacked {total} files from {bns_path}", "green"))

# File Repacking function

def repack_worker(notify):
    try:
        _bns_repack_one(jpbns_file, folder1, notify)
        _bns_repack_one(usbns_file, folder2, notify)
        notify(("done", "Repack complete."))
    except Exception as e:
        notify(("status", f"Repack failed: {e}", "red"))
        notify(("done", "Error."))

def _bns_repack_one(out_filename, src_folder, notify):
    files = [f for f in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))]
    files.sort(key=natural_key)
    if not files:
        raise RuntimeError(f"No .ogg files found in {src_folder}")

    os.makedirs(folder3, exist_ok=True)
    out_path = os.path.join(folder3, out_filename)
    total = len(files)
    notify(("status", f"Repacking {src_folder} → {out_path}", "green"))
    notify(("progress", 0, total, "Repacking…"))

    with open(out_path, "wb") as dst:
        for i, name in enumerate(files, 1):
            with open(os.path.join(src_folder, name), "rb") as src:
                dst.write(src.read())
            pad_eof_to_sector(dst)
            if (i & 31) == 0 or i == total:
                notify(("progress", i, total, None))
    
# Utility functions

def set_buttons_state(root, state):
    for b in getattr(root, "_bns_buttons", ()):
        b.config(state=state)

def start_unpack_thread(root, progress, status_label, _):
    set_buttons_state(root, "disabled")
    # UI bootstrap
    set_progress(root, progress, 0, 1, "Preparing (unpack)…")

    def notify(msg):
        # marshal back to Tk safely
        root.after(0, handle_msg, root, progress, status_label, msg)

    t = threading.Thread(target=unpack_worker, args=(notify,), daemon=True)
    t.start()

def start_repack_thread(root, progress, status_label, _):
    set_buttons_state(root, "disabled")
    set_progress(root, progress, 0, 1, "Preparing (repack)…")

    def notify(msg):
        root.after(0, handle_msg, root, progress, status_label, msg)

    t = threading.Thread(target=repack_worker, args=(notify,), daemon=True)
    t.start()

def handle_msg(root, progress, status_label, msg):
    kind = msg[0]
    if kind == "status":
        _, text, color = msg
        status_label.config(text=text, fg=color)
    elif kind == "progress":
        _, done, total, note = msg
        set_progress(root, progress, done, total, note)
    elif kind == "done":
        _, note = msg
        set_progress(root, progress, 1, 1, note)
        set_buttons_state(root, "normal")
        
def natural_key(s):
    """Handles sorting of incrementing filenames"""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def pad_eof_to_sector(f, sector=SECTOR):
    """Pad with 0x00 until f.tell() is a multiple of sector."""
    pos = f.tell()
    pad = (-pos) & (sector - 1)
    if pad:
        f.write(b"\x00" * pad)

def init_progress(root):
    prog = {}
    prog["var"] = tk.StringVar(value="Idle")
    prog["bar"] = ttk.Progressbar(root, mode="determinate", length=320)
    prog["bar"].grid(row=99, column=0, columnspan=3, pady=(8, 0), sticky="ew")

    tk.Label(root, textvariable=prog["var"], anchor="w").grid(
        row=100, column=0, columnspan=3, sticky="ew"
    )
    return prog

def set_progress(root, prog, done, total, note=None):
    total = max(1, int(total))
    done = min(int(done), total)

    if int(prog["bar"]["maximum"] or 0) != total:
        prog["bar"].configure(maximum=total)

    prog["bar"]["value"] = done
    if note is None:
        pct = (done * 100) // total
        prog["var"].set(f"Unpacking… {done}/{total} ({pct}%)")
    else:
        prog["var"].set(note)

    # Keep UI responsive without reentering the event loop
    root.update_idletasks()

if __name__ == "__main__":
    GUI()
