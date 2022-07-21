import bpy, mathutils, math

bl_info = {
    "name": "Clipboard: Adobe After Effects 6.0 Keyframe Data",
    "description": "Export motion tracking markers to Adobe After Effects 6.0 compatible text data.",
    "author": "Noroino Hanako",
    "version": (0, 0, 1),
    "blender": (2, 93, 3),
    "location": "Motion Tracker > Right-Click Context Menu > Copy AAE Keyframes to clipboard",
    "warning": "",
    "category": "Import-Export",
    }

def generate_header(context):
    scene = context.scene
    clip = context.edit_movieclip
    fps = scene.render.fps / scene.render.fps_base
    header = ("Adobe After Effects 6.0 Keyframe Data\r\n\r\n" +
                "\tUnits Per Second\t{0:.3f}\r\n".format(fps) +
                "\tSource Width\t{0}\r\n".format(clip.size[0]) +
                "\tSource Height\t{0}\r\n".format(clip.size[1]) +
                "\tSource Pixel Aspect Ratio\t1\r\n" +
                "\tComp Pixel Aspect Ratio\t1\r\n\r\n")
    return header


class ClipboardAAEFXCornerPinKeyFrames(bpy.types.Operator):
    bl_idname = "export.clipboardafxcornerpinkey"
    bl_label = "Export to Adobe After Effects 6.0 Corner Pin Keyframe Data to clipboard"    

    def execute(self, context):
        clip = context.edit_movieclip
        track = clip.tracking.tracks.active
        if track == None or len(track.markers) == 0:
            self.report({"ERROR_INVALID_INPUT"},"Error: No selected tracker!")
            return {'CANCELLED'}

        body = ""
        for pin_n in [3,4,1,2]:
            section_header = "Effects ADBE Corner Pin #1  ADBE Corner Pin-000{0}\r\n\tFrame\tX pixels\tY pixels".format(pin_n)
            data = []
            for frameno in range(context.edit_movieclip.frame_start, clip.frame_duration + 1):
                marker = track.markers.find_frame(frameno)
                if not marker or marker.mute:
                    continue
                x_pos = (marker.co[0]+marker.pattern_corners[pin_n - 1][0]) * clip.size[0]
                y_pos = (1-(marker.co[1]+marker.pattern_corners[pin_n - 1][1])) * clip.size[1]
                data.append([frameno,x_pos,y_pos])
            section_body = "\r\n".join(["\t{0}\t{1:.3f}\t{2:.3f}".format(d[0],d[1],d[2]) for d in data])
            body = "\r\n".join([body,section_header,section_body+"\r\n"]) 
        context.window_manager.clipboard = generate_header(context) + body
        return {'INTERFACE'} 

class ClipboardAAEFXPlaneTrackCornerPinKeyFrames(bpy.types.Operator):
    bl_idname = "export.clipboardafxplanetrackcornerpinkey"
    bl_label = "Export Plane Track to Adobe After Effects 6.0 Corner Pin Keyframe Data to clipboard"    

    def execute(self, context):
        clip = context.edit_movieclip
        track = clip.tracking.plane_tracks.active
        if track == None or len(track.markers) == 0:
            self.report({"ERROR_INVALID_INPUT"},"Error: No selected tracker!")
            return {'CANCELLED'}

        body = ""
        for pin_n in [3,4,1,2]:
            section_header = "Effects ADBE Corner Pin #1  ADBE Corner Pin-000{0}\r\n\tFrame\tX pixels\tY pixels".format(pin_n)
            data = []
            for frameno in range(context.edit_movieclip.frame_start, clip.frame_duration + 1):
                marker = track.markers.find_frame(frameno)
                if not marker or marker.mute:
                    continue
                x_pos = marker.corners[pin_n - 1][0] * clip.size[0]
                y_pos = (1-marker.corners[pin_n - 1][1]) * clip.size[1]
                data.append([frameno,x_pos,y_pos])
            section_body = "\r\n".join(["\t{0}\t{1:.3f}\t{2:.3f}".format(d[0],d[1],d[2]) for d in data])
            body = "\r\n".join([body,section_header,section_body+"\r\n"]) 
        context.window_manager.clipboard = generate_header(context) + body
        return {'INTERFACE'} 

