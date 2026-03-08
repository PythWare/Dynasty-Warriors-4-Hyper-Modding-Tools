# Update as of 3/7/2026

I am going to redesign the tools for Dynasty Warriors 4 Hyper, new GUI and code logic will be released in version 2.0. It's going to be as high end as Katsuki Engine and Aldnoah Engine, stay tuned.

# Upcoming 2.0 Version

While not ready to release yet, here are sneak peaks of 2.0 of DW4 Hyper Modding Tools.

The new Mod Manager is meant to compete with the Constellation Mod Manager I created for Aldnoah Engine but reimagined for DW4 Hyper with a full ocean/fleet theme. Instead of a plain list based interface, mods are represented as ships on a navigable sea. Enabled mods dock in the Harbor, available mods sail in open Waters, and invalid or damaged mods sink into the Reef. Selecting a ship opens its manifest showing metadata, description, and preview images in a preview bay. The manager is not just a visual redesign, it now includes a scrollable/zoomable ocean, ship based mod selection, search and filtering, persistent mod library support through Mods_Folder, signature validation for proper DW4 Hyper mod formats, and clearer status handling for enabled, available, and invalid packages. It presents everything through a more premium high end interface designed to make managing DW4 Hyper mods feel like commanding a fleet rather than clicking through a utility.

Mod Creator matches the Aquatic Mod Manager visually/functionally instead of being a basic utility window. Single file mods/package mods now have dedicated source selection controls, you can choose a single payload file in advance or choose a package folder ahead of time rather than doing everything through sudden popups during creation, mods no longer have to be written only to the current working folder, the creator now lets you choose and open a custom output folder for finished mod files, you can attach up to 3 preview images to a mod and the creator now has a Preview Bay so you can see how those images will look before building the mod, selected preview images are shown as thumbnails and you can cycle through them with previous/next controls, preview images are now handled with Pillow (Python imaging library) which allows cleaner scaling and better preview support, images are prepared in a way that works properly with the Aquatic Mod Manager’s fixed preview area, creator now writes proper signatures for mod files (this lets the Aquatic Mod Manager quickly detect valid mods and mark fake, invalid, or broken files as Reef/sunken ships instead of treating random renamed files like real mods), etc.

Linkdata unpacker also got overhauled with new code, better performance, aquatic GUI, etc. Same will happen for other tools such as the resource_bin/bns unpackers though I may instead just make a central unpacker instead of having several unpacker scripts, still deciding.

<img width="1718" height="955" alt="o6" src="https://github.com/user-attachments/assets/a326db4d-7f6f-4b1f-af9f-399dfee257a1" />
<img width="1717" height="1008" alt="o7" src="https://github.com/user-attachments/assets/a908dce2-da06-4194-af93-1edd1a876fee" />
<img width="1717" height="1017" alt="o2" src="https://github.com/user-attachments/assets/6eefd908-63df-4040-9952-4dd37bbb723c" />
<img width="1716" height="1015" alt="o3" src="https://github.com/user-attachments/assets/1c7e58fa-e0df-4f6f-b215-ac30a2e54ced" />
<img width="1723" height="1014" alt="o4" src="https://github.com/user-attachments/assets/5fa36a6f-1ea9-487d-846d-90b19d1f8306" />
<img width="1722" height="995" alt="o5" src="https://github.com/user-attachments/assets/8b9bd9e7-3a51-48fa-bbd9-b31c6a17c8a9" />
<img width="1719" height="975" alt="o8" src="https://github.com/user-attachments/assets/6d4b4d69-6897-4ead-a8a5-d2d1cf1bf283" />
<img width="1493" height="952" alt="o10" src="https://github.com/user-attachments/assets/fc5d23fe-77ad-44b3-a69f-85978cec6f30" />
<img width="1540" height="972" alt="o12" src="https://github.com/user-attachments/assets/686211bf-ced9-4b7b-874e-e9d6b1323a23" />
<img width="1542" height="940" alt="o13" src="https://github.com/user-attachments/assets/26625559-b900-4931-af65-8af3eb345509" />


# Info

Lightweight, GUI-first modding tools for Dynasty Warriors 4 Hyper (English version). Currently there are unpackers, repackers, a mod creator, mod manager to manage/apply mods. It's written in pure Python/Tkinter with minimal dependencies. Designed to be friendly for both modders and curious players. Mods can be any size, tools handle dynamic sizes (no “original size” constraint). It's important to read the guide section and Extra info & tips. Credit goes to Michael, Gamerman, and HighPriestFuneral for documentation/info on DW4 Hyper. If you encounter any issues or have questions, let me know on here or reddit (username on reddit is ThatFlowerGamu). If you own the Japanese/Chinese version of DW4 Hyper and would like the PD2 Unpacker/Repacker I made for the English version of DW4 Hyper supported for your versions then I can make a standalone version, just let me know.

