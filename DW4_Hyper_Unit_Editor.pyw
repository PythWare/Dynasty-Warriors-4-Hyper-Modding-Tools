import os
import tkinter as tk
from tkinter import ttk, filedialog

RECORD_SIZE = 24
HEADER_SIZE = 4
LILAC = "#C8A2C8"

def setup_lilac_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")  # clam respects bg colors nicely
    except tk.TclError:
        pass
    style.configure("Lilac.TFrame",  background=LILAC)
    style.configure("Lilac.TLabel",  background=LILAC, foreground="black", padding=0)
    style.map("Lilac.TLabel", background=[("active", LILAC)])
    
class UnitEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("DW4 Hyper Unit Data Editor")
        self.root.geometry("860x600")
        self.root.resizable(False, False)

        setup_lilac_styles()
        
        # State
        self.bin_path = ""  # set via Open
        self.slot_hex_values = [f"0x{n:X}" for n in range(0x200)]
        self._build_ui()

    # UI
    def _build_ui(self):
         # Full-window lilac background for labels
        self.bg = ttk.Frame(self.root, style="Lilac.TFrame")
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        # Top bar: Open + selected file label
        open_btn = ttk.Button(self.root, text="Open UNITDATA.BIN", command=self.ask_file)
        open_btn.place(x=20, y=20)

        self.file_label = ttk.Label(self.bg, text="No file selected.", style="Lilac.TLabel")
        self.file_label.place(x=180, y=24)

        ttk.Label(self.bg, text="Slot (hex):", style="Lilac.TLabel").place(x=20, y=60)
        self.slot_cb = ttk.Combobox(self.root, values=self.slot_hex_values, state="readonly", width=10)
        self.slot_cb.place(x=100, y=58)
        self.slot_cb.bind("<<ComboboxSelected>>", self._on_slot_change)
        self.slot_cb.current(0)  # default 0x0

        # Button

        self.write_btn = ttk.Button(self.root, text="Write Data", command=self.submit_unit, width=14)
        self.write_btn.place(x=220, y=56)

        # Status line
        self.status_label = ttk.Label(self.bg, text="", style="Lilac.TLabel", foreground="green")
        self.status_label.place(x=20, y=560)

        # Field labels and spinboxes
        # Order must match file binary layout (after 2 byte Name)
        self.labels = [
            "Name (2 bytes)",      # 0
            "Unknown 1",           # 1
            "Voice",               # 2
            "Model",               # 3
            "Unknown 2",           # 4
            "Moveset",             # 5
            "Unknown 3",           # 6
            "Unknown 4",           # 7
            "Unknown 5",           # 8
            "Unknown 6",           # 9
            "Unknown 7",           #10
            "Unknown 8",           #11
            "Unknown 9",           #12
            "Movement Speed",      #13
            "Unknown 10",          #14
            "Jump Height",         #15
            "Unknown 11",          #16
            "Unknown 12",          #17
            "Unknown 13",          #18
            "Unknown 14",          #19
            "Weapon",              #20
            "Unknown 15",          #21
            "Unknown 16",          #22
        ]

        # Spinboxes
        # Name is 0-65535 (2 bytes), others are 0-255 (1 byte)
        self.spin_widgets = []
        left_x_label, left_x_box = 20, 170
        right_x_label, right_x_box = 440, 590
        row_h = 26
        top_y = 110

        for i, label_text in enumerate(self.labels):
            if i <= 11:  # first 12 labels left column
                y = top_y + i * row_h
                ttk.Label(self.bg, text=label_text, style="Lilac.TLabel").place(x=left_x_label, y=y+2)
                if i == 0:
                    sb = ttk.Spinbox(self.root, from_=0, to=65535, increment=1, width=8, wrap=False)
                else:
                    sb = ttk.Spinbox(self.root, from_=0, to=255, increment=1, width=6, wrap=True)
                sb.place(x=left_x_box, y=y)
            else:        # remaining labels right column
                y = top_y + (i-12) * row_h
                ttk.Label(self.bg, text=label_text, style="Lilac.TLabel").place(x=right_x_label, y=y+2)
                sb = ttk.Spinbox(self.root, from_=0, to=255, increment=1, width=6, wrap=True)
                sb.place(x=right_x_box, y=y)
            self.spin_widgets.append(sb)

    # Helpers
    def _slot_index(self) -> int:
        """Get selected slot as an int by combobox index (values are sequential)."""
        idx = self.slot_cb.current()
        return 0 if idx is None or idx < 0 else idx

    def _slot_offset(self, slot_index: int) -> int:
        """Compute record offset in file."""
        return HEADER_SIZE + slot_index * RECORD_SIZE

    # Spinbox helpers
    def _set_sb(self, sb: ttk.Spinbox, value: int):
        sb.delete(0, tk.END)
        sb.insert(0, str(value))

    def _b(self, sb: ttk.Spinbox) -> int:
        """Read a 1 byte field, clamped to 0-255."""
        s = sb.get().strip()
        try:
            v = int(s)
        except Exception:
            v = 0
        return 0 if v < 0 else 255 if v > 255 else v

    def _w(self, sb: ttk.Spinbox) -> int:
        """Read a 2 byte field, clamped to 0-65535."""
        s = sb.get().strip()
        try:
            v = int(s)
        except Exception:
            v = 0
        return 0 if v < 0 else 65535 if v > 65535 else v

    # File picking
    def ask_file(self):
        path = filedialog.askopenfilename(
            title="Select UNITDATA.BIN",
            initialdir=os.getcwd(),
            filetypes=[("BIN files", "*.BIN"), ("All files", "*.*")]
        )
        if not path:
            self.status_label.config(text="No file selected.", foreground="orange")
            return
        self.bin_path = path
        self.file_label.config(text=os.path.basename(path))
        # Show slot 0 immediately
        self.slot_cb.current(0)
        self.read_current_slot()

    # Read/Write
    def _on_slot_change(self, _event=None):
        if not self.bin_path:
            self.status_label.config(text="Open a BIN file first.", foreground="red")
            return
        self.read_current_slot()

    def read_current_slot(self):
        """Read currently selected slot and populate the spinboxes."""
        if not self.bin_path:
            self.status_label.config(text="Open a BIN file first.", foreground="red")
            return
        try:
            slot = self._slot_index()
            off = self._slot_offset(slot)

            with open(self.bin_path, "rb") as f:
                # If file is too small, show zeros (don't auto grow on read)
                f.seek(0, os.SEEK_END)
                size = f.tell()
                if size < off + RECORD_SIZE:
                    # Not enough data for this slot, fill defaults
                    values = [0] * 23
                else:
                    f.seek(off)
                    # Read the 24 bytes and unpack (2 byte name + 22 bytes)
                    name = int.from_bytes(f.read(2), "little")
                    rest = list(f.read(22))
                    values = [name] + rest  # name first, then 22 bytes

            # Populate spinboxes
            for sb, val in zip(self.spin_widgets, values):
                self._set_sb(sb, val)

            self.status_label.config(
                text=f"Loaded slot {self.slot_hex_values[slot]} @ 0x{off:X}", foreground="green"
            )

        except Exception as e:
            self.status_label.config(text=f"Error reading: {e}", foreground="red")

    def submit_unit(self):
        """Write current spinbox values to the selected slot."""
        if not self.bin_path:
            self.status_label.config(text="Open a BIN file first.", foreground="red")
            return
        try:
            slot = self._slot_index()
            off = self._slot_offset(slot)

            # Build the 24 bytes: 2 byte name + 22 single bytes
            name = self._w(self.spin_widgets[0]).to_bytes(2, "little")
            bvals = [self._b(sb) for sb in self.spin_widgets[1:]]  # 22 bytes
            if len(bvals) != 22:
                raise ValueError("Internal field count mismatch.")

            record = name + bytes(bvals)  # total 24 bytes

            # If file is smaller than needed, extend with zeros
            need_size = off + RECORD_SIZE
            cur_size = os.path.getsize(self.bin_path)
            if cur_size < need_size:
                with open(self.bin_path, "ab") as fext:
                    fext.write(b"\x00" * (need_size - cur_size))

            # Write record
            with open(self.bin_path, "r+b") as f:
                f.seek(off)
                f.write(record)

            self.status_label.config(
                text=f"Saved slot {self.slot_hex_values[slot]} @ 0x{off:X}", foreground="green"
            )

        except Exception as e:
            self.status_label.config(text=f"Error writing: {e}", foreground="red")


def main():
    root = tk.Tk()
    editor = UnitEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
