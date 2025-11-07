Lightweight, GUI-first modding tools for Dynasty Warriors 4 Hyper. Currently there are unpackers, repackers, a mod creator, mod manager to manage/apply mods. It's written in pure Python/Tkinter with minimal dependencies. Designed to be friendly for both modders and curious players.

Tools included as of November 7 2025:

Linkdata Tools (DW4_Hyper_linkdata_bin.pyw) that unpacks linkdata.bin, unpacks PD2s (mini containers stored within linkdata.bin), repack PD2s, progress UI.
![dw41](https://github.com/user-attachments/assets/44d58576-0303-4937-80f7-1a4bf17f2eff)

Mod Creator (DW4_Hyper_Mod_Creator.pyw) that turns unpacked files you mod from linkdata.bin into single file mods (.DW4HM) or packaged mods (.DW4HP, useful for large scale/batch mods, essentially a custom container I designed to store mods that are meant to contain more than 1 file).
![dw42](https://github.com/user-attachments/assets/9a70708f-c5ee-465e-a4d5-85fe15bc165c)

Mod Manager (DW4_Hyper_Mod_Manager.pyw) that applies/disables mods safely by appending to linkdata.bin on 2048 boundaries at the end of the container file, manages mdata.bin (essentially a metadata file that stores references to files packed within linkdata.bin, like the idx file format of later PC koei tecmo games), keeps a ledger and original backups.
![dw43](https://github.com/user-attachments/assets/8656b729-f04f-4b13-b849-4ab46fc94c4b)

BNS Tools (DW4_Hyper_BNS.pyw) that unpacks/repacks voice BNS (JP/US), it's sector-aligned to 2048 on repack for each file (since PS2 games typically need to be sector aligned, that happens to be the case for DW4 Hyper).
![dw46](https://github.com/user-attachments/assets/c3af9818-ec12-4bd7-8c6e-05833c357c75)

resource.bin Tools (DW4_Hyper_resource_bin.pyw) that unpacks/repacks resource.bin.
![dw45](https://github.com/user-attachments/assets/9256ee0f-3f28-4f74-aef3-d027d812ce33)

Unit Editor (DW4_Hyper_Unit_Editor.pyw), editor for UNITDATA.BIN which stores unit data like parameters (model, weapon model, voice id, motion/moveset, movement speed, jump speed, etc).
![dw44](https://github.com/user-attachments/assets/f611fbbf-156a-47bb-b801-7e14d2af0e75)
