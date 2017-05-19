from configparser import ConfigParser
import urllib
import webbrowser
import json
# from london_database_connections import sqlcur, sqlcon, mdbclient, mdb, mdbcollection
import time
from datetime import datetime
from Tkinter import *
import tkSimpleDialog


# http://countdown.tfl.gov.uk/stopBoard/75288
# also http://blog.tfl.gov.uk/2013/12/20/understanding-our-new-api-part-2/



class MyDialog(tkSimpleDialog.Dialog):

     def body(self, master):
        Label(master, text="Bus routes:").grid(row=0)
        Label(master, text="Repetitions:").grid(row=1)
        Label(master, text="Update frequency minutes:").grid(row=2)

        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        return self.e1 # initial focus

     def apply(self):
        first = self.e1.get()
        second = self.e2.get()
        third = self.e3.get()
        self.result = first, second, third


def print_naptan_data(naptan, tfl_key):
    print naptan
    myurl = 'https://api.tfl.gov.uk/StopPoint/' + naptan + \
            '?' + tfl_key
    u = urllib.urlopen(myurl)
    data = u.read()
    naptan_json = json.loads(data)
    location = (naptan_json['lat'], naptan_json['lon'])
    return location


def print_bus_data(json_element):
    # print('*' * 10)
    keys = json_element.keys()
    location_str = ''
    j = 0
    while j < len(json_element):
        # print(keys[j] + ': ' + str(json_element[keys[j]]))
        if keys[j]=='naptanId':
            naptan_str = json_element[keys[j]]
            location_str = print_naptan_data(json_element[keys[j]])
        j+=1
    print(json_element['naptanId'])
    return json_element['naptanId']


def store_bus_arrival_data (line_id, bus_item, location, updatecount):
    # note we created the table using set_up_bus_movements_table.sql
    # and we can see the table structure in mysql using "DESCRIBE bus_movements;"
    sqlcur.execute("INSERT INTO bus_movements (lineId, vehicleId, direction, naptanId, timeToStation, lat, lon, updatecount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (line_id, bus_item[0], bus_item[1][0], bus_item[1][1],
                    bus_item[1][2], location[0], location[1], updatecount))

    # Mondgodb
    result = mdbcollection.insert_one(
        {
            "lineId": line_id,
            "vehicleId": bus_item[0],
            "direction": bus_item[1][0],
            "location": {
                "naptanId": bus_item[1][1],
                "lat": location[0],
                "lon": location[1]
            },
            "timeToStation": bus_item[1][2],
            "updatecount": updatecount,
            "updatetime": datetime.now()
        }
    )


def html_page(page_heading, lineids_images):
    html_text =  '''
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
        <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8">
            <title>London Bus Arrivals</title>
            <style type="text/css">
            </style>
        </head>
        <body bgcolor="#000000"style="background: #000000">
        <p style="margin-bottom: 0cm; line-height: 100%"><font color="#ffffff"><font face="Verdana, sans-serif"><b>'''
    html_text = html_text + page_heading + '''</b></font></font></p>
        <p><br></p>
        '''
    for lineid_image in lineids_images:
        caption = 'Bus Route: ' + lineid_image[0].upper()
        image_source = lineid_image[1]
        html_text = html_text + "<p><br></p>"
        html_text = html_text + '''<p style="margin-bottom: 0cm; line-height: 100%"><font color="#ffffff"><font face="Verdana, sans-serif">'''
        html_text = html_text + caption
        html_text = html_text + '''</font></font></p>
            <div style="overflow: hidden; width: 100%;"><p style="margin-bottom: 0cm; line-height: 100%"><img src="
            '''
        html_text = html_text + image_source
        html_text =html_text + '''
            " name="Image0" align="left" width="583" height="583" border="0"><br></p></div>
            '''
    html_text = html_text + '''
    </body>
    </html>
    '''
    return (html_text)

def main():
    parser = ConfigParser()
    parser.read('tokens.cfg')
    tfl_key = parser.get('tokens', 'tfl')
    google_key = parser.get('tokens', 'google')

    tkdroot = Tk()      # the root, main window
    tkdroot.title("this is the root window")
    d = MyDialog(tkdroot, "Specify download parameters")  #
    print d.result
    tkdroot.destroy()

    all_lines = d.result[0].split(',')
    repetition_count = d.result[1]
    r = 1

    # sqlcur.execute("SELECT max(updatecount) FROM bus_movements")
    # updatecount = int(sqlcur.fetchone()[0] + 1)
    updatecount=0

    while r <= int(repetition_count):
        if r > 1:
            print ('Completed repetition: ' + str(r-1) + ', now waiting ' +
                   d.result[2] + ' minutes' )
            time.sleep(float(d.result[2])*60)

        lineids_images = []; # an empty list
        for line_id in all_lines:
            # line_id = str(raw_input('enter a bus route')).lower()
            line_id = str(line_id).lower()
            myurl = 'https://api.tfl.gov.uk/Line/' + line_id + \
                    '/Arrivals?' + tfl_key
            u = urllib.urlopen(myurl)
            data = u.read()
            parsed_json = json.loads(data)

            i = 0
            all_buses = {}
            while i < len(parsed_json):
                arrival = parsed_json[i]
                if not arrival['vehicleId'] in all_buses:
                    all_buses[arrival['vehicleId']] = \
                        (arrival['direction'], arrival['naptanId'],
                         arrival['timeToStation'])
                else:
                    place_time_tuple = all_buses[arrival['vehicleId']]
                    if arrival['timeToStation'] < place_time_tuple[2]:
                        all_buses[arrival['vehicleId']] = \
                            (arrival['direction'], arrival['naptanId'],
                             arrival['timeToStation'])
                i+=1
            # iterate through all nearest arrivals, and identify bus stop location
            j = 0
            location = ''
            outbound_locations = ''
            inbound_locations = ''
            # for place_time_tuple in all_buses.values():
            for bus_item in all_buses.items():
                place_time_tuple = bus_item[1]
                location = print_naptan_data(place_time_tuple[1], tfl_key)
                # store_bus_arrival_data (line_id, bus_item, location, updatecount)
                location_str = str(location[0]) + ',' + str(location[1])
                if place_time_tuple[0] == 'outbound':
                    if len(outbound_locations) == 0:
                        outbound_locations += location_str
                    else:
                        outbound_locations += ('|' + location_str)
                else:
                    if len(inbound_locations) == 0:
                        inbound_locations += location_str
                    else:
                        inbound_locations += ('|' + location_str)
                j += 1

            if len(all_buses) > 0:
                myMarkers = '&markers=color:blue%7Clabel:O%7C' + \
                            outbound_locations + '&markers=color:red%7Clabel:I%7C' + \
                            inbound_locations
                image_source = 'https://maps.googleapis.com/maps/api/staticmap?size=800x800&2' + \
                               myMarkers + '&' + google_key
                lineids_images.append((line_id, image_source))
            else:
                print ('No bus arrivals found for route ' + line_id)
        # if sqlcon:
        #     sqlcon.commit()
        if r == 1 and len(lineids_images) > 0:
            filename="/home/ai/projects/bus-movements/web_pages/temp.html"
            html_page_heading = "Bus arrival points for routes " + \
                                ','.join(map(str, all_lines))
            output = open (filename,"w")
            output.write(html_page(html_page_heading, lineids_images))
            output.close()
            webbrowser.open("file:///" + filename)
        r += 1
        updatecount += 1
    # if sqlcon:
    #     sqlcon.close()

if __name__ == '__main__':
  main()


