Lightweight, GUI-first modding tools for Dynasty Warriors 4 Hyper. Currently there are unpackers, repackers, a mod creator, mod manager to manage/apply mods. It's written in pure Python/Tkinter with minimal dependencies. Designed to be friendly for both modders and curious players. It's important to read the guide section. If you encounter any issues or have questions, let me know on here or reddit (username on reddit is ThatFlowerGamu).

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

You must have Python 3 installed.

Please backup your linkdata.bin, resource.bin, BNS files, and mdata.bin files before using these tools.

You don't have to have the tools within the same directory, you just need them in the same folder that the files it needs. So if you want to keep things clean, i'd suggest making a "modding" folder, storing the files needed each tool needs (it'll be lsited below) within that folder along with the scripts but it's up to you. All that matters is each script that I list below is paired with its needed files, Unit Editor and Mod Creator are exceptions since they use filedialog but again, your choice. 

Linkdata tools must be within the same directory as linkdata.bin, filenames.ref (a custom text file I made storing filenames for files within linkdata.bin that I found within the executable), mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods).

Mod Manager must be within the same directory as DW4_Hyper.MODS (a custom file designed by my tools, meant to store currently enabled mods), linkdata.bin, mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods).

BNS tools must be within the same directory as the BNS files (your base game stores it within the media\data\sound\voice directory). It'll create 2 files which are voice_jp.ref and voice_us.ref, those are custom metadata files made by the unpacker to support unpacking the Ogg files. To make an audio mod that replaces the Ogg files from the BNS files, you'll probably need the version of LibVorbis that was used for Dynasty Warriors 4 Hyper which I think is 20020717. Once you replace the Ogg files with compartible ogg files you made/chose to use, repack with the repack button.

Resource_bin tools must be within the same directory as the resource.bin file (your base game stores it within the media\data\etc directory).

When you run the repacker button for resource_bin tools, linkdata tools, or BNS tools make sure you only have files you want repacked stored within the folder that will be repacked.

Extra Info:

the mod manager is meant to be used with linkdata.bin which does not use file repacking, it instead injects/appends your mods. resource.bin and the BNS files repack with their own script I made.

I chose to do file repacking for resource.bin and BNS files since they're significantly smaller than linkdata.bin. Your mods/replacements can be any file size, the mod manager and repackers support dynamic file sizes so that means you're not restricted to original file sizes.

To clarify, the game does not have useful (for us) filenames for files stored within PD2 files (mini containers stored within the larger container linkdata.bin). DW4 Hyper also does not have relevant filenames for files stored within BNS files and the resource.bin file.

I've already checked the executable and files, so every file with proper filenames within linkdata.bin is given the correct/relevant filename but files stored within mini containers like PD2 files have incrementing filenames (i.e., title.pd2 is the named container file but the 59 files unpacked from it have no useful filenames like "title.bmp" used by the game so they're being given incrementing filenames with extensions based on the type of file it is). That's not an issue on my part, koei just at the time seemed to name the containers like pd2 files and used a hash name or something else not relevant for each packed file within the PD2 file. Same for resource.bin and BNS files.

So to summarize, if a file is given an incrementing filename it's atleast assigned the proper extension based on the file data but most of the game's assets and things most modders would be interested in modding such as stage/battlefield data, textures, models, etc are within linkdata.bin so it's not a big problem. 

Future Plans:

I'd like to build more GUI file modding tools like the Unit Editor. For example, I'd like to make a stage/battlefield editor, translation tool for translators that want to translate DW4 hyper, item editor, etc.
