bl_info = {
	"name": "Fluid Baker",
	"author": "Artell",
	"version": (0, 3),
	"blender": (2, 7, 5),
	"location": "3D View > Tool Shelf > Physics > Fluid Baker",
	"description": "Import-Export tools to bake metaballs and isosurfaces",	
	"category": "Object"}

import bpy
from mathutils import Matrix, Vector
from bpy.app.handlers import persistent


#BUTTON CLASSES
class import_metaball(bpy.types.Operator):
	""" Import the exported file """
	
	bl_idname = "id.import_metaball"
	bl_label = "import_metaball"
	bl_options = {'UNDO'}	

	#filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='abc')
	
	@classmethod
	def poll(cls, context):	
		if bpy.data.objects.get(context.scene.metaball_name):
			return True
	
	def execute(self, context):		  
		scene = context.scene
		
		try:
			obj = context.active_object
			
		except:
			is_hidden = True
			i = 0
			while is_hidden:
				obj = bpy.data.objects[i]
				if obj.hide:
					i += 1
				else:
					is_hidden = False
					
			('set active', bpy.data.objects[i].name)
			set_active_object(bpy.data.objects[i].name)
			
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		if bpy.data.objects.get(scene.metaball_name+'_baked'):
			set_active_object(scene.metaball_name+'_baked')
			bpy.ops.object.delete(use_global=False)
		
		#export to abc
		bpy.ops.wm.alembic_import(filepath=scene.abc_filepath, set_frame_range=False, is_sequence = False, validate_meshes = False)
		
		#disable metaballs
		scene.metaball_active = False
		update_metaball_active(self,context)
		
		
		return {'FINISHED'}

	#def invoke(self, context, event):		
	#context.window_manager.fileselect_add(self)
	#return {'RUNNING_MODAL'}

class export_metaball(bpy.types.Operator):
	""" Bake the selected metaball animation to Alembic file format """
	
	bl_idname = "id.export_metaball"
	bl_label = "export_metaball"
	bl_options = {'UNDO'}	

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='abc')
	
	@classmethod
	def poll(cls, context):	
		if bpy.data.objects.get(context.scene.metaball_name):
			return True
	
	def execute(self, context):		  
		scene = context.scene
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		_export_metaball_init()
		
		#check particles enabled in viewport are also enabled for renderable_only	
		modifier_dict = {}
		
		for obj in bpy.data.objects:
			if len(obj.modifiers) > 0:
				for modifier in obj.modifiers:
					if modifier.type == 'PARTICLE_SYSTEM':
						#store in dict
						modifier_dict[obj.name] = modifier.name, modifier.show_viewport, modifier.show_render
						if modifier.show_viewport:
							modifier.show_render = True
		
		"""
			if len(obj.particle_systems) > 0:
				for part_sys in obj.particle_systems:
					particle_settings = part_sys.settings
					if particle_settings.dupli_object == bpy.data.objects[scene.metaball_name]:
						if len(obj.modifiers) > 0:
							for modifier in obj.modifiers:
								if modifier.type == 'PARTICLE_SYSTEM':
									if modifier.show_viewport:
										modifier.show_render = True
		"""
						
				
		
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.metaball_name+'_baked')
		
		#add extension
		if self.filepath[-4:] != ".abc":
			self.filepath += ".abc"
		
		bpy.ops.wm.alembic_export(filepath=self.filepath, start = scene.frame_start, end=scene.frame_end, selected=True, renderable_only = False, uvs=False, packuv=False, apply_subdiv=False, vcolors=False)

		scene.abc_filepath = self.filepath
		
		
		
		return {'FINISHED'}

	def invoke(self, context, event):		
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class import_isosurface(bpy.types.Operator):
	""" Import the isosurface alembic file """
	
	bl_idname = "id.import_isosurface"
	bl_label = "import_isosurface"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):	
		if bpy.data.objects.get(context.scene.isosurface_name):
			return True
	
	def execute(self, context):	 	
		
		bpy.ops.wm.alembic_import(filepath=context.scene.abc_filepath, set_frame_range=False, is_sequence = False, validate_meshes = False)
		
		context.scene.isosurface_active = False
		
		update_isosurface_active(self,context)
				
			
		return {'FINISHED'}


