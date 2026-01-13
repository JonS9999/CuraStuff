# Cura PostProcessingPlugin
# Author:   Jon Scheer (JonS)
# Date:     January 7th, 2026
# Version:  1.0
#
# Copyright (c) 2025 Jon Scheer
#
# Description:  This plugin will add M117 messages to your G-Code for things
#               like layer information, etc.  It can be used to add M117
#               messages based on :
#
#                  - Layer number.
#                  - The first few layers.
#                  - The last few layers.
#                  - The percent complete.
#
# Inspired by 'DisplayFilenameAndLayerOnLCD.py' by Amanda de Castilho.
#
# Put this script where your Cura 4.x or Cura 5.x post processing scripts
# are located.
#
# For example, for Cura 4.13.1 :
#
#    C:\Program Files\Ultimaker Cura 4.13.1\plugins\PostProcessingPlugin\scripts\
#
# And for Cura 5.11.0 :
#
#    C:\Program Files\UltiMaker Cura 5.11.0\share\cura\plugins\PostProcessingPlugin\scripts\
#
###############################################################################

from ..Script import Script
from UM.Application import Application


class AddLayerMessages(Script):

    def __init__(self):
        super().__init__()


    def getSettingDataString(self):

        return """{
            "name": "Add M117 Layer Messages",
            "key": "AddLayerMessages",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "formatString":
                {
                    "label": "Format string to use:",
                    "description": "Possible keys : {F} for file name; {L} for layer number; {M} for max layer number; {P} for percent complete; {S} for starting layer number; {D} for debug information.  Default = 'Layer {L} of {S}..{M} : {P} % : {F}'.",
                    "type": "str",
                    "default_value": "Layer {L} of {S}..{M} : {P} % : {F}"
                },

                "addToEveryNthLayer":
                {
                    "label": "Add every Nth layer?",
                    "description": "If set, an M117 message will be added for 'N' layers.  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                },
                    "addToEveryNthLayerCount":
                    {
                        "label": "   How often?",
                        "description": "How often to add the M117 message?  A value of '1' means that the M117 messages will be added for layers 0, 1, 2, 3...  A value of '2' means layers 0, 2, 4, 6...  A value of '3' means layers 0, 3, 6, 9...  And so on...  (Default is '1'.)",
                        "type": "int",
                        "default_value": 1,
                        "minimum_value": 0,
                        "enabled": "addToEveryNthLayer"
                    },

                "addToFirstLayers":
                {
                    "label": "Add to first layers?",
                    "description": "If set, an M117 message will be added to the first few layers.  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                },
                    "addToFirstLayersCount":
                    {
                        "label": "   Number of layers?",
                        "description": "Number of first layers to add the M117 message to.  (Default is '10'.)",
                        "type": "int",
                        "default_value": 10,
                        "minimum_value": 0,
                        "enabled": "addToFirstLayers"
                    },

                "addToLastLayers":
                {
                    "label": "Add to last layers?",
                    "description": "If set, an M117 message will be added for the last few layers.  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                },
                    "addToLastLayersCount":
                    {
                        "label": "   Number of layers?",
                        "description": "Number of last layers to add the M117 message to.  (Default is '10'.)",
                        "type": "int",
                        "default_value": 10,
                        "minimum_value": 0,
                        "enabled": "addToLastLayers"
                    },

                "addToEveryNthPercent":
                {
                    "label": "Add after percentage?",
                    "description": "If set, an M117 message will be added everytime we cross a user specified 'percentage' threshold (e.g., if the percentage set to '10', then an M117 message will be inserted when we go from 9% to 10%, from 19% to 20%, etc).  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                },
                    "addToEveryNthPercentPercentage":
                    {
                        "label": "   Percentage?",
                        "description": "Percent threshold for adding M117 messages.  (Default is '10'.)",
                        "type": "int",
                        "default_value": 10,
                        "minimum_value": 0,
                        "maximum_value": 100,
                        "enabled": "addToEveryNthPercent"
                    },

                "applyLayerCountOffset":
                {
                    "label": "Apply layer offset?",
                    "description": "Sometimes Cura miscounts and sets LAYER_COUNT to the wrong value.  For example, in Cura 4.x, if there are 10 layers, LABEL_COUNT will be set to 11, not 10.  Enable this to apply a user specified offset.  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                },
                    "layerCountOffset":
                    {
                        "label": "Layer count offset:",
                        "description": "Sometimes Cura miscounts and sets LAYER_COUNT to the wrong value.  For example, in Cura 4.x, if there are 10 layers, LABEL_COUNT will be set to 11, not 10.  Use this offset to correct for incorrect LAYER_COUNT values.  Use a negative value to decrease the layer count.  Use a positive value to increase the layer count.  (Default is '-1'.)",
                        "type": "int",
                        "default_value": -1,
                        "enabled": "applyLayerCountOffset"
                    },

                "oneBased":
                {
                    "label": "One-based display?",
                    "description": "Do we want to display M117 messages as one-based (e.g., display layers as 1..10) or as zero-based (display layers as 0..9)?  (Default is 'false'.)",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""


    #######################################################################
    #
    #  Main routine
    #
    #######################################################################

    def execute(self, data):

        fileName = Application.getInstance().getPrintInformation().jobName

        flagAddToEveryNthLayer   = False                # Flag : Output M117 at every so many layer changes ?
        flagAddToFirstLayers     = False                # Flag : Output M117 to the first 10 lines ?
        flagAddToLastLayers      = False                # Flag : Output M117 to the last 10 lines ?
        flagAddToEveryNthPercent = False                # Flag : Output M117 at every Nth percent of print ?

        layerNum                 = 0                    # Which layer we are processing (LAYER -- found in the G-Code file).
        numLayers                = 0                    # Number of layers in the print (LAYER_COUNT -- found in the G-Code file).
        lastLayer                = 0                    # Last (Maximum) layers in our file (numLayers - 1).
        numEveryNthLayers        = 0                    # Used if we are adding M117 messages based on Nth layer.
        numEveryNthPercent       = 0                    # Used if we are adding M117 messages based on Nth percent complete.
        numFirstLayers           = 0                    # Used if we are adding M117 messages to the first few layers.
        numLastLayers            = 0                    # Used if we are adding M117 messages to the last few layers.
        lastLayerStart           = 0                    # Used to determine where we start inserting M117 lines again.
        nextNthPercent           = 0                    # If doing "Nth percent" check, this is when to output the next M117 mesg.
        layerOffset              = 0                    # Used to display layers as zero-based (0..9) or one-based (1..10).
        layerCountOffset         = 0                    # Used to fix LAYER_COUNT (e.g., Cura 4.x sets LAYER_COUNT one too high).


        #
        #  Did the user specify a format string ?
        #
        if self.getSettingValueByKey("formatString") != "":
            formatString = self.getSettingValueByKey("formatString")
        else:
            formatString = "na"


        #
        #  Determine which flags the user set :
        #
        if self.getSettingValueByKey("addToEveryNthLayer"):
            numEveryNthLayers = self.getSettingValueByKey("addToEveryNthLayerCount")
            flagAddToEveryNthLayer = True

        if self.getSettingValueByKey("addToFirstLayers"):
            numFirstLayers = self.getSettingValueByKey("addToFirstLayersCount")
            flagAddToFirstLayers = True

        if self.getSettingValueByKey("addToLastLayers"):
            numLastLayers = self.getSettingValueByKey("addToLastLayersCount")
            flagAddToLastLayers = True

        if self.getSettingValueByKey("addToEveryNthPercent"):
            everyNthPercent = self.getSettingValueByKey("addToEveryNthPercentPercentage")
            flagAddToEveryNthPercent = True

        if self.getSettingValueByKey("applyLayerCountOffset"):
            if self.getSettingValueByKey("layerCountOffset") != "":
                layerCountOffset = self.getSettingValueByKey("layerCountOffset")

        if self.getSettingValueByKey("oneBased"):
            layerOffset = 1                                             # Display layers as 1..10.
        else:
            layerOffset = 0                                             # Display layers as 0..9.


        #############################################
        #
        #  Loop for every layer in our data :
        #
        #############################################

        for layer in data:

            layerIndex = data.index(layer)

            lines = layer.split("\n")                           # Break up the glob into separate lines.

            #########################################
            #
            #  Loop for every line in 'lines' :
            #
            #########################################

            for line in lines:

                if line.startswith(";LAYER_COUNT:"):

                    #
                    #   Do some calculations...  For example, if we are
                    #   printing a file with 10 layers (0..9) :
                    #
                    #       LAYER_COUNT will be *11*  (it's a bug in Cura 4.x)
                    #       LAYER will be 0..9.
                    #       numLayers will be 10.
                    #       lastLayer will be 9.
                    #
                    numLayers = line
                    numLayers = numLayers.split(":")[1]

                    #
                    #   Note that for some reason, Cura 4.x calculates
                    #   LAYER_COUNT incorrectly -- it is 1 too high.
                    #   For example, say we have a print with 10 layers,
                    #   numbered 0..9.  Well, LAYER_COUNT will be 11,
                    #   not 10.  So, we correct it here :
                    #
                    numLayers = str(int(numLayers) + int(layerCountOffset))

                    #
                    #   Our last printable layer (i.e., simply the
                    #   number of layers minus 1) :
                    #
                    lastLayer = ( int(numLayers) - 1 )

                    lastLayerStart = int(lastLayer) - int(numLastLayers) + 1                # Where we start adding M117 mesgs back in.

                    nextNthPercent = 0                                # If doing "Nth percent" check, this is when to output the next M117 mesg.


                if line.startswith(";LAYER:"):

                    #######################################################
                    #
                    #   Calculate the percent complete.  Note that we add
                    #   one to the 'lastLayer' since we are displaying
                    #   the message before we print the layer :
                    #
                    #######################################################

                    percentComplete = ( ( layerNum / ( int(lastLayer) + 1 ) ) * 100 )
                    percentComplete = round ( percentComplete, 2 )

                    #######################################################
                    #
                    #  Are we supposed to add an M117 line at this point ?
                    #
                    #######################################################

                    debugInfo = ""

                    addM117 = False

                    if flagAddToEveryNthLayer == True:
                        if ( int(layerNum) % int(numEveryNthLayers) ) == 0:
                            debugInfo = debugInfo + " (Add Nth Layer is TRUE : layer " + str(layerNum) + " / Nth layers " + str(numEveryNthLayers) + ")"
                            addM117 = True

                    if flagAddToFirstLayers == True:
                        if int(layerNum) < int(numFirstLayers):
                            debugInfo = debugInfo + " (Add to first " + str(numFirstLayers) + " layers (" + str(layerNum) + " in " + str(0) + ".." + str(int(numFirstLayers)-1) + "))"
                            addM117 = True

                    if flagAddToLastLayers == True:
                        if int(layerNum) >= int(lastLayerStart):
                            debugInfo = debugInfo + " (Add to last " + str(numLastLayers) + " layers (" + str(layerNum) + " in " + str(lastLayerStart) + ".." + str(lastLayer) + "))"
                            addM117 = True

                    if flagAddToEveryNthPercent == True:
                        if int(percentComplete) >= int(nextNthPercent):
                            debugInfo = debugInfo + " (Add Nth percent : " + str(percentComplete) + "% is in " + str(nextNthPercent) + ".."
                            nextNthPercent = ( int(nextNthPercent) + int(everyNthPercent) )     # Calculate next layer to print at.
                            debugInfo = debugInfo + str(nextNthPercent) + ")"
                            addM117 = True


                    #######################################################
                    #
                    #  Are we supposed to add the M117 line ?
                    #
                    #######################################################

                    if addM117 == True:

                        #
                        #   Format the output string ("M117 <formatString>") :
                        #
                        displayText = formatString
                        displayText = displayText.replace("{D}", debugInfo.lstrip())
                        displayText = displayText.replace("{F}", fileName)
                        displayText = displayText.replace("{L}", str(int(layerNum)  + layerOffset))
                        displayText = displayText.replace("{M}", str(int(lastLayer) + layerOffset))
                        displayText = displayText.replace("{P}", str(percentComplete))
                        displayText = displayText.replace("{S}", str(layerOffset))
                        displayText = "M117 " + displayText

                        lineIndex = lines.index(line)
                        lines.insert(lineIndex + 1, displayText)

                    layerNum += 1

            finalLines = "\n".join(lines)
            data[layerIndex] = finalLines

        return data

