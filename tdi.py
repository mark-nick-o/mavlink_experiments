# ------------------------------------------------------
#
# Simple Python to parse an XML Stream from the  
# TDI Sensors Output Data Standard Format V2.0 Feb 2020
# TD-1600 Report Data Packet Label Structure
#
# -----------------------------------------------------
import xml.etree.ElementTree as ET 

# send and email with the data
# Import smtplib for the actual sending function
#
import smtplib
# Import the email modules we'll need
#
from email.message import EmailMessage

# read the xml stream xml_data_stream
# root = ET.fromstring(xml_data_stream)

# open the XML File output from the camera
#
tree = ET.parse('c:\\pg\shopDoor1.xml') 

# XML
root = tree.getroot()

print(root.tag,root.attrib)

# if you want the whole thing
#
for child in root:
    print(" %s : %s \n" % (child.tag, child.attrib))

for cnt in root.findall('Count'):
    # add these keys to the XML output 
    #
    newKey_shoppers = ET.SubElement(cnt, 'total_shoppers') 
    newKey_insideBuilding = ET.SubElement(cnt, 'ppl_inside_building') 
	
    # parse the xml for the number of people coming in and out of enterance 
    #
    startTime = cnt.find('StartTime').text
    endTime = cnt.find('EndTime').text
    enters = cnt.find('Enters').text
	  exits = cnt.find('Exits').text
	  status = cnt.find('Status').text
	  staff = cnt.find('Staffs').text

    VIPs = cnt.find('VIPs').text
    Male0_14 = cnt.find('Male0_14').text
    Female0_14 = cnt.find('Female0_14').text
    Male15_29 = cnt.find('Male15_29').text
    Female15_29 = cnt.find('Female15_29').text
    Male30_59 = cnt.find('Male30_59').text
    Female30_59 = cnt.find('Female30_59').text
    Male60_ = cnt.find('Male60_').text
    Female60_ = cnt.find('Female60_').text

    female = int(Female0_14) + int(Female15_29) + int(Female30_59) + int(Female60_)
    male = int(Male0_14) + int(Male15_29) + int(Male30_59) + int(Male60_)

    young = int(Male0_14) + int(Female0_14) 
    teen = int(Male15_29) + int(Female15_29)
    mid = int(Male30_59) + int(Female30_59)
    old = int(Male60_) + int(Female60_)
	
	  inside = enters - exits
	  shoppers = inside - staff
    print(startTime)
    print(endTime)
    print(" total inside = %u shoppers inside = %u\n" % (inside,shoppers)) 
    print(" male = %u female = %u vip = %u" % (male,female,vip)) 
    print(" young = %u teen = %u mid = %u old = %u" % (young,teen,mid,old)) 

    # adds a section to the XML  (writes -1 if the data cant be trusted)  
    #
	  if ( int(status) == 0 ):
        newKey_shoppers = shoppers
        newKey_insideBuilding = inside
    else:
        newKey_shoppers = -1
        newKey_insideBuilding = -1

    # Create a text/plain message
    #
    msg = EmailMessage()
    emailData = " total inside = " + str(inside) + " total shoppers inside = " + str(shoppers) + "\n start time : " + startTime + "\n end time : \b" + endTime
    msg.set_content(emailData)
    msg['Subject'] = f'The contents of camera data from {startTime}'
    msg['From'] = me@myemail.com
    msg['To'] = you@myemail.com

    # Send the message via our own SMTP server. 
    #
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    tree = ET.ElementTree(root)

# print VIP key
#
for taggedPerson in root.iter('VIP'):
    print(taggedPerson.attrib)

# print Service key
#
for cnt in root.findall('Service'):
    status = cnt.find('Status').text
    if ( int(status) == 0 ):
        startTime = cnt.find('StartTime').text
	      endTime = cnt.find('EndTime').text
        nos = cnt.find('NumberServed').text
        so =  cnt.find('SecondsOccupied').text  
        tso = cnt.find('TotalSecondsOccupied').text    
        print(startTime)
        print(endTime)
        print(" number served = %u occupied (seconds) = %u total (seconds) = %u\n" % (nos,so,tso)) 

for cnt in root.findall('DwellTimes'):
    for DwellTime in cnt.iter('ServiceTime'):
        print(DwellTime.attrib)   
   
tree.write('C:\pg\shopDoor1-1.xml', encoding="UTF-8")

