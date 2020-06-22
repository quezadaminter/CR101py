import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk

def mainStyle():
   css = b"""
* {
    background-image: none;
    background-color: #1C1C1C;
    font: 12px Cantarell;
}

button {
    color: #569E52;
    /*background-color: #3C3C3C;*/

    /*border-style: solid;
    padding: 12px 4px;*/
}

/*button:first-child {
    border-radius: 5px 0 0 5px;
}

button:last-child {
    border-radius: 0 5px 5px 0;
    border-width: 2px;
}*/

button:hover {
    background-color: #2b5c38;
}

button *:hover {
    color: white;
}

button:hover:active,
button:active {
    background-color: #993401;
}

label {
   color: #569E52;
}

label:hover {
    background-color: #993401;
}

scrolledwindow treeview {
   background: #2C2C2C;
}

GtkTreeView row:nth-child(odd) {
    background-color: #FF00FF;
}
GtkTreeView row:nth-child(even) {
    background-color: #00FFFF;
}
   """
   style_provider = Gtk.CssProvider()
   style_provider.load_from_data(css)
   
   Gtk.StyleContext.add_provider_for_screen(
       Gdk.Screen.get_default(),
       style_provider,
       Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
   )
