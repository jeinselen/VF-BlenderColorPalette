bl_info = {
	"name": "VF Color Palette",
	"author": "John Einselen - Vectorform LLC",
	"version": (0, 0, 2),
	"blender": (3, 0, 0),
	"location": "Scene > VF Tools > Color Palette",
	"description": "Stores colors in a plain text for sharing across multiple projects",
	"warning": "inexperienced developer, use at your own risk",
	"doc_url": "https://github.com/jeinselenVF/VF-BlenderColorPalette",
	"tracker_url": "https://github.com/jeinselenVF/VF-BlenderColorPalette/issues",
	"category": "3D View"}

import bpy
import os

###########################################################################
# Property group definition

# Define the property group for color palette
class ColorPaletteProperty(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(
		name='Name',
		default='Color'
	)
	color: bpy.props.FloatVectorProperty(
		name="Color",
		subtype='COLOR',
		size=4,
		default=(1.0, 1.0, 1.0, 1.0)
	)

###########################################################################
# Palette management operators

class AddColorOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.add_color"
	bl_label = "Add Color"
	
	def execute(self, context):
		palette = context.scene.palette_local.add()
		palette.name = f"Color {len(context.scene.palette_local)}"
		# This operator may be called when no palette exists yet, so it's important to enter edit mode to allow saving
		bpy.context.scene.vf_color_palette_settings.palette_edit = True
		return {'FINISHED'}

class RemoveColorOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.remove_color"
	bl_label = "Remove Color Palette"
	
	palette_index: bpy.props.IntProperty()
	
	def execute(self, context):
		context.scene.palette_local.remove(self.palette_index)
		return {'FINISHED'}

class ReorderColorOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.reorder_color"
	bl_label = "Reorder Color Palette"
	
	palette_index: bpy.props.IntProperty()
	new_index: bpy.props.IntProperty()
	
	def execute(self, context):
		context.scene.palette_local.move(self.palette_index, self.new_index)
		return {'FINISHED'}

class CopyColorOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.copy_color"
	bl_label = "Copy Color"
	
	palette_index: bpy.props.IntProperty()
	
	def execute(self, context):
		palette = context.scene.palette_local[self.palette_index]
		color_str = '[' + ", ".join([str(value) for value in palette.color]) + ']'
		context.window_manager.clipboard = color_str
		return {'FINISHED'}

###########################################################################
# Palette editing operators

# Edit Palette
class EditPaletteOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.edit_palette"
	bl_label = "Edit"
	
	def execute(self, context):
		load_palette_from_file(bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_location)
		bpy.context.scene.vf_color_palette_settings.palette_edit = True
		return {'FINISHED'}

# Save Palette
class SavePaletteOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.save_palette"
	bl_label = "Save"
	
	def execute(self, context):
		save_palette_to_file(bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_location)
		bpy.context.scene.vf_color_palette_settings.palette_edit = False
		return {'FINISHED'}

# Load Palette Operator
class LoadPaletteOperator(bpy.types.Operator):
	bl_idname = "vfcolorpalette.load_palette"
	bl_label = "Load Palette"
	
	def execute(self, context):
		load_palette_from_file(bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_location)
		bpy.context.scene.vf_color_palette_settings.palette_edit = False
		return {'FINISHED'}

###########################################################################
# Palette open/save functions

def save_palette_to_file(filepath):
	try:
		filepath = os.path.join(filepath, bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_file_name)
		filepath = bpy.path.abspath(filepath)
			
		with open(filepath, 'w') as file:
			for palette in bpy.context.scene.palette_local:
				color = ",".join([str(value) for value in palette.color])
				file.write(f"{palette.name}={color}\n")
	except Exception as exc:
		print(str(exc) + " | Error in VF Color Palette save palette file function")

def load_palette_from_file(filepath):
	try:
		filepath = os.path.join(filepath, bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_file_name)
		filepath = bpy.path.abspath(filepath)
		
		bpy.context.scene.palette_local.clear()
		
		with open(filepath, 'r') as file:
			lines = file.readlines()
			for line in lines:
				name, color_str = line.strip().split('=')
				color_values = [float(value) for value in color_str.split(',')]
				palette = bpy.context.scene.palette_local.add()
				palette.name = name
				palette.color = color_values
	except Exception as exc:
		print(str(exc) + " | Error in VF Color Palette load palette file function")

###########################################################################
# Global plugin preferences and UI display

class ColorPalettePreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	# Global Variables
	palette_location: bpy.props.StringProperty(
		name = "Palette Location",
		description = "Location of the colour library saved alongside project files, should always be a relative path",
		default = "//",
		maxlen = 4096,
		subtype = "DIR_PATH")
	palette_file_name: bpy.props.StringProperty(
		name = "Palette File Name",
		description = "Name of the plain text library file",
		default = "VF_colorPalette.txt",
		maxlen = 1024)
	
	# User Interface
	def draw(self, context):
		layout = self.layout
		
		grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=False)
		grid.prop(self, "palette_location", text='')
		grid.prop(self, "palette_file_name", text='')

