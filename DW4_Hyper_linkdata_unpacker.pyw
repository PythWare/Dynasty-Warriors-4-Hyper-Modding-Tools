import os, sys, threading, tkinter as tk
from tkinter import ttk

filename_list = "filenames.ref" # custom text file storing filenames, obtained from the executable
container_file = "linkdata.BIN" # main container file
metadata_file = "mdata.bin" # metadata file, similar to the idx format
folder = "Unpacked" # stores unpacked files
error_file = "Error.txt"

filecount = 2364 # amount of files within container_file, mini containers such as PD2 files store additional files
offset_to_metadata = 0x10 # for metadata file
png_check = b'\x89\x50\x4E\x47'
xkm_check = b'\x58\x4B\x4D'
xft_check = b'\x58\x46\x54'
bmp_check = b'\x42\x4D'
jpg_check = b'\x4A\x46\x49\x46'
tim2_check = b'\x54\x49\x4D\x32'

# GUI

def GUI():
    root = tk.Tk()
    root.title("Dynasty Warriors 4 Hyper Unpacker")
    root.minsize(1000, 700)
    root.resizable(False, False)

    status_label = gui_stuff(root)  # return the label so we can pass it
    progress = init_progress(root)  # capture the progress object

    btn_unpack = tk.Button(
        root,
        text="Unpack files",
        command=lambda: start_unpack_thread(root, progress, status_label),
        height=5, width=25
    )
    btn_unpack.place(x=700, y=50)

    # stash buttons so we can disable/enable during work
    root._dw4_buttons = (btn_unpack,)
    
    root.mainloop()


def gui_stuff(root):
    tk.Label(
        root,
        text="To unpack the files, click the Unpack button and ensure the needed files are in the same directory."
    ).place(x=60, y=50)

    # Status label
    status_label = tk.Label(root, text="", fg="green")
    status_label.place(x=60, y=200)

    return status_label

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


# Core Functions

def set_buttons_state(root, state):
    for b in getattr(root, "_dw4_buttons", ()):
        b.config(state=state)

def start_unpack_thread(root, progress, status_label):
    set_buttons_state(root, "disabled")
    set_progress(root, progress, 0, 1, "Preparing…")

    def notify(msg):
        # bounce messages back to the Tk thread
        root.after(0, handle_msg, root, progress, status_label, msg)

    t = threading.Thread(target=unpack_worker, args=(notify,), daemon=True)
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
        _, text = msg
        set_progress(root, progress, 1, 1, text)
        set_buttons_state(root, "normal")

def unpack_worker(notify):
    try:
        notify(("progress", 0, 1, "Preparing…"))

        with open(container_file, "rb") as f1, open(metadata_file, "rb") as f2, open(filename_list, "r") as f3:
            f2.seek(offset_to_metadata)

            total = filecount
            notify(("progress", 0, max(1, total), "Unpacking…"))

            for i in range(filecount):
                metadata_offset = f2.tell()
                total_offset = int.from_bytes(f2.read(4), "little") << 11
                f2.read(4)  # unknown1
                size = int.from_bytes(f2.read(4), "little")
                f2.read(4)  # unknown2

                f1.seek(total_offset)
                file_data = f1.read(size)

                fname = f3.readline().strip()
                file_writer(total_offset, size, file_data, fname, None, metadata_offset.to_bytes(4, "little"))

                # throttle UI updates
                if (i & 31) == 0 or (i + 1) == total:
                    notify(("progress", i + 1, total, None))

        remove_error_file()
        notify(("done", "Unpack complete."))
    except FileNotFoundError:
        notify(("status", f"Missing files. Ensure {container_file}, {metadata_file}, {filename_list} are present.", "red"))
        notify(("done", "Error."))
    except PermissionError:
        notify(("status", "Permission denied for one or more files.", "red"))
        notify(("done", "Error."))
    except IOError as e:
        notify(("status", f"I/O error: {e}", "red"))
        notify(("done", "Error."))
    except Exception as e:
        notify(("status", f"Unexpected error: {e}", "red"))
        notify(("done", "Error."))

def file_writer(offset: int, file_size: int, data: bytes, fname: str, status_label, metadata: bytes):
    """Handles unpacking of a single file"""
    os.makedirs(folder, exist_ok=True)
    file_dir = os.path.dirname(fname)
    file_path = os.path.join(folder, file_dir)
    os.makedirs(file_path, exist_ok=True)

    complete_path = os.path.join(file_path, os.path.basename(fname))
    try:
        with open(complete_path, "wb") as w1:
            w1.write(data + metadata)
        if complete_path.lower().endswith(".pd2"):
            base = os.path.splitext(os.path.basename(complete_path))[0]
            pd2_folder = os.path.join(os.path.dirname(complete_path), base + "_PD2")
            PD2_Unpack(complete_path, pd2_folder)
    except Exception as e:
        error_function(f"Error writing {fname}: {e}", status_label)

def PD2_Unpack(file: str, folder: str):
    """Unpack PD2 container into 'folder' (ignores ANY trailing metadata in the caller)."""
    counter = 0
    the_extension = None
    try:
        # Use the folder directly; do NOT join it with 'file'
        os.makedirs(folder, exist_ok=True)

        sizes = []
        with open(file, "rb") as f1:
            file_count = int.from_bytes(f1.read(4), "little")
            for _ in range(file_count):
                size = int.from_bytes(f1.read(4), "little")
                sizes.append(size << 4)
            pos = f1.tell()
            pad = (-pos) & 0xF
            if pad:
                f1.seek(pad, 1)
            for s in sizes:
                data = f1.read(s)
                counter += 1
                check_header = data[:4]
                short_check = data[:2]
                long_check = data[:10]
                
                if check_header == png_check:
                    the_extension = "png"
                elif short_check == bmp_check:
                    the_extension = "bmp"
                elif jpg_check in long_check:
                    the_extension = "jpg"
                elif check_header == tim2_check:
                    the_extension = "tm2"
                elif check_header == xkm_check:
                    the_extension = "xkm"
                elif check_header == xft_check:
                    the_extension = "xft"
                else:
                    the_extension = "bin"
                with open(os.path.join(folder, f"File_{counter}.{the_extension}"), "wb") as f2:
                    f2.write(data)

    except Exception as e:
        error_function(f"Script failed in PD2_Unpack for {file}: {e}")

# Utility Functions

def error_function(message: str, status_label=None):
    """Handles error management and status updates"""
    try:
        with open(error_file, "a") as w1:
            w1.write(message + "\n")
        if status_label:
            status_label.config(text="An error occurred. See Error.txt for details.", fg="red")
    except Exception as e:
        if status_label:
            status_label.config(text=f"Failed to write to error log: {e}", fg="red")

def remove_error_file():
    """Removes existing error log if present (clean successful run)"""
    if os.path.isfile(error_file):
        os.remove(error_file)


# Main

if __name__ == "__main__":
    GUI()
