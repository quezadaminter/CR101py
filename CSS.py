import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib, Gdk

def mainStyle():
   css = b"""
* {
   /*
    transition-property: color, background-color, border-color, background-image, padding, border-width;
    transition-duration: 1s;
*/
    background-image: none;
    font: Cantarell 12px;
}

GtkWindow {
    /*background: linear-gradient(153deg, #151515, #151515 5px, transparent 5px) 0 0,
                linear-gradient(333deg, #151515, #151515 5px, transparent 5px) 10px 5px,
                linear-gradient(153deg, #222, #222 5px, transparent 5px) 0 5px,
                linear-gradient(333deg, #222, #222 5px, transparent 5px) 10px 10px,
                linear-gradient(90deg, #1b1b1b, #1b1b1b 10px, transparent 10px),
                linear-gradient(#1d1d1d, #1d1d1d 25%, #1a1a1a 25%, #1a1a1a 50%, transparent 50%, transparent 75%, #242424 75%, #242424); */
    background-color: #1C1C1C;
    /*background-size: 20px 20px;*/
}

.button {
    color: #569E52;
    background-color: #3C3C3C;
    border-style: solid;
   /* border-width: 2px 0 2px 2px; */
   /* border-color: #333; */

    padding: 12px 4px;
}

.button:first-child {
    border-radius: 5px 0 0 5px;
}

.button:last-child {
    border-radius: 0 5px 5px 0;
    border-width: 2px;
}

.button:hover {
    /*padding: 12px 48px;*/
    background-color: #2b5c38;
}

.button *:hover {
    color: white;
}

.button:hover:active,
.button:active {
    background-color: #993401;
}

.label {
   color: #569E52;
}

.scrolledwindow treeview {
   background: #2C2C2C;
}
   """
   style_provider = Gtk.CssProvider()
   style_provider.load_from_data(css)
   
   Gtk.StyleContext.add_provider_for_screen(
       Gdk.Screen.get_default(),
       style_provider,
       Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
   )
