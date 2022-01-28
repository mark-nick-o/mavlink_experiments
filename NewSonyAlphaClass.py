# ===============================================================================================================================
#
# Name : NewSonyAlphaClass.py
# Desc : Communicate with new Sony Alpha Series of Camera
# Auth : AIR-obots Ai-Robots
#
# ===============================================================================================================================
import shlex, subprocess, pprint

class sonyAlphaNewCamera():

    def set_sony_iso( self, isoVal ):

        # run the API command in the shell and look for the descriptor for the field
        #
        isoValArg=str(isoVal)
        cmd='/home/pi/cams/SonyTEST32/set_iso/RemoteCli ' + isoValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "ISO_Mode"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('ISO_Format') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers	

    def set_sony_aperture( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_aperture/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Aperture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Aperture_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers	

    def set_sony_ex_pro( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_ex_pro/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Exposure_Program_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Exposure_Program_Value') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers	

    def set_sony_focus( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_focus/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Focus_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def set_sony_focus_area( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_fa/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Area_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Focus_Area_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def set_sony_shutter( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_shutter/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Shutter_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Shutter_Value') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def set_sony_white_bal( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_wb/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "White_Bal_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('White_Bal_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_still_cap_mode( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/still_cap_mode/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Still_Capture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Still_Capture_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_white_balance( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/white_bal/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "White_Bal_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('White_Bal_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_ex_pro( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/exp_pro_mode/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Exposure_Program_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Exposure_Program_Value') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_aperture( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_aperture/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Aperture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Aperture_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_focus( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_focus/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Focus_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def set_sony_still_cap( self, Val ):

        # run the API command in the shell and look for the descriptor for the field
        #
        ValArg=str(Val)
        cmd='/home/pi/cams/SonyTEST32/set_still_cap/RemoteCli ' + ValArg
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Still_Capture_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Still_Capture_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_focus_area( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_focus_dist/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Focus_Area_Val"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Focus_Area_Val') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_iso( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_iso/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "ISO_Format"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('ISO_Format') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers

    def get_sony_shut_spd( self ):

        # run the API command in the shell and look for the descriptor for the field
        #
        cmd='/home/pi/cams/SonyTEST32/get_shutter/RemoteCli ' 
        args = shlex.split(cmd)
        s=subprocess.Popen(args, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "Shutter_Value"], stdin=s.stdout, stdout=subprocess.PIPE)	   # look for only this string in the output
        output = p2.communicate()[0]
        print(output)
        s.stdout.close()
        # consider if needed (if check of setval isnt working look for "cancelled" in the program output
        # 
        # s=subprocess.Popen(args, stdout=subprocess.PIPE)
        # p3 = subprocess.Popen(["grep", "cancelled"], stdin=s.stdout, stdout=subprocess.PIPE)
        # output2 = p3.communicate()[0]
        
        z = output.decode('ascii')         # convert bytes array output to ascii string 
        a = shlex.split(z)                 # split this unique output into fields separated by commas
        #
        # Using this parser as it sometimes missed the bracket at the start (odd??) in the popen output
        # we get the value fields before and after and return that list
        #
        itemNo = 0
        idx = 0
        answers = []
        for xx in a:
            if xx.find('Shutter_Value') > -1:
                idx = itemNo
            else:
                if (idx != 0):
                    if xx.find(':') > -1:
                        idx = itemNo
                    else:
                        if not (xx.isdigit()):
                            if xx.find("AUTO") > -1:
                                xx = 0     
                        answers.append(xx)
                        idx = 0
            itemNo += 1
        return answers
        
if __name__ == '__main__':

    mySonyCam = sonyAlphaNewCamera()
    ans = mySonyCam.set_sony_iso( 6 )
    print( ans )
    print( ans[1] == 2 )
    ans = mySonyCam.set_sony_aperture( 0 )
    print( ans[1] == 280 )                             # need to make a checking routine for all these functions
    ans = mySonyCam.set_sony_ex_pro( 2 )               # needs to be in a movie mode first
    print( ans[1] == 32859 )                                
    ans = mySonyCam.set_sony_focus_area( 0 )
    print( ans[1] == 1 ) 
    ans = mySonyCam.set_sony_focus( 0 )
    print( ans[1] == 2 ) 
    ans = mySonyCam.set_sony_shutter( 0 )
    print( ans[1] == 0 ) 
    ans = mySonyCam.set_sony_white_bal( 0 )
    print( ans[1] == 0 )
    ans = mySonyCam.set_sony_still_cap( 2 )            # 
    print( ans[1] == 65543 )    
    ans = mySonyCam.get_sony_still_cap_mode( )
    print(f" Still Cap Mode {ans}")
    ans = mySonyCam.get_sony_ex_pro( )
    print(f" Exposure Prog Mode {ans}")
    ans = mySonyCam.get_sony_aperture( )
    print(f" Aperture {ans}")
    ans = mySonyCam.get_sony_focus( )
    print(f" Focus {ans}")
    ans = mySonyCam.get_sony_focus_area( )
    print(f" Focus Area {ans}")
    ans = mySonyCam.get_sony_iso( )
    print(f" ISO {ans}")
    ans = mySonyCam.get_sony_shut_spd( )
    print(f" Shutter Speed {ans}")
    ans = mySonyCam.get_sony_white_balance( )
    
