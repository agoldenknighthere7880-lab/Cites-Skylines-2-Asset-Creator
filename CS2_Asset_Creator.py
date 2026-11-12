import os, sys, json, re, shutil, zipfile, subprocess, threading, urllib.request, urllib.error, random
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP="CS2 Asset Creator"; VERSION="2.3.0"
TEMPLATES={"Toll plaza":"toll","Gas station":"gas","Warehouse":"warehouse","Bridge":"bridge","Shop":"shop","Street props":"props"}

def q(x): return repr(str(x))

def make_blender_script(mode, kind, prompt, scene, fbx, lod, collision):
    src = r"""
import bpy, math, os, re
from mathutils import Vector
MODE=__MODE__; KIND=__KIND__; PROMPT=__PROMPT__; SCENE=__SCENE__; FBX=__FBX__; TEXDIR=__TEXDIR__; LOD=__LOD__; COLLISION=__COLLISION__
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.7):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF"); bs.inputs["Base Color"].default_value=(*c,1); bs.inputs["Metallic"].default_value=metal; bs.inputs["Roughness"].default_value=rough
 noise=m.node_tree.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=5
 bump=m.node_tree.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.1; bump.inputs["Distance"].default_value=.06
 m.node_tree.links.new(noise.outputs["Fac"],bump.inputs["Height"]); m.node_tree.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
 return m
M={"concrete":mat("CS2 Concrete",(.43,.44,.42)),"asphalt":mat("CS2 Asphalt",(.06,.07,.075)),"white":mat("CS2 Painted White",(.8,.81,.78)),"roof":mat("CS2 Roof",(.12,.15,.17),.3),"glass":mat("CS2 Glass",(.035,.2,.27),.2,.2),"metal":mat("CS2 Metal",(.34,.39,.42),.7,.3),"yellow":mat("CS2 Safety Yellow",(.95,.58,.02)),"red":mat("CS2 Red",(.8,.025,.02)),"green":mat("CS2 Green",(.02,.22,.1)),"wood":mat("CS2 Wood",(.28,.15,.07))}
def cube(n,loc,dim,ma="concrete"):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(M[ma])
 b=o.modifiers.new("Edge bevel","BEVEL"); b.width=.035; b.segments=2; o.modifiers.new("Weighted normals","WEIGHTED_NORMAL"); return o
def cyl(n,loc,r,d,ma="metal"):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(M[ma]); return o
def shop_shell(w=12,d=9,h=5):
 cube("Building shell",(0,0,h/2),(w,d,h),"white"); cube("Flat roof",(0,0,h+.15),(w+.2,d+.2,.3),"roof")
 for x in (-w*.3,0,w*.3): cube("Glazed storefront",(x,-d/2-.04,h*.53),(w*.18,.08,h*.34),"glass")
 cube("Entrance door",(w*.12,-d/2-.07,h*.28),(w*.12,.1,h*.55),"metal")
def toll():
 cube("Toll plaza apron",(0,0,-.15),(30,24,.3),"asphalt")
 for x in (-7.5,0,7.5): cube("Raised island",(x,0,.2),(.7,22,.5),"concrete"); cube("Yellow island nose",(x,-10,.5),(.75,1,.15),"yellow")
 for x in (-11.25,-3.75,3.75,11.25):
  cube("Toll booth",(x,0,1.4),(3,3.5,2.8),"white"); cube("Booth window",(x,-1.8,1.7),(1.4,.08,1.1),"glass"); cube("Barrier post",(x,-4,.8),(.2,.2,1.6),"yellow"); cube("Barrier arm",(x,-4.8,1.65),(3,.1,.12),"red")
 cube("Canopy roof",(0,.2,5),(30,5,.45),"roof")
 for x in (-14,-7,0,7,14): cube("Canopy column",(x,2.1,2.5),(.35,.35,5),"metal")
 for x in (-11.25,-3.75,3.75,11.25): cube("Lane sign",(x,-2.4,4.7),(2.5,.14,.7),"green")
def gas():
 cube("Forecourt",(0,0,-.1),(25,22,.2),"asphalt"); shop_shell(9,7,4)
 cube("Fuel canopy",(0,5,5.2),(17,8,.4),"roof")
 for x in (-7.5,-2.5,2.5,7.5): cube("Canopy column",(x,5,2.6),(.28,.28,5),"metal")
 for x in (-5,0,5): cube("Fuel pump",(x,2,1),(.8,.7,1.8),"white"); cube("Pump screen",(x,1.62,1.35),(.45,.04,.3),"glass")
def warehouse():
 cube("Warehouse shell",(0,0,5),(22,15,10),"white"); cube("Warehouse roof",(0,0,10.2),(22.5,15.5,.4),"roof")
 for x in (-7,0,7): cube("Loading bay",(x,-7.58,3),(4,.12,5.5),"roof"); cube("Loading dock",(x,-8.4,.5),(4.5,1.5,1),"concrete")
 cube("Loading apron",(0,-12,-.1),(30,10,.2),"asphalt")
def bridge():
 cube("Bridge deck",(0,0,4),(28,7,.8),"concrete")
 for x in (-12,-8,-4,0,4,8,12): cube("Bridge rail",(x,0,5),(.12,7.2,1),"metal")
 for x in (-9,9): cube("Bridge pier",(x,0,1.8),(1.2,5,4),"concrete")
 cube("Approach road",(0,-7,3.5),(28,7,.2),"asphalt"); cube("Far approach road",(0,7,3.5),(28,7,.2),"asphalt")
def shop():
 shop_shell(12,9,5); cube("Shop awning",(0,-5,4),(12,1,.25),"red")
def props():
 cyl("Streetlight pole",(0,0,3.8),.11,7.4); cube("Lamp arm",(.7,0,7.3),(1.5,.12,.12),"metal"); cube("Lamp head",(1.4,0,7.2),(.6,.35,.16),"white")
 for x in (-3,0,3): cyl("Bollard",(x,-2,.6),.12,1.2,"yellow")
 cube("Bench seat",(0,2,.65),(3,.55,.18),"wood")
 for x in (-1.2,1.2): cube("Bench leg",(x,2,.32),(.14,.5,.65),"metal")
def prompt_model():
 p=PROMPT.lower(); nums=re.findall(r'(\d+(?:\.\d+)?)\s*(?:m|meter|metre)',p)
 w=float(nums[0]) if nums else 12; d=float(nums[1]) if len(nums)>1 else 9; h=float(nums[2]) if len(nums)>2 else 5
 w=max(2,min(w,100)); d=max(2,min(d,100)); h=max(2,min(h,80))
 if "bridge" in p or "overpass" in p: bridge()
 elif "toll" in p: toll()
 elif "gas station" in p or "petrol" in p: gas()
 elif "warehouse" in p or "factory" in p: warehouse()
 elif "streetlight" in p or "bench" in p or "bollard" in p: props()
 elif "shop" in p or "store" in p or "cafe" in p: shop()
 else:
  shop_shell(w,d,h); count=max(2,min(8,int(w//2)))
  for i in range(count):
   x=-w/2+(i+.5)*w/count; cube("Generated upper window",(x,-d/2-.05,h*.78),(w/count*.5,.08,h*.2),"glass")
if MODE=="prompt": prompt_model()
else: {"toll":toll,"gas":gas,"warehouse":warehouse,"bridge":bridge,"shop":shop,"props":props}.get(KIND,shop)()
main=[o for o in bpy.context.scene.objects if o.type=="MESH"]
# Smart UV project
for o in main:
 bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active=o
 if not o.data.uv_layers:
  try: bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode="OBJECT")
  except:
   try:bpy.ops.object.mode_set(mode="OBJECT")
   except:pass
# Generate game-ready image texture maps (base color, roughness, metallic, normal)
# These are generated maps, not shader-baked maps; UVs are created above.
import random, re
os.makedirs(TEXDIR,exist_ok=True)
seen={}
for obj in main:
 for material in obj.data.materials:
  if not material or material.name in seen: continue
  seen[material.name]=True
  bs=material.node_tree.nodes.get("Principled BSDF") if material.use_nodes else None
  if not bs: continue
  safe=re.sub(r"[^A-Za-z0-9_-]+","_",material.name)
  base=bs.inputs["Base Color"].default_value
  rough=float(bs.inputs["Roughness"].default_value); metal=float(bs.inputs["Metallic"].default_value)
  size=256; rng=random.Random(material.name)
  maps={k:bpy.data.images.new(safe+"_"+k,width=size,height=size,alpha=(k=="BaseColor")) for k in ("BaseColor","Roughness","Metallic","Normal")}
  pix={k:[] for k in maps}
  for y in range(size):
   for x in range(size):
    n=rng.uniform(-.035,.035)
    pix["BaseColor"].extend((max(0,min(1,base[0]+n)),max(0,min(1,base[1]+n)),max(0,min(1,base[2]+n)),1))
    rv=max(0,min(1,rough+rng.uniform(-.04,.04))); pix["Roughness"].extend((rv,rv,rv,1))
    mv=max(0,min(1,metal)); pix["Metallic"].extend((mv,mv,mv,1))
    pix["Normal"].extend((.5,.5,1,1))
  for k,img in maps.items():
   img.pixels.foreach_set(pix[k]); img.filepath_raw=os.path.join(TEXDIR,safe+"_"+k+".png"); img.file_format="PNG"; img.save()
  nodes=material.node_tree.nodes; links=material.node_tree.links
  for k,socket in (("BaseColor","Base Color"),("Roughness","Roughness"),("Metallic","Metallic")):
   tex=nodes.new("ShaderNodeTexImage"); tex.image=maps[k]; tex.label=k+" texture"; links.new(tex.outputs["Color"],bs.inputs[socket])
  nm=nodes.new("ShaderNodeTexImage"); nm.image=maps["Normal"]; nm.label="Normal texture"
  normal=nodes.new("ShaderNodeNormalMap"); links.new(nm.outputs["Color"],normal.inputs["Color"]); links.new(normal.outputs["Normal"],bs.inputs["Normal"])
# LOD duplicates; keep separate collection
if LOD:
 col=bpy.data.collections.new("CS2_LOD"); bpy.context.scene.collection.children.link(col)
 for o in main:
  d=o.copy(); d.data=o.data.copy(); d.name="LOD_"+o.name; col.objects.link(d)
  mod=d.modifiers.new("LOD Decimate","DECIMATE"); mod.ratio=.35
  try:bpy.context.view_layer.objects.active=d; bpy.ops.object.modifier_apply(modifier=mod.name)
  except:pass
# Per-mesh convex-hull collision proxies, easier to refine than one giant box
if COLLISION and main:
 import bmesh
 col=bpy.data.collections.new("CS2_Collision"); bpy.context.scene.collection.children.link(col)
 for index,source in enumerate(main):
  mesh=source.data.copy(); bm=bmesh.new(); bm.from_mesh(mesh)
  try:
   bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
   bmesh.ops.delete(bm,geom=[f for f in bm.faces if not f.is_valid],context='FACES')
   bm.to_mesh(mesh)
  finally: bm.free()
  proxy=bpy.data.objects.new("COL_"+source.name,mesh); col.objects.link(proxy)
  proxy.matrix_world=source.matrix_world.copy(); proxy.display_type="WIRE"; proxy.hide_render=True
# Save editable Blender scene including LOD and collision
os.makedirs(os.path.dirname(SCENE),exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=SCENE)
# Export only base meshes; game-specific LOD/collision must be reviewed in Editor
bpy.ops.object.select_all(action="DESELECT")
for o in main:o.select_set(True)
if main:
 bpy.context.view_layer.objects.active=main[0]; os.makedirs(os.path.dirname(FBX),exist_ok=True)
 bpy.ops.export_scene.fbx(filepath=FBX,use_selection=True,apply_unit_scale=True,bake_space_transform=True,object_types={"MESH"},mesh_smooth_type="FACE",path_mode="COPY",embed_textures=False)
print("CS2_ASSET_DONE",len(main))
"""
    repl={"__MODE__":q(mode),"__KIND__":q(kind),"__PROMPT__":q(prompt),"__SCENE__":q(scene),"__FBX__":q(fbx),"__TEXDIR__":q(str(Path(scene).parent.parent/"Textures")),"__LOD__":repr(bool(lod)),"__COLLISION__":repr(bool(collision))}
    for a,b in repl.items(): src=src.replace(a,b)
    return src

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title(f"{APP} {VERSION}"); self.geometry("1080x780"); self.minsize(930,660); self.configure(bg="#151b24")
  self.parent=tk.StringVar(); self.name=tk.StringVar(value="My_CS2_Asset"); self.template=tk.StringVar(value="Toll plaza")
  self.prompt=tk.StringVar(); self.ai_model=tk.StringVar(value="gpt-6-luna"); self.blender=tk.StringVar(); self.game=tk.StringVar(); self.output=tk.StringVar()
  self.lod=tk.BooleanVar(value=True); self.collision=tk.BooleanVar(value=True); self.status=tk.StringVar(value="Ready — create a project to begin.")
  self.style_ui(); self.ui()
 def style_ui(self):
  s=ttk.Style(self)
  try:s.theme_use("clam")
  except:pass
  s.configure(".",font=("Segoe UI",10)); s.configure("TFrame",background="#151b24"); s.configure("Panel.TFrame",background="#202b39")
  s.configure("TLabel",background="#151b24",foreground="#edf2f8"); s.configure("Panel.TLabel",background="#202b39",foreground="#edf2f8")
  s.configure("Muted.TLabel",background="#151b24",foreground="#a2afbf"); s.configure("Title.TLabel",background="#151b24",foreground="white",font=("Segoe UI",22,"bold"))
  s.configure("TButton",padding=9,background="#35485e",foreground="white"); s.map("TButton",background=[("active","#4a6380")])
  s.configure("Accent.TButton",padding=10,background="#267bd6",foreground="white",font=("Segoe UI",10,"bold"))
  s.map("Accent.TButton",background=[("active","#3b8ce7")]); s.configure("TEntry",fieldbackground="#2a3748",foreground="white",insertcolor="white")
  s.configure("TCombobox",fieldbackground="#2a3748",foreground="white"); s.configure("TNotebook",background="#151b24",borderwidth=0)
  s.configure("TNotebook.Tab",padding=(16,10),background="#202b39",foreground="#dce5ef")
  s.map("TNotebook.Tab",background=[("selected","#267bd6")],foreground=[("selected","white")])
  s.configure("TLabelframe",background="#202b39",foreground="white"); s.configure("TLabelframe.Label",background="#202b39",foreground="#8fc5ff",font=("Segoe UI",10,"bold"))
 def ui(self):
  h=ttk.Frame(self,padding=(22,18,22,8));h.pack(fill="x");ttk.Label(h,text="CS2 ASSET CREATOR",style="Title.TLabel").pack(anchor="w")
  ttk.Label(h,text="Procedural asset studio • Blender scene generation • CS2 Editor handoff",style="Muted.TLabel").pack(anchor="w")
  self.nb=ttk.Notebook(self);self.nb.pack(fill="both",expand=True,padx=18,pady=10)
  self.project_tab();self.create_tab();self.preview_tab();self.handoff_tab();self.pack_tab()
  f=ttk.Frame(self,padding=(18,8,18,14));f.pack(fill="x");ttk.Label(f,textvariable=self.status,style="Muted.TLabel").pack(side="left",fill="x",expand=True);ttk.Label(f,text="v"+VERSION,style="Muted.TLabel").pack(side="right")
 def panel(self,p,title,desc=None):
  x=ttk.LabelFrame(p,text=title,padding=15)
  if desc:ttk.Label(x,text=desc,style="Panel.TLabel",wraplength=900).pack(anchor="w",pady=(0,9))
  return x
 def field(self,p,label,var,browse=None):
  r=ttk.Frame(p,style="Panel.TFrame");r.pack(fill="x",pady=5);ttk.Label(r,text=label,style="Panel.TLabel",width=20).pack(side="left")
  ttk.Entry(r,textvariable=var).pack(side="left",fill="x",expand=True,padx=(0,8))
  if browse:ttk.Button(r,text="Browse",command=lambda:self.browse(var,browse)).pack(side="left")
 def browse(self,var,kind):
  x=filedialog.askdirectory() if kind=="dir" else filedialog.askopenfilename(filetypes=[("Programs / models","*.exe *.blend *.fbx *.obj *.glb *.gltf"),("All files","*.*")])
  if x:var.set(x)
 def root(self):
  if not self.parent.get().strip():return None
  return Path(self.parent.get())/re.sub(r"[^A-Za-z0-9_-]+","_",self.name.get().strip())
 def project_tab(self):
  t=ttk.Frame(self.nb,padding=20);self.nb.add(t,text="1  Project");p=self.panel(t,"Project workspace","Separate folders for source, generated Blender scenes, exports, Editor handoff and mod source packages.");p.pack(fill="x")
  self.field(p,"Project name",self.name);self.field(p,"Parent folder",self.parent,"dir")
  ttk.Button(p,text="Create project workspace",style="Accent.TButton",command=self.create_project).pack(anchor="e",pady=(10,0))
  q=self.panel(t,"Project structure");q.pack(fill="x",pady=12);ttk.Label(q,text="Models • Textures • Blender • Scripts • Exports • EditorImport • EditorOutput • ModPackage",style="Panel.TLabel").pack(anchor="w")
 def create_tab(self):
  t=ttk.Frame(self.nb,padding=20);self.nb.add(t,text="2  Create Asset")
  p=self.panel(t,"Built-in asset templates","Choose a starting structure and generate editable Blender geometry.");p.pack(fill="x",pady=(0,12))
  r=ttk.Frame(p,style="Panel.TFrame");r.pack(fill="x");ttk.Label(r,text="Template",style="Panel.TLabel",width=20).pack(side="left")
  ttk.Combobox(r,textvariable=self.template,state="readonly",values=list(TEMPLATES),width=30).pack(side="left")
  ttk.Label(p,text="Toll plazas • Gas stations • Warehouses • Bridges • Shops • Street props",style="Panel.TLabel").pack(anchor="w",pady=8)
  q=self.panel(t,"Describe an asset","Prompt-assisted local generator interprets common asset types and metric dimensions. Example: “A 15 meter wide modern roadside diner, 8 meters deep, 5 meters tall.”");q.pack(fill="x",pady=(0,12))
  self.field(q,"Description",self.prompt)
  a=ttk.Frame(q,style="Panel.TFrame");a.pack(fill="x",pady=(10,0))
  ttk.Button(a,text="Generate template",style="Accent.TButton",command=lambda:self.generate("template")).pack(side="left")
  ttk.Button(a,text="Generate from description",command=lambda:self.generate("prompt")).pack(side="left",padx=8)
  ttk.Button(a,text="AI design + generate",style="Accent.TButton",command=self.ai_generate).pack(side="left",padx=8)
  ttk.Label(q,text="AI model (requires OPENAI_API_KEY):",style="Panel.TLabel").pack(anchor="w",pady=(10,2))
  ttk.Entry(q,textvariable=self.ai_model,width=24).pack(anchor="w")
  z=self.panel(t,"Automatic geometry helpers","Basic LOD and collision are starting points and need visual/game validation.");z.pack(fill="x")
  ttk.Checkbutton(z,text="Create simplified LOD duplicate (Decimate)",variable=self.lod).pack(anchor="w",pady=3)
  ttk.Checkbutton(z,text="Create per-mesh convex-hull collision proxies",variable=self.collision).pack(anchor="w",pady=3)
 def preview_tab(self):
  t=ttk.Frame(self.nb,padding=20);self.nb.add(t,text="3  Preview & Export")
  p=self.panel(t,"Blender setup","Blender creates the model, procedural materials, smart UVs, optional LOD and collision, and saves an editable .blend scene.");p.pack(fill="x")
  self.field(p,"Blender executable",self.blender,"file")
  ttk.Button(p,text="Generate / update scene",style="Accent.TButton",command=lambda:self.generate("template")).pack(anchor="e",pady=8)
  q=self.panel(t,"Interactive 3D preview","The preview opens in Blender. Orbit with middle mouse, pan with Shift + middle mouse, zoom with the wheel.");q.pack(fill="x",pady=12)
  ttk.Button(q,text="Open Blender preview",command=self.preview).pack(side="left")
  ttk.Button(q,text="Export FBX for CS2",style="Accent.TButton",command=self.export).pack(side="left",padx=8)
  ttk.Button(q,text="Import FBX into project…",command=self.import_fbx).pack(side="left",padx=8)
  self.log=tk.Text(t,height=16,bg="#0d131b",fg="#dce8f6",insertbackground="white",relief="flat",font=("Consolas",9),padx=10,pady=8);self.log.pack(fill="both",expand=True,pady=12);self.write("Generation and export log.")
 def handoff_tab(self):
  t=ttk.Frame(self.nb,padding=20);self.nb.add(t,text="4  Editor Handoff")
  p=self.panel(t,"Game-ready Editor project","Builds the folder structure expected by the CS2 Asset Importer: Project Root / Assets / your asset. Copies the main FBX and available textures, with LOD and collision exports kept separately as optional source extras.");p.pack(fill="x")
  self.field(p,"Cities: Skylines II EXE",self.game,"file")
  ttk.Button(p,text="1. Build Editor Import Project",style="Accent.TButton",command=self.build_editor_project).pack(anchor="w",pady=(6,8))
  row=ttk.Frame(p,style="Panel.TFrame");row.pack(fill="x")
  ttk.Button(row,text="Open Project Root",command=self.open_editor_project).pack(side="left")
  ttk.Button(row,text="2. Launch Cities: Skylines II",command=self.launch_game).pack(side="left",padx=8)
  ttk.Label(t,text="In the Editor, open Asset Importer, set Project Root to the generated CS2_Editor_Project folder, set Assets Folder to Assets/<asset name>, choose Building or Static Object (or an existing prefab), then click Import. Place the imported asset, configure its properties, and save it from the Workspace. The Editor performs the final prefab creation.",style="Muted.TLabel",wraplength=850).pack(anchor="w",pady=12)
 def pack_tab(self):
  t=ttk.Frame(self.nb,padding=20);self.nb.add(t,text="5  Mod Pack Builder")
  p=self.panel(t,"Collect Editor / Toolchain output","Choose the folder containing the saved asset files. The builder preserves folder structure in a source pack and ZIP.");p.pack(fill="x")
  self.field(p,"Saved output folder",self.output,"dir")
  ttk.Button(p,text="Build source pack + ZIP",style="Accent.TButton",command=self.build_pack).pack(anchor="e",pady=10)
  q=self.panel(t,"Publishing note","This prepares an organized source handoff. It does not sign, publish, or generate a finished Paradox Mods package. Complete the official Modding Toolchain steps.");q.pack(fill="x",pady=12)
 def ai_generate(self):
  description=self.prompt.get().strip()
  if not description: messagebox.showwarning(APP,"Describe your asset first."); return
  if not os.environ.get("OPENAI_API_KEY"):
   messagebox.showwarning(APP,"OPENAI_API_KEY is not set. Add your API key as a Windows environment variable, then restart this app."); return
  self.busy(True); self.log_status("Asking AI to design an asset specification…")
  def work():
   try:
    payload={"model":self.ai_model.get().strip() or "gpt-6-luna","input":[{"role":"system","content":"You are a Cities: Skylines II asset design assistant. Return concise plain text only: a practical detailed design brief for a Blender procedural asset, with asset category, approximate metric dimensions, silhouette, facade, roof, supports, entrances, windows, signage, materials, and modular details. Do not output code or markdown. Preserve user intent."},{"role":"user","content":description}]}
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode("utf-8"),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=120) as response: data=json.loads(response.read().decode("utf-8"))
    brief=data.get("output_text","")
    if not brief:
     parts=[]
     for item in data.get("output",[]):
      for content in item.get("content",[]):
       if content.get("type")=="output_text": parts.append(content.get("text",""))
     brief="\n".join(parts)
    if not brief.strip(): raise RuntimeError("The AI response did not contain a design brief.")
    self.after(0,lambda:self.ai_ready(brief))
   except urllib.error.HTTPError as e:
    detail=e.read().decode("utf-8",errors="replace")[:1200]; self.after(0,lambda:self.ai_failed(f"API error {e.code}: {detail}"))
   except Exception as e:self.after(0,lambda:self.ai_failed(str(e)))
  threading.Thread(target=work,daemon=True).start()
 def ai_ready(self,brief):
  self.busy(False); self.prompt.set(brief); self.write("AI design brief:\n"+brief); self.log_status("AI design ready. Generating Blender scene…"); self.generate("prompt")
 def ai_failed(self,error):
  self.busy(False); self.log_status("AI design request failed."); messagebox.showerror(APP,"AI design failed:\n"+error)
 def create_project(self):
  root=self.root()
  if not root or not self.name.get().strip():messagebox.showwarning(APP,"Enter a project name and choose a parent folder.");return
  try:
   for d in ("Models","Textures","Blender","Scripts","Exports","EditorImport","EditorOutput","ModPackage"):(root/d).mkdir(parents=True,exist_ok=True)
   (root/"asset_project.json").write_text(json.dumps({"name":self.name.get(),"version":VERSION,"game":"Cities: Skylines II"},indent=2),encoding="utf-8")
   self.log_status(f"Project created: {root}");messagebox.showinfo(APP,str(root))
  except Exception as e:messagebox.showerror(APP,str(e))
 def required(self):
  root=self.root();bl=Path(self.blender.get()) if self.blender.get() else None
  if not root or not root.exists():messagebox.showwarning(APP,"Create a project first.");return None
  if not bl or not bl.is_file():messagebox.showwarning(APP,"Select blender.exe first.");return None
  return root,bl
 def generate(self,mode):
  r=self.required()
  if not r:return
  root,bl=r
  if mode=="prompt" and not self.prompt.get().strip():messagebox.showwarning(APP,"Describe your asset first.");return
  scene=root/"Blender"/(root.name+".blend");fbx=root/"Exports"/(root.name+".fbx");script=root/"Scripts"/"generate_asset.py"
  script.write_text(make_blender_script(mode,TEMPLATES[self.template.get()],self.prompt.get(),str(scene),str(fbx),self.lod.get(),self.collision.get()),encoding="utf-8")
  self.busy(True);self.log_status("Generating Blender geometry, procedural materials, UVs, LOD and collision…")
  def work():
   try:
    x=subprocess.run([str(bl),"--background","--python",str(script)],capture_output=True,text=True,timeout=900)
    self.after(0,lambda:self.generated(x.returncode,x.stdout,x.stderr,scene,fbx))
   except Exception as e:self.after(0,lambda:self.generated(1,"",str(e),scene,fbx))
  threading.Thread(target=work,daemon=True).start()
 def generated(self,rc,out,err,scene,fbx):
  self.busy(False);self.write(out[-7000:]+("\n"+err[-3500:] if err else ""))
  if rc==0 and scene.exists():
   self.log_status("Scene generated. Open preview or export FBX.");messagebox.showinfo("Generated",f"Blender scene:\n{scene}\nFBX:\n{fbx}")
  else:self.log_status("Generation failed — inspect log.");messagebox.showerror(APP,"Blender generation failed. Check the log.")
 def preview(self):
  r=self.required()
  if not r:return
  root,bl=r;scene=root/"Blender"/(root.name+".blend")
  if not scene.exists():messagebox.showwarning(APP,"Generate the scene first.");return
  subprocess.Popen([str(bl),str(scene)]);self.log_status("Opened Blender viewport preview.")
 def export(self):
  r=self.required()
  if not r:return
  root,bl=r;scene=root/"Blender"/(root.name+".blend");out=root/"Exports"/(root.name+".fbx")
  if not scene.exists():messagebox.showwarning(APP,"Generate the scene first.");return
  helper=root/"Scripts"/"export_fbx.py"
  helper.write_text("import bpy,os\nbase="+q(str(out))+"\nscene=bpy.context.scene\nos.makedirs(os.path.dirname(base),exist_ok=True)\ndef export_group(path, predicate):\n objs=[o for o in scene.objects if o.type=='MESH' and predicate(o)]\n bpy.ops.object.select_all(action='DESELECT')\n for o in objs:o.select_set(True)\n if objs:\n  bpy.context.view_layer.objects.active=objs[0]\n  bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,bake_space_transform=True,object_types={'MESH'},mesh_smooth_type='FACE',path_mode='COPY',embed_textures=False)\n  print('EXPORTED',path,len(objs))\nexport_group(base,lambda o:not o.name.startswith(('LOD_','COL_')))\nexport_group(os.path.splitext(base)[0]+'_LOD.fbx',lambda o:o.name.startswith('LOD_'))\nexport_group(os.path.splitext(base)[0]+'_Collision.fbx',lambda o:o.name.startswith('COL_'))\n",encoding="utf-8")
  self.busy(True);self.log_status("Exporting FBX…")
  def work():
   try:
    x=subprocess.run([str(bl),"--background",str(scene),"--python",str(helper)],capture_output=True,text=True,timeout=900)
    self.after(0,lambda:self.exported(x.returncode,x.stdout,x.stderr,out))
   except Exception as e:self.after(0,lambda:self.exported(1,"",str(e),out))
  threading.Thread(target=work,daemon=True).start()
 def import_fbx(self):
  r=self.required()
  if not r:return
  root,bl=r
  source=filedialog.askopenfilename(title="Select FBX model to import",filetypes=[("FBX model","*.fbx"),("All files","*.*")])
  if not source:return
  source=Path(source)
  if not source.is_file():messagebox.showerror(APP,"The selected FBX file could not be found.");return
  scene=root/"Blender"/(root.name+".blend")
  scene.parent.mkdir(parents=True,exist_ok=True)
  helper=root/"Scripts"/"import_fbx.py"
  helper.parent.mkdir(parents=True,exist_ok=True)
  # Open the existing project scene when present, then import the selected FBX
  # and save it as the project's main editable Blender scene.
  script=("import bpy, os\n"
          "scene="+q(str(scene))+"\n"
          "source="+q(str(source))+"\n"
          "if os.path.isfile(scene): bpy.ops.wm.open_mainfile(filepath=scene)\n"
          "bpy.ops.import_scene.fbx(filepath=source)\n"
          "os.makedirs(os.path.dirname(scene),exist_ok=True)\n"
          "bpy.ops.wm.save_as_mainfile(filepath=scene)\n"
          "print('IMPORTED_FBX',source,'SAVED_SCENE',scene)\n")
  helper.write_text(script,encoding="utf-8")
  self.busy(True);self.log_status(f"Importing {source.name} into the project scene…")
  def work():
   try:
    x=subprocess.run([str(bl),"--background","--python",str(helper)],capture_output=True,text=True,timeout=900)
    self.after(0,lambda:self.imported(x.returncode,x.stdout,x.stderr,scene,source))
   except Exception as e:self.after(0,lambda:self.imported(1,"",str(e),scene,source))
  threading.Thread(target=work,daemon=True).start()
 def imported(self,rc,out,err,scene,source):
  self.busy(False);self.write(out[-5000:]+("\n"+err[-3000:] if err else ""))
  if rc==0 and scene.exists():
   self.log_status(f"Imported {source.name} into {scene}")
   messagebox.showinfo("FBX imported",f"Imported model:\n{source}\n\nProject scene updated:\n{scene}\n\nUse Open Blender preview to inspect it, then Export FBX for CS2 when ready.")
  else:
   self.log_status("FBX import failed — inspect log.")
   messagebox.showerror(APP,"Blender could not import the FBX. Check the log and confirm the file is valid.")
 def exported(self,rc,out,err,path):
  self.busy(False);self.write(out[-4000:]+("\n"+err[-2500:] if err else ""))
  if rc==0 and path.exists():self.log_status(f"FBX exported: {path}");messagebox.showinfo("FBX ready",str(path))
  else:self.log_status("FBX export failed.");messagebox.showerror(APP,"FBX export failed. Check log.")
 def editor_project_path(self):
  root=self.root()
  return root/"CS2_Editor_Project" if root else None
 def build_editor_project(self):
  root=self.root()
  if not root or not root.exists():messagebox.showwarning(APP,"Create a project first.");return
  exports=root/"Exports"; base=root.name
  fbx=exports/(base+".fbx")
  if not fbx.is_file():
   messagebox.showwarning(APP,"No main FBX export found. Generate or import your model, then click Export FBX for CS2 first.");return
  project=self.editor_project_path(); asset_dir=project/"Assets"/base; extras=project/"Source_Extras"
  try:
   asset_dir.mkdir(parents=True,exist_ok=True)
   shutil.copy2(fbx,asset_dir/(base+".fbx"))
   copied_textures=[]
   tex=root/"Textures"
   if tex.exists():
    for item in tex.rglob("*"):
     if item.is_file():
      dest=asset_dir/item.name
      shutil.copy2(item,dest);copied_textures.append(dest.name)
   copied_extras=[]
   extras.mkdir(parents=True,exist_ok=True)
   for suffix in ("_LOD.fbx","_Collision.fbx"):
    item=exports/(base+suffix)
    if item.is_file():shutil.copy2(item,extras/item.name);copied_extras.append(item.name)
   instructions=f"""CITIES: SKYLINES II — EDITOR IMPORT PROJECT
Asset: {base}

FOLDER SETUP
Project Root: {project}
Assets Folder: {asset_dir}
Main model: {base}.fbx
Textures copied: {len(copied_textures)}
Optional source extras: {', '.join(copied_extras) if copied_extras else 'None found'}

IMPORT IN THE CITIES: SKYLINES II EDITOR
1. Start Cities: Skylines II and open the Editor from the main menu.
2. Open the Asset Importer panel/button.
3. Set Project Root to this folder:
   {project}
4. Set Assets Folder to this folder:
   {asset_dir}
5. Choose a Prefab Preset. Use Building for buildings; use Static Object for props. You can also use Existing Prefab in Project to copy settings from an existing asset.
6. Click Import and wait for the Editor to finish processing.
7. Place the imported asset in the scene. Adjust its position, scale, lot/footprint, object info, components, paths and decorations as appropriate.
8. Save the finished asset from the Editor Workspace. The Editor creates the actual game prefab/output; this folder is the import source, not a finished prefab or publishable mod.

IMPORTANT
- Review the model in the Editor before saving. Check scale, orientation, pivot, materials, texture appearance, collision, and LOD behavior.
- Source_Extras contains optional LOD/collision FBX exports for reference or manual use. They are not automatically wired into the imported asset.
- If the Editor reports missing textures or unsupported material data, adjust the source materials/texture setup and re-export.
- Keep the Blender project and original model as backups.
"""
   (project/"IMPORT_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")
   (project/"project_manifest.json").write_text(json.dumps({"game":"Cities: Skylines II","asset_name":base,"project_root":str(project),"assets_folder":str(project/"Assets"/base),"main_model":base+".fbx","textures":copied_textures,"source_extras":copied_extras,"status":"Ready for import in the official Editor; not yet a saved game prefab."},indent=2),encoding="utf-8")
   self.log_status(f"Editor project prepared: {project}")
   messagebox.showinfo("Editor project ready",f"Project Root:\n{project}\n\nAssets Folder:\n{asset_dir}\n\nNext: open the Editor and follow IMPORT_INSTRUCTIONS.txt.")
  except Exception as e:
   self.log_status("Editor project preparation failed.");messagebox.showerror(APP,f"Could not prepare Editor project:\n{e}")
 def open_editor_project(self):
  project=self.editor_project_path()
  if not project or not project.is_dir():
   messagebox.showwarning(APP,"Build the Editor Import Project first.");return
  try:
   if sys.platform=="win32":os.startfile(str(project))
   elif sys.platform=="darwin":subprocess.Popen(["open",str(project)])
   else:subprocess.Popen(["xdg-open",str(project)])
  except Exception as e:messagebox.showerror(APP,f"Could not open project folder:\n{e}")
 def launch_game(self):
  game=Path(self.game.get()) if self.game.get().strip() else None
  if not game or not game.is_file():
   messagebox.showwarning(APP,"Select the Cities: Skylines II executable first. If the Editor does not launch directly, open it from the game's main menu.");return
  try:
   subprocess.Popen([str(game)],cwd=str(game.parent))
   self.log_status("Launched Cities: Skylines II. Open Editor from the main menu.")
  except Exception as e:messagebox.showerror(APP,f"Game launch failed:\n{e}")
 def handoff(self):
  self.build_editor_project()
  self.launch_game()
 def build_pack(self):
  root=self.root();src=Path(self.output.get()) if self.output.get() else None
  if not root or not root.exists():messagebox.showwarning(APP,"Create project first.");return
  if not src or not src.is_dir():messagebox.showwarning(APP,"Select Editor / Toolchain output folder.");return
  files=[p for p in src.rglob("*") if p.is_file()]
  if not files:messagebox.showwarning(APP,"No files found.");return
  pkg=root/"ModPackage";assets=pkg/"Assets";assets.mkdir(parents=True,exist_ok=True)
  try:
   for p in files:
    dest=assets/p.relative_to(src);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
   (pkg/"asset_pack_manifest.json").write_text(json.dumps({"name":root.name,"game":"Cities: Skylines II","note":"Source pack for official Modding Toolchain; not a publish-ready package."},indent=2),encoding="utf-8")
   (pkg/"README.txt").write_text("Complete packaging, validation and publishing with the official Cities: Skylines II Modding Toolchain. This ZIP is a source handoff only.",encoding="utf-8")
   z=root/"Exports"/(root.name+"_ModdingToolchain_Source.zip")
   with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as a:
    for p in pkg.rglob("*"):
     if p.is_file():a.write(p,p.relative_to(pkg).as_posix())
   self.log_status(f"Built source pack from {len(files)} files: {z}");messagebox.showinfo("Source pack ready",f"{pkg}\n\n{z}\n\nFinish with the official Modding Toolchain.")
  except Exception as e:messagebox.showerror(APP,str(e))
 def write(self,s):
  if hasattr(self,"log"):self.log.insert("end",str(s)+"\n");self.log.see("end")
 def log_status(self,s):self.status.set(s);self.write(s)
 def busy(self,b):self.configure(cursor="watch" if b else "");self.update_idletasks()

if __name__=="__main__":App().mainloop()
