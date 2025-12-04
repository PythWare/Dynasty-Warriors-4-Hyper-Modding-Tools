import os, tkinter as tk
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
            
class ModCreator():
    LILAC = "#C8A2C8"
    def __init__(self, root):
        self.root = root
        self.root.configure(bg=self.LILAC)
        self.root.title("Dynasty Warriors 4 Hyper Mod Creator")
        self.root.minsize(700, 700)
        self.root.resizable(False, False)
        self.extension = ".DW4HM" # single file mods
        self.package = ".DW4HP" # multi file mods
        self.mods_file = "DW4_Hyper.MODS" # metadata file storing mods enabled
        self.modname = tk.StringVar()
        self.authorname = tk.StringVar()
        self.version = tk.StringVar()
        self.mod_info = tk.StringVar()
        self.image_paths = []  # up to 3 image paths

        self.create_metadata_file()
        self.gui_labels()
        self.gui_entries()
        self.gui_misc()

    def lilac_label(self, parent, **kw):
        base = dict(bg=self.LILAC, bd=0, relief="flat", highlightthickness=0, takefocus=0)
        base.update(kw)
        return tk.Label(parent, **base)

    def create_metadata_file(self):
        if not os.path.isfile(self.mods_file): # if mod metadata file doesn't exist
            with open(self.mods_file, "a"): # create blank metadata file, used for storing mods enabled
                pass
            
    def gui_labels(self):
        self.lilac_label(self.root, text="Mod Creator for applying mods to DW4 Hyper.").place(x=10, y=10)
        self.lilac_label(self.root, text="Author of Mod:").place(x=10, y=50)
        self.lilac_label(self.root, text="Mod Name(only the name, leave out extension):").place(x=10, y=100)
        self.lilac_label(self.root, text="Version Number for mod:").place(x=10, y=150)
        self.lilac_label(self.root, text="Mod Description:").place(x=10, y=200)
        
    def gui_entries(self):
        tk.Entry(self.root, textvariable=self.authorname).place(x=100, y=50)
        tk.Entry(self.root, textvariable=self.modname).place(x=280, y=100)
        tk.Entry(self.root, textvariable=self.version).place(x=160, y=150)
    
    def gui_misc(self):
        self.status_label = self.lilac_label(self.root, text="", fg="green")
        self.status_label.place(x=10, y=500)

        self.description = tk.Text(self.root, height=20, width=52)
        self.description.place(x=110, y=200)

        btn1 = tk.Button(self.root, text="Create Mod", command=self.create_mod,
                         height=3, width=20)
        btn1.place(x=500, y=50)

        btn2 = tk.Button(self.root, text="Create Mod Package", command=self.create_package,
                         height=3, width=20)
        btn2.place(x=500, y=200)

        # image selection
        btn_img = tk.Button(self.root, text="Select Images (0–3)",
                            command=self.select_images, height=2, width=20)
        btn_img.place(x=500, y=350)

        self.images_label = self.lilac_label(self.root, text="No images selected.")
        self.images_label.place(x=500, y=320)

        ToolTip(btn1, "This button creates a mod file from a file modded, used for single file mods.")
        ToolTip(btn2, "This button creates a package mod file for large mods, used for mods that mod more than 1 file.")

    def select_images(self):
        paths = filedialog.askopenfilenames(
            initialdir=os.getcwd(),
            title="Select up to 3 preview images",
            filetypes=[
                ("Images", "*.png *.gif")
            ]
        )
        if not paths:
            return
        # Hard limit to 3
        self.image_paths = list(paths[:3])
        self.images_label.config(
            text=f"{len(self.image_paths)} image(s) selected."
        )

    def _write_image_section(self, f1):
        """
        Write image_count + size/offset table + image bytes
        Offsets are absolute from start of file
        """
        images = []
        for path in self.image_paths:
            try:
                with open(path, "rb") as imf:
                    images.append(imf.read())
            except Exception:
                # If an image fails to read, just skip it
                continue

        image_count = min(len(images), 3)
        # Write count byte
        f1.write(image_count.to_bytes(1, "little"))

        if image_count == 0:
            return  # nothing more to do

        # Currently just after the count byte
        index_start = f1.tell()
        # Each entry = size (4) + offset (4)
        index_size = image_count * 8
        base_data_offset = index_start + index_size

        current_offset = base_data_offset

        # Write table
        for img in images[:image_count]:
            size = len(img)
            f1.write(size.to_bytes(4, "little"))
            f1.write(current_offset.to_bytes(4, "little"))
            current_offset += size

        # Write image data
        for img in images[:image_count]:
            f1.write(img)
       
    def create_mod(self):
        new_mod = self.modname.get() + self.extension
        self.file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a DW4 Hyper file",
            filetypes=(
                ("Supported Files", "*.*"),
            ))
        
        try:
            # 4 byte file count
            file_count = 1
            if self.file_path:
                new_mod_raw = new_mod.encode("utf-8")
                author_name = self.authorname.get().encode("utf-8")
                version_number = self.version.get().encode("utf-8")
                description_text = self.description.get("1.0", tk.END).strip()
                description_bytes = description_text.encode("utf-8")

                new_mod_raw_len = len(new_mod_raw)
                author_len = len(author_name)
                version_len = len(version_number)
                description_len = len(description_bytes)
                size = os.path.getsize(self.file_path) # size of mod file
                # Write to new mod file
                with open(new_mod, "wb") as f1, open(self.file_path, "rb") as original:
                    # Header (unchanged)
                    f1.write(new_mod_raw_len.to_bytes(1, "little"))
                    f1.write(new_mod_raw)
                    f1.write(file_count.to_bytes(4, "little"))
                    f1.write(author_len.to_bytes(1, "little"))
                    f1.write(author_name)
                    f1.write(version_len.to_bytes(1, "little"))
                    f1.write(version_number)
                    f1.write(description_len.to_bytes(2, "little"))
                    f1.write(description_bytes)

                    # NEW: image section
                    self._write_image_section(f1)

                    # Payload (unchanged format)
                    f1.write(size.to_bytes(4, "little"))
                    file_data = original.read()
                    f1.write(file_data)
                    
                self.status_label.config(text=f"The Mod {new_mod} was created successfully!", fg="green")
                self.image_paths.clear()
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")

    def create_package(self):
        """Handle multi-file mods: header + [size][data] x N (no filenames)."""
        new_mod = (self.modname.get().strip() or "Unnamed") + self.package

        package_path = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Select a folder with the DW4 Hyper mods to be part of a package file"
        )
        if not package_path:  # user canceled
            self.status_label.config(text="Canceled.", fg="red")
            return

        # Collect files in the chosen folder
        files = [f for f in os.listdir(package_path)
                 if os.path.isfile(os.path.join(package_path, f))]

        # 4 byte file count
        file_count = len(files).to_bytes(4, "little")

        try:
            new_mod_raw = new_mod.encode("utf-8")
            author_name = self.authorname.get().encode("utf-8")
            version_number = self.version.get().encode("utf-8")
            description_text = self.description.get("1.0", tk.END).strip()
            description_bytes = description_text.encode("utf-8")

            new_mod_raw_len = len(new_mod_raw)
            author_len = len(author_name)
            version_len = len(version_number)
            description_len = len(description_bytes)

            with open(new_mod, "wb") as f1:
                # Header
                f1.write(new_mod_raw_len.to_bytes(1, "little"))
                f1.write(new_mod_raw)
                f1.write(file_count)
                f1.write(author_len.to_bytes(1, "little"))
                f1.write(author_name)
                f1.write(version_len.to_bytes(1, "little"))
                f1.write(version_number)
                f1.write(description_len.to_bytes(2, "little"))
                f1.write(description_bytes)

                # NEW: image section (applies to whole package)
                self._write_image_section(f1)

                # Payload (unchanged format)
                for fname in files:
                    full_path = os.path.join(package_path, fname)
                    size = os.path.getsize(full_path)
                    f1.write(size.to_bytes(4, "little"))
                    with open(full_path, "rb") as original:
                        f1.write(original.read())

            self.status_label.config(
                text=f"The Mod Package {new_mod} was created successfully.", fg="green"
            )
            self.image_paths.clear()

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")

                    
def runner():
    root = tk.Tk()
    creator = ModCreator(root)
    root.mainloop()
if __name__ == "__main__":
    runner()
