import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk

# For ideas and instruction
# https://thegnomejournal.wordpress.com/2011/03/15/styling-gtk-with-css/

def mainStyle():
   css = b"""

* {
    background-image: none;
    background-color: #2998EA;
    font: 12px Cantarell;
}


GtkButton,
GtkButton .label {
    color: #202020;
    background-color: #D8D8D8;
}

GtkButton:hover, GtkLabel:hover
{
    background-color: #E7E7E7;
}

GtkLabel {
    color: #002EB3;
    background-color: #A8A8A8;
}

GtkBox, GtkGrid {
    color: #002EB3;
    background-color: #A8A8A8;
}

GtkTreeView row:selected {
    background-color: #49B8FA;
}

/*
GtkTreeView row{
}

button:first-child {
    border-radius: 5px 0 0 5px;
}

button:last-child {
    border-radius: 0 5px 5px 0;
    border-width: 2px;
}

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
   background-color: #C8C8C8;
}

label:hover {
    background-color: #993401;
}
*/
scrolledwindow treeview {
   background: #2C2C2C;
}
/*
GtkTreeView row:nth-child(odd) {
    background-color: #FF00FF;
}
GtkTreeView row:nth-child(even) {
    background-color: #00FF00;
}
*/
   """
   style_provider = Gtk.CssProvider()
   style_provider.load_from_data(css)
   
   Gtk.StyleContext.add_provider_for_screen(
       Gdk.Screen.get_default(),
       style_provider,
       Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
   )