Tools included as of December 4 2025:

Linkdata Tools (DW4_Hyper_linkdata_bin.pyw) that unpacks linkdata.bin, unpacks PD2s (mini containers stored within linkdata.bin), repack PD2s, progress UI.
![dw41](https://github.com/user-attachments/assets/44d58576-0303-4937-80f7-1a4bf17f2eff)

Mod Creator (DW4_Hyper_Mod_Creator.pyw) that turns unpacked files you mod from linkdata.bin into single file mods (.DW4HM) or packaged mods (.DW4HP, useful for large scale/batch mods, essentially a custom container I designed to store mods that are meant to contain more than 1 file). Whenever you mod an unpacked file from linkdata.bin, run mod creator to turn it into a single file or mod package file then apply/disable with mod manager. Mods you make for BNS files & resource.bin are handled by their own repackers by having the modded file within the same folder that is being repacked (i.e, changing title screen image means replacing it with your image you want and placing it in the same folder that the original file was in so it's repacked in its place). Now supports preview images to include with your mod release, up to 3 images per mod file. To keep things minimal i'm not using Pillow (if enough people want pillow support i'll include it but that would require users to install pillow, my goal is minimal dependencies) so you'll need to have your images as PNG files (just use paint or some app/website to convert image format to PNG or screenshot as PNG) and I suggest resizing images to 500x500 since the label that is used to display images in Mod Manager is set to 500x500 for width/height but if you choose to use images larger than 500x500 then it'll still work but it's auto-adjusted.
<img width="1430" height="875" alt="n4" src="https://github.com/user-attachments/assets/9501f1eb-2a9c-47f9-94f9-2207b51d5b86" />

Mod Manager (DW4_Hyper_Mod_Manager.pyw) that applies/disables mods safely by appending to linkdata.bin on 2048 boundaries at the end of the container file, manages mdata.bin (essentially a metadata file that stores references to files packed within linkdata.bin, like the idx file format of later PC koei tecmo games), keeps a ledger and original backups. Now supports image display for mods loaded, each mod file may have up to 3 images each. Also, the Mod Manager now auto copies/pastes your mdata.bin file to data\etc directory (where the game reads mdata.bin by default) but if you're using the modding tools in a separate directory then the mod manager will still apply/disable mods but will tell you to manually copy/paste mdata.bin to data\etc. I suggest keeping Mod Manager and its needed files in the game's directory, specifically media directory but it's up to you it'll work either way.
<img width="1694" height="826" alt="n5" src="https://github.com/user-attachments/assets/5a10a611-5b57-4fd8-a74c-8cbeeb60e10f" />

BNS Tools (DW4_Hyper_BNS.pyw) that unpacks/repacks voice BNS (JP/US), it's sector-aligned to 2048 on repack for each file (since PS2 games typically need to be sector aligned, that happens to be the case for DW4 Hyper).
![dw46](https://github.com/user-attachments/assets/c3af9818-ec12-4bd7-8c6e-05833c357c75)

resource.bin Tools (DW4_Hyper_resource_bin.pyw) that unpacks/repacks resource.bin.
![dw45](https://github.com/user-attachments/assets/9256ee0f-3f28-4f74-aef3-d027d812ce33)

Unit Editor (DW4_Hyper_Unit_Editor.pyw), editor for UNITDATA.BIN which stores unit data like parameters (model, weapon model, voice id, motion/moveset, movement speed, jump speed, etc). You can now expand the unitdata.bin file which means you can add more units into the game than what it originally started with. The Unit Editor now essentially supports having more units in the game than Dynasty Warriors 4 XL by being able to expand the unitdata.bin file.
![u1](https://github.com/user-attachments/assets/e7dfc7ba-1437-4e20-80a8-9dda7832a19d)

Example Mods:
![b3](https://github.com/user-attachments/assets/931f8b12-f581-454b-8fb7-48fffb7b2a8c)

![examp](https://github.com/user-attachments/assets/71452cc2-2eeb-4f48-b50f-23f4ab6b6e31)

<img width="1014" height="791" alt="n8" src="https://github.com/user-attachments/assets/56db5cb0-48bd-40af-8d37-e62a5b116436" />


Guide Section:

1. You must have Python 3 installed.

2. Please backup your linkdata.bin, resource.bin, BNS files, and mdata.bin files before using these tools.

3. You don't have to have the tools within the same directory, you just need them in the same folder with the files it needs. So if you want to keep things clean, i'd suggest making a "modding" folder, storing the files needed each tool needs (it'll be listed below) within that folder along with the scripts but it's up to you. All that matters is each script that I list below is paired with its needed files, Unit Editor and Mod Creator are exceptions since they use filedialog but again, your choice. For the releases, i'll include the files within the modding folder to make it easy.

4. Linkdata tools must be within the same directory as linkdata.bin, filenames.ref (a custom text file I made storing filenames for files within linkdata.bin that I found within the executable), mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods).

5. Mod Manager must be within the same directory as DW4_Hyper.MODS (a custom file designed by my tools, meant to store currently enabled mods), linkdata.bin, mdata.bin (your base game stores it within the media\data\etc directory), and original_mdata.bin (it's essentially a backup of a vanilla/non-modded mdata.bin file that the mod manager uses for disabling mods). When you finish applying mods, copy the mdata.bin within the directory that the mod manager is in and paste it in media\data\etc (where it's originally stored/read by the game). This will overwrite the mdata.bin file and ensure the game uses the updated mdata.bin file to accept the mods applied to linkdata.bin.

6. BNS tools must be within the same directory as the BNS files (your base game stores it within the media\data\sound\voice directory). It'll create 2 files which are voice_jp.ref and voice_us.ref, those are custom metadata files made by the unpacker to support unpacking the Ogg files. To make an audio mod that replaces the Ogg files from the BNS files, you'll probably need the version of LibVorbis that was used for Dynasty Warriors 4 Hyper or a compatible version or atleast something that creates/converts to an ogg format DW4 Hyper accepts. Once you replace the Ogg files with compartible ogg files you made/chose to use, repack with the repack button.

7. Resource_bin tools must be within the same directory as the resource.bin file (your base game stores it within the media\data\etc directory).

8. When you run the repacker button for resource_bin tools, linkdata tools, or BNS tools make sure you only have files you want repacked stored within the folder that will be repacked.

Notes on filenames:

DW4 Hyper often stores relavent filenames for container files (e.g., title.pd2) & loose files for files stored within linkdata.bin but not for files inside PD2/BNS/resource.bin containers.

For internal entries (files stored within a PD2, BNS, resource.bin container that are unpacked), tools assign incrementing filenames with a correct extension based on content.

Most interesting mod content (stages, units, textures, models, etc) lives in linkdata.bin, so this is rarely a blocker.

Extra info & tips

I am not affiliated with Koei Tecmo, these tools are provided as a means to mod an offline, singleplayer game that came out in 2005. If Koei Tecmo takes issue, please contact me.

Every file unpacked from linkdata.bin is given an additional 4 bytes called "taildata" at the end of the file, you must not remove it. It's used for the mod manager for applying/disabling mods. You can mod files unpacked that have taildata but please keep the last 4 bytes unchanged unless you know what you're doing since the mod manager relies on taildata. The taildata does not impact the usablity of files, it's purely used for mod manager.

I've only been reverse engineering Dynasty Warriors 4 Hyper for a week or so (as of November 11 2025), so if you have any knowledge of stuff like stage/battlefield data, item data, values, etc and would like to help then it would speed up the process of developing more GUI tools since anything without documentation (which is the case for DW4 Hyper, i reversed it without existing documentation) I have to manually reverse. So the less time I have to spend reversing file formats that someone else may already know, the sooner I can build more editors. If you share any knowledge/documentation, I will credit you. I want to have GUI modder and non-modder friendly tools that make modding easy. Not everyone has hours to spend learning modding so having easy to use tools is essential to me.

The Mod Manager is purpose-built for linkdata.bin. resource.bin and BNS use their own repackers.

For BNS audio, DW4 Hyper used an early Vorbis (libVorbis I 20020717). Use compatible Oggs for best results.

DW4HM (single file mods) and DW4HP (mod packages, meant to store a lot of mod files, think of it as a container for bulk mods) are designed to be sharable as well. I'll be seeing about creating a nexus page for Dynasty Warriors 4 Hyper mods but essentially, as long as you have the mod manager it can apply any DW4HM and DW4HP mod files. So let's say I made a custom battle, changed models, modded unit data, etc. I create the mod file or package after I finish modding the file I wanted to mod and upload it. If you have the mod manager you could apply/disable the downloaded/shared mods.

Roadmap:

More GUI editors (stages/battlefields, translation, items, etc).
