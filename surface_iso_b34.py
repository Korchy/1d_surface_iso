# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_surface_iso

import bmesh
import bpy
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

bl_info = {
    "name": "Surface Iso",
    "description": "Creates surface from points cloud and iso-lines",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (3, 4, 1),
    "location": "N-panel - 1D - Surface ISO",
    "doc_url": "https://github.com/Korchy/1d_surface_iso",
    "tracker_url": "https://github.com/Korchy/1d_surface_iso",
    "category": "All"
}


# MAIN CLASS

class SurfaceIso:

    @classmethod
    def make_surface(cls, active_obj):
        # create surface from active object, which consists from points and iso-lines (edges lines)
        if active_obj:
            mode = active_obj.mode
            if active_obj.mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
            # switch to bmesh
            bm = bmesh.new()
            bm.from_mesh(active_obj.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            # deselect all
            cls._deselect_bm_all(bm=bm)
            # matrix
            world_matrix = active_obj.matrix_world.copy()
            # get vertices coordinates in 2d
            vertices_co = [world_matrix @ vertex.co for vertex in bm.verts]
            vertices_co_2d = [Vector((vertex.x, vertex.y)) for vertex in vertices_co]
            # get edges as indices by vertices_co_2d list
            edges = [[edge.verts[0].index, edge.verts[1].index] for edge in bm.edges]
            # calculate with delaunay
            vert_coords, edges, faces, orig_verts, orig_edges, orig_faces = delaunay_2d_cdt(
                vertices_co_2d, edges, [], 0, 0.01, True
            )
            # next - by calculated faces
            #   faces = [[vert_index0, vert_index1, vert_index2], [vert_index3, ...], ...]
            for face in faces:
                # in try-catch because some faces do not correspond source geometry, just ignore them
                try:
                    # switch from indices to bm_verts
                    face_v = [bm.verts[face[0]], bm.verts[face[1]], bm.verts[face[2]]]
                    # create new face
                    bm.faces.new(face_v)
                except:
                    pass
            # save changed data to mesh
            bm.to_mesh(active_obj.data)
            bm.free()
            # return mode back
            bpy.ops.object.mode_set(mode=mode)


    @staticmethod
    def _deselect_bm_all(bm):
        # remove all selection from edges and vertices in bmesh
        for face in bm.faces:
            face.select = False
        for edge in bm.edges:
            edge.select = False
        for vertex in bm.verts:
            vertex.select = False

    @staticmethod
    def ui(layout, context):
        # ui panel
        op = layout.operator(
            operator='surface_iso.make_surface',
            icon='MOD_WAVE'
        )

# OPERATORS

class SurfaceIso_OT_make_surface(Operator):
    bl_idname = 'surface_iso.make_surface'
    bl_label = 'Make Surface'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        SurfaceIso.make_surface(
            active_obj=context.active_object
        )
        return {'FINISHED'}


# PANELS

class SurfaceIso_PT_panel(Panel):
    bl_idname = 'SURFACE_ISO_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '1D'
    bl_label = 'Surface ISO'

    def draw(self, context):
        SurfaceIso.ui(
            layout=self.layout,
            context=context
        )


# REGISTER

def register(ui=True):
    register_class(SurfaceIso_OT_make_surface)
    if ui:
        register_class(SurfaceIso_PT_panel)


def unregister(ui=True):
    if ui:
        unregister_class(SurfaceIso_PT_panel)
    unregister_class(SurfaceIso_OT_make_surface)


if __name__ == '__main__':
    register()
