import os, re, threading, tkinter as tk
from tkinter import ttk

# meta details
container_file = "resource.bin"
repacked_file = "resource.bin"
folder1 = "Unpacked"
folder2 = "Repacked"
HEADER_SIZE = 26624
file_count = 3201
metadata_offsets = 0x10 # section of 8 byte chunk entries (offset << 11 and file size)
SECTOR = 2048
LILAC = "#C8A2C8"

# GUI

def GUI():
    root = tk.Tk()
    root.configure(bg=LILAC)
    root.title("Dynasty Warriors 4 Hyper resource_bin Unpacker")
    root.minsize(1000, 700)
    root.resizable(False, False)

    status_label = gui_stuff(root)  # return the label so we can pass it
    progress = init_progress(root)  # CAPTURE the progress object

    # Create buttons
    
    btn_unpack = tk.Button(
        root,
        text="Unpack files",
        command=lambda: start_unpack_thread(root, progress, status_label),
        height=5, width=25
    )
    btn_unpack.place(x=700, y=50)

    btn_repack = tk.Button(
        root,
        text="Repack files",
        command=lambda: start_repack_thread(root, progress, status_label),
        height=5, width=25
    )
    btn_repack.place(x=700, y=250)

    # keep refs so we can disable/enable during work
    root._bns_buttons = (btn_unpack, btn_repack)
    
    root.mainloop()
    

def gui_stuff(root):
    lilac_label(
        root,
        text="To unpack the files, click the Unpack button and ensure the needed files are in the same directory."
    ).place(x=60, y=50)

    lilac_label(
        root,
        text=f"To repack the files, click the Repack button and ensure the needed files are in the {folder2} folder."
    ).place(x=60, y=250)

    # Status label
    status_label = lilac_label(root, text="", fg="green")
    status_label.place(x=60, y=500)
    return status_label
    
# Threading Functions

def set_buttons_state(root, state):
    for b in getattr(root, "_bns_buttons", ()):
        b.config(state=state)

def start_unpack_thread(root, progress, status_label):
    set_buttons_state(root, "disabled")
    set_progress(root, progress, 0, 1, "Preparing…")

    def notify(msg):
        # marshal back to UI thread
        root.after(0, handle_msg, root, progress, status_label, msg)

    t = threading.Thread(target=unpack_worker, args=(notify,), daemon=True)
    t.start()

def start_repack_thread(root, progress, status_label):
    set_buttons_state(root, "disabled")
    set_progress(root, progress, 0, 1, "Preparing (repack)…")

    def notify(msg):
        root.after(0, handle_msg, root, progress, status_label, msg)

    # run on a worker thread
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

# Worker (background thread)

def unpack_worker(notify):
    try:
        notify(("progress", 0, 1, "Preparing…"))

        # Make sure output & future repack folders exist
        os.makedirs(folder1, exist_ok=True)
        os.makedirs(folder2, exist_ok=True)

        # Create a starter repack file (header copy)
        with open(container_file, "rb") as f1, open(os.path.join(folder2, repacked_file), "wb") as i1:
            init_data = f1.read(26624)   # header chunk preserved for repack
            i1.write(init_data)

            # Jump to metadata table
            f1.seek(metadata_offsets)
            total = file_count
            notify(("progress", 0, max(1, total), "Unpacking…"))

            for i in range(file_count):
                base_offset  = int.from_bytes(f1.read(4), "little")
                true_offset  = base_offset << 11
                size         = int.from_bytes(f1.read(4), "little")
                return_pos   = f1.tell()

                f1.seek(true_offset)
                data = f1.read(size)

                # first 4 bytes are the extension in this format
                try:
                    extension = data[:4].decode(errors="strict")
                except Exception:
                    extension = "bin"  # fallback if decode fails

                out_path = os.path.join(folder1, f"File_{i+1}.{extension}")
                with open(out_path, "wb") as w1:
                    w1.write(data)

                f1.seek(return_pos)

                # throttle UI updates
                if (i & 31) == 0 or (i + 1) == total:
                    notify(("progress", i + 1, total, None))

        # success message via progress bar note
        notify(("done", f"Unpack complete. {file_count} files extracted."))

    except FileNotFoundError:
        notify(("status", f"Missing file: {container_file}", "red"))
        notify(("done", "Error."))
    except PermissionError:
        notify(("status", "Permission denied for one or more files.", "red"))
        notify(("done", "Error."))
    except Exception as e:
        notify(("status", f"Unexpected error: {e}", "red"))
        notify(("done", "Error."))

def repack_worker(notify):
    try:
        os.makedirs(folder1, exist_ok=True)
        os.makedirs(folder2, exist_ok=True)

        dst_path = os.path.join(folder2, repacked_file)
        if not os.path.isfile(dst_path):
            with open(container_file, "rb") as f1, open(dst_path, "wb") as i1:
                i1.write(f1.read(HEADER_SIZE))

        with open(dst_path, "r+b") as dst:
            dst.truncate(HEADER_SIZE)     # reset to header
            dst.seek(HEADER_SIZE) # seek end of toc before appending files
            files = list_unpacked_files()
            if not files:
                raise RuntimeError(f"No files found in {folder1} to repack.")

            total   = len(files)
            offsets = []
            sizes   = []
            notify(("progress", 0, total, "Repacking…"))

            for i, name in enumerate(files, 1):
                src_path = os.path.join(folder1, name)
                start = dst.tell()
                with open(src_path, "rb") as src:
                    data = src.read()
                dst.write(data)
                sizes.append(len(data))
                offsets.append(start)
                pad_eof_to_sector(dst)

                if (i & 31) == 0 or i == total:
                    notify(("progress", i, total, None))

            # write TOC at metadata_offsets: (offset>>11, size)
            dst.seek(metadata_offsets)
            for off, sz in zip(offsets, sizes):
                dst.write((off >> 11).to_bytes(4, "little"))
                dst.write(sz.to_bytes(4, "little"))

        notify(("done", f"Repack complete → {dst_path}"))

    except Exception as e:
        notify(("status", f"Repack failed: {e}", "red"))
        notify(("done", "Error."))

# Utility functions

def list_unpacked_files():
    """Return sorted list from folder1"""
    files = [f for f in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, f))]
    files.sort(key=natural_key)
    return files

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def pad_eof_to_sector(f, sector=SECTOR):
    pos = f.tell()
    pad = (-pos) & (sector - 1)
    if pad:
        f.write(b"\x00" * pad)

def init_progress(root):
    prog = {}
    prog["var"] = tk.StringVar(value="Idle")
    prog["bar"] = ttk.Progressbar(root, mode="determinate", length=320)
    prog["bar"].grid(row=99, column=0, columnspan=3, pady=(8, 0), sticky="ew")
    lilac_label(root, textvariable=prog["var"], anchor="w").grid(
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
        prog["var"].set(f"{done}/{total} ({pct}%)")
    else:
        prog["var"].set(note)
    root.update_idletasks()

def lilac_label(parent, **kw):
    base = dict(bg=LILAC, bd=0, relief="flat", highlightthickness=0, takefocus=0)
    base.update(kw)
    return tk.Label(parent, **base)

# main

if __name__ == "__main__":
    GUI()
