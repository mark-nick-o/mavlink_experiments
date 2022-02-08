//
// Mission Planner Screen Example
//
// https://dianxnao.com/cs%E3%82%B3%E3%83%B3%E3%83%9C%E3%83%9C%E3%83%83%E3%82%AF%E3%82%B9%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9/
//
// https://gist.github.com/mrgarita/847e945fd1726ce2e6ee45961e4ee4d2#file-form1-cs
//
//
// https://github.com/kkouer/PcGcs/blob/master/GCSViews/welcomeForm.cs


// =============================================================================================================================

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace aerostation.Forms
{
	public partial class sonyCameraScreenMissionPlanner : Form
	{
		public sonyCameraScreenMissionPlanner()
		{
			InitializeComponent();
		}

		private void sonyCameraScreenMissionPlanner_Load(object sender, EventArgs e)
		{
			// Create the menu item
			comboBox1.Items.Add("AWB");
			comboBox1.Items.Add("Daylight");
			comboBox1.Items.Add("Shadow");
			comboBox1.Items.Add("Cloudy");
			comboBox1.Items.Add("Tungsten");
			comboBox1.Items.Add("Fluorescent WarmWhite");
			comboBox1.Items.Add("Fluorescent CoolWhite");
			comboBox1.Items.Add("Fluorescent DayWhite");
			comboBox1.Items.Add("Fluorescent Daylight");
			comboBox1.Items.Add("Flush");
			comboBox1.Items.Add("ColorTemp");
			comboBox1.Items.Add("Custom 1");
			comboBox1.Items.Add("Custom 2");
			comboBox1.Items.Add("Custom 3");
			// drop down box style
			comboBox1.DropDownStyle = ComboBoxStyle.DropDownList;
			// Description
			label1.Text = "White Balance";
			comboBox1.SelectedIndex = -1;    // make no selection
		}

                // selection is string so convert to float
		//
                private float stringArg2Float( string s )
		{
	    	   float num = 0.0f;
                   try
                   {
                      num = float.Parse(val);
                      //Console.WriteLine($"Writing to Mavlink '{val}' {num}.");
                   }
                  catch (FormatException)
                  {
                      //Console.WriteLine($"Unable to convert '{val}'.");
		      num = -1.0;
                  }
                 catch (OverflowException)
                 {
                      //Console.WriteLine($"'{val}' is out of range of the float type.");
		       num = -2.0;
                }
		return num;
              }

              // selection is string so convert to float
	      //
              private Int32 stringArg2Int32( string s )
	      {
	    	Int32 num = 0;
                try
                {
                   num = Int32.Parse(val);
                   //Console.WriteLine($"Writing to Mavlink '{val}' {num}.");
                }
                catch (FormatException)
                {
                   //Console.WriteLine($"Unable to convert '{val}'.");
		   num = -2;
                }
                catch (OverflowException)
                {
                  //Console.WriteLine($"'{val}' is out of range of the float type.");
		   num = -3;
                }
		return num;
              }

            private Int32 enumerate_white_bal_sony_a7( Int32 dataV )
    	    {
	      switch(dataV)
              {
               case 0:
               ret = 0;
               break;
		   
               case 1:
               ret = 17;
               break;
	    	   
               case 2:
               ret = 18;
               break;

               case 3:
               ret = 19;
               break;
		   
               case 4:
               ret = 20;
               break;

               case 5:
               ret = 33;
               break;
		   
               case 6:
               ret = 34;
               break;

               case 7:
               ret = 35;
               break;
		   
               case 8:
               ret = 36;
               break;

               case 9:
               ret = 48;
               break;

               case 10:
               ret = 1;
               break;

               case 11:
               ret = 256;
               break;

               case 12:
               ret = 257;
               break;
		   
               case 13:
               ret = 258;
               break;

               case 14:
               ret = 259;
               break;
		   
               default:
               //Console.WriteLine("Error");
			   ret = -4;
               break;
              }
	      return ret;
	  }

               // selection is string so convert to int32
               //		
               private void sendParamSetMessageWhiteBalAsFloat( float pVal )
               {
                  mavlink_param_set_t req = new mavlink_param_set_t();
                  req.target_system = MAV.sysid;
                  req.target_component = MAV.compid;

                  req.param_id = "S_WHITE_BAL";
                  req.param_value = pVal; 
                  req.param_type = MAVLINK_MSG_ID.MAV_PARAM_TYPE_REAL32; 

                  // send each one twice.
                  generatePacket((byte) MAVLINK_MSG_ID.PARAM_SET, req);
                  generatePacket((byte) MAVLINK_MSG_ID.PARAM_SET, req);
               }

              // sends the value as an int
	      //
              private void sendParamSetMessageWhiteBalAsInt32( Int32 pVal )
              {
                 mavlink_param_set_t req = new mavlink_param_set_t();
                 req.target_system = MAV.sysid;
                 req.target_component = MAV.compid;

                 req.param_id = "S_WHITE_BAL";
                 req.param_value = Convert.ToSingle(pVal); 
                 req.param_type = MAVLINK_MSG_ID.MAV_PARAM_TYPE_UINT32; 

                  // send each one twice.
                  generatePacket((byte) MAVLINK_MSG_ID.PARAM_SET, req);
                  generatePacket((byte) MAVLINK_MSG_ID.PARAM_SET, req);
                }

                // when the object is selected then write to mavlink using PARAM_SET message
                //		
		private void comboBox1_SelectionChangeCommitted(object sender, EventArgs e)
		{
		    string selectedItem = comboBox1.SelectedItem.ToString();
		    label1.Text = selectedItem + " for Camera White Balance";
		    Int32 optionSelection = stringArg2Int32( selectedItem );
		    if ( optionSelection >= 0 )
		    {
			Int32 cameraValue = enumerate_white_bal_sony_a7( optionSelection );
			if ( cameraValue >= 0 )
			{
			   sendParamSetMessageWhiteBalAsInt32( cameraValue );
			}
		    }
		}
	}
}