class export_isosurface(bpy.types.Operator):
	""" Bake isosurface animation to Alembic file format """
	
	bl_idname = "id.export_isosurface"
	bl_label = "export_isosurface"
	bl_options = {'UNDO'}	

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='abc')
	
	@classmethod
	def poll(cls, context):	
		if bpy.data.objects.get(context.scene.isosurface_name):
			return True
	
	def execute(self, context):		  
		
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(context.scene.isosurface_name)
		
		#add extension
		if self.filepath[-4:] != ".abc":
			self.filepath += ".abc"
		
		bpy.ops.wm.alembic_export(filepath=self.filepath, start = bpy.context.scene.frame_start, end=bpy.context.scene.frame_end, selected=True, renderable_only = False, uvs=False, packuv=False, apply_subdiv=False, vcolors=False)

		return {'FINISHED'}

	def invoke(self, context, event):		
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
		
		
class set_all(bpy.types.Operator):
	""" Set all particle systems visibility """
	
	bl_idname = "id.set_all"
	bl_label = "set_all"
	bl_options = {'UNDO'}	

	"""
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)
	"""
	
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
	   
	   
		try:			
			_set_all()
		
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}
		

	
#FUNCTIONS ############################################################
def set_active_object(object_name):
	 bpy.context.scene.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select = True


def _set_all():
	scene = bpy.context.scene
	for obj in bpy.data.objects:
		if len(obj.modifiers) > 0:					  
			for mod in obj.modifiers:
				if mod.type == 'PARTICLE_SYSTEM':					
					mod.show_viewport = scene.particles_viewport_on					
					mod.show_render = scene.particles_render_on			
						
def update_isosurface_active(self,context):

	scene = context.scene
	if bpy.data.objects.get(scene.isosurface_name) != None:
		isosurface_object = bpy.data.objects[scene.isosurface_name]
		
		for isosurf in isosurface_object.IsoSurf:
			isosurf.active = context.scene.isosurface_active
			
		isosurface_object.hide = not context.scene.isosurface_active
		isosurface_object.hide_render = not context.scene.isosurface_active

	return None
	
def update_metaball_active(self,context):

	
	scene = context.scene
	
	if bpy.data.objects.get(context.scene.metaball_name):
		obj = bpy.data.objects[context.scene.metaball_name]
	else:
		obj = None

	if obj != None:
		if obj.type == 'META':
			if not scene.metaball_active:
				obj.data.update_method = 'NEVER'
				obj.hide = True
				obj.hide_render = True
			if scene.metaball_active:
				obj.data.update_method = 'UPDATE_ALWAYS'
				obj.hide = False
				obj.hide_render = False
			
	return None
	
