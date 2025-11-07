Lightweight, GUI-first modding tools for Dynasty Warriors 4 Hyper. Currently there are unpackers, repackers, a mod creator, mod manager to manage/apply mods. It's written in pure Python/Tkinter with minimal dependencies. Designed to be friendly for both modders and curious players. It's important to read the guide section and Extra info & tips. If you encounter any issues or have questions, let me know on here or reddit (username on reddit is ThatFlowerGamu).

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

Guide Section:

1. You must have Python 3 installed.

2. Please backup your linkdata.bin, resource.bin, BNS files, and mdata.bin files before using these tools.

3. You don't have to have the tools within the same directory, you just need them in the same folder with the files it needs. So if you want to keep things clean, i'd suggest making a "modding" folder, storing the files needed each tool needs (it'll be listed below) within that folder along with the scripts but it's up to you. All that matters is each script that I list below is paired with its needed files, Unit Editor and Mod Creator are exceptions since they use filedialog but again, your choice. 

4. Linkdata tools must be within the same directory as linkdata.bin, filenames.ref (a custom text file I made storing filenames for files within linkdata.bin that I found within the executable), mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods).

5. Mod Manager must be within the same directory as DW4_Hyper.MODS (a custom file designed by my tools, meant to store currently enabled mods), linkdata.bin, mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods).

6. BNS tools must be within the same directory as the BNS files (your base game stores it within the media\data\sound\voice directory). It'll create 2 files which are voice_jp.ref and voice_us.ref, those are custom metadata files made by the unpacker to support unpacking the Ogg files. To make an audio mod that replaces the Ogg files from the BNS files, you'll probably need the version of LibVorbis that was used for Dynasty Warriors 4 Hyper which I think is 20020717. Once you replace the Ogg files with compartible ogg files you made/chose to use, repack with the repack button.

7. Resource_bin tools must be within the same directory as the resource.bin file (your base game stores it within the media\data\etc directory).

8. When you run the repacker button for resource_bin tools, linkdata tools, or BNS tools make sure you only have files you want repacked stored within the folder that will be repacked.

Notes on filenames:

DW4 Hyper often stores useful names for container files (e.g., title.pd2) but not for files inside PD2/BNS/resource.bin containers.

For internal entries (files stored within a PD2, BNS, resource.bin container that are unpacked), tools assign incrementing filenames with a correct extension based on content.

Most interesting mod content (stages, units, textures, models, etc) lives in linkdata.bin, so this is rarely a blocker.

Extra info & tips

Every file unpacked from linkdata.bin is given an additional 4 bytes called "taildata" at the end of the file, you must not remove it. It's used for the mod manager for applying/disabling mods. You can mod files unpacked that have taildata but please keep the last 4 bytes unchanged unless you know what you're doing since the mod manager relies on taildata. The taildata does not impact the usablity of files, it's purely used for mod manager.

I've only been reverse engineering Dynasty Warriors 4 Hyper for a week or so (as of November 7 2025), so if you have any knowledge of stuff like stage/battlefield data, item data, values, etc and would like to help then it would speed up the process of developing more GUI tools since anything without documentation (which is the case for DW4 Hyper, i reversed it without existing documentation) I have to manually reverse. So the less time I have to spend reversing file formats that someone else may already know, the sooner I can build more editors. If you share any knowledge/documentation, I will credit you. I want to have GUI modder and non-modder friendly tools that make modding easy. Not everyone has hours to spend learning modding so having easy to use tools is essential to me.

The Mod Manager is purpose-built for linkdata.bin. resource.bin and BNS use their own repackers.

Mods can be any size; tools handle dynamic sizes (no “original size” constraint).

For BNS audio, DW4 Hyper used an early Vorbis (libVorbis I 20020717). Use compatible Oggs for best results.

Roadmap:

More GUI editors (stages/battlefields, translation, items, etc.).
