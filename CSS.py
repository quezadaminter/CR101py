import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk

# For ideas and instruction
# https://thegnomejournal.wordpress.com/2011/03/15/styling-gtk-with-css/

def mainStyle():
   css = b"""

label
{
    color: #002EB3;
    background-color: #A8A8A8;
}

box, grid {
    color: #002EB3;
    background-color: #A8A8A8;
}

button
{
background-image: none;
    color: #AA00AA;
    background-color: #A8A8A8;
}

treeview 
{
background-color: #A0A0A0;
}
treeview:selected
{
background-color: rgba(255,255,0,1.0);
color: rgba(0,0,255,1.0);
}

/*
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
*/
/*
scrolledwindow treeview {
   background: #777777;
}
*/

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
