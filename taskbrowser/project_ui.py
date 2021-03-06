#=== IMPORT ====================================================================
#system imports
import pygtk
pygtk.require('2.0')
import gtk.glade

#our own imports
from gnome_frontend import GnomeConfig

#=== OBJECTS ===================================================================

#=== MAIN CLASS ================================================================

class ProjectEditDialog:

    def __init__(self, datastore, project=None):
        
        #Set the Glade file
        self.gladefile = GnomeConfig.GLADE_FILE  
        self.wTree = gtk.glade.XML(self.gladefile, "ProjectEditDialog") 
        
        #Get the Main Window, and connect the "destroy" event
        self.window = self.wTree.get_widget("ProjectEditDialog")
        #if (self.window):
        #    self.window.connect("destroy", gtk.main_quit)

        #Create our dictionay and connect it
        dic = {
                "on_save_btn_clicked"   : self.on_save_btn_clicked,
                "on_cancel_btn_clicked" : self.on_cancel_btn_clicked
              }
        self.wTree.signal_autoconnect(dic)
        self.ds = datastore
        self.project = project
        self.on_close_cb = None

        if self.project != None:
            tv   = self.wTree.get_widget("project_desc_tv")
            buff = tv.get_buffer()
            buff.set_text(self.project.get_name())
        
    def main(self):
        self.window.show()
        return 0

    def set_on_close_cb(self, cb):
        self.on_close_cb = cb

    def on_save_btn_clicked(self, widget): #pylint: disable-msg=W0613
        # Extract project name
        tv   = self.wTree.get_widget("project_desc_tv")
        buff = tv.get_buffer()
        text = buff.get_text(buff.get_start_iter(),buff.get_end_iter())
        
        if not self.project :
            # Create project
            p = self.ds.new_project(text)
        else:
            p = self.project
            p.set_name(text)
            projects = self.ds.get_all_projects()
            b = projects[p.get_pid()][0]
            b.sync_project()
            
        self.window.destroy()
        # Trigger parent window to do whatever is needed to do
        self.on_close_cb()
        return 0

    def on_cancel_btn_clicked(self, widget): #pylint: disable-msg=W0613
        self.on_close_cb()
        self.window.destroy()


