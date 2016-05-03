""""
Script to parse A10 files and create a tab-delimited file with the most
important data.

Should work with g8 and g9.

Jeff Kennedy
USGS
"""

import string
import re
import os
import Tkinter, tkFileDialog
from time import strftime

gravity_data_archive = "E:\\Shared\\Gravity Data Archive\\A-10"
##gravity_data_archive = "X:\\Absolute Data\\A-10"
root = Tkinter.Tk()
root.withdraw()
data_directory = tkFileDialog.askdirectory(
    parent=root,initialdir=gravity_data_archive)
a = data_directory.split('/')

# File save name is directory plus time and date
filesavename = os.getcwd()  + '/' + a[-1] + '_' +\
strftime("%Y%m%d-%H%M") + '.txt'
print filesavename

output_line=0
inComments = 0

#open file for overwrite (change to "r" to append)
fout = open(filesavename,"w")

#write data descriptor file header
fout.write("Created\tProject\tStation Name\tLat\tLong\tElev\tSetup Height\
\tTransfer Height\tActual Height\tGradient\tNominalAP\tPolar(x)\tPolar(y)\
\tDF File\tOL File\tClock\tBlue\tRed\tDate\tTime\tOffset\tGravity\tSet Scatter\
\tPrecision\tUncertainty\tCollected\tProcessed\tTransfer ht corr\
\tPolar(x) error\tPolar(y) error\tComments\n")

# For each file in the data_directory
for dirname,dirnames,filenames in os.walk(data_directory):
    if 'unpublished' in dirnames:
        dirnames.remove('unpublished')
    for filename in filenames:
        fname = os.path.join(dirname, filename)
        # If the file name ends in "project.txt"
        if string.find(fname,'project.txt') != -1:
            project_file = open(fname)
            data_descriptor = 0
            data_array = ['a']*32
            # Look for these words in the g file
            tags = re.compile(r'Project|Name|Created|DFFile|OLFile|Setht\
            |Transfer|Actual|Date|Time|Offset|Gradient|Nominal|RubFrequency|Red\
            |Blue|Gravity|Scatter|SetsColl|SetsProc|Precision|Total_unc')

            # 'Lat' is special because there are three data on the same line:
            # (Lat, Long, Elev)
            Lat_tag = re.compile(r'Lat')

            #'Polar' is also special, for the same reason
            Pol_tag = re.compile(r'Polar')

            Comment_tag = re.compile(r'Comments')
            for line in project_file:
                # Change up some text in the g file to make it easier to parse
                # (remove duplicates, etc.)
                line = string.strip(line)
                line = string.replace(line,'\n\n','\n')
                line = string.replace(line,":  ",": ")
                # Repeat to take care of ":   " (three spaces)
                line = string.replace(line,":  ",": ")
                line = string.replace(line,":  ",": ")
                line = string.replace(line,"Project Name:","Project")
                line = string.replace(line,"File Created:","Created")
                line = string.replace(line,"Setup Height:","Setht")
                line = string.replace(line,"Delta Factor Filename:","DFFile")
                line = string.replace(line,"Ocean Load ON, Filename:","OLFile")
                line = string.replace(line," Height:","")
                line = string.replace(line,"Nominal Air Pressure:","Nominal")
                line = string.replace(line,"Barometric Admittance Factor:","Admittance")
                line = string.replace(line," Motion Coord:","")
                line = string.replace(line,"Set Scatter:","Scatter")
                line = string.replace(line,"Offset:","ofst")
                line = string.replace(line,"Time Offset (D h:m:s):","Offset")
                line = string.replace(line,"Ocean Load:","OLC")
                line = string.replace(line,"Rubidium Frequency:","RubFrequency")
                line = string.replace(line,"Blue Lock:","Blue")
                line = string.replace(line,"Red Lock:","Red")
                line = string.replace(line,"Red/Blue Separation:","Separation")
                line = string.replace(line,"Red/Blue Interval:","Interval")
                line = string.replace(line,"Gravity Corrections","Corrections")
                line = string.replace(line,"Number of Sets Collected:","SetsColl")
                line = string.replace(line,"Number of Sets Processed:","SetsProc")
                line = string.replace(line,"Polar Motion:","PolMotC") # This is the PM error, not the values
                line = string.replace(line,"Barometric Pressure:","")
                line = string.replace(line,"System Setup:","")
                line = string.replace(line,"Total Uncertainty:","Total_unc")
                line = string.replace(line,"Measurement Precision:","Precision")
                line = string.replace(line,":","")
                line = string.replace(line,",","")
                line_elements = string.split(line," ")

                # Look for tags
                tags_found = re.search(tags,line)
                Lat_tag_found = re.search(Lat_tag,line)
                Pol_tag_found = re.search(Pol_tag,line)
                Comment_tag_found = re.search(Comment_tag,line)

                if tags_found != None:
                    data_array[data_descriptor] = line_elements[1]
                    data_descriptor = data_descriptor + 1

                if Lat_tag_found != None:
                    data_array[data_descriptor] = line_elements[1]
                    data_descriptor = data_descriptor+1
                    data_array[data_descriptor] = line_elements[3]
                    data_descriptor = data_descriptor+1
                    data_array[data_descriptor] = line_elements[5]
                    data_descriptor = data_descriptor+1

                if Pol_tag_found != None:
                    data_array[data_descriptor] = line_elements[1]
                    data_descriptor = data_descriptor+1
                    data_array[data_descriptor] = line_elements[3]
                    data_descriptor = data_descriptor+1

                if inComments > 0:
                    comments = comments + line
                    if inComments > 1:
                        comments = comments + ' | '
                    inComments += inComments

                if Comment_tag_found != None:
                    inComments = 1
                    comments = ''
            # This adds an Excel formula that looks up the correct polar motion
            data_array[data_descriptor] = "=VLOOKUP(S"+`output_line+2`+",\
            '\\\\Igswztwwwsjken2\Shared\Gravity\[finals.data.xlsx]Sheet1'\
            !$F$1:$G$20000,2,FALSE)-L"+`output_line+2`
            data_descriptor = data_descriptor+1
            data_array[data_descriptor] = "=VLOOKUP(S"+`output_line+2`+",\
            '\\\\Igswztwwwsjken2\Shared\Gravity\[finals.data.xlsx]Sheet1'\
            !$F$1:$I$20000,4,FALSE)-M"+`output_line+2`
            data_descriptor = data_descriptor+1
            data_array[data_descriptor] = comments

            project_file.close()
            output_line = output_line +1

            # Write data_array to file
            for eachelement in data_array:
                fout.write(eachelement + "\t")
            fout.write('\n')
fout.close()
