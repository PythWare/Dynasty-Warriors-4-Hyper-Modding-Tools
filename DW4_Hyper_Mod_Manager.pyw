import os, base64, shutil
import tkinter as tk
from tkinter import filedialog

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")  # Get position
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # No window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ModManager():
    LILAC = "#C8A2C8"
    def __init__(self, root):
        self.root = root
        self.root.configure(bg=self.LILAC)
        self.root.title("Dynasty Warriors 4 Hyper Mod Manager")
        self.root.minsize(1700, 800)
        self.root.resizable(False, False)

        # Files
        self.backups = "Backups_Folder"
        self.mods_enabled_file = "DW4_Hyper.MODS"
        self.main_container = "linkdata.BIN"      # payload container
        self.metadata_container = "mdata.bin"     # metadata container
        self.original_metadata_container = "original_mdata.bin" # used to retrieve original values for mods being disabled

        # State
        self.modname = None
        self.package_entries = []   # data_padded, size_real, taildata
        self.mod_size = None
        self.mod_data = None
        self.taildata = None
        self.original_container_size = 1086416896 # original unmodded size of linkdata.bin, will be used for truncating
        self.SECTOR = 0x800
        self.mod_images = []         # list for photos
        self.current_image_index = 0

        # GUI
        self.gui_labels()
        self.gui_misc()
        self.current_mods()
        self._clear_images()

        if not os.path.exists(self.original_metadata_container):
            self.status_label.config(
                text=f"Warning: {self.original_metadata_container} not found. Disables will fall back to ledger values.",
                fg="red"
            )

    # GUI
    def lilac_label(self, parent, **kw):
        base = dict(bg=self.LILAC, bd=0, relief="flat", highlightthickness=0, takefocus=0)
        base.update(kw)
        return tk.Label(parent, **base)

    def gui_labels(self):
        self.lilac_label(self.root, text="Mod Manager for applying and disabling mods to DW4 Hyper.").place(x=10, y=10)
        self.lilac_label(self.root, text="Mod Name:").place(x=10, y=50)
        self.lilac_label(self.root, text="Mod Author:").place(x=10, y=100)
        self.lilac_label(self.root, text="Mod Version:").place(x=10, y=150)
        self.lilac_label(self.root, text="Mod Description:").place(x=10, y=200)
        self.lilac_label(self.root, text="Current Mods Enabled:").place(x=570, y=200)

        self.mod_file = self.lilac_label(self.root, text="No mod selected.")
        self.mod_file.place(x=100, y=50)
        self.mod_author = self.lilac_label(self.root, text="")
        self.mod_author.place(x=100, y=100)
        self.mod_version = self.lilac_label(self.root, text="")
        self.mod_version.place(x=100, y=150)

    def gui_misc(self):
        self.status_label = self.lilac_label(self.root, text="", fg="green")
        self.status_label.place(x=10, y=700)

        self.description = tk.Text(self.root, wrap=tk.WORD, height=20, width=52)
        self.description.place(x=110, y=200)
        self.description.config(state=tk.DISABLED)

        btn1 = tk.Button(self.root, text="Select a Mod", command=self.mod_reader,
                         height=3, width=20)
        btn1.place(x=500, y=100)
        ToolTip(btn1, "Read a .DW4HM or .DW4HP and show its description.")

        self.apply_btn = tk.Button(self.root, text="Apply Mod", command=self.mod_writer,
                                   height=3, width=20)
        self.apply_btn.place(x=700, y=100)
        ToolTip(self.apply_btn, "Append payload to linkdata.bin and update mdata.bin.")

        self.disable_btn = tk.Button(self.root, text="Disable Mod", command=self.disable_mod,
                                     height=3, width=20)
        self.disable_btn.place(x=900, y=100)
        ToolTip(self.disable_btn, "Restore original base/size for the selected mod name.")

        btn4 = tk.Button(self.root, text="Disable All Mods (metadata restore)",
                         command=self.disable_mods, height=3, width=40)
        btn4.place(x=100, y=600)
        ToolTip(btn4, "Restores mdata.bin entries for all tracked mods and clears the ledger.")

        # image preview
        self.image_label = tk.Label(self.root, bg=self.LILAC, bd=1, relief="sunken")
        self.image_label.place(x=1100, y=200, width=500, height=500)

        self.prev_img_btn = tk.Button(self.root, text="<", command=self.show_prev_image, width=3)
        self.prev_img_btn.place(x=1300, y=725)

        self.next_img_btn = tk.Button(self.root, text=">", command=self.show_next_image, width=3)
        self.next_img_btn.place(x=1370, y=725)

        self.mods_list = tk.Listbox(height=20, width=52)
        self.mods_list.place(x=700, y=200)

        # helpers
    def _sync_metadata_to_game(self) -> bool:
        """
        Copy the working mdata.bin (self.metadata_container) into the game's
        mdata.bin location

        Tries a couple of common layouts based on the current working directory:
          <cwd>/media/data/etc/mdata.bin
          <cwd>/data/etc/mdata.bin

        Returns True if at least one copy succeeded, False otherwise
        """
        try:
            src = self.metadata_container
            if not os.path.exists(src):
                return False

            root = os.getcwd()
            candidates = [
                os.path.join(root, "media", "data", "etc", "mdata.bin"),
                os.path.join(root, "data", "etc", "mdata.bin"),
            ]

            copied = False
            for dst in candidates:
                dst_dir = os.path.dirname(dst)
                if os.path.isdir(dst_dir):
                    shutil.copy2(src, dst)
                    copied = True

            return copied
        except Exception:
            return False

    def _write_padding(self, f, boundary=2048):
        current = f.tell()
        pad = (-current) % boundary
        if pad:
            f.write(b"\x00" * pad)
            current += pad
        return current

    def _pad_to_sector_2048(self, f, size_real: int):
        pad = (-size_real) & (self.SECTOR - 1)
        if pad:
            f.write(b"\x00" * pad)

    def _finalize_archive(self):
        with open(self.main_container, "r+b") as f:
            f.seek(0, os.SEEK_END)
            pad = (-f.tell()) & (self.SECTOR - 1)
            if pad:
                f.write(b"\x00" * pad)

    def _clear_images(self):
        self.mod_images = []
        self.current_image_index = 0
        self.image_label.config(image="", text="No image", compound="center")

    def _show_image(self):
        if not self.mod_images:
            self._clear_images()
            self.prev_img_btn.config(state=tk.DISABLED)
            self.next_img_btn.config(state=tk.DISABLED)
            return
        self.current_image_index %= len(self.mod_images)
        img = self.mod_images[self.current_image_index]
        self.image_label.config(image=img, text="", compound="center")
        # Enable/disable arrows
        if len(self.mod_images) <= 1:
            self.prev_img_btn.config(state=tk.DISABLED)
            self.next_img_btn.config(state=tk.DISABLED)
        else:
            self.prev_img_btn.config(state=tk.NORMAL)
            self.next_img_btn.config(state=tk.NORMAL)

    def show_next_image(self):
        if not self.mod_images:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.mod_images)
        self._show_image()

    def show_prev_image(self):
        if not self.mod_images:
            return
        self.current_image_index = (self.current_image_index - 1) % len(self.mod_images)
        self._show_image()

    def _restore_entry_from_original(self, tail: int) -> bool:
        """
        Copy the original 16 byte metadata chunk (base, unk1, size, unk2)
        from self.original_metadata_container at `tail` into self.metadata_container
        Returns True on success, False if the original file is missing or invalid
        """
        try:
            if not os.path.exists(self.original_metadata_container):
                return False
            with open(self.original_metadata_container, "rb") as orig:
                orig.seek(tail)
                chunk = orig.read(16)
                if len(chunk) != 16:
                    return False
            with open(self.metadata_container, "r+b") as cur:
                cur.seek(tail)
                cur.write(chunk)
            return True
        except Exception:
            return False

    def _read_images_from_mod(self, f1):
        """
        Read image_count + size/offset table + image bytes from the file like f1
        Leaves f1 positioned at the start of the payload

        If the first byte after description looks like a legacy size byte (>3),
        fall back to old format and leave f1 positioned so payload parsing still works
        """
        self._clear_images()

        # position is directly after description bytes
        start_after_desc = f1.tell()

        count_byte = f1.read(1)
        if not count_byte:
            # no data, treat as legacy
            f1.seek(start_after_desc)
            return

        image_count = int.from_bytes(count_byte, "little")

        # Legacy mod (no image section): this byte is actually the first size byte
        if image_count > 3:
            # rewind to treat it as legacy
            f1.seek(start_after_desc)
            return

        if image_count == 0:
            # no images, payload starts right here
            return

        entries = []
        for _ in range(image_count):
            size = int.from_bytes(f1.read(4), "little")
            offset = int.from_bytes(f1.read(4), "little")
            entries.append((size, offset))

        # Read images
        imgs_bytes = []
        for size, offset in entries:
            f1.seek(offset)
            data = f1.read(size)
            if data:
                imgs_bytes.append(data)

        # Compute where payload starts: after last image
        if entries:
            last_size, last_offset = entries[-1]
            payload_offset = last_offset + last_size
            f1.seek(payload_offset)
        else:
            # shouldn't happen but to be safe
            f1.seek(start_after_desc + 1 + 8 * image_count)

        # Build PhotoImage objects from bytes (base64)
        self.mod_images = []
        for data in imgs_bytes:
            try:
                b64 = base64.b64encode(data)
                img = tk.PhotoImage(data=b64)
                self.mod_images.append(img)
            except Exception:
                # If Tk can't decode this image, skip it
                continue

        self.current_image_index = 0
        self._show_image()

    # Reading mods
    def mod_reader(self):
        """Handles mod file/package reading"""
        self.file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a DW4 Hyper Mod file",
            filetypes=[("Single Mod", "*.DW4HM"), ("Package Mod", "*.DW4HP")]
        )
        try:
            if not self.file_path:
                return

            filename = os.path.basename(self.file_path)
            self.modname = filename
            self.mod_file.config(text=filename)

            # If this mod is already enabled, don't load/apply again
            if self.is_mod_enabled(self.modname):
                self.status_label.config(text=f"'{self.modname}' is already enabled. Disable it first to reapply.", fg="blue")
                # select it in the listbox if present
                try:
                    for i in range(self.mods_list.size()):
                        if self.mods_list.get(i).strip().lower() == self.modname.strip().lower():
                            self.mods_list.selection_clear(0, tk.END)
                            self.mods_list.selection_set(i)
                            self.mods_list.see(i)
                            break
                except Exception:
                    pass
                # prevent accidental apply
                self.apply_btn.config(state=tk.DISABLED)
                return
            else:
                self.apply_btn.config(state=tk.NORMAL)

            with open(self.file_path, "rb") as f1:
                # shared header
                mod_name_len = int.from_bytes(f1.read(1), "little")
                f1.read(mod_name_len)  # skip stored display name
                file_count = int.from_bytes(f1.read(4), "little")
                author_len = int.from_bytes(f1.read(1), "little")
                author_data = f1.read(author_len).decode()
                version_len = int.from_bytes(f1.read(1), "little")
                version_data = f1.read(version_len).decode()
                description_len = int.from_bytes(f1.read(2), "little")
                description = f1.read(description_len).decode()

                # Show details
                self.mod_author.config(text=author_data)
                self.mod_version.config(text=version_data)
                self.description.config(state=tk.NORMAL)
                self.description.delete("1.0", tk.END)
                self.description.insert(tk.END, description)
                self.description.config(state=tk.DISABLED)

                # read image section
                self._read_images_from_mod(f1)

                # package vs single
                is_package = self.file_path.lower().endswith(".dw4hp")
                self.package_entries = []
                self.mod_data = None
                self.mod_size = None
                self.taildata = None

                if not is_package:
                    size = int.from_bytes(f1.read(4), "little")
                    raw = f1.read(size)
                    data, tail = raw[:-4], raw[-4:]
                    size_real = len(data)
                    self.mod_data = data
                    self.mod_size = size_real
                    self.taildata = int.from_bytes(tail, "little")
                else:
                    for _ in range(file_count):
                        size = int.from_bytes(f1.read(4), "little")
                        raw = f1.read(size)
                        data, tail = raw[:-4], raw[-4:]
                        size_real = len(data)
                        self.package_entries.append((data, size_real, int.from_bytes(tail, "little")))

            self.status_label.config(text="Mod loaded.", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")

    # Tracking .MODS
    def _track_entry(self, mod_name: str, taildata: int, write_name: bool = True):
        """Append one tracking record. If write_name=False, write a 0 name-len byte so readers inherit the last name"""
        # Read original values from mdata at taildata
        with open(self.metadata_container, "rb") as f:
            f.seek(taildata)
            original_base = int.from_bytes(f.read(4), "little")
            f.seek(4, 1)  # skip unk1
            original_size = int.from_bytes(f.read(4), "little")

        with open(self.mods_enabled_file, "ab") as w:
            if write_name:
                name_bytes = mod_name.encode("utf-8")
                w.write(len(name_bytes).to_bytes(1, "little"))
                w.write(name_bytes)
            else:
                # zero length = inherit last non-empty name
                w.write((0).to_bytes(1, "little"))
            w.write(taildata.to_bytes(4, "little"))
            w.write(original_base.to_bytes(4, "little"))
            w.write(original_size.to_bytes(4, "little"))

    # Applying mods
    def mod_writer(self):
        """Apply mod(s): 2048-align each write, update mdata per entry, refresh UI, clear temp state"""
        
        try:
            # Prevent duplicate applies by NAME only (even if metadata already restored differently)
            if self.modname and self.is_mod_enabled(self.modname):
                self.status_label.config(text=f"'{self.modname}' is already enabled. Disable it first to reapply.", fg="blue")
                return

            if self.mod_data is None and not self.package_entries:
                self.status_label.config(text="No mod loaded.", fg="red")
                return

            def append_one(data: bytes, size_real: int, taildata: int, write_name: bool):
                # Step 1, Append to linkdata.bin at a 2048 boundary
                with open(self.main_container, "r+b") as a1:
                    a1.seek(0, os.SEEK_END)
                    current_offset = self._write_padding(a1, 2048)
                    a1.write(data)
                    # Step 2, Tail pad so EOF is sector-rounded
                    self._pad_to_sector_2048(a1, size_real)
                # Step 3 Track BEFORE overwriting metadata
                self._track_entry(self.modname, taildata, write_name=write_name)
                # 3) Update mdata.bin
                base_offset = current_offset >> 11
                with open(self.metadata_container, "r+b") as f1:
                    f1.seek(taildata)
                    f1.write(base_offset.to_bytes(4, "little"))
                    f1.seek(4, 1)  # skip unk1
                    f1.write(size_real.to_bytes(4, "little"))
                    f1.seek(4, 1)  # skip unk2

            if self.package_entries:
                for idx, (data_padded, size_real, taildata) in enumerate(self.package_entries):
                    append_one(data_padded, size_real, taildata, write_name=(idx == 0))
            else:
                append_one(self.mod_data, self.mod_size, self.taildata, write_name=True)

            # Success + refresh
            self.status_label.config(text="Mod(s) applied successfully.", fg="green")
            self.current_mods()
            # if we just applied this mod, ensure Apply button is disabled on re-select
            self.apply_btn.config(state=tk.NORMAL)

            # clear temporary state
            self.package_entries.clear()
            self.mod_data = None
            self.mod_size = None
            self.taildata = None
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            
        self._finalize_archive()
        # Sync mdata.bin to the game's directory
        sync_ok = self._sync_metadata_to_game()
        if sync_ok:
            self.status_label.config(
                text="Mod(s) applied successfully and mdata.bin synced to game folder.",
                fg="green"
            )
        else:
            # Keep mods applied, but warn that the game-side mdata wasn't found
            self.status_label.config(
                text=f"Mod(s) applied, but game's mdata.bin directory (media\\data\\etc) not found in {os.getcwd()}. You'll need to \ncopy/paste mdata.bin manually.",
                fg="red"
            )

    # Ledger readers
    def _iter_mod_ledger(self, want_positions=False):
        """Yield records from DW4_Hyper.MODS"""
        if not os.path.exists(self.mods_enabled_file):
            return
        last_name = None
        with open(self.mods_enabled_file, "rb") as f:
            while True:
                start = f.tell()
                b = f.read(1)
                if not b:
                    break
                nlen = int.from_bytes(b, "little")
                if nlen > 0:
                    last_name = f.read(nlen).decode("utf-8")
                tail = int.from_bytes(f.read(4), "little")
                obase = int.from_bytes(f.read(4), "little")
                osize = int.from_bytes(f.read(4), "little")
                end = f.tell()
                if want_positions:
                    yield (last_name, tail, obase, osize, start, end, nlen)
                else:
                    yield (last_name, tail, obase, osize)

    # UI: list current mods
    def current_mods(self):
        try:
            self.mods_list.delete(0, tk.END)
            seen = set()
            for name, tail, obase, osize in self._iter_mod_ledger():
                if name and name not in seen:
                    self.mods_list.insert(tk.END, name)
                    seen.add(name)
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

    # Enabled checks
    def is_mod_enabled(self, mod_name: str) -> bool:
        """True if the mod name exists in the ledger (name-only check)"""
        try:
            target = (mod_name or "").strip().lower()
            if not target:
                return False
            for name, *_ in self._iter_mod_ledger():
                if name and name.strip().lower() == target:
                    return True
            return False
        except Exception:
            return False

    def check_if_applied(self, mod_name: str) -> bool:
        """Return True if any record in the ledger resolves to mod_name (case-insensitive)"""
        try:
            match = False
            for name, *_ in self._iter_mod_ledger():
                if name and name.strip().lower() == mod_name.strip().lower():
                    match = True
                    break
            if not match:
                self.status_label.config(
                    text=f"'{mod_name}' not found in {self.mods_enabled_file}.", fg="red"
                )
            return match
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            return False

    def clean_mods(self, kept_bytes: bytes):
        """Rewrite the ledger to an exact byte stream (kept_bytes), then refresh list"""
        try:
            with open(self.mods_enabled_file, "wb") as f1:
                f1.write(kept_bytes)
            self.current_mods()
            return True
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            return False

    def update_mods(self, mod_name: str):
        """Remove all records for mod_name from the ledger and compact it"""
        try:
            kept = bytearray()
            for name, tail, obase, osize, start, end, nlen in self._iter_mod_ledger(want_positions=True):
                # keep record if it doesn't belong to target mod
                if not (name and name.strip().lower() == mod_name.strip().lower()):
                    # Re-emit record as read (preserve 0-len continuation or named entry)
                    with open(self.mods_enabled_file, "rb") as f:
                        f.seek(start)
                        kept.extend(f.read(end - start))
            self.clean_mods(bytes(kept))
            return True
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")
            return False

    # Disabling
    def disable_mod(self):
        """Disable the selected mod from the list (restore metadata for all its entries)"""
        try:
            sel = self.mods_list.curselection()
            if not sel:
                self.status_label.config(text="Select a mod name in the list first.", fg="red")
                return
            mod_name = self.mods_list.get(sel[0])
            if not self.check_if_applied(mod_name):
                return

            # Restore metadata for all matching records and rebuild ledger without them
            kept = bytearray()
            restored_any = False
            for name, tail, obase, osize, start, end, nlen in self._iter_mod_ledger(want_positions=True):
                if name and name.strip().lower() == mod_name.strip().lower():
                    ok = self._restore_entry_from_original(tail)
                    if not ok:
                        # Fallback to values stored in the ledger if original is missing
                        with open(self.metadata_container, "r+b") as m:
                            m.seek(tail)
                            m.write(obase.to_bytes(4, "little"))
                            m.seek(4, 1)
                            m.write(osize.to_bytes(4, "little"))
                            m.seek(4, 1)
                    # mark success for either path
                    restored_any = True
                else:
                    with open(self.mods_enabled_file, "rb") as f:
                        f.seek(start)
                        kept.extend(f.read(end - start))


            with open(self.mods_enabled_file, "wb") as out:
                out.write(kept)

            if restored_any:
                self.status_label.config(
                    text=f"Disabled '{mod_name}' and restored original metadata.",
                    fg="blue"
                )
                # Sync mdata.bin to the game's directory
                sync_ok = self._sync_metadata_to_game()
                if not sync_ok:
                    self.status_label.config(
                        text=self.status_label.cget("text") +
                             f" Warning: game's mdata.bin directory (data\\etc) not found in {os.getcwd()}, you'll need to \ncopy/paste mdata.bin manually to media\\data\\etc",
                        fg=self.status_label.cget("fg")
                    )
            else:
                self.status_label.config(text=f"'{mod_name}' not found in ledger.", fg="red")

            self.current_mods()
            self.apply_btn.config(state=tk.NORMAL)

        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

    def disable_mods(self):
        """Restore metadata for ALL records and clear the ledger."""
        try:
            for name, tail, obase, osize in self._iter_mod_ledger():
                ok = self._restore_entry_from_original(tail)
                if not ok:
                    # Fallback if original not present / invalid
                    with open(self.metadata_container, "r+b") as m:
                        m.seek(tail)
                        m.write(obase.to_bytes(4, "little"))
                        m.seek(4, 1)
                        m.write(osize.to_bytes(4, "little"))
                        m.seek(4, 1)
                        
            if os.path.getsize(self.main_container) > self.original_container_size:
                with open(self.main_container, "r+b") as f:
                    f.truncate(self.original_container_size)

                        # clear ledger
            open(self.mods_enabled_file, "wb").close()
            self.mods_list.delete(0, tk.END)
            self.status_label.config(
                text="All mods disabled (mdata.bin & linkdata.bin restored to unmodded copies.",
                fg="blue"
            )

            # Sync mdata.bin to the game's directory
            sync_ok = self._sync_metadata_to_game()
            if not sync_ok:
                self.status_label.config(
                    text=self.status_label.cget("text") +
                         f" Warning: game's mdata.bin directory (data\\etc) not found in {os.getcwd()}, you'll need to \ncopy/paste mdata.bin manually to media\\data\\etc",
                    fg=self.status_label.cget("fg")
                )

        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

# Runner
def runner():
    root = tk.Tk()
    manager = ModManager(root)
    root.mainloop()

if __name__ == "__main__":
    runner()