###########################################################################
# Project settings and UI rendering classes

class vfColorPaletteSettings(bpy.types.PropertyGroup):
	palette_edit: bpy.props.BoolProperty(
		name = "Editing Status",
		description = "Editing status of the palette",
		default = False)

class VFTOOLS_PT_colorPalette(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = 'VF Tools'
	bl_order = 2
	bl_options = {'DEFAULT_CLOSED'}
	bl_label = "Color Palette"
	bl_idname = "VFTOOLS_PT_colorPalette"
	
	@classmethod
	def poll(cls, context):
		return True #len(bpy.data.filepath) > 0
	
	def draw_header(self, context):
		try:
			layout = self.layout
		except Exception as exc:
			print(str(exc) + " | Error in VF Color Palette panel header")
			
	def draw(self, context):
		try:
			layout = self.layout
			layout.use_property_decorate = False # No animation
			
			# If project file isn't saved yet
			if not bpy.data.filepath:
				box = layout.box()
				col = box.column(align=True)
				col.label(text='Project must be saved first')
				col.label(text='to create or load color palette')
			else:
				# If no local palette entries exist yet
				if len(context.scene.palette_local) < 1:
					# Check for local file
					filepath = os.path.join(bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_location, bpy.context.preferences.addons['VF_colorPalette'].preferences.palette_file_name)
					filepath = bpy.path.abspath(filepath)
					if os.path.isfile(filepath):
						layout.operator("vfcolorpalette.load_palette", text="Load Palette", icon='FILE') # FILE FILE_BLANK FILE_CACHE FILE_REFRESH
					else:
						layout.operator("vfcolorpalette.add_color", text='Create Palette', icon='ADD')
				else:
					# If in edit mode
					if bpy.context.scene.vf_color_palette_settings.palette_edit:
						edit_grid = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=True, align=False)
						for index, color in enumerate(context.scene.palette_local):
							row = edit_grid.row(align=False)
							row.prop(color, "color", text='')
							row.prop(color, "name", text='')
							buttons = row.row(align=True)
							move_up = buttons.operator("vfcolorpalette.reorder_color", text='', icon='TRIA_UP')
							move_up.palette_index = index
							move_up.new_index = index - 1
							move_down = buttons.operator("vfcolorpalette.reorder_color", text='', icon='TRIA_DOWN')
							move_down.palette_index = index
							move_down.new_index = index + 1
							buttons.operator("vfcolorpalette.remove_color", text='', icon='X').palette_index = index
						layout.operator("vfcolorpalette.add_color", icon='ADD') # ADD PLUS PRESET_NEW
						row = layout.row()
						row.operator("vfcolorpalette.load_palette", text='Cancel', icon='CANCEL')
						row.operator("vfcolorpalette.save_palette", icon='CURRENT_FILE') # CURRENT_FILE
					# Standard display
					else:
						display_grid = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=True, align=False)
						for index, color in enumerate(context.scene.palette_local):
							row = display_grid.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
							row.prop(color, "color", text='')
							row.operator("vfcolorpalette.copy_color", text=color.name, icon='COPYDOWN').palette_index = index
						row = layout.row()
						row.operator("vfcolorpalette.edit_palette", icon='PREFERENCES') # PREFERENCES
				
		except Exception as exc:
			print(str(exc) + " | Error in VF Color Palette panel")

###########################################################################
# Addon registration functions

classes = (
	ColorPaletteProperty, AddColorOperator, RemoveColorOperator, ReorderColorOperator, CopyColorOperator,
	EditPaletteOperator, SavePaletteOperator, LoadPaletteOperator,
	ColorPalettePreferences, vfColorPaletteSettings, VFTOOLS_PT_colorPalette)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.palette_local = bpy.props.CollectionProperty(type=ColorPaletteProperty)
	bpy.types.Scene.vf_color_palette_settings = bpy.props.PointerProperty(type=vfColorPaletteSettings)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.palette_local
	del bpy.types.Scene.vf_color_palette_settings

if __name__ == "__main__":
	register()