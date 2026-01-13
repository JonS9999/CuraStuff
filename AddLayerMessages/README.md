# Overview

_AddLayerMessages_ is a post processing script that can add M117 messages to the G-code file that Cura generates.

I created this script as I am running Klipper (on a Raspberry Pi), and I wanted a way to be notified on my phone as to the progress of an object I'm printing.  Klipper allows M117 messages to be sent to an MQTT broker, so I setup the MQTT broker as well as NodeRED on the Raspberry Pi, and then I created a NoteRED _flow_ to send a message to my phone when the MQTT broker receives an M117 message.  (I can write up more details on this whole thing separately if there is interest.)

So, I made this script to make is easy to add M117 messages to all the G-code files that I slice in Cura.


# Installation

To install this script, download it and copy it to the Cura 4.x or Cura 5.x post processing scripts directory.

For example, for Cura 4.13.1 :

   - C:\Program Files\Ultimaker Cura 4.13.1\plugins\PostProcessingPlugin\scripts\

And for Cura 5.11.0 :

   - C:\Program Files\UltiMaker Cura 5.11.0\share\cura\plugins\PostProcessingPlugin\scripts\


# Usage

Once you've installed the script, fire up Cura then go to the "Add a script" window which can be accessed via :

   - Extensions -> Post Processing -> Modify G-Code -> Add a script

If everything went well, you should see a script called "__Add M117 Layer Messages__" in the left part (pane) of the window, and a list of options in the right pane.  _(If you do not see the options in the right pane, see the 'Troubleshooting' section located further down in this README.md file.)_

The options are as follows :

- __Format string to use__ : This is the string that will be used when the M117 message is added.  For example, the default string is "__Layer {L} of {S}..{M} : {P} % : {F}__".

   The keywords ({L}, {S}, etc) will be replaced with :

   - {F} : The name of the file that is being sliced.  Note that if you slice the object, then save the file as a different name, the original file name will be used (which make sense if you think about it -- when you slice the file, Cura doesn't know what you are going to call the resulting G-Code file, so it does a _best guess_ as to what the file will be called).

   - {L} : Current layer number.

   - {M} : Maximum layer number.

   - {P} : Percent complete.  Note that this is the calcuated from the number of __layers__ being printed, not from the amount of filament that is being extruded.

   - {S} : The starting layer number.

   - {D} : Debugging information (which really isn't of any use to anyone besides myself :-)

- __Add every Nth layer?__ : This option will insert the M117 line every so often.

   - __How often?__ : How often to add the M117 message?  A value of '1' means that the M117 messages will be added for layers 0, 1, 2, 3...  A value of '2' means layers 0, 2, 4, 6...  A value of '3' means layers 0, 3, 6, 9...  And so on...  Default is '1'.

- __Add to first layers?__ : This option allows you to add an M117 to the first few layers of the file.

   - __Number of layers?__ : The number of first layers to add the M117 message to.  Default is '10' (meaning an M117 message will be added to the first ten layers).

- __Add to last layers?__ : Similar to "Add to first layers" but this allows you to add M117 messages to the last few layers.

   - __Number of layers?__ : The number of last layers to add the M117 message to.  Default is '10' (meaning an M117 message will be added to the last ten layers).

- __Add after percentage?__ : If enabled, an M117 message will be added everytime we cross a user specified layer 'percentage' threshold (e.g., if the percentage set to '10', then an M117 message will be inserted when we go from 9% to 10%, from 19% to 20%, etc).

   - __Percentage?__ : Percent threshold for adding M117 messages.  Default is '10'.

- __Apply layer offset?__ : Sometimes Cura miscounts and sets LAYER_COUNT to the wrong value.  For example, in Cura 4.x, if there are 10 layers, LABEL_COUNT will be set to 11, not 10.  However, in Cura 5.x, the LAYER_COUNT is correct (e.g., 10, not 11).  Enable this to apply a user specified offset to LAYER_COUNT.

   - __Layer count offset__ : This offset will be applied to LAYER_COUNT to correct for incorrectly calculated LAYER_COUNT values.  Use a negative value to decrease the layer count.  Use a positive value to increase the layer count.  Default is '-1', which works for Cura 4.x.

- __One-based display?__ : Enable this if you want layer numbers to start at 1 instead of 0.  For example, if a print has 10 layers, by default they are numbered 0..9, however, if you enable this option, they will be numbered 1..10.  Default is 'false' (not enabled).


# Troubleshooting

I have noticed that sometimes when you add the script (via Extensions -> Post Processing -> Modify G-Code -> Add a script), even though the name of the script ("Add M117 Layer Messages") shows up in the left window pane, none of the options show up in the right window pane.  I don't know why this is happening (I'm open to suggestions/solutions!), but one way around this is to add a different script, then remove that script -- the options for AddLayerMessages will now appear.