def _export_metaball_init():
	scene = bpy.context.scene
	obj = bpy.data.objects[scene.metaball_name]
	
	
	metaball_loc = obj.location
	
	#create mesh
	bpy.ops.mesh.primitive_plane_add(view_align=True, enter_editmode=False, location=obj.location, rotation=obj.rotation_euler, layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
	bpy.context.active_object.name = scene.metaball_name+'_baked'
	bpy.context.active_object.scale = obj.scale
	
	#add a blank modifier to enable alembic export
	bpy.ops.object.modifier_add(type='WAVE')
	bpy.context.object.modifiers["Wave"].speed = 0
	bpy.context.object.modifiers["Wave"].width = 0
	bpy.context.object.modifiers["Wave"].height = 0
	bpy.context.object.modifiers["Wave"].narrowness = 0


	
	
@persistent
def mball_converter(scene):
	scene = bpy.context.scene
	
	if scene.metaball_name != "":
		if bpy.data.objects.get(scene.metaball_name) != None and bpy.data.objects.get(scene.metaball_name+'_baked') != None:
			if len(bpy.data.objects[scene.metaball_name+'_baked'].modifiers) > 0:
				if bpy.data.objects[scene.metaball_name+'_baked'].modifiers[0].type == 'WAVE':
					me = bpy.data.objects[scene.metaball_name].to_mesh(bpy.context.scene, False, 'PREVIEW', calc_tessface=False)
					bpy.data.objects[scene.metaball_name+'_baked'].data = me
			
			
			
			

#UI PANEL ##########################################################
class copy_paste_ui(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Physics'
	bl_label = "Fluid Baker"
	bl_idname = "id_fluid_baker"
	
   

	
	# button visibility conditions
	"""
	@classmethod
	def poll(cls, context):
		if context.mode == 'POSE' or context.mode == 'OBJECT':
			return True
		else:
			return False
	"""

	def draw(self, context):
		layout = self.layout.column(align=True)
		#pose_bone = context.active_object.pose.bones
		object = context.object		  
		scene = context.scene    

		layout.label('Particles Systems:')
		row = layout.row(align=True)
		
		row.operator('id.set_all', "Set All")
		row.prop(scene, 'particles_viewport_on', "", icon='RESTRICT_VIEW_OFF')
		row.prop(scene, 'particles_render_on', "", icon='SCENE')		
		
		layout.separator()		
	
		layout.label('CubeSurfer Baker:', icon='META_BALL')
		row = layout.row(align=True)
		row.prop_search(scene, 'isosurface_name', bpy.data, 'objects', "")
		row = layout.row(align=True)
		row.prop(scene, "isosurface_active", 'Enable Isosurfaces')
		
		row = layout.row(align=True)
		row.operator('id.export_isosurface', 'Export')
		row = layout.row(align=True)
		row.operator('id.import_isosurface', 'Import')
		
		layout.separator()
		layout.separator()
		
		layout.label('Metaballs Baker:', icon='OUTLINER_OB_META')
		row = layout.row(align=True)
		row.prop_search(scene, 'metaball_name', bpy.data, 'objects', "")
		row = layout.row(align=True)
		row.prop(scene, "metaball_active", 'Enable Meta')
		
		row = layout.row(align=True)
		row.operator('id.export_metaball', 'Export')
		row = layout.row(align=True)
		row.operator('id.import_metaball', 'Import')
		
#REGISTER

def register():
	bpy.utils.register_module(__name__) 	
	bpy.types.Scene.particles_render_on = bpy.props.BoolProperty(name='Render', description = 'Enable for rendering too', default=True)
	bpy.types.Scene.particles_viewport_on = bpy.props.BoolProperty(name='Viewport', description = 'Enable for viewport', default=True)
	bpy.types.Scene.isosurface_name = bpy.props.StringProperty(name='isosurface_name', description = 'Isosurface name', default = "")
	bpy.types.Scene.isosurface_active = bpy.props.BoolProperty(name='isosurface_active', description = 'Enable IsoSurfaces (CubeSurfer addon)', update=update_isosurface_active)
	bpy.types.Scene.metaball_name = bpy.props.StringProperty(name='Metaball name', description = 'Metaball name', default = "")
	bpy.types.Scene.metaball_active = bpy.props.BoolProperty(name='metaball_active', description = 'Enable selected Metaball', update=update_metaball_active)
	bpy.types.Scene.abc_filepath = bpy.props.StringProperty(name='abc_filepath', description = 'Metaball file path', subtype='FILE_PATH')
	
	
	bpy.app.handlers.frame_change_post.append(mball_converter)
	
def unregister():
	bpy.utils.unregister_module(__name__) 	
	del bpy.types.Scene.particles_render_on
	del bpy.types.Scene.particles_viewport_on
	del bpy.types.Scene.isosurface_name
	del bpy.types.Scene.isosurface_active
	del bpy.types.Scene.metaball_name	
	del bpy.types.Scene.metaball_active
	del bpy.types.Scene.abc_filepath
	
	bpy.app.handlers.frame_change_post.remove(mball_converter)
	
if __name__ == "__main__":
	register()
