# CS2 Asset Creator 2.3

A Windows desktop helper for creating starter assets for Cities: Skylines II using Blender and the official CS2 Editor / Modding Toolchain.

## What's new in 2.3
- **Game-ready Editor project builder:** one click creates the official Editor import folder layout `CS2_Editor_Project/Assets/<AssetName>/`, copies the main FBX and available textures, and keeps optional LOD/collision FBX files in `Source_Extras/`.
- **Editor handoff instructions:** generates `IMPORT_INSTRUCTIONS.txt` with the exact Project Root and Assets Folder paths, recommended prefab preset, and steps to import, place, configure and save the asset in the CS2 Editor.
- **Open project / launch game controls:** opens the prepared folder and launches Cities: Skylines II so you can open the Editor from the main menu.

## What's new in 2.1
- **AI-assisted design briefs:** the `AI design + generate` button sends the asset description to the OpenAI Responses API, then uses the returned design brief to drive the local procedural Blender generator. This is AI-assisted design, not unrestricted AI-generated mesh topology or a full text-to-3D model.
- **Image-based PBR texture sets:** creates PNG BaseColor, Roughness, Metallic and Normal maps for each material and wires them into the Blender material. These are generated texture maps, not physically baked high-detail maps; the normal map is currently a neutral starter map.
- **Better collision starting geometry:** creates a separate convex-hull proxy for each source mesh rather than one giant bounding box.
- **Separate exports:** exports the render mesh, LOD meshes and collision proxies as separate FBX files. The Editor project builder places the main FBX and generated texture PNGs in the asset folder; LOD and collision FBX files are preserved separately as source extras.
- **Windows build script:** checks Python, installs PyInstaller and creates a single-file windowed EXE.

## Requirements
- Windows 10/11
- Python 3.10+ (Tkinter included)
- Blender 3.6+ with FBX export support
- Cities: Skylines II and its official Editor / Modding Toolchain
- Optional AI feature: an OpenAI API key with API billing enabled

## Run
Double-click `Launch_CS2_Asset_Creator.bat`.

## Enable AI design
1. Create an API key using the OpenAI Platform key setup flow.
2. In Windows, open **Edit environment variables for your account**.
3. Add a user variable named `OPENAI_API_KEY` and set its value to your API key. Do not paste the key into chats, screenshots, source code, or project files.
4. Close and reopen the app. The AI model field defaults to `gpt-6-luna`; you can change it to another model available to your API project.
5. Enter an asset description and choose **AI design + generate**.

API usage is billed separately from a ChatGPT subscription and is subject to current API pricing and project limits. The key is read from the environment and is not saved in the app's project files.

## Build the Windows EXE
On a Windows PC, double-click `Build_Windows_EXE.bat`. It installs/updates PyInstaller and writes `dist\\CS2_Asset_Creator.exe`. The EXE is not prebuilt in this ZIP because Windows executable packaging must be performed on Windows.

## Import an existing FBX model
1. Create or open your project workspace and set the **Blender executable** in the **Preview & Export** tab.
2. Click **Import FBX into project…** and select the `.fbx` file from your computer.
3. The app opens the existing project Blender scene if one exists, imports the selected FBX into it, and saves the result as `Blender\<ProjectName>.blend`. If no project scene exists yet, Blender creates one for the imported model.
4. Click **Open Blender preview** to inspect, rotate, edit materials or adjust geometry. Save any manual edits in Blender.
5. Click **Export FBX for CS2** to export the scene. The export includes regular mesh objects and separately exports objects named with the `LOD_` and `COL_` prefixes. Review the imported model's scale, orientation, materials, UVs and object names before using it in the CS2 Editor.

**Note:** Importing an FBX adds its objects to the current project scene; it does not replace existing scene objects. Importing the same FBX more than once can create duplicate geometry. Back up your `.blend` scene before repeated imports. Blender's FBX importer must be available in your Blender installation.

## Game-ready Editor import workflow (new in 2.3)
1. Create a project workspace.
2. Import an existing FBX or create an asset with a template / description.
3. Set the Blender executable. Open the Blender preview, check the model, then export the FBX.
4. In **Editor Handoff**, click **Build Editor Import Project**.
5. The app creates this layout:

   ```text
   <ProjectFolder>/CS2_Editor_Project/
   ├── IMPORT_INSTRUCTIONS.txt
   ├── project_manifest.json
   ├── Assets/
   │   └── <AssetName>/
   │       ├── <AssetName>.fbx
   │       └── [generated texture PNG files]
   └── Source_Extras/
       ├── <AssetName>_LOD.fbx       (if generated)
       └── <AssetName>_Collision.fbx (if generated)
   ```

6. Click **Open Project Root** if you want the folder visible in File Explorer. Click **Launch Cities: Skylines II**, then open **Editor** from the game's main menu.
7. In the Editor, open **Asset Importer**. Set **Project Root** to the `CS2_Editor_Project` folder shown in the app. Set **Assets Folder** to `CS2_Editor_Project/Assets/<AssetName>`.
8. Choose **Building** for a building or **Static Object** for a prop. Alternatively, use **Existing Prefab in Project** to copy settings from a suitable existing asset. Click **Import** and wait for processing.
9. Place the imported asset in the scene. Review its scale, orientation, materials, textures and footprint. Configure object properties and any required components, paths, areas or decorations.
10. Save the finished asset from the Editor **Workspace**. The Editor creates the actual game prefab/output. Use the app's Mod Pack Builder on the saved Editor output if you want a source archive.

The Editor's official workflow requires setting a Project Root and an Assets Folder, selecting a prefab preset, importing, then placing/customizing and saving the asset from Workspace. The creator prepares the import source; the Editor performs final prefab creation.

## General workflow
1. Create a project workspace.
2. Choose a built-in template, enter a local description, or use AI design.
3. Set Blender executable and generate the scene, or import an existing FBX.
4. Inspect/refine the model in Blender.
5. Export the main FBX and optional LOD/collision FBX files.
6. Build the Editor Import Project as described above.

## Important limitations
- The AI creates a structured design brief; geometry is still assembled by the app's procedural Blender templates. It does not yet generate arbitrary bespoke mesh topology directly from text.
- PBR images are starter maps generated from material colors and values. The normal map is flat; texture maps are not Cycles-baked high-detail maps or a guarantee of game-ready shader compatibility.
- LOD uses Blender Decimate duplicates. Review triangle counts, silhouette and naming in the Editor.
- Collision uses per-mesh convex hulls. Complex concave assets may need hand-built colliders.
- Preview opens Blender; it is not embedded in the app window.
- The Editor project builder prepares the official Asset Importer folder layout, but cannot click the Editor UI or automatically choose its importer settings. You must import, configure, place and save the asset in the Editor.
- The pack builder creates a source archive, not a signed or publish-ready Paradox Mods package. Complete packaging and publishing with the official Modding Toolchain.
