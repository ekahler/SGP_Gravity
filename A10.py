import string
import re

class A10project(object):
    created = None
    project = None
    stationname = None
    lat = None
    long = None
    elev = None
    setupht = None
    transferht = None
    actualht = None
    gradient = None
    nominalAP = None
    polarx = None
    polary = None
    dffile = None
    olfile = None
    clock = None
    blue = None
    red = None
    date = None
    time = None
    timeoffset = None
    gravity = None
    setscatter = None
    precision = None
    uncertainty = None
    collected = None
    processed = None
    transferhtcorr = None
    comments = None

    def __init__(self):
        self.created = None
        self.project = None
        self.stationname = None
        self.lat = None
        self.long = None
        self.elev = None
        self.setupht = None
        self.transferht = None
        self.actualht = None
        self.gradient = None
        self.nominalAP = None
        self.polarx = None
        self.polary = None
        self.dffile = None
        self.olfile = None
        self.clock = None
        self.blue = None
        self.red = None
        self.date = None
        self.time = None
        self.timeoffset = None
        self.gravity = None
        self.setscatter = None
        self.precision = None
        self.uncertainty = None
        self.collected = None
        self.processed = None
        self.transferhtcorr = None
        self.comments = None

    def read_project_dot_txt(self, filename):
        dtf = False
        olf = False
        skip_grad = False
        data_descriptor = 0
        inComments = 0
        project_file = open(filename)
        data_array = []  # ['a']*32
        # Look for these words in the g file
        tags = re.compile(r'Project|Name|Created|Setup' +
                          r'|Transfer|Actual|Date|Time|TimeOffset|Nominal|Red' +
                          r'|Blue|Scatter|SetsColl|SetsProc|Precision|Total_unc')
        # 'Lat' is special because there are three data on the same line:
        # (Lat, Long, Elev)
        Lat_tag = re.compile(r'Lat')

        # 'Polar' is also special, for the same reason
        Pol_tag = re.compile(r'Polar')

        Version_tag = re.compile(r'Version')

        # Apparently using a delta file is optional, it's not always written to the .project file
        Delta_tag = re.compile(r'DFFile')
        OL_tag = re.compile(r'OLFile')
        Rub_tag = re.compile(r'RubFrequency')
        Grav_tag = re.compile(r'Grv')
        Grad_tag = re.compile(r'Gradient')

        # This one, because "Gradient:" is repeated exactly in this section
        Unc_tag = re.compile(r'Uncertainties')

        # This deals with multi-line comments
        Comment_tag = re.compile(r'Comments')

        for line in project_file:
            # Change up some text in the g file to make it easier to parse
            # (remove duplicates, etc.)
            line = string.strip(line)
            line = string.replace(line, '\n\n', '\n')
            line = string.replace(line, ":  ", ": ")
            # Repeat to take care of ":   " (three spaces)
            line = string.replace(line, ":  ", ": ")
            line = string.replace(line, ":  ", ": ")
            line = string.replace(line, "g Acquisition Version", "Acq")
            line = string.replace(line, "g Processing ", "")
            line = string.replace(line, "Project Name:", "Project")
            line = string.replace(line, "File Created:", "Created")
            line = string.replace(line, 'Gravity Corrections', 'grvcorr')
            line = string.replace(line, " Height:", ":")
            line = string.replace(line, "Delta Factor Filename:", "DFFile")
            line = string.replace(line, "Ocean Load ON, Filename:", "OLFile")
            line = string.replace(line, "Nominal Air Pressure:", "Nominal")
            line = string.replace(line, "Barometric Admittance Factor:", "Admittance")
            line = string.replace(line, " Motion Coord:", "")
            line = string.replace(line, "Set Scatter:", "Scatter")
            line = string.replace(line, "Offset:", "ofst")
            line = string.replace(line, "Time Offset (D h:m:s):", "TimeOffset")
            line = string.replace(line, "Ocean Load:", "OLC")
            line = string.replace(line, "Rubidium Frequency:", "RubFrequency")
            line = string.replace(line, "Blue Lock:", "Blue")
            line = string.replace(line, "Red Lock:", "Red")
            line = string.replace(line, "Red/Blue Separation:", "Separation")
            line = string.replace(line, "Red/Blue Interval:", "Interval")
            line = string.replace(line, "Gravity Corrections", "Corrections")
            line = string.replace(line, "Gravity:", "Grv:")
            line = string.replace(line, "Number of Sets Collected:", "SetsColl")
            line = string.replace(line, "Number of Sets Processed:", "SetsProc")
            line = string.replace(line, "Polar Motion:", "PolMotC")  # This is the PM error, not the values
            line = string.replace(line, "Barometric Pressure:", "")
            line = string.replace(line, "System Setup:", "")
            line = string.replace(line, "Total Uncertainty:", "Total_unc")
            line = string.replace(line, "Measurement Precision:", "Precision")
            line = string.replace(line, ":", "", 1)
            line = string.replace(line, ",", "")
            line_elements = string.split(line, " ")

            # Look for tags
            tags_found = re.search(tags, line)
            Lat_tag_found = re.search(Lat_tag, line)
            Pol_tag_found = re.search(Pol_tag, line)
            Comment_tag_found = re.search(Comment_tag, line)
            Version_tag_found = re.search(Version_tag, line)
            Delta_tag_found = re.search(Delta_tag, line)
            OL_tag_found = re.search(OL_tag, line)
            Grav_tag_found = re.search(Grav_tag, line)
            Unc_tag_found = re.search(Unc_tag, line)
            Grad_tag_found = re.search(Grad_tag, line)
            Rub_tag_found = re.search(Rub_tag, line)

            if Unc_tag_found != None:
                skip_grad = True

            if Grad_tag_found != None:
                if skip_grad == False:
                    data_array.append(line_elements[1])

            # Old g versions don't output Time Offset, which comes right before gravity
            if Grav_tag_found != None:
                if version < 5:
                    data_array.append('-999')
                data_array.append(line_elements[1])

            if Delta_tag_found != None:
                dtf = True
                df = " ".join(line_elements[1:])

            if OL_tag_found != None:
                olf = True
                of = " ".join(line_elements[1:])

            if Rub_tag_found != None:
                if dtf == True:
                    data_array.append(df)
                else:
                    data_array.append('-999')
                if olf == True:
                    data_array.append(of)
                else:
                    data_array.append('-999')
                data_array.append(line_elements[1])

            if Version_tag_found != None:
                version = float(line_elements[1])

            if tags_found != None:
                try:
                    data_array.append(line_elements[1])
                except:
                    data_array.append('-999')

            if Lat_tag_found != None:
                data_array.append(line_elements[1])
                data_array.append(line_elements[3])
                data_array.append(line_elements[5])
                # This accomodates old versions of g. If these data are to be published,
                # though, they should be reprocessed in a more recent version.
                if version < 5:
                    data_array.append('-999')  # Setup Height
                    data_array.append('-999')  # Transfer Height
                    data_array.append('-999')  # Actual Height

            if Pol_tag_found != None:
                data_array.append(line_elements[1])
                data_array.append(line_elements[3])

            if inComments > 0:
                comments = comments + line
                if inComments > 1:
                    comments += ' | '
                inComments += inComments

            if Comment_tag_found != None:
                inComments = 1
                comments = ''

        data_array.append(comments)

        # Old g versions don't output transfer height correction
        if version < 5:
            data_array.append('-999')
        project_file.close()

        self.created = data_array[0]
        self.project = data_array[1]
        self.stationname = data_array[2]
        self.lat = data_array[3]
        self.long = data_array[4]
        self.elev = data_array[5]
        self.setupht = data_array[6]
        self.transferht = data_array[7]
        self.actualht = data_array[8]
        self.gradient = data_array[9]
        self.nominalAP = data_array[10]
        self.polarx = data_array[11]
        self.polary = data_array[12]
        self.dffile = data_array[13]
        self.olfile = data_array[14]
        self.clock = data_array[15]
        self.blue = data_array[16]
        self.red = data_array[17]
        self.date = data_array[18]
        self.time = data_array[19]
        self.timeoffset = data_array[20]
        self.gravity = data_array[21]
        self.setscatter = data_array[22]
        self.precision = data_array[23]
        self.uncertainty = data_array[24]
        self.collected = data_array[25]
        self.processed = data_array[26]
        self.transferhtcorr = data_array[27]
        self.comments = data_array[28]