class ClipboardAAEFXKeyFrames(bpy.types.Operator):
    """Export motion tracking markers to Adobe After Effects 6.0 compatible files"""
    bl_idname = "export.clipboardafxkey"
    bl_label = "Export to Adobe After Effects 6.0 Transform Keyframe Data to clipboard"

    def execute(self, context):
        clip = context.edit_movieclip
        track = clip.tracking.tracks.active
        if track == None or len(track.markers) == 0:
            self.report({"ERROR_INVALID_INPUT"},"Error: No selected tracker!")
            return {'CANCELLED'}
        
        frameno = context.edit_movieclip.frame_start
        startarea = None
        startwidth = None
        startheight = None
        startrot = None
                
        data = []
        while frameno <= clip.frame_duration:
            marker = track.markers.find_frame(frameno)
            frameno += 1
            
            if not marker or marker.mute:
                continue
            
            coords = marker.co
            corners = marker.pattern_corners
            
            area = 0
            width = math.sqrt((corners[1][0] - corners[0][0]) * (corners[1][0] - corners[0][0]) + (corners[1][1] - corners[0][1]) * (corners[1][1] - corners[0][1]))
            height = math.sqrt((corners[3][0] - corners[0][0]) * (corners[3][0] - corners[0][0]) + (corners[3][1] - corners[0][1]) * (corners[3][1] - corners[0][1]))
            for i in range(1,3):
                x1 = corners[i][0] - corners[0][0]
                y1 = corners[i][1] - corners[0][1]
                x2 = corners[i+1][0] - corners[0][0]
                y2 = corners[i+1][1] - corners[0][1]
                area += x1 * y2 - x2 * y1
            area = abs(area / 2)

            if startarea == None:
                startarea = area
                        
            if startwidth == None:
                startwidth = width
            if startheight == None:
                startheight = height

            zoom = math.sqrt(area / startarea) * 100
            xscale = width / startwidth * 100
            yscale = height / startheight * 100

            p1 = mathutils.Vector(corners[0])
            p2 = mathutils.Vector(corners[1])
            mid = (p1 + p2) / 2
            diff = mid - mathutils.Vector((0,0))

            rotation = math.atan2(diff[0], diff[1]) * 180 / math.pi

            if startrot == None:
                startrot = rotation
                rotation = 0
            else:
                rotation -= startrot - 360

            x = coords[0] * clip.size[0]
            y = (1 - coords[1]) * clip.size[1]
            data.append([marker.frame, x, y, xscale, yscale, rotation])
            
        posline = "\t{0}\t{1:.3f}\t{2:.3f}\t0"
        scaleline = "\t{0}\t{1:.3f}\t{2:.3f}\t100"
        rotline = "\t{0}\t{1:.3f}"

        positions = "\r\n".join([posline.format(d[0], d[1], d[2]) for d in data]) + "\r\n\r\n"
        scales = "\r\n".join([scaleline.format(d[0], d[3], d[4]) for d in data]) + "\r\n\r\n"
        rotations = "\r\n".join([rotline.format(d[0], d[5]) for d in data]) + "\r\n\r\n"

        body = ("Anchor Point\r\n"+
                "\tFrame\tX pixels\tY pixels\tZ pixels\r\n"+
                positions+
                "Position\r\n"+
                "\tFrame\tX pixels\tY pixels\tZ pixels\r\n"+
                positions+
                "Scale\r\n"+
                "\tFrame\tX percent\tY percent\tZ percent\r\n"+
                scales+
                "Rotation\r\n"+
                "\tFrame Degrees\r\n"+
                rotations+
                "End of Keyframe Data\r\n")

        context.window_manager.clipboard = generate_header(context) + body
        return {'INTERFACE'} 
    
def draw_menu(self,context):
    layout = self.layout
    layout.separator()
    layout.operator(ClipboardAAEFXKeyFrames.bl_idname,text="Copy AAE Keyframes Transforms of selected to clipboard")
    layout.operator(ClipboardAAEFXCornerPinKeyFrames.bl_idname,text="Copy AAE Corner Pins of selected to clipboard")
    layout.separator()
    layout.operator(ClipboardAAEFXPlaneTrackCornerPinKeyFrames.bl_idname,text="Copy AAE Corner Pins of selected Plane Track to clipboard")

    
    
def register():
    bpy.utils.register_class(ClipboardAAEFXKeyFrames)
    bpy.utils.register_class(ClipboardAAEFXCornerPinKeyFrames)
    bpy.utils.register_class(ClipboardAAEFXPlaneTrackCornerPinKeyFrames)
    bpy.types.CLIP_MT_tracking_context_menu.append(draw_menu)
    
def unregister():
    bpy.utils.unregister_class(ClipboardAAEFXKeyFrames)
    bpy.utils.unregister_class(ClipboardAAEFXCornerPinKeyFrames)
    bpy.utils.unregister_class(ClipboardAAEFXPlaneTrackCornerPinKeyFrames)
    bpy.types.CLIP_MT_tracking_context_menu.remove(draw_menu)
    
if __name__ == "__main__":
    register()