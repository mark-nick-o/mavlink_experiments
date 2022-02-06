#include <cstdlib>
#if defined(USE_EXPERIMENTAL_FS)
#include <experimental/filesystem>
namespace fs = std::experimental::filesystem;
#else
#include <filesystem>
namespace fs = std::filesystem;
#if defined(__APPLE__)
#include <unistd.h>
#endif
#endif
#include <cstdint>
#include <iomanip>
#include "CRSDK/CameraRemote_SDK.h"
#include "CameraDevice.h"
#include "Text.h"

#include <string>
// ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//
// Desc : This application controls Sony Alpha 1 Camera from the command line
// Date / Revision : 1.001 02-11-2021
//
// using http://tclap.sourceforge.net/manual.html
// argument parser library for any o/s
//
// ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#include <iostream>
#include <algorithm>
#define TCLAP_LIB_VER tclap-1.2.5
#include <tclap/TCLAP_LIB_VER/CmdLine.h>
#include <regex>
#include <map>

// for json files or stream support
#if __has_include(<optional>)
  #include <optional>
  #define have_optional 1
#elif __has_include(<experimental/optional>)
  #include <experimental/optional>
  #define have_optional 1
  #define experimental_optional 1
#else
  #define have_optional 0
#endif

#include <nlohmann/json.hpp>
// files
#include <iostream>
#include <fstream>
#include <stdexcept>
// clock
#include <ctime>

// the sony alpha one camera library
#include "alpha.cpp"

using json = nlohmann::json;
using namespace std;

// ================================================================= Functions ===============================================================================================
//

// parses string input to an int or null
//
std::optional<int> ParseStringToInt(string& arg)
{
    try 
    {
        return { std::stoi(arg) };
    }
    catch (...)
    {
        std::cout << "cannot convert \'" << arg << "\' to int!\n";
    }
 
    return { };
}

// Take a string of command words and emplace them into a vector string list
//
std::vector<std::string> splitStringLineToWordVector(const std::string str, const std::string regex_str)
{
    return { std::sregex_token_iterator(str.begin(), str.end(), std::regex(regex_str), -1), std::sregex_token_iterator() };
}

// List all the possible actions for the given command shell (things about the camera)
//
enum OptionTCLAPAction : CrInt32u
{
  Option_MovieRecord,
  Option_Release,
  Option_MediaFormat_Slot1Offset,
  Option_MediaFormat_Slot2Offset,
  Option_MediaQuickFormat_Slot1Offset,
  Option_MediaQuickFormat_Slot2Offset,
  Option_CancelMediaFormat,
  Option_S1_unlock,
  Option_S1_lock,
  Option_AEL_unlock,
  Option_AEL_lock,
  Option_FEL_unlock,
  Option_FEL_lock,
  Option_AWBL_unlock,
  Option_AWBL_lock,
  Option_AFL_unlock,
  Option_AFL_lock,
  Option_FNumber,
  Option_ExposureBiasCompensation,
  Option_FlashCompensation,
  Option_ShutterSpeed,
  Option_IsoSensitivity,
  Option_FocusArea,
  Option_ExposureProgramMode,
  Option_CompressionFileFormatStill,
  Option_FileType,
  Option_JpegQuality,
  Option_WhiteBalance,
  Option_FocusMode,
  Option_MeteringMode,
  Option_FlashMode,
  Option_WirelessFlash,
  Option_RedEyeReduction,
  Option_DriveMode,
  Option_DRO,
  Option_ImageSize,
  Option_AspectRatio,
  Option_PictureEffect,
  Option_Colortemp,
  Option_ColorTuningAB,
  Option_ColorTuningGM,
  Option_LiveViewDisplayEffect,
  Option_StillImageStoreDestination,
  Option_PriorityKeySettings,
  Option_DateTime_Settings,
  Option_Focus_Magnifier_Setting,
  Option_NearFar,
  Option_NearFar_AF_Area,
  Option_Zoom_Scale,
  Option_Zoom_Setting,
  Option_Zoom_Operation,
  Option_Movie_File_Format,
  Option_Movie_Recording_Setting,
  Option_Movie_Recording_FrameRateSetting,
  Option_Interval_Rec_Mode,
  Option_Still_Image_Trans_Size,
  Option_RAW_J_PC_Save_Image,
  Option_LiveView_Image_Quality,
  Option_CustomWB_Capture_Standby,
  Option_CustomWB_Capture_Standby_Button,
  Option_CustomWB_Capture_Standby_Cancel,
  Option_CustomWB_Capture,
  Option_SnapshotInfo,
  Option_BatteryRemain,
  Option_BatteryLevel,
  Option_RecordingState,
  Option_LiveViewStatus,
  Option_FocusIndication,
  Option_MediaSLOT1_Status,
  Option_MediaSLOT1_RemainingNumber,
  Option_MediaSLOT1_RemainingTime,
  Option_MediaSLOT1_FormatEnableStatus,
  Option_MediaSLOT2_Status,
  Option_MediaSLOT2_RemainingNumber,
  Option_MediaSLOT2_RemainingTime,
  Option_MediaSLOT2_FormatEnableStatus,
  Option_Media_FormatProgressRate,
  Option_Interval_Rec_Status,
  Option_CustomWB_Execution_State,
  Option_CustomWB_Capture_get,
  Option_CustomWB_Capture_Frame_Size,
  Option_CustomWB_Capture_Operation,
  Option_Zoom_Operation_Status,
  Option_Zoom_Bar_Information,
  Option_Zoom_Type_Status,
  Option_MediaSLOT1_FileType,
  Option_MediaSLOT2_FileType,
  Option_MediaSLOT1_JpegQuality,
  Option_MediaSLOT2_JpegQuality,
  Option_MediaSLOT1_ImageSize,
  Option_MediaSLOT2_ImageSize,
  Option_RAW_FileCompressionType,
  Option_MediaSLOT1_RAW_FileCompressionType,
  Option_MediaSLOT2_RAW_FileCompressionType,
  Option_MediaSLOT1_QuickFormatEnableStatus,
  Option_MediaSLOT2_QuickFormatEnableStatus,
  Option_Cancel_Media_FormatEnableStatus,
  Option_Cancel_Media_FormatEnableStatus,
  Option_Get_Props,
  Option_Get_LiveView_Props,
  Option_getCustomPairWB,
  Option_EstimatePictureSize,
  Option_FocalPosition,
  Option_CustomWB_Capturable_Area,
  Option_cancelShoot,
  Option_setS2,
  Option_getMovie_Recording_Setting,
  Option_get_AF_Area_Position,
  Option_get_LiveViewArea,
  Option_GetOnly,
  Option_getSDKversion,
  Option_getSDKserial,
  Option_SetA,
  Option_SetB,
  Option_SetDefault,
  Option_SetFromJsonFile,
  Option_WriteToJsonFile,
  Option_DoDelay
};

// ----------------------------------------------------------------- define various pre-set environments ----------------------------------------------------------------------
//

// a reader from a JSON file or stream sets that data to the environment when it is pointed to 
//

// store each variable you want to read / write to file
struct jsonItemList
{
	std::uint32_t readStatus;
    std::int32_t fn;
	std::int32_t bias;
	std::int32_t ss;
	std::int32_t wb;
	std::int32_t fc;
	std::pair iso;
	std::int32_t imgsz;
};
typedef SCRSDK::CrInt32 CrError_JsonParam;
enum
{
	// set to true state means error in this bitmap
	// 
	CrError_None							= 0x0000,
	CrError_fn								= 0x0001,
	CrError_bias							= 0x0002, /* Do not use. Will be removed in the next release. */
	CrError_ss								= 0x0004,
	CrError_wb								= 0x0008,
	CrError_fc								= 0x0010,
	CrError_iso1							= 0x0020,
	CrError_iso2							= 0x0040,
	CrError_imgsz							= 0x0080	
};
jsonItemList g_JsonList;
jsonItemList g_currentList;
std::string myJsonFileName = "/mnt/c/linuxmirror/testJSON";
 
const std::string FNUM = "fNum";
const std::string BIAS = "bias";
const std::string SHUT_SPEED = "shutSpeed";
const std::string WHITE_BAL = "whiteBal";
const std::string FLASH_COMP = "flashComp";
const std::string ISO_SENS1 = "iso1Sens";
const std::string ISO_SENS2 = "iso2Sens";
const std::string IMG_SZ = "imgSz";

// default (e.g. inside)
//
struct camSettings
{
	// this is an example of a parameter that never changes these are per structure type (static)
    std::int32_t alwaysThis() { return 1; }
    // virtual function method is overriden with the override declaration in the next structure(s) if the pointer is set to it (dynamic)
	// this is an example or spare paramter
    virtual std::int32_t param1() { return 1; }
	// these are the parameters i envisage as the application settings
	virtual std::int32_t isParamError( CrError_JsonParam p ) { return 0; }
	virtual std::int32_t setFnum() { return 1; }
	virtual std::int32_t setBias() { return 1; }
	virtual std::int32_t setShutSpeed() { return 1; }
	virtual std::int32_t setWhiteBalance() { return 1; }
	virtual std::int32_t setFlashComp() { return 1; }
	virtual std::pair setIsoSens() { return make_pair(1,1); }
	virtual std::int32_t setImageSz() { return SCRSDK::CrImageSize::CrImageSize_S; }
	// this is only an example but shows how to change a calcualtion as a set-up
    virtual float calc1(std::int32_t a, std::int32_t b) { return static_cast<float>a/static_cast<float>b; }
};

// a non-default setting No.1 (e.g. summer evening)
// 
struct setA : camSettings
{
    std::int32_t alwaysThis() { return 2; }
    // override declaration makes it the master when the structure pointer is set to this
    std::int32_t param1() override { return 2; }
	std::int32_t isParamError( CrError_JsonParam p ) override { return 0; }
	std::int32_t setFnum() override { return 2; }
	std::int32_t setBias() override { return 2; }
	std::int32_t setShutSpeed() override  { return 2; }
	std::int32_t setWhiteBalance() override { return 2; }	
	std::int32_t setFlashComp() override { return 2; }
	std::pair setIsoSens() override { return make_pair(2,2); }
	std::int32_t setImageSz() override { return SCRSDK::CrImageSize::CrImageSize_VGA; }	
    float calc1(std::int32_t a, std::int32_t b) override { return static_cast<float>b/(2.0f*static_cast<float>a); }
};

// a non-default setting No.2 (e.g. winter morning)
//
struct setB : camSettings
{
    std::int32_t alwaysThis() { return 3; }
    // override declaration makes it the master when the structure pointer is set to this
    std::int32_t param1() override { return 3; }
	std::int32_t isParamError( CrError_JsonParam p ) override { return 0; }
	std::int32_t setFnum() override { return 3; }
	std::int32_t setBias() override { return 3; }
	std::int32_t setShutSpeed() override { return 3; }
	std::int32_t setWhiteBalance() override { return 3; }
	std::int32_t setFlashComp() override { return 3; }
	std::pair setIsoSens() override { return make_pair(3,3); }
	std::int32_t setImageSz() override { return SCRSDK::CrImageSize::CrImageSize_L; }	
    float calc1(std::int32_t a, std::int32_t b) override { return static_cast<float>b/(3.0f*static_cast<float>a); }
};

// json file is read to the global structure and returned by the methods
//
struct setJSON : camSettings
{
    std::int32_t alwaysThis() { return 99; }
    // override declaration makes it the master when the structure pointer is set to this
    std::int32_t param1() override { return 99; }
	std::int32_t isParamError( CrError_JsonParam p ) override { return (g_JsonList.readStatus&p); }
	std::int32_t setFnum() override { return g_JsonList.fn; }
	std::int32_t setBias() override { return g_JsonList.bias; }
	std::int32_t setShutSpeed() override { return g_JsonList.ss; }
	std::int32_t setWhiteBalance() override { return g_JsonList.wb; }
	std::int32_t setFlashComp() override { return g_JsonList.fc; }
	std::pair setIsoSens() override { return g_JsonList.iso; }
	std::int32_t setImageSz() override { return g_JsonList.imgsz; }	
    float calc1(std::int32_t a, std::int32_t b) override { return static_cast<float>b/(3.0f*static_cast<float>a); }
};

string JsonConfigDump( jsonItemList* jList ) 
{
   json request;
   request[FNUM] = jList->fn;
   request[BIAS] = jList->bias;
   request[SHUT_SPEED] = jList->ss;
   request[WHITE_BAL] = jList->wb;
   request[FLASH_COMP] = jList->fc;
   std::pair pp = jlist->iso;
   request[ISO_SENS1] = pp.first;
   request[ISO_SENS2] = pp.second;  
   request[IMG_SZ] = jlist->imgsz;  
   return request.dump();
}

void writeJSONFile(std::string FilNam, jsonItemList* jList)
{
   // write prettified JSON to specified file
   std::string s = JsonConfigDump( jList );
   std::ofstream o(FilNam);
   if (!o.is_open())
   {
       throw std::runtime_error{"Unable to open file"};
   }
   o << std::setw(4) << j << std::endl;
}

bool readJSONData(std::string_view message, jsonItemList* jList)
{
	jList->readStatus = 0;
	auto parsed = json::parse(message);
    std::string fn = parsed[FNUM];
	auto intFn = ParseStringToInt(fn);
	if (!intFn) 
		jList->readStatus |= CrError_fn;
	else
	    jList->fn = intFn;
	std::string bias = parsed[BIAS];
	auto intBias = ParseStringToInt(bias);
	if (!intBias) 
		jList->readStatus |= CrError_bias;
	else
	   jList->bias = intBias;
	std::string ss = parsed[SHUT_SPEED];
	auto intSS = ParseStringToInt(ss);
	if (!intSS) 
		jList->readStatus |= CrError_ss;
	else
	    jList->ss = intBias;
	std::string wb = parsed[WHITE_BAL];
	auto intWB = ParseStringToInt(wb);
	if (!intWB) 
		jList->readStatus |= CrError_wb;
	else
	    jList->wb = intWB;
	std::string fc = parsed[FLASH_COMP];
	auto intFC = ParseStringToInt(fc);
	if (!intFC) 
		jList->readStatus |= CrError_fc;
	else
	    jList->fc = intFC;
	std::string iso1 = parsed[ISO_SENS1];
	auto intIsoSens1 = ParseStringToInt(iso1);
	if (!intIsoSens1) 
		jList->readStatus |= CrError_iso1;		
	std::string iso2 = parsed[ISO_SENS2];
	auto intIsoSens2 = ParseStringToInt(iso2);
	if (!intIsoSens2) 
		jList->readStatus |= CrError_iso2;	
	if (((jList->readStatus&CrError_iso2)==0)&&((jList->readStatus&CrError_iso1)==0))
	   jList->fc = std::make_pair(intIsoSens1,intIsoSens2);
	std::string imgsz = parsed[IMG_SZ];
	auto intIS = ParseStringToInt(imgsz);
	if (!intIS) 
		jList->readStatus |= CrError_imgsz;
	else
	    jList->imgsz = intIS;
	return (readStatus==0);
}

bool readJSONFile(std::string fileName, jsonItemList* jList)
{
	jList->readStatus = 0;
	// read a JSON file
    std::ifstream i(fileName);
	if (!i.is_open())
    {
       throw std::runtime_error{"Unable to open file"};
    }
    json parsed;
    i >> parsed;
    std::string fn = parsed[FNUM];
	auto intFn = ParseStringToInt(fn);
	if (!intFn) 
		jList->readStatus |= CrError_fn;
	else
	    jList->fn = intFn;
	std::string bias = parsed[BIAS];
	auto intBias = ParseStringToInt(bias);
	if (!intBias) 
		jList->readStatus |= CrError_bias;
	else
	   jList->bias = intBias;
	std::string ss = parsed[SHUT_SPEED];
	auto intSS = ParseStringToInt(ss);
	if (!intSS) 
		jList->readStatus |= CrError_ss;
	else
	    jList->ss = intBias;
	std::string wb = parsed[WHITE_BAL];
	auto intWB = ParseStringToInt(wb);
	if (!intWB) 
		jList->readStatus |= CrError_wb;
	else
	    jList->wb = intWB;
	std::string fc = parsed[FLASH_COMP];
	auto intFC = ParseStringToInt(fc);
	if (!intFC) 
		jList->readStatus |= CrError_fc;
	else
	    jList->fc = intFC;
	std::string iso1 = parsed[ISO_SENS1];
	auto intIsoSens1 = ParseStringToInt(iso1);
	if (!intIsoSens1) 
		jList->readStatus |= CrError_iso1;		
	std::string iso2 = parsed[ISO_SENS2];
	auto intIsoSens2 = ParseStringToInt(iso2);
	if (!intIsoSens2) 
		jList->readStatus |= CrError_iso2;	
	if (((jList->readStatus&CrError_iso2)==0)&&((jList->readStatus&CrError_iso1)==0))
	   jList->fc = std::make_pair(intIsoSens1,intIsoSens2);
	std::string imgsz = parsed[IMG_SZ];
	auto intIS = ParseStringToInt(imgsz);
	if (!intIS) 
		jList->readStatus |= CrError_imgsz;
	else
	    jList->imgsz = intIS;
	return (readStatus==0);
}


// ================================================================ Main Proram ===============================================================================================
//
std::uint16_t main(std::uint16_t argc, std::char** argv)
{

	// Wrap everything in a try block.  Do this every time, 
	// because exceptions will be thrown for problems.
	//
	try 
	{  

	    // Define the command line object, and insert a message
	    // that describes the program. The "Command description message" 
	    // is printed last in the help text. The second argument is the 
	    // delimiter (usually space) and the last one is the version number. 
	    // The CmdLine object parses the argv array based on the Arg objects
	    // that it contains. 
		//
	    TCLAP::CmdLine cmd("Command description message", ' ', "0.9");

        // if you dont want help and version
		//
		// TCLAP::CmdLine cmd("this has no help or version info", ' ', "0.99", false );
		
	    // Tell the command line to ignore any unmatched args.
		//
	    cmd.ignoreUnmatched(true);

        // Define a Map between the program operation tags and the enumeration values which call that chosen operation
        //
		// The first item in the map defines the tag you supply to the command line of this 
		// application to activate the chosen method (the second paramter given)
		// which is the corresponding enumerted type for that operational state in OptionTCLAPAction within the alphaSonyCam class object
		//
        map<std::string, std::int32_t> activeFunctions;	
        activeFunctions.insert(std::make_pair("StartStopMovie",   Option_MovieRecord));
        activeFunctions.insert(std::make_pair("ReleaseShutterShoot",  Option_Release));
        activeFunctions.insert(std::make_pair("MediaFormatSlot1",  Option_MediaFormat_Slot1Offset));
        activeFunctions.insert(std::make_pair("MediaFormatSlot2",  Option_MediaFormat_Slot2Offset));
        activeFunctions.insert(std::make_pair("MediaQuickFormatSlot1",  Option_MediaQuickFormat_Slot1Offset));
        activeFunctions.insert(std::make_pair("MediaQuickFormatSlot2",  Option_MediaQuickFormat_Slot2Offset));
        activeFunctions.insert(std::make_pair("CancelMediaFormat",  Option_CancelMediaFormat));
        activeFunctions.insert(std::make_pair("SetShutterHalfReleaseUnlock",  Option_S1_unlock));
        activeFunctions.insert(std::make_pair("SetShutterHalfReleaseLock",  Option_S1_lock));
        activeFunctions.insert(std::make_pair("SetAELUnlock",  Option_AEL_unlock));
        activeFunctions.insert(std::make_pair("SetAELLock",  Option_AEL_lock));
        activeFunctions.insert(std::make_pair("SetFELUnlock",  Option_FEL_unlock));
        activeFunctions.insert(std::make_pair("SetFELLock",  Option_FEL_lock));
        activeFunctions.insert(std::make_pair("SetAWBLUnlock",  Option_AWBL_unlock));
        activeFunctions.insert(std::make_pair("SetAWBLLock",  Option_AWBL_lock));	
        activeFunctions.insert(std::make_pair("SetAFLUnlock",  Option_AFL_unlock));
        activeFunctions.insert(std::make_pair("SetAFLLLock",  Option_AFL_lock));
        activeFunctions.insert(std::make_pair("SetApertureFNum",  Option_FNumber));
        activeFunctions.insert(std::make_pair("SetExposureBiasCompensation",  Option_ExposureBiasCompensation));
        activeFunctions.insert(std::make_pair("SetFlashCompensation",  Option_FlashCompensation));
        activeFunctions.insert(std::make_pair("SetShuterSpeed",  Option_ShutterSpeed));
        activeFunctions.insert(std::make_pair("SetISOSensitivity",  Option_IsoSensitivity));
        activeFunctions.insert(std::make_pair("SetFocusArea",  Option_FocusArea));
        activeFunctions.insert(std::make_pair("SetExposureProgramMode",  Option_ExposureProgramMode));
        activeFunctions.insert(std::make_pair("SetStillFileCompressionFormat",  Option_CompressionFileFormatStill));
        activeFunctions.insert(std::make_pair("SetStillFileFormat",  Option_FileType));
        activeFunctions.insert(std::make_pair("SetStillJpegQuality",  Option_JpegQuality));
        activeFunctions.insert(std::make_pair("SetWhiteBalance",  Option_WhiteBalance));
        activeFunctions.insert(std::make_pair("SetFocusMode",  Option_FocusMode));
        activeFunctions.insert(std::make_pair("SetExposureMeteringMode",  Option_MeteringMode));
        activeFunctions.insert(std::make_pair("SetFlashMode",  Option_FlashMode));
        activeFunctions.insert(std::make_pair("SetWirelessFlashMode",  Option_WirelessFlash));
        activeFunctions.insert(std::make_pair("SetRedEyeRed",  Option_RedEyeReduction));
        activeFunctions.insert(std::make_pair("SetStillCaptureMode",  Option_DriveMode));
        activeFunctions.insert(std::make_pair("SetDynamicRangeOperator",  Option_DRO));
        activeFunctions.insert(std::make_pair("SetImageSize",  Option_ImageSize));
        activeFunctions.insert(std::make_pair("SetAspectRatio",  Option_AspectRatio));
        activeFunctions.insert(std::make_pair("SetPictureEffect",  Option_PictureEffect));
        activeFunctions.insert(std::make_pair("SetColorTemp",  Option_Colortemp));
        activeFunctions.insert(std::make_pair("SetBiaxialFineTuneDirAB",  Option_ColorTuningAB));
        activeFunctions.insert(std::make_pair("SetBiaxialFineTuneDirGM",  Option_ColorTuningGM));
        activeFunctions.insert(std::make_pair("SetLiveViewDisplayEffect",  Option_LiveViewDisplayEffect));
        activeFunctions.insert(std::make_pair("SetStillImageStoreDestination",  Option_StillImageStoreDestination));
        activeFunctions.insert(std::make_pair("SetPositionKeySetting",  Option_PriorityKeySettings));
        activeFunctions.insert(std::make_pair("SetDateTime",  Option_DateTime_Settings));
        activeFunctions.insert(std::make_pair("SetFocusMagnifierSetting",  Option_Focus_Magnifier_Setting));
        activeFunctions.insert(std::make_pair("SetNearFarEnable",  Option_NearFar));
        activeFunctions.insert(std::make_pair("SetAFAreaPosition", Option_NearFar_AF_Area));
        activeFunctions.insert(std::make_pair("SetZoomScale",  Option_Zoom_Scale));
        activeFunctions.insert(std::make_pair("SetZoom",  Option_Zoom_Setting));
        activeFunctions.insert(std::make_pair("SetZoomOperation",  Option_Zoom_Operation));
        activeFunctions.insert(std::make_pair("SetFileFormatMovie",  Option_Movie_File_Format));
		activeFunctions.insert(std::make_pair("GetMovieRecordingSetting",  Option_Movie_Recording_Setting));
        activeFunctions.insert(std::make_pair("SetMovieFrameRate",  Option_Movie_Recording_FrameRateSetting));
        activeFunctions.insert(std::make_pair("IntervalRecModeEnable",  Option_Interval_Rec_Mode));
        activeFunctions.insert(std::make_pair("SetStillImageTransSize",  Option_Still_Image_Trans_Size));
        activeFunctions.insert(std::make_pair("SetRawJPCSaveImage",  Option_RAW_J_PC_Save_Image));
        activeFunctions.insert(std::make_pair("SetLiveViewImageQuality",  Option_LiveView_Image_Quality));
        activeFunctions.insert(std::make_pair("SetStandbyCaptureWBOperation",  Option_CustomWB_Capture_Standby));
        activeFunctions.insert(std::make_pair("SetStandbyCaptureWBCapButton",  Option_CustomWB_Capture_Standby_Button));  
        activeFunctions.insert(std::make_pair("SetCaptureStandbyCancel",  Option_CustomWB_Capture_Standby_Cancel));
        activeFunctions.insert(std::make_pair("SetCustomWBCapture",  Option_CustomWB_Capture));
        activeFunctions.insert(std::make_pair("GetSnapshotInfo",  Option_SnapshotInfo));
        activeFunctions.insert(std::make_pair("GetBatteryRemain",  Option_BatteryRemain));
        activeFunctions.insert(std::make_pair("GetBatteryLevel",  Option_BatteryLevel));
        activeFunctions.insert(std::make_pair("GetMoveRecordState",  Option_RecordingState));
        activeFunctions.insert(std::make_pair("GetLiveViewStatus",  Option_LiveViewStatus));
        activeFunctions.insert(std::make_pair("GetFocusIndication",  Option_FocusIndication));
        activeFunctions.insert(std::make_pair("GetMediaSlot1Status",  Option_MediaSLOT1_Status));
        activeFunctions.insert(std::make_pair("GetMediaSlot1RemainingNumber",  Option_MediaSLOT1_RemainingNumber));
        activeFunctions.insert(std::make_pair("GetMediaSlot1RemainingTime",  Option_MediaSLOT1_RemainingTime));
        activeFunctions.insert(std::make_pair("GetMediaSlot1FormatStatus",  Option_MediaSLOT1_FormatEnableStatus));
        activeFunctions.insert(std::make_pair("GetMediaSlot2Status",  Option_MediaSLOT2_Status));
        activeFunctions.insert(std::make_pair("GetMediaSlot2RemainingNumber",  Option_MediaSLOT2_RemainingNumber));
        activeFunctions.insert(std::make_pair("GetMediaSlot2RemainingTime",  Option_MediaSLOT2_RemainingTime));
        activeFunctions.insert(std::make_pair("GetMediaSlot2FormatStatus",  Option_MediaSLOT2_FormatEnableStatus));
        activeFunctions.insert(std::make_pair("GetMediaFormatProgressRatePercent",  Option_Media_FormatProgressRate));
        activeFunctions.insert(std::make_pair("GetIntervalStatus",  Option_Interval_Rec_Status));
        activeFunctions.insert(std::make_pair("GetCustomWBExecutionStatus",  Option_CustomWB_Execution_State));
        activeFunctions.insert(std::make_pair("GetCustomWBCapture",  Option_CustomWB_Capture_get));
        activeFunctions.insert(std::make_pair("GetCaptureFrameSize",  Option_CustomWB_Capture_Frame_Size));
        activeFunctions.insert(std::make_pair("GetCustomWBOperation",  Option_CustomWB_Capture_Operation));
        activeFunctions.insert(std::make_pair("GetZoomOperationStatus",  Option_Zoom_Operation_Status));
        activeFunctions.insert(std::make_pair("GetZoomBarInfo",  Option_Zoom_Bar_Information));
        activeFunctions.insert(std::make_pair("GetZoomTypeStatus",  Option_Zoom_Type_Status));
        activeFunctions.insert(std::make_pair("GetMediaSLOT1FileType",  Option_MediaSLOT1_FileType));
        activeFunctions.insert(std::make_pair("GetMediaSLOT2FileType",  Option_MediaSLOT2_FileType));
        activeFunctions.insert(std::make_pair("GetMediaSLOT1JpegQuality",  Option_MediaSLOT1_JpegQuality));
        activeFunctions.insert(std::make_pair("GetMediaSLOT2JpegQuality",  Option_MediaSLOT2_JpegQuality));
        activeFunctions.insert(std::make_pair("GetMediaSLOT1ImageSize",  Option_MediaSLOT1_ImageSize));
        activeFunctions.insert(std::make_pair("GetMediaSLOT2ImageSize",  Option_MediaSLOT2_ImageSize));
        activeFunctions.insert(std::make_pair("GetRawCompressionType",  Option_RAW_FileCompressionType));
        activeFunctions.insert(std::make_pair("GetRawCompressionTypeSLOT1",  Option_MediaSLOT1_RAW_FileCompressionType));
        activeFunctions.insert(std::make_pair("GetRawCompressionTypeSLOT2",  Option_MediaSLOT2_RAW_FileCompressionType));
        activeFunctions.insert(std::make_pair("GetQuickFormatStatusSLOT1",  Option_MediaSLOT1_QuickFormatEnableStatus));
        activeFunctions.insert(std::make_pair("GetQuickFormatStatusSLOT2",  Option_MediaSLOT2_QuickFormatEnableStatus));
        activeFunctions.insert(std::make_pair("GetQuickFormatStatusCancel",  Option_Cancel_Media_FormatEnableStatus));
        activeFunctions.insert(std::make_pair("GetQuickFormatStatusCancel",  Option_Cancel_Media_FormatEnableStatus));		
        activeFunctions.insert(std::make_pair("GetProperties",  Option_Get_Props));
        activeFunctions.insert(std::make_pair("GetLiveViewProperties",  Option_Get_LiveView_Props));
		activeFunctions.insert(std::make_pair("GetCustomWBCaptureAsPair", Option_getCustomPairWB));
		activeFunctions.insert(std::make_pair("GetEstimatePictureSize", Option_EstimatePictureSize));
		activeFunctions.insert(std::make_pair("GetFocalPosition", Option_FocalPosition));
		activeFunctions.insert(std::make_pair("CustomWB_Capturable_Area", Option_CustomWB_Capturable_Area));
		activeFunctions.insert(std::make_pair("getSDKVersion", Option_getSDKversion));	
		activeFunctions.insert(std::make_pair("getSDKSerial", Option_getSDKserial));
		activeFunctions.insert(std::make_pair("cancelShoting", Option_cancelShoot));
		activeFunctions.insert(std::make_pair("setParamS2", Option_setS2));
		activeFunctions.insert(std::make_pair("getMovieRecordingSetting", Option_getMovie_Recording_Setting));
		activeFunctions.insert(std::make_pair("getAFAreaPosition", Option_get_AF_Area_Position));
		activeFunctions.insert(std::make_pair("getLiveAreaPosition", Option_get_LiveViewArea));
		activeFunctions.insert(std::make_pair("getOnly", Option_GetOnly));
		activeFunctions.insert(std::make_pair("usePresetA", Option_SetA));
		activeFunctions.insert(std::make_pair("usePresetB", Option_SetB));
		activeFunctions.insert(std::make_pair("usePresetDefaults", Option_SetDefault));	
		activeFunctions.insert(std::make_pair("useJsonFilePresets", Option_SetFromJsonFile));		
		activeFunctions.insert(std::make_pair("writeJsonFilePresets", Option_WriteToJsonFile));
		activeFunctions.insert(std::make_pair("doDelaySeconds", Option_DoDelay));

		
        // uncomment this line here if you want to use multiple command strings in one macro passed to this application
		//
#define ACTIVATE_STRING_FILTER
#if defined(ACTIVATE_STRING_FILTER)		
	    // Define a value argument and add it to the command line.
	    // A value arg defines a flag and a type of value that it expects,
   	    // such as "-c StartStopMovie".
	    //
		//
		// Set up a constraint for each allowable command strings to the camera interace
		//
		std::vector<std::string> allowed;
		// example like this for each tag you permit
		//
		// allowed.push_back("StartStopMovie");
		// allowed.push_back("ReleaseShutterShoot");
		// allowed.push_back("SetShutterHalfReleaseUnlock");


        // populate the string vector for command line tag choice directly from the map definition if you want use separate, then do defs as above in commented out code 
		//
        for (auto& item: activeFunctions)
        {
		    allowed.push_back(item.first);	
		}			
		ValuesConstraint<std::string> allowedVals( allowed );
		
	    // Adds a string which is the command associated with the camera attribute you want its filtered by allowed values
        //	
	    TCLAP::ValueArg<std::string> commandArg("c", "command", "Command to use", true, "zoom", &allowedVals);
#else
		// There is No filter with this one instead
		//
		TCLAP::ValueArg<std::string> commandArg("c", "command", "Command to use", true, "zoom", "string");
#endif
		
	    //
	    // Adds a integer which is the value you want to set the attribute to
        //	
        TCLAP::ValueArg<std::int32_t> intValArg("i", "IntValue", "integer value to use", true, 0, "int");
	    //
	    // Adds a long integer which is the value you want to set the attribute to
        //	
        TCLAP::ValueArg<std::int64_t> longValArg("l", "LongValue", "long integer value to use", true, 0, "long");
	    //
	    // Adds a float which is the value you want to set the attribute to
        //	
        TCLAP::ValueArg<float> floatValArg("f", "FloatValue", "float value to use", true, 0, "float");
	    //
	    // Adds a pair (integer and float) which is the values you want to set to the attributes
        //
        TCLAP::ValueArg<std::pair< std::int32_t, double> > pairIFValArg("p", "pairIFValue", "int,double pair", true, std::make_pair(0, 0.0f), "int,double", cmd);
	    //
	    // Adds a pair (of two integers) which is the values you want to set to the attributes
        //
        TCLAP::ValueArg<std::pair< std::int32_t, std::int32_t> > pair2IValArg("q", "pairIIValue", "int,int pair", true, std::make_pair(0, 0), "int,int", cmd);
	    //
	    // Adds a tie (of three integers) which is the values you want to set to the attributes
        //
        TCLAP::ValueArg<std::tie< std::int32_t, std::int32_t, std::int32_t> > tie3IValArg("t", "tie3IValue", "int,int,int tie", true, std::make_tie(0, 0, 0), "int,int,int", cmd);
	    //
	    // Adds a tie (of three integers) which is the values you want to set to the attributes
        //
        TCLAP::ValueArg<std::tuple<std::string, std::int32_t> > tupleSIValArg("u", "tupleSIValue", "string,int tuple", true, std::make_tuple("default", 0), "string,int", cmd);
		
	    // Add the argument commandArg to the CmdLine object. The CmdLine object
	    // uses this Arg to parse the command line.
		//	
	    cmd.add( commandArg );
	    cmd.add( intValArg );
	    cmd.add( floatValArg );
	    cmd.add( pairIFValArg );
	    cmd.add( pair2IValArg );
	    cmd.add( tie3IValArg );
	    cmd.add( tupleSIValArg );

        //  =========================== use the following to read each of these types in the code =============================
        //
	    //  std::int32_t intVal = intValArg.getValue();
	    //  float floatVal = floatValArg.getValue();
		//	std::pair pairIFVal = pairIFValArg.getValue();
		//	std::pair pair2IVal = pair2IValArg.getValue();
		//	std::tie tripleIVal = tie3IValArg.getValue();
		//	std::tuple tupleSIVal = tupleSIValArg.getValue();	

        // define the allowable pre-defined datasets and equations applicable (at current this is just set to arbitary data)
		// options are pre-defined sets (setA setB camSettings) or a set read from a JSON config file (type is setJSON)
		//
		setB b;
		setA a;
		camSettings c;
        setJSON fileSavedSettings;
        // set the pointer to any set (choose default)		
		camSettings *myCamSetUp = &c;
		
		// below is examples of how to use ::
		
		// select set B and get param1
		//
        //camSettings *myCamSetUp = &b;
		//int p1b = myCamSetUp->param1();
		
		// select set A and get param1	(test parameter)
        //		
        //myCamSetUp = &a;
		//int p1a = myCamSetUp->param1();
		
	    // select set c and do calc1 on the variables a1 and b1	
		//
        //myCamSetUp = &c;		
		//float c1 = myCamSetUp->calc1(p1b,p1a);
		
	
#ifndef ACTIVATE_STRING_FILTER		
	    // Define a switch and add it to the command line.
	    // A switch arg is a boolean argument and only defines a flag that
	    // indicates true or false.  In this example the SwitchArg adds itself
	    // to the CmdLine object as part of the constructor.  This eliminates
	    // the need to call the cmd.add() method.  All args have support in
	    // their constructors to add themselves directly to the CmdLine object.
	    // It doesn't matter which idiom you choose, they accomplish the same thing.
	    //
	    TCLAP::SwitchArg setSwitch("s", "exe", "Execute multiple functions specified", cmd, false);
		//
		// This switch will enable the use of the default pre-set environments rather than the command line args
		//
		TCLAP::SwitchArg envSwitch("e", "env", "Use default environment pre-sets", cmd, false);
#endif
		
	    // Parse the command line argv array.
	    //
	    cmd.parse( argc, argv );

	    // Get the value parsed by each arg. TOTEST:: I believe setValue is ignored if the string filter has been enabled 
        //		
	    std::string userCommand = commandArg.getValue();
		bool setValue = false;
		bool envValue = false;
		
        // with no string filter we permit with the "s" switch to send a series of command strings on the command line and this is read into a vector string
        //		
#ifndef ACTIVATE_STRING_FILTER
	    setValue = setSwitch.getValue();
	    envValue = envSwitch.getValue();
		
        // if set value is true you are specifying multiple commands (argument filter must be turned off for this)
		// each command is delimeted by regex_str which in this case is space
        //
        if ( setValue == true)
        {
			std::string regex_str = " ";
            auto tokens = splitStringLineToWordVector(userCommand, const std::string regex_str)			
		}
#endif
		
        // create camera class instance
	    //
        alphaSonyCam myAlphaCameraNo1;

        // initialise locale
        //
        myAlphaCameraNo1.localeInit();	
		
	    // initialise communication with the camera
	    //
        if ((myAlphaCameraNo1.alphaInit() == true) && ( setValue == false))
        {
		  // create enumeration object
		  //
	      SCRSDK::ICrCameraObjectInfo* e = myAlphaCameraNo1.Enumerate_Camera_USB();
          if ( e != NULL)
          {
			 // connect the camera
			 //
		     SCRSDK::CrDeviceHandle h = myAlphaCameraNo1.alphaConnectCamera(e); 

             // use the following calls to read each given type of variables from the standard input 
			 //
			 // std::int32_t timeVal = intValArg.getValue();
			 // long longV = longValArg.getValue();
	         // float floatVal = floatValArg.getValue();
			 // std::pair pairIFVal = pairIFValArg.getValue();
			 // std::pair pair2IVal = pair2IValArg.getValue();
			 // std::tie tripleIVal = tie3IValArg.getValue();
			 // std::tuple tupleSIVal = tupleSIValArg.getValue();

             OptionTCLAPAction listNumber = 0;
			 bool weGotMatch = false;	

             // uncomment if you just want to use a string vector for the commands rather than a map (also comment out the map code below)
             //			 
             // for (auto& item: allowed)
             // {
             //   ++listNumber;
             //   regex pattern(".*" + item + ".*");	
             //   std::cout<<item << "  " << listNumber <<std::endl; 
             //		

             // for loop using the map definition
             //			 
             for (auto& item: activeFunctions)
             {
				listNumber = static_cast<OptionTCLAPAction>item.second; 
                regex pattern(".*" + item.first + ".*");
                // std::cout<< "item in list  " << item.first << "  " << item.second <<std::endl; 			   

                if (regex_match(userCommand, pattern))	
                {
				   weGotMatch = true;
				   switch(listNumber)
				   {
					   case Option_MovieRecord:
					   myAlphaCameraNo1.alphaStartStopMovie( h );
					   std::cout << "movie record" << std::endl;
					   break;
		
					   case Option_Release:
	                   std::int32_t timeVal = intValArg.getValue();
					   myAlphaCameraNo1.alphaReleaseShutterShoot(h, timeVal);
					   std::cout << "release shutter shoot" << std::endl;
					   break;

					   case Option_MediaFormat_Slot1Offset:
					   myAlphaCameraNo1.alphaMediaFormatSlot1(h);
					   std::cout << "media format slot 1" << std::endl;
					   break;
					   
					   case Option_MediaFormat_Slot2Offset:
					   myAlphaCameraNo1.alphaMediaFormatSlot2(h);
					   std::cout << "media format slot 2" << std::endl;
					   break;	

					   case Option_MediaQuickFormat_Slot1Offset:
					   myAlphaCameraNo1.alphaMediaQuickFormatSlot1(h);
					   std::cout << "quick media format slot 1" << std::endl;
					   break;

					   case Option_MediaQuickFormat_Slot2Offset:
					   myAlphaCameraNo1.alphaMediaQuickFormatSlot2(h);
					   std::cout << "quick media format slot 2" << std::endl;
					   break;
					   
					   case Option_CancelMediaFormat:
					   std::int32_t timeVal = intValArg.getValue();
					   myAlphaCameraNo1.alphaCancelMediaFormat(h, timeVal);
					   std::cout << "cancel media format " << std::endl;
					   break;
					   
					   case Option_S1_unlock:
					   myAlphaCameraNo1.alphaSetShutterHalfReleaseUnlock(h);
					   std::cout << "set Shutter half release-unLock " << std::endl;
					   break;

					   case Option_S1_lock:
					   myAlphaCameraNo1.alphaSetShutterHalfReleaseLock(h);
					   std::cout << "set Shutter half release-Lock " << std::endl;
					   break;

					   case Option_AEL_unlock:
					   myAlphaCameraNo1.alphaSetAELUnlock(h);
					   std::cout << "set AEL-unLock " << std::endl;
					   break;

					   case Option_AEL_lock:
					   myAlphaCameraNo1.alphaSetAELLock(h);
					   std::cout << "set AEL-Lock " << std::endl;
					   break;

					   case Option_FEL_unlock:
					   myAlphaCameraNo1.alphaSetFELUnlock(h);
					   std::cout << "set FEL-unLock " << std::endl;
					   break;

					   case Option_FEL_lock:
					   myAlphaCameraNo1.alphaSetFELLock(h);
					   std::cout << "set FEL-Lock " << std::endl;
					   break;

					   case Option_AWBL_unlock:
					   myAlphaCameraNo1.alphaSetAWBLUnlock(h);
					   std::cout << "set AWB un-Lock " << std::endl;
					   break;

					   case Option_AWBL_lock:
					   myAlphaCameraNo1.alphaSetAWBLLock(h);
					   std::cout << "set AWB Lock " << std::endl;
					   break;

					   case Option_AFL_unlock:
					   myAlphaCameraNo1.alphaSetAFLUnlock(h);
					   std::cout << "set AFL un-Lock " << std::endl;
					   break;

					   case Option_AFL_lock:
					   myAlphaCameraNo1.alphaSetAFLLock(h)
					   std::cout << "set AFL Lock " << std::endl;
					   break;
					   
					   case Option_FNumber:
					   std::int32_t fNum = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetApertureFNum( h, static_cast<SCRSDK::CrCommandParam>fNum );
					   std::cout << " F-Number value @= " << fNum << std::endl;
					   break;

					   case Option_ExposureBiasCompensation:
					   std::int32_t bias = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetExposureBiasCompensation( h, static_cast<SCRSDK::CrCommandParam>bias );
					   std::cout << " exposure bias value @= " << bias << std::endl;
					   break;

					   case Option_FlashCompensation:
					   std::int32_t fc = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFlashCompensation( h, static_cast<SCRSDK::CrCommandParam>fc );
					   std::cout << " flash comp value @= " << fc << std::endl;
					   break;

					   case Option_ShutterSpeed:
					   std::int32_t ss = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetShuterSpeed( h, static_cast<SCRSDK::CrCommandParam>ss );
					   std::cout << " shutter speed f value @= " << ss << std::endl;
					   break;

					   case Option_IsoSensitivity:
					   std::pair pair2IVal = pair2IValArg.getValue();
					   myAlphaCameraNo1.alphaSetISOSensitivity( h, static_cast<SCRSDK::CrCommandParam>pair2IVal.first, static_cast<SCRSDK::CrISOMode>pair2IVal.second  );
					   myAlphaCameraNo1.printCrISOMode(static_cast<SCRSDK::CrISOMode>pair2IVal.second);
					   std::cout << " iso value @= " << pair2IVal.first << std::endl;
					   break;

					   case Option_FocusArea:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFocusArea( h, static_cast<SCRSDK::CrFocusArea>mode  );
					   myAlphaCameraNo1.printCrFocusArea(static_cast<SCRSDK::CrFocusArea>mode);
					   break;

					   case Option_ExposureProgramMode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetExposureProgramMode( h, static_cast<SCRSDK::CrExposureProgram>mode  );
					   myAlphaCameraNo1.printCrExposureProgram(static_cast<SCRSDK::CrExposureProgram>mode);
					   break;

					   case Option_CompressionFileFormatStill:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillFileCompressionFormat( h, static_cast<SCRSDK::CrCompressionFileFormat>mode  );
					   myAlphaCameraNo1.printCrCompressionFileFormat(static_cast<SCRSDK::CrCompressionFileFormat>mode);
					   break;

					   case Option_FileType:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillFileFormat( h, static_cast<SCRSDK::CrFileType>mode  );
					   myAlphaCameraNo1.printCrFileType(static_cast<SCRSDK::CrFileType>mode);
					   break;

					   case Option_JpegQuality:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillJpegQuality( h, static_cast<SCRSDK::CrJpegQuality>mode  );
					   myAlphaCameraNo1.printCrJpegQuality(static_cast<SCRSDK::CrJpegQuality>mode);
					   break;

					   case Option_WhiteBalance:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetWhiteBalance( h, static_cast<SCRSDK::CrWhiteBalanceSetting>mode  );
					   myAlphaCameraNo1.printCrWhiteBalanceSetting(static_cast<SCRSDK::CrWhiteBalanceSetting>mode);
					   break;

					   case Option_FocusMode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFocusMode( h, static_cast<SCRSDK::CrFocusMode>mode  );
					   myAlphaCameraNo1.printCrFocusMode(static_cast<SCRSDK::CrFocusMode>mode);
					   break;

					   case Option_MeteringMode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetExposureMeteringMode( h, static_cast<SCRSDK::CrMeteringMode>mode  );
					   myAlphaCameraNo1.printCrMeteringMode(static_cast<SCRSDK::CrMeteringMode>mode);
					   break;

					   case Option_FlashMode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFlashMode( h, static_cast<SCRSDK::CrFlashMode>mode  );
					   myAlphaCameraNo1.printCrFlashMode(static_cast<SCRSDK::CrFlashMode>mode);
					   break;

					   case Option_WirelessFlash:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetWirelessFlashMode( h, static_cast<SCRSDK::CrWirelessFlash>mode  );
					   myAlphaCameraNo1.printCrWirelessFlash(static_cast<SCRSDK::CrWirelessFlash>mode);
					   break;

					   case Option_RedEyeReduction:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetRedEyeRed( h, static_cast<SCRSDK::CrRedEyeReduction>mode  );
					   myAlphaCameraNo1.printCrRedEyeReduction(static_cast<SCRSDK::CrRedEyeReduction>mode);
					   break;

					   case Option_DriveMode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillCaptureMode( h, static_cast<SCRSDK::CrDriveMode>mode  );
					   myAlphaCameraNo1.printCrDriveMode(static_cast<SCRSDK::CrDriveMode>mode);
					   break;

					   case Option_DRO:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetDynamicRangeOperator( h, static_cast<SCRSDK::CrDRangeOptimizer>mode  );
					   myAlphaCameraNo1.printCrDRangeOptimizer(static_cast<SCRSDK::CrDRangeOptimizer>mode);
					   break;

					   case Option_ImageSize:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetImageSize( h, static_cast<SCRSDK::CrImageSize>mode  );
					   myAlphaCameraNo1.printCrImageSize:(static_cast<SCRSDK::CrImageSize>mode);
					   break;

					   case Option_AspectRatio:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetAspectRatio( h, static_cast<SCRSDK::CrAspectRatioIndex>mode  );
					   myAlphaCameraNo1.printCrAspectRatioIndex(static_cast<SCRSDK::CrAspectRatioIndex>mode);
					   break;

					   case Option_PictureEffect:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetPictureEffect( h, static_cast<SCRSDK::CrPictureEffect>mode  );
					   myAlphaCameraNo1.printCrPictureEffect(static_cast<SCRSDK::CrPictureEffect>mode);
					   break;

					   case Option_Colortemp:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetColorTemp( h, static_cast<SCRSDK::CrColortemp>mode  );
					   myAlphaCameraNo1.printCrColortemp(static_cast<SCRSDK::CrColortemp>mode);
					   break;

					   case Option_ColorTuningAB:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetBiaxialFineTuneDirAB( h, static_cast<SCRSDK::CrColorTuning>mode  );
					   myAlphaCameraNo1.printCrColorTuning(static_cast<SCRSDK::CrColorTuning>mode);
					   break;

					   case Option_ColorTuningGM:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetBiaxialFineTuneDirGM( h, static_cast<SCRSDK::CrColorTuning>mode  );
					   myAlphaCameraNo1.printCrColorTuning(static_cast<SCRSDK::CrColorTuning>mode);
					   break;

					   case Option_LiveViewDisplayEffect:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetLiveViewDisplayEffect( h, static_cast<SCRSDK::CrLiveViewDisplayEffect>mode  );
					   myAlphaCameraNo1.printCrLiveViewDisplayEffect(static_cast<SCRSDK::CrLiveViewDisplayEffect>mode);
					   break;

					   case Option_StillImageStoreDestination:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillImageStoreDestination( h, static_cast<SCRSDK::CrStillImageStoreDestination>mode  );
					   myAlphaCameraNo1.printCrStillImageStoreDestination(static_cast<SCRSDK::CrStillImageStoreDestination>mode);
					   break;

					   case Option_PriorityKeySettings:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetPositionKeySetting( h, static_cast<SCRSDK::CrPriorityKeySettings>mode  );
					   myAlphaCameraNo1.printCrPriorityKeySettings(static_cast<SCRSDK::CrPriorityKeySettings>mode);
					   break;

					   case Option_DateTime_Settings:
					   long mode = longValArg.getValue();
					   myAlphaCameraNo1.alphaSetDateTime( h, mode  );
					   std::cout << "date time @= " << mode << std::endl;
					   break;

					   case Option_Focus_Magnifier_Setting:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFocusMagnifierSetting( h, static_cast<SCRSDK::CrCommandParam>mode  );
					   std::cout << "focus mag @= " << mode << std::endl;
					   break;

					   case Option_NearFar:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetNearFarEnable( h, static_cast<SCRSDK::CrNearFarEnableStatus>mode  );
					   myAlphaCameraNo1.printCrNearFarEnableStatus(static_cast<SCRSDK::CrNearFarEnableStatus>mode);
					   break;

					   case Option_NearFar_AF_Area:
					   std::pair xyCoord = pair2IValArg.getValue();
					   myAlphaCameraNo1.alphaSetAFAreaPosition( h, static_cast<CrInt16>xyCoord.first, static_cast<CrInt16>xyCoord.second  );
					   std::cout << "near far x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl; 
					   break;

					   case Option_Zoom_Scale:
					   std::int32_t mode = intValArg.getValue();
					   SCRSDK::CrCommandParam setVal = myAlphaCameraNo1.alphaSetZoomScale( h, static_cast<SCRSDK::CrCommandParam>mode  );
					   std::cout << "set Zoom Scale @= " << setVal << std::endl;
					   break;

					   case Option_Zoom_Setting:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetZoom( h, static_cast<SCRSDK::CrZoomSettingType>mode  );
					   myAlphaCameraNo1.printCrZoomSettingType(static_cast<SCRSDK::CrZoomSettingType>mode);
					   break;

					   case Option_Zoom_Operation:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetZoomOperation( h, static_cast<SCRSDK::CrZoomOperation>mode  );
					   myAlphaCameraNo1.printCrZoomOperation(static_cast<SCRSDK::CrZoomOperation>mode);
					   break;

					   case Option_Movie_File_Format:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetFileFormatMovie( h, static_cast<SCRSDK::CrFileFormatMovie>mode  );
					   myAlphaCameraNo1.printCrFileFormatMovie(static_cast<SCRSDK::CrFileFormatMovie>mode);
					   break;

					   case Option_Movie_Recording_Setting:
					   SCRSDK::CrRecordingSettingMovie ffm = myAlphaCameraNo1.alphaMovieRecordingSetting(h);
					   myAlphaCameraNo1.printCrRecordingSettingMovie(ffm);
					   break;
					   
					   case Option_Movie_Recording_FrameRateSetting:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetMovieFrameRate( h, static_cast<SCRSDK::CrRecordingFrameRateSettingMovie>mode  );
					   myAlphaCameraNo1.printCrRecordingFrameRateSettingMovie(static_cast<SCRSDK::CrRecordingFrameRateSettingMovie>mode);
					   break;

					   case Option_Interval_Rec_Mode:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaIntervalRecModeEnable( h, static_cast<SCRSDK::CrIntervalRecMode>mode  );
					   myAlphaCameraNo1.printCrIntervalRecMode(static_cast<SCRSDK::CrIntervalRecMode>mode);
					   break;

					   case Option_Still_Image_Trans_Size:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStillImageTransSize( h, static_cast<SCRSDK::CrPropertyStillImageTransSize>mode  );
					   myAlphaCameraNo1.printCrPropertyStillImageTransSize(static_cast<SCRSDK::CrPropertyStillImageTransSize>mode);
					   break;

					   case Option_RAW_J_PC_Save_Image:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetRawJPCSaveImage( h, static_cast<SCRSDK::CrPropertyRAWJPCSaveImage>mode  );
					   myAlphaCameraNo1.printCrPropertyRAWJPCSaveImage(static_cast<SCRSDK::CrPropertyRAWJPCSaveImage>mode);
					   break;

					   case Option_LiveView_Image_Quality:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetLiveViewImageQuality( h, static_cast<SCRSDK::CrPropertyLiveViewImageQuality>mode  );
					   myAlphaCameraNo1.printCrPropertyLiveViewImageQuality(static_cast<SCRSDK::CrPropertyLiveViewImageQuality>mode);
					   break;

					   case Option_CustomWB_Capture_Standby:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStandbyCaptureWBOperation( h, static_cast<SCRSDK::CrPropertyCustomWBOperation>mode  );
					   myAlphaCameraNo1.printCrPropertyCustomWBOperation(static_cast<SCRSDK::CrPropertyCustomWBOperation>mode);
					   break;

					   case Option_CustomWB_Capture_Standby_Button:   
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetStandbyCaptureWBCapButton( h, static_cast<SCRSDK::CrPropertyCustomWBCaptureButton>mode  );
					   myAlphaCameraNo1.printCrPropertyCustomWBCaptureButton(static_cast<SCRSDK::CrPropertyCustomWBCaptureButton>mode);
					   break;
					   
					   case Option_CustomWB_Capture_Standby_Cancel:
					   std::int32_t mode = intValArg.getValue();
					   myAlphaCameraNo1.alphaSetCaptureStandbyCancel( h, static_cast<SCRSDK::CrCommandParam>mode  );
					   myAlphaCameraNo1.printCrCommandParam(static_cast<SCRSDK::CrCommandParam>mode);
					   break;

					   case Option_CustomWB_Capture:
					   std::pair xyCoord = pair2IValArg.getValue();
					   myAlphaCameraNo1.alphaSetCustomWBCapture( h, static_cast<CrInt16>xyCoord.first, static_cast<CrInt16>xyCoord.second  );
					   std::cout << "Custom WB Capture x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl;
					   break;

					   case Option_SnapshotInfo:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetSnapshotInfo(h);
					   std::cout << " Snaphot Info @= " << retVal << std::endl;					   
					   break;
					   
					   case Option_BatteryRemain:
					   SCRSDK::CrInt16u retVal = myAlphaCameraNo1.alphaGetBatteryRemain(h);
					   std::cout << " Battery Remaining @= " << retVal << std::endl;
					   break;

					   case Option_BatteryLevel:
					   SCRSDK::CrBatteryLevel retVal = myAlphaCameraNo1.alphaGetBatteryLevel(h);
					   myAlphaCameraNo1.printBatteryLevel( retVal );
					   break;

					   case Option_RecordingState:
					   SCRSDK::CrMovie_Recording_State retVal = myAlphaCameraNo1.alphaGetMoveRecordState(h);
					   myAlphaCameraNo1.printCrMovie_Recording_State(retVal);
					   break;

					   case Option_LiveViewStatus:
					   SCRSDK::CrLiveViewStatus retVal = myAlphaCameraNo1.alphaGetLiveViewStatus(h);
					   myAlphaCameraNo1.printCrLiveViewStatus:(retVal);
					   break;

					   case Option_FocusIndication:
					   SCRSDK::CrFocusIndicator retVal = myAlphaCameraNo1.alphaGetFocusIndication(h);
					   myAlphaCameraNo1.printCrFocusIndicator(retVal);
					   break;
						   
					   case Option_MediaSLOT1_Status:
					   SCRSDK::CrSlotStatus retVal = myAlphaCameraNo1.alphaGetMediaSlot1Status(h);
					   myAlphaCameraNo1.printCrSlotStatus(retVal);
					   break;

					   case Option_MediaSLOT1_RemainingNumber:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot1RemainingNumber(h);
					   std::cout << " slot 1 remaining number @= " << retVal << std::endl;						   
					   break;

					   case Option_MediaSLOT1_RemainingTime:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot1RemainingTime(h);
					   std::cout << " slot 1 remaining time @= " << retVal << std::endl;					   
					   break;

					   case Option_MediaSLOT1_FormatEnableStatus:
					   SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetMediaSlot1FormatStatus(h);
					   myAlphaCameraNo1.printCrMediaFormat(retVal);
					   break;

					   case Option_MediaSLOT2_Status:
					   SCRSDK::CrSlotStatus retVal = myAlphaCameraNo1.alphaGetMediaSlot2Status(h);
					   myAlphaCameraNo1.printCrSlotStatus(retVal);
					   break;

					   case Option_MediaSLOT2_RemainingNumber:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot2RemainingNumber(h);
					   std::cout << " slot 2 remaining number @= " << retVal << std::endl;	
					   break;

					   case Option_MediaSLOT2_RemainingTime:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot2RemainingTime(h);
					   std::cout << " slot 2 remaining time @= " << retVal << std::endl;					   
					   break;

					   case Option_MediaSLOT2_FormatEnableStatus:
					   SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetMediaSlot2FormatStatus(h);
					   myAlphaCameraNo1.printCrMediaFormat(retVal);
					   break;
					   
					   case Option_Media_FormatProgressRate:
					   float formatPercent = alphaGetMediaFormatProgressRatePercent(h);
					   std::cout << " format percent @= " << formatPercent << std::endl;
					   break;
					   
					   case Option_Interval_Rec_Status:
					   SCRSDK::CrIntervalRecStatus retVal = myAlphaCameraNo1.alphaGetIntervalStatus(h);
					   myAlphaCameraNo1.printCrIntervalRecStatus(retVal);
					   break;
						   
					   case Option_CustomWB_Execution_State:
					   SCRSDK::CrPropertyCustomWBExecutionState retVal = myAlphaCameraNo1.alphaGetCustomWBExecutionStatus(h);
					   myAlphaCameraNo1.printCrPropertyCustomWBExecutionState(retVal);
					   break;

                       // this one seems the same as the set command ??
					   //
					   case Option_CustomWB_Capture_get:
					   std::pair xyCoord = myAlphaCameraNo1.alphaGetCustomWBCaptureAsPair(h);
					   std::cout << "Get custom WB Capture x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl;
					   break;

					   case Option_CustomWB_Capture_Frame_Size:
					   auto frameHeightWidth = myAlphaCameraNo1.alphaGetCaptureFrameSizeAsPair(h);
					   std::cout << "Frame height @= " << frameHeightWidth.first << " width @= " << frameHeightWidth.second << std::endl; 
					   break;

					   case Option_CustomWB_Capture_Frame_Size_As_Tuple:
					   auto frameHeightWidth = myAlphaCameraNo1.alphaGetCaptureFrameSizeAsTuple(h);
					   std::cout << "Frame height @= " << std::get<0>(frameHeightWidth) << " width @= " << std::get<1>(frameHeightWidth) << std::endl; 
					   break;
					   
					   case Option_CustomWB_Capture_Operation:
					   SCRSDK::CrPropertyCustomWBOperation retVal = myAlphaCameraNo1.alphaGetCustomWBOperation(h);
					   myAlphaCameraNo1.printCrPropertyCustomWBOperation(retVal);
					   break;

					   case Option_Zoom_Operation_Status:
					   SCRSDK::CrZoomOperationEnableStatus retVal = myAlphaCameraNo1.alphaGetZoomOperationStatus(h);
					   myAlphaCameraNo1.printCrZoomOperationEnableStatus(retVal);
					   break;

					   case Option_Zoom_Bar_Information:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetZoomBarInfo(h);
					   std::cout << "zoom bar info @= " << retVal << std::endl;
					   break;

					   case Option_Zoom_Type_Status:
					   SCRSDK::CrZoomTypeStatus retVal = myAlphaCameraNo1.alphaGetZoomTypeStatus(h);
					   myAlphaCameraNo1.printCrZoomTypeStatus(retVal);
					   break;

					   case Option_MediaSLOT1_FileType:
					   SCRSDK::CrFileType retVal = myAlphaCameraNo1.alphaGetMediaSLOT1FileType(h);
					   myAlphaCameraNo1.printCrFileType(retVal);
					   break;

					   case Option_MediaSLOT2_FileType:
					   SCRSDK::CrFileType retVal = myAlphaCameraNo1.alphaGetMediaSLOT2FileType(h);
					   myAlphaCameraNo1.printCrFileType(retVal);
					   break;					   

					   case Option_MediaSLOT1_JpegQuality:
					   SCRSDK::CrJpegQuality retVal = myAlphaCameraNo1.alphaGetMediaSLOT1JpegQuality(h);
					   myAlphaCameraNo1.printCrJpegQuality(retVal);
					   break;
					   
					   case Option_MediaSLOT2_JpegQuality:
					   SCRSDK::CrJpegQuality retVal = myAlphaCameraNo1.alphaGetMediaSLOT2JpegQuality(h);
					   myAlphaCameraNo1.printCrJpegQuality(retVal);
					   break;

					   case Option_MediaSLOT1_ImageSize:
					   SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetMediaSLOT1ImageSize(h);
					   myAlphaCameraNo1.printCrImageSize:(retVal);
					   break;

					   case Option_MediaSLOT2_ImageSize:
					   SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetMediaSLOT2ImageSize(h);
					   myAlphaCameraNo1.printCrImageSize:(retVal);
					   break;

					   case Option_RAW_FileCompressionType:
					   SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionType(h);
					   myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					   break;
					   
					   case Option_MediaSLOT1_RAW_FileCompressionType:
					   SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionTypeSLOT1(h);
					   myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					   break;

					   case Option_MediaSLOT2_RAW_FileCompressionType:
					   SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionTypeSLOT2(h);
					   myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					   break;

					   case Option_MediaSLOT1_QuickFormatEnableStatus:
					   SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusSLOT1(h);
					   myAlphaCameraNo1.printCrMediaFormat(retVal);
					   break;

					   case Option_MediaSLOT2_QuickFormatEnableStatus:
					   SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusSLOT2(h);
					   myAlphaCameraNo1.printCrMediaFormat(retVal);
					   break;

					   case Option_Cancel_Media_FormatEnableStatus:
					   SCRSDK::CrCancelMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusCancel(h);
					   myAlphaCameraNo1.printCrCancelMediaFormat(retVal);
					   break;

					   case Option_EstimatePictureSize:
					   SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetEstimatePictureSize(h);
					   myAlphaCameraNo1.printCrImageSize:(retVal);
					   break;
					   
					   case Option_FocalPosition:
					   SCRSDK::CrFocusArea retVal = myAlphaCameraNo1.alphaGetFocalPosition(h);
					   myAlphaCameraNo1.printCrFocusArea(retVal);
					   break;

                       case Option_CustomWB_Capturable_Area:
					   SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetCustomWBCapturableArea(h);
					   std::cout << "CustomWB Capture Area @=  " << retVal << std::endl;
					   break;
					   
					   case Option_Get_Props:
					   bool b = myAlphaCameraNo1.alphaGetProperties(h);
					   break;

					   case Option_Get_LiveView_Props:
					   myAlphaCameraNo1.alphaGetLiveViewProperties(h);				 
					   break;

					   case Option_getCustomPairWB:
					   std::pair<CrInt16u, CrInt16u> pairname = myAlphaCameraNo1.alphaGetCustomWBCaptureAsPair(h);
					   std::cout << "CustomWB Capture x @=  " << pairname.first << " y @= " << pairname.second << std::endl;
					   break;

                       case option_cancelShoot:
					   SCRSDK::CrCommandParam setVal = SCRSDK::CrCommandParam::CrCommandParam_Down;
					   SCRSDK::CrCommandParam setVal = myAlphaCameraNo1.alphaCancelShooting(h, setVal);
					   myAlphaCameraNo1.printCrCommandParam(setVal);
					   break;

                       case Option_setS2:
					   std::int32_t s2set = intValArg.getValue();
					   s2set = myAlphaCameraNo1.alphaSetParameterS2( h, static_cast<SCRSDK::CrCommandParam>s2set );
					   myAlphaCameraNo1.printCrCommandParam(static_cast<SCRSDK::CrCommandParam>s2set);
                       break;

                       case Option_getMovie_Recording_Setting:
                       SCRSDK::CrFileFormatMovie retVal = myAlphaCameraNo1.alphaMovieRecordingSetting(h);		
                       myAlphaCameraNo1.printCrFileFormatMovie(SCRSDK::CrFileFormatMovie retVal);
                       break;

                       case Option_get_AF_Area_Position:
                       SCRSDK::CrFocusArea retVal = myAlphaCameraNo1.alphaAFAreaPosition(h);
                       myAlphaCameraNo1.printCrFocusArea(retVal);	
                       break;

                       case Option_get_LiveViewArea:		
                       SCRSDK::CrInt32u retVal myAlphaCameraNo1.alphaGetLiveViewArea(h);
                       std::cout << "Live view area @= " << retVal << std::endl;
                       break;

                       case Option_GetOnly:
                       SCRSDK::CrInt32u getVal = alphaGetOnly(h);
                       std::cout << " get Only @= " << getVal << std::endl;
                       break;
					   
                       case Option_getSDKversion:
					   auto sdkVer = myAlphaCameraNo1.alphaGetSDKVersion();
					   // print as tuple :
                       // std::cout << "SDK version major @=  " << std::get<0>(sdkVer) << " minor @= " << std::get<1>(sdkVer) << " patch @= " << std::get<2>(sdkVer) << std::endl;
					   // or print with a tie :
					   // std::make_tie(major,minor,patch) = sdkVer;
					   auto& [major,minor,patch] = sdkVer;
					   std::cout << "SDK version major @=  " << major << " minor @= " << minor << " patch @= " << patch << std::endl;
					   break;

                       case Option_getSDKserial:
					   auto sdkVer = myAlphaCameraNo1.alphaGetSDKSerial();
					   std::cout << "SDK serial @=  " << sdkVer << std::endl;
					   break;
 					   
                       default:
					   std::cout << "Inavlid option passed - parser error - check this case code!" << std::endl;
                       break;					   
				   }
                }
				// exit the iteration if we got a match
				//
                if (weGotMatch == true)
                {
                  break;
                }				  
             }
             
             // disconnect the camera
             //			 
		     bool b = myAlphaCameraNo1.alphaDisconnect(h);
	      }	
		  // terminate the session
		  //
          bool term = myAlphaCameraNo1.alphaTerminate();		  
        }
		// with no string filter multiple unchecked commands may be executed in one execution of the command
		//
#ifndef ACTIVATE_STRING_FILTER
        else if ((myAlphaCameraNo1.alphaInit() == true) && (setValue == true))
        {
		  // create enumeration object
		  //
	      SCRSDK::ICrCameraObjectInfo* e = myAlphaCameraNo1.Enumerate_Camera_USB();
          if ( e != NULL)
          {
			 // connect the camera
			 //
		     SCRSDK::CrDeviceHandle h = myAlphaCameraNo1.alphaConnectCamera(e); 

             // use the following to read variables from the standard input 
			 //
			 // std::int32_t timeVal = intValArg.getValue();
			 // long longV = longValArg.getValue();
	         // float floatVal = floatValArg.getValue();
			 // std::pair pairIFVal = pairIFValArg.getValue();
			 // std::pair pair2IVal = pair2IValArg.getValue();
			 // std::tie tripleIVal = tie3IValArg.getValue();
			 // std::tuple tupleSIVal = tupleSIValArg.getValue();

             OptionTCLAPAction listNumber = 0;
			 bool weGotMatch = false;	

             // uncomment and replace the code starting (auto& item: activeFunctions)
			 // if you just want to use a string vector for the commands rather than a map
             //			 
             // for (auto& item: allowed)
             // {
             //   ++listNumber;
             //   regex pattern(".*" + item + ".*");	
             //   std::cout<<item << "  " << listNumber <<std::endl; 
             //	
             for (auto& tk: tokens)
             {				 
                 for (auto& item: activeFunctions)
                 {
				    listNumber = static_cast<OptionTCLAPAction>item.second; 
                    regex pattern(".*" + item.first + ".*");
                    std::cout<<item.first << "  " << listNumber <<std::endl; 			   

                    if (regex_match(tk, pattern))	
                    {
				       weGotMatch = true;
			   	       switch(listNumber)
				       {
					       case Option_MovieRecord:
					       myAlphaCameraNo1.alphaStartStopMovie( h );
					       std::cout << "movie record" << std::endl;
					       break;
		
					       case Option_Release:
	                       std::int32_t timeVal = intValArg.getValue();
					       myAlphaCameraNo1.alphaReleaseShutterShoot(h, timeVal);
					       std::cout << "release shutter shoot" << std::endl;
					       break;

					       case Option_MediaFormat_Slot1Offset:
					       myAlphaCameraNo1.alphaMediaFormatSlot1(h);
					       std::cout << "media format slot 1" << std::endl;
					       break;
					   
					       case Option_MediaFormat_Slot2Offset:
					       myAlphaCameraNo1.alphaMediaFormatSlot2(h);
					       std::cout << "media format slot 2" << std::endl;
					       break;	

					       case Option_MediaQuickFormat_Slot1Offset:
					       myAlphaCameraNo1.alphaMediaQuickFormatSlot1(h);
					       std::cout << "quick media format slot 1" << std::endl;
					       break;

					       case Option_MediaQuickFormat_Slot2Offset:
					       myAlphaCameraNo1.alphaMediaQuickFormatSlot2(h);
					       std::cout << "quick media format slot 2" << std::endl;
					       break;
					   
					       case Option_CancelMediaFormat:
					       std::int32_t timeVal = intValArg.getValue();
					       myAlphaCameraNo1.alphaCancelMediaFormat(h, timeVal);
					       std::cout << "cancel media format " << std::endl;
					       break;
					   
					       case Option_S1_unlock:
					       myAlphaCameraNo1.alphaSetShutterHalfReleaseUnlock(h);
					       std::cout << "set Shutter half release-unLock " << std::endl;
					       break;

					       case Option_S1_lock:
					       myAlphaCameraNo1.alphaSetShutterHalfReleaseLock(h);
					       std::cout << "set Shutter half release-Lock " << std::endl;
					       break;

					       case Option_AEL_unlock:
					       myAlphaCameraNo1.alphaSetAELUnlock(h);
					       std::cout << "set AEL-unLock " << std::endl;
					       break;

					       case Option_AEL_lock:
					       myAlphaCameraNo1.alphaSetAELLock(h);
					       std::cout << "set AEL-Lock " << std::endl;
					       break;

					       case Option_FEL_unlock:
					       myAlphaCameraNo1.alphaSetFELUnlock(h);
					       std::cout << "set FEL-unLock " << std::endl;
					       break;

					       case Option_FEL_lock:
					       myAlphaCameraNo1.alphaSetFELLock(h);
					       std::cout << "set FEL-Lock " << std::endl;
					       break;

					       case Option_AWBL_unlock:
					       myAlphaCameraNo1.alphaSetAWBLUnlock(h);
					       std::cout << "set AWB un-Lock " << std::endl;
					       break;

					       case Option_AWBL_lock:
					       myAlphaCameraNo1.alphaSetAWBLLock(h);
					       std::cout << "set AWB Lock " << std::endl;
					       break;

					       case Option_AFL_unlock:
					       myAlphaCameraNo1.alphaSetAFLUnlock(h);
					       std::cout << "set AFL un-Lock " << std::endl;
					       break;

					       case Option_AFL_lock:
					       myAlphaCameraNo1.alphaSetAFLLock(h)
					       std::cout << "set AFL Lock " << std::endl;
					       break;
					   
					       case Option_FNumber:
						   // when envValue condition has been set true with -s switch read either an environment setting or the json file 
						   // instead of the command line
						   //
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_fn )==0) 
					              g_currentList.fn = myCamSetUp->setFnum();
						   }
						   else
						   {
					          g_currentList.fn = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetApertureFNum( h, static_cast<SCRSDK::CrCommandParam>g_currentList.fn );
					       std::cout << " F-Number value @= " << g_currentList.fn << std::endl;
					       break;

					       case Option_ExposureBiasCompensation:
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_bias )==0) 
							      g_currentList.bias = myCamSetUp->setBias(); 
						   }
						   else
						   {
					          g_currentList.bias = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetExposureBiasCompensation( h, static_cast<SCRSDK::CrCommandParam>g_currentList.bias );
					       std::cout << " exposure bias value @= " << g_currentList.bias << std::endl;
					       break;

					       case Option_FlashCompensation:
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_fc )==0) 
					              g_currentList.fc = myCamSetUp->setFlashComp();
						   }
						   else
						   {
					          g_currentList.fc = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetFlashCompensation( h, static_cast<SCRSDK::CrCommandParam>g_currentList.fc );
					       std::cout << " flash comp value @= " << g_currentList.fc << std::endl;
					       break;

					       case Option_ShutterSpeed:
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_ss )==0) 
							      g_currentList.ss = myCamSetUp->setShutSpeed(); 
						   }
						   else
						   {
					          g_currentList.ss = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetShuterSpeed( h, static_cast<SCRSDK::CrCommandParam>g_currentList.ss );
					       std::cout << " shutter speed f value @= " << g_currentList.ss << std::endl;
					       break;

					       case Option_IsoSensitivity:					   
						   if (envValue == true)
						   {
							  if ((myCamSetUp->isParamError( CrError_iso1 )==0)&&(myCamSetUp->isParamError( CrError_iso2 )==0)) 
							      g_currentList.iso = myCamSetUp->setIsoSens(); 
						   }
						   else
						   {
					          g_currentList.iso = pair2IValArg.getValue();
						   }						    
					       myAlphaCameraNo1.alphaSetISOSensitivity( h, static_cast<SCRSDK::CrCommandParam>g_currentList.iso.first, static_cast<SCRSDK::CrISOMode>g_currentList.iso.second  );
					       myAlphaCameraNo1.printCrISOMode(static_cast<SCRSDK::CrISOMode>g_currentList.iso.second);
					       std::cout << " iso value @= " << g_currentList.iso.first << std::endl;
					       break;

					       case Option_FocusArea:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetFocusArea( h, static_cast<SCRSDK::CrFocusArea>mode  );
					       myAlphaCameraNo1.printCrFocusArea(static_cast<SCRSDK::CrFocusArea>mode);
					       break;

					       case Option_ExposureProgramMode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetExposureProgramMode( h, static_cast<SCRSDK::CrExposureProgram>mode  );
					       myAlphaCameraNo1.printCrExposureProgram(static_cast<SCRSDK::CrExposureProgram>mode);
					       break;

					       case Option_CompressionFileFormatStill:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillFileCompressionFormat( h, static_cast<SCRSDK::CrCompressionFileFormat>mode  );
					       myAlphaCameraNo1.printCrCompressionFileFormat(static_cast<SCRSDK::CrCompressionFileFormat>mode);
					       break;

					       case Option_FileType:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillFileFormat( h, static_cast<SCRSDK::CrFileType>mode  );
					       myAlphaCameraNo1.printCrFileType(static_cast<SCRSDK::CrFileType>mode);
					       break;

					       case Option_JpegQuality:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillJpegQuality( h, static_cast<SCRSDK::CrJpegQuality>mode  );
					       myAlphaCameraNo1.printCrJpegQuality(static_cast<SCRSDK::CrJpegQuality>mode);
					       break;

					       case Option_WhiteBalance:
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_wb )==0) 
							      g_currentList.wb = myCamSetUp->setWhiteBalance(); 
						   }
						   else
						   {
					          g_currentList.wb = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetWhiteBalance( h, static_cast<SCRSDK::CrWhiteBalanceSetting>g_currentList.wb  );
					       myAlphaCameraNo1.printCrWhiteBalanceSetting(static_cast<SCRSDK::CrWhiteBalanceSetting>g_currentList.wb);
					       break;

					       case Option_FocusMode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetFocusMode( h, static_cast<SCRSDK::CrFocusMode>mode  );
					       myAlphaCameraNo1.printCrFocusMode(static_cast<SCRSDK::CrFocusMode>mode);
					       break;

					       case Option_MeteringMode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetExposureMeteringMode( h, static_cast<SCRSDK::CrMeteringMode>mode  );
					       myAlphaCameraNo1.printCrMeteringMode(static_cast<SCRSDK::CrMeteringMode>mode);
					       break;

					       case Option_FlashMode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetFlashMode( h, static_cast<SCRSDK::CrFlashMode>mode  );
					       myAlphaCameraNo1.printCrFlashMode(static_cast<SCRSDK::CrFlashMode>mode);
					       break;

					       case Option_WirelessFlash:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetWirelessFlashMode( h, static_cast<SCRSDK::CrWirelessFlash>mode  );
					       myAlphaCameraNo1.printCrWirelessFlash(static_cast<SCRSDK::CrWirelessFlash>mode);
					       break;

					       case Option_RedEyeReduction:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetRedEyeRed( h, static_cast<SCRSDK::CrRedEyeReduction>mode  );
					       myAlphaCameraNo1.printCrRedEyeReduction(static_cast<SCRSDK::CrRedEyeReduction>mode);
					       break;

					       case Option_DriveMode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillCaptureMode( h, static_cast<SCRSDK::CrDriveMode>mode  );
					       myAlphaCameraNo1.printCrDriveMode(static_cast<SCRSDK::CrDriveMode>mode);
					       break;

					       case Option_DRO:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetDynamicRangeOperator( h, static_cast<SCRSDK::CrDRangeOptimizer>mode  );
					       myAlphaCameraNo1.printCrDRangeOptimizer(static_cast<SCRSDK::CrDRangeOptimizer>mode);
					       break;

					       case Option_ImageSize:
						   if (envValue == true)
						   {
							  if (myCamSetUp->isParamError( CrError_imgsz )==0) 
							      g_currentList.imgsz = myCamSetUp->setImageSz(); 
						   }
						   else
						   {
					          g_currentList.imgsz = intValArg.getValue();
						   }
					       myAlphaCameraNo1.alphaSetImageSize( h, static_cast<SCRSDK::CrImageSize>g_currentList.imgsz );
					       myAlphaCameraNo1.printCrImageSize:(static_cast<SCRSDK::CrImageSize>g_currentList.imgsz );
					       break;

					       case Option_AspectRatio:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetAspectRatio( h, static_cast<SCRSDK::CrAspectRatioIndex>mode  );
					       myAlphaCameraNo1.printCrAspectRatioIndex(static_cast<SCRSDK::CrAspectRatioIndex>mode);
					       break;

					       case Option_PictureEffect:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetPictureEffect( h, static_cast<SCRSDK::CrPictureEffect>mode  );
					       myAlphaCameraNo1.printCrPictureEffect(static_cast<SCRSDK::CrPictureEffect>mode);
					       break;

					       case Option_Colortemp:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetColorTemp( h, static_cast<SCRSDK::CrColortemp>mode  );
					       myAlphaCameraNo1.printCrColortemp(static_cast<SCRSDK::CrColortemp>mode);
					       break;

					       case Option_ColorTuningAB:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetBiaxialFineTuneDirAB( h, static_cast<SCRSDK::CrColorTuning>mode  );
					       myAlphaCameraNo1.printCrColorTuning(static_cast<SCRSDK::CrColorTuning>mode);
					       break;

					       case Option_ColorTuningGM:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetBiaxialFineTuneDirGM( h, static_cast<SCRSDK::CrColorTuning>mode  );
					       myAlphaCameraNo1.printCrColorTuning(static_cast<SCRSDK::CrColorTuning>mode);
					       break;

					       case Option_LiveViewDisplayEffect:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetLiveViewDisplayEffect( h, static_cast<SCRSDK::CrLiveViewDisplayEffect>mode  );
					       myAlphaCameraNo1.printCrLiveViewDisplayEffect(static_cast<SCRSDK::CrLiveViewDisplayEffect>mode);
					       break;

					       case Option_StillImageStoreDestination:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillImageStoreDestination( h, static_cast<SCRSDK::CrStillImageStoreDestination>mode  );
					       myAlphaCameraNo1.printCrStillImageStoreDestination(static_cast<SCRSDK::CrStillImageStoreDestination>mode);
					       break;

					       case Option_PriorityKeySettings:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetPositionKeySetting( h, static_cast<SCRSDK::CrPriorityKeySettings>mode  );
					       myAlphaCameraNo1.printCrPriorityKeySettings(static_cast<SCRSDK::CrPriorityKeySettings>mode);
					       break;

					       case Option_DateTime_Settings:
					       long mode = longValArg.getValue();
					       myAlphaCameraNo1.alphaSetDateTime( h, mode  );
					       std::cout << "date time @= " << mode << std::endl;
					       break;

					       case Option_Focus_Magnifier_Setting:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetFocusMagnifierSetting( h, static_cast<SCRSDK::CrCommandParam>mode  );
					       std::cout << "focus mag @= " << mode << std::endl;
					       break;

					       case Option_NearFar:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetNearFarEnable( h, static_cast<SCRSDK::CrNearFarEnableStatus>mode  );
					       myAlphaCameraNo1.printCrNearFarEnableStatus(static_cast<SCRSDK::CrNearFarEnableStatus>mode);
					       break;

					       case Option_NearFar_AF_Area:
					       std::pair xyCoord = pair2IValArg.getValue();
					       myAlphaCameraNo1.alphaSetAFAreaPosition( h, static_cast<CrInt16>xyCoord.first, static_cast<CrInt16>xyCoord.second  );
					       std::cout << "near far x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl; 
					       break;

					       case Option_Zoom_Scale:
					       std::int32_t mode = intValArg.getValue();
					       SCRSDK::CrCommandParam setVal = myAlphaCameraNo1.alphaSetZoomScale( h, static_cast<SCRSDK::CrCommandParam>mode  );
					       std::cout << "set Zoom Scale @= " << setVal << std::endl;
					       break;

					       case Option_Zoom_Setting:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetZoom( h, static_cast<SCRSDK::CrZoomSettingType>mode  );
					       myAlphaCameraNo1.printCrZoomSettingType(static_cast<SCRSDK::CrZoomSettingType>mode);
					       break;

					       case Option_Zoom_Operation:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetZoomOperation( h, static_cast<SCRSDK::CrZoomOperation>mode  );
					       myAlphaCameraNo1.printCrZoomOperation(static_cast<SCRSDK::CrZoomOperation>mode);
					       break;

					       case Option_Movie_File_Format:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetFileFormatMovie( h, static_cast<SCRSDK::CrFileFormatMovie>mode  );
					       myAlphaCameraNo1.printCrFileFormatMovie(static_cast<SCRSDK::CrFileFormatMovie>mode);
					       break;

					       case Option_Movie_Recording_Setting:
					       SCRSDK::CrRecordingSettingMovie ffm = myAlphaCameraNo1.alphaMovieRecordingSetting(h);
					       myAlphaCameraNo1.printCrRecordingSettingMovie(ffm);
					       break;
					   
					       case Option_Movie_Recording_FrameRateSetting:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetMovieFrameRate( h, static_cast<SCRSDK::CrRecordingFrameRateSettingMovie>mode  );
					       myAlphaCameraNo1.printCrRecordingFrameRateSettingMovie(static_cast<SCRSDK::CrRecordingFrameRateSettingMovie>mode);
					       break;

					       case Option_Interval_Rec_Mode:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaIntervalRecModeEnable( h, static_cast<SCRSDK::CrIntervalRecMode>mode  );
					       myAlphaCameraNo1.printCrIntervalRecMode(static_cast<SCRSDK::CrIntervalRecMode>mode);
					       break;

					       case Option_Still_Image_Trans_Size:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStillImageTransSize( h, static_cast<SCRSDK::CrPropertyStillImageTransSize>mode  );
					       myAlphaCameraNo1.printCrPropertyStillImageTransSize(static_cast<SCRSDK::CrPropertyStillImageTransSize>mode);
					       break;

					       case Option_RAW_J_PC_Save_Image:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetRawJPCSaveImage( h, static_cast<SCRSDK::CrPropertyRAWJPCSaveImage>mode  );
					       myAlphaCameraNo1.printCrPropertyRAWJPCSaveImage(static_cast<SCRSDK::CrPropertyRAWJPCSaveImage>mode);
					       break;

					       case Option_LiveView_Image_Quality:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetLiveViewImageQuality( h, static_cast<SCRSDK::CrPropertyLiveViewImageQuality>mode  );
					       myAlphaCameraNo1.printCrPropertyLiveViewImageQuality(static_cast<SCRSDK::CrPropertyLiveViewImageQuality>mode);
					       break;

					       case Option_CustomWB_Capture_Standby:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStandbyCaptureWBOperation( h, static_cast<SCRSDK::CrPropertyCustomWBOperation>mode  );
					       myAlphaCameraNo1.printCrPropertyCustomWBOperation(static_cast<SCRSDK::CrPropertyCustomWBOperation>mode);
					       break;

					       case Option_CustomWB_Capture_Standby_Button:   
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetStandbyCaptureWBCapButton( h, static_cast<SCRSDK::CrPropertyCustomWBCaptureButton>mode  );
					       myAlphaCameraNo1.printCrPropertyCustomWBCaptureButton(static_cast<SCRSDK::CrPropertyCustomWBCaptureButton>mode);
					       break;
					   
					       case Option_CustomWB_Capture_Standby_Cancel:
					       std::int32_t mode = intValArg.getValue();
					       myAlphaCameraNo1.alphaSetCaptureStandbyCancel( h, static_cast<SCRSDK::CrCommandParam>mode  );
					       myAlphaCameraNo1.printCrCommandParam(static_cast<SCRSDK::CrCommandParam>mode);
					       break;

					       case Option_CustomWB_Capture:
					       std::pair xyCoord = pair2IValArg.getValue();
					       myAlphaCameraNo1.alphaSetCustomWBCapture( h, static_cast<CrInt16>xyCoord.first, static_cast<CrInt16>xyCoord.second  );
					       std::cout << "Custom WB Capture x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl;
					       break;

					       case Option_SnapshotInfo:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetSnapshotInfo(h);
					       std::cout << " Snaphot Info @= " << retVal << std::endl;					   
					       break;
					   
					       case Option_BatteryRemain:
					       SCRSDK::CrInt16u retVal = myAlphaCameraNo1.alphaGetBatteryRemain(h);
					       std::cout << " Battery Remaining @= " << retVal << std::endl;
					       break;

					       case Option_BatteryLevel:
					       SCRSDK::CrBatteryLevel retVal = myAlphaCameraNo1.alphaGetBatteryLevel(h);
					       myAlphaCameraNo1.printBatteryLevel( retVal );
					       break;

					       case Option_RecordingState:
					       SCRSDK::CrMovie_Recording_State retVal = myAlphaCameraNo1.alphaGetMoveRecordState(h);
					       myAlphaCameraNo1.printCrMovie_Recording_State(retVal);
					       break;

					       case Option_LiveViewStatus:
					       SCRSDK::CrLiveViewStatus retVal = myAlphaCameraNo1.alphaGetLiveViewStatus(h);
					       myAlphaCameraNo1.printCrLiveViewStatus:(retVal);
					       break;

					       case Option_FocusIndication:
					       SCRSDK::CrFocusIndicator retVal = myAlphaCameraNo1.alphaGetFocusIndication(h);
					       myAlphaCameraNo1.printCrFocusIndicator(retVal);
					       break;
						   
					       case Option_MediaSLOT1_Status:
					       SCRSDK::CrSlotStatus retVal = myAlphaCameraNo1.alphaGetMediaSlot1Status(h);
					       myAlphaCameraNo1.printCrSlotStatus(retVal);
					       break;

					       case Option_MediaSLOT1_RemainingNumber:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot1RemainingNumber(h);
					       std::cout << " slot 1 remaining number @= " << retVal << std::endl;						   
					       break;

					       case Option_MediaSLOT1_RemainingTime:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot1RemainingTime(h);
					       std::cout << " slot 1 remaining time @= " << retVal << std::endl;					   
					       break;

					       case Option_MediaSLOT1_FormatEnableStatus:
					       SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetMediaSlot1FormatStatus(h);
					       myAlphaCameraNo1.printCrMediaFormat(retVal);
					       break;

					       case Option_MediaSLOT2_Status:
					       SCRSDK::CrSlotStatus retVal = myAlphaCameraNo1.alphaGetMediaSlot2Status(h);
					       myAlphaCameraNo1.printCrSlotStatus(retVal);
					       break;

					       case Option_MediaSLOT2_RemainingNumber:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot2RemainingNumber(h);
					       std::cout << " slot 2 remaining number @= " << retVal << std::endl;	
					       break;

					       case Option_MediaSLOT2_RemainingTime:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetMediaSlot2RemainingTime(h);
					       std::cout << " slot 2 remaining time @= " << retVal << std::endl;					   
					       break;

					       case Option_MediaSLOT2_FormatEnableStatus:
					       SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetMediaSlot2FormatStatus(h);
					       myAlphaCameraNo1.printCrMediaFormat(retVal);
					       break;
					   
					       case Option_Media_FormatProgressRate:
					       float formatPercent = alphaGetMediaFormatProgressRatePercent(h);
					       std::cout << " format percent @= " << formatPercent << std::endl;
					       break;
					   
					       case Option_Interval_Rec_Status:
					       SCRSDK::CrIntervalRecStatus retVal = myAlphaCameraNo1.alphaGetIntervalStatus(h);
					       myAlphaCameraNo1.printCrIntervalRecStatus(retVal);
					       break;
						   
					       case Option_CustomWB_Execution_State:
					       SCRSDK::CrPropertyCustomWBExecutionState retVal = myAlphaCameraNo1.alphaGetCustomWBExecutionStatus(h);
					       myAlphaCameraNo1.printCrPropertyCustomWBExecutionState(retVal);
					       break;

                           // this one seems the same as the set command ??
					       //
					       case Option_CustomWB_Capture_get:
					       std::pair xyCoord = myAlphaCameraNo1.alphaGetCustomWBCaptureAsPair(h);
					       std::cout << "Get custom WB Capture x @= " << xyCoord.first << " y @= " << xyCoord.second << std::endl;
					       break;

					       case Option_CustomWB_Capture_Frame_Size:
					       auto frameHeightWidth = myAlphaCameraNo1.alphaGetCaptureFrameSizeAsPair(h);
					       std::cout << "Frame height @= " << frameHeightWidth.first << " width @= " << frameHeightWidth.second << std::endl; 
					       break;

					       case Option_CustomWB_Capture_Frame_Size_As_Tuple:
					       auto frameHeightWidth = myAlphaCameraNo1.alphaGetCaptureFrameSizeAsTuple(h);
					       std::cout << "Frame height @= " << std::get<0>(frameHeightWidth) << " width @= " << std::get<1>(frameHeightWidth) << std::endl; 
					       break;
					   
					       case Option_CustomWB_Capture_Operation:
					       SCRSDK::CrPropertyCustomWBOperation retVal = myAlphaCameraNo1.alphaGetCustomWBOperation(h);
					       myAlphaCameraNo1.printCrPropertyCustomWBOperation(retVal);
					       break;

					       case Option_Zoom_Operation_Status:
					       SCRSDK::CrZoomOperationEnableStatus retVal = myAlphaCameraNo1.alphaGetZoomOperationStatus(h);
					       myAlphaCameraNo1.printCrZoomOperationEnableStatus(retVal);
					       break;

					       case Option_Zoom_Bar_Information:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetZoomBarInfo(h);
					       std::cout << "zoom bar info @= " << retVal << std::endl;
					       break;

					       case Option_Zoom_Type_Status:
					       SCRSDK::CrZoomTypeStatus retVal = myAlphaCameraNo1.alphaGetZoomTypeStatus(h);
					       myAlphaCameraNo1.printCrZoomTypeStatus(retVal);
					       break;

					       case Option_MediaSLOT1_FileType:
					       SCRSDK::CrFileType retVal = myAlphaCameraNo1.alphaGetMediaSLOT1FileType(h);
					       myAlphaCameraNo1.printCrFileType(retVal);
					       break;

					       case Option_MediaSLOT2_FileType:
					       SCRSDK::CrFileType retVal = myAlphaCameraNo1.alphaGetMediaSLOT2FileType(h);
					       myAlphaCameraNo1.printCrFileType(retVal);
					       break;					   

					       case Option_MediaSLOT1_JpegQuality:
					       SCRSDK::CrJpegQuality retVal = myAlphaCameraNo1.alphaGetMediaSLOT1JpegQuality(h);
					       myAlphaCameraNo1.printCrJpegQuality(retVal);
					       break;
					   
					       case Option_MediaSLOT2_JpegQuality:
					       SCRSDK::CrJpegQuality retVal = myAlphaCameraNo1.alphaGetMediaSLOT2JpegQuality(h);
					       myAlphaCameraNo1.printCrJpegQuality(retVal);
					       break;

					       case Option_MediaSLOT1_ImageSize:
					       SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetMediaSLOT1ImageSize(h);
					       myAlphaCameraNo1.printCrImageSize:(retVal);
					       break;

					       case Option_MediaSLOT2_ImageSize:
					       SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetMediaSLOT2ImageSize(h);
					       myAlphaCameraNo1.printCrImageSize:(retVal);
					       break;

					       case Option_RAW_FileCompressionType:
					       SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionType(h);
					       myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					       break;
					   
					       case Option_MediaSLOT1_RAW_FileCompressionType:
					       SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionTypeSLOT1(h);
					       myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					       break;

					       case Option_MediaSLOT2_RAW_FileCompressionType:
					       SCRSDK::CrRAWFileCompressionType retVal = myAlphaCameraNo1.alphaGetRawCompressionTypeSLOT2(h);
					       myAlphaCameraNo1.printCrRAWFileCompressionType(retVal);
					       break;

					       case Option_MediaSLOT1_QuickFormatEnableStatus:
					       SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusSLOT1(h);
					       myAlphaCameraNo1.printCrMediaFormat(retVal);
					       break;

					       case Option_MediaSLOT2_QuickFormatEnableStatus:
					       SCRSDK::CrMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusSLOT2(h);
					       myAlphaCameraNo1.printCrMediaFormat(retVal);
					       break;

					       case Option_Cancel_Media_FormatEnableStatus:
					       SCRSDK::CrCancelMediaFormat retVal = myAlphaCameraNo1.alphaGetQuickFormatStatusCancel(h);
					       myAlphaCameraNo1.printCrCancelMediaFormat(retVal);
					       break;

					       case Option_EstimatePictureSize:
					       SCRSDK::CrImageSize retVal = myAlphaCameraNo1.alphaGetEstimatePictureSize(h);
					       myAlphaCameraNo1.printCrImageSize:(retVal);
					       break;
					   
					       case Option_FocalPosition:
					       SCRSDK::CrFocusArea retVal = myAlphaCameraNo1.alphaGetFocalPosition(h);
					       myAlphaCameraNo1.printCrFocusArea(retVal);
					       break;

                           case Option_CustomWB_Capturable_Area:
					       SCRSDK::CrInt32u retVal = myAlphaCameraNo1.alphaGetCustomWBCapturableArea(h);
					       std::cout << "CustomWB Capture Area @=  " << retVal << std::endl;
					       break;
					   
					       case Option_Get_Props:
					       bool b = myAlphaCameraNo1.alphaGetProperties(h);
					       break;

					       case Option_Get_LiveView_Props:
					       myAlphaCameraNo1.alphaGetLiveViewProperties(h);				 
					       break;

					       case Option_getCustomPairWB:
					       std::pair<CrInt16u, CrInt16u> pairname = myAlphaCameraNo1.alphaGetCustomWBCaptureAsPair(h);
					       std::cout << "CustomWB Capture x @=  " << pairname.first << " y @= " << pairname.second << std::endl;
					       break;

                           case option_cancelShoot:
					       SCRSDK::CrCommandParam setVal = SCRSDK::CrCommandParam::CrCommandParam_Down;
					       SCRSDK::CrCommandParam setVal = myAlphaCameraNo1.alphaCancelShooting(h, setVal);
					       myAlphaCameraNo1.printCrCommandParam(setVal);
					       break;

                           case Option_setS2:
					       std::int32_t s2set = intValArg.getValue();
					       s2set = myAlphaCameraNo1.alphaSetParameterS2( h, static_cast<SCRSDK::CrCommandParam>s2set );
					       myAlphaCameraNo1.printCrCommandParam(static_cast<SCRSDK::CrCommandParam>s2set);
                           break;

                           case Option_getMovie_Recording_Setting:
                           SCRSDK::CrFileFormatMovie retVal = myAlphaCameraNo1.alphaMovieRecordingSetting(h);		
                           myAlphaCameraNo1.printCrFileFormatMovie(SCRSDK::CrFileFormatMovie retVal);
                           break;

                           case Option_get_AF_Area_Position:
                           SCRSDK::CrFocusArea retVal = myAlphaCameraNo1.alphaAFAreaPosition(h);
                           myAlphaCameraNo1.printCrFocusArea(retVal);	
                           break;

                           case Option_get_LiveViewArea:		
                           SCRSDK::CrInt32u retVal myAlphaCameraNo1.alphaGetLiveViewArea(h);
                           std::cout << "Live view area @= " << retVal << std::endl;
                           break;

                           case Option_GetOnly:
                           SCRSDK::CrInt32u getVal = alphaGetOnly(h);
                           std::cout << " get Only @= " << getVal << std::endl;
                           break;
					   
                           case Option_getSDKversion:
					       auto sdkVer = myAlphaCameraNo1.alphaGetSDKVersion();
					       // print as tuple :
                           // std::cout << "SDK version major @=  " << std::get<0>(sdkVer) << " minor @= " << std::get<1>(sdkVer) << " patch @= " << std::get<2>(sdkVer) << std::endl;
					       // or print with a tie :
					       // std::make_tie(major,minor,patch) = sdkVer;
					       auto& [major,minor,patch] = sdkVer;
					       std::cout << "SDK version major @=  " << major << " minor @= " << minor << " patch @= " << patch << std::endl;
					       break;

                           case Option_getSDKserial:
					       auto sdkVer = myAlphaCameraNo1.alphaGetSDKSerial();
					       std::cout << "SDK serial @=  " << sdkVer << std::endl;
					       break;

                           case Option_SetA:
                           myCamSetUp = &a;
                           break;

                           case Option_SetB:
                           myCamSetUp = &b;
                           break;

                           case Option_SetC:
                           myCamSetUp = &c;
                           break;

                           case Option_SetDefault:
                           myCamSetUp = &c;
						   if (myCamSetUp->isParamError( CrError_wb )==0) 
						       g_currentList.wb = myCamSetUp->setWhiteBalance(); 	
					       myAlphaCameraNo1.alphaSetWhiteBalance( h, static_cast<SCRSDK::CrWhiteBalanceSetting>g_currentList.wb  );
					       myAlphaCameraNo1.printCrWhiteBalanceSetting(static_cast<SCRSDK::CrWhiteBalanceSetting>g_currentList.wb);
						   if (myCamSetUp->isParamError( CrError_fn )==0) 
					          g_currentList.fn = myCamSetUp->setFnum();
					       myAlphaCameraNo1.alphaSetApertureFNum( h, static_cast<SCRSDK::CrCommandParam>g_currentList.fn );
						   std::cout << " aperture value @= " << g_currentList.fn << std::endl;
						   if (myCamSetUp->isParamError( CrError_bias )==0) 
							  g_currentList.bias = myCamSetUp->setBias(); 
					       myAlphaCameraNo1.alphaSetExposureBiasCompensation( h, static_cast<SCRSDK::CrCommandParam>g_currentList.bias );
					       std::cout << " exposure bias value @= " << g_currentList.bias << std::endl;	
						   if (myCamSetUp->isParamError( CrError_ss )==0) 
							  g_currentList.ss = myCamSetUp->setShutSpeed(); 
					       myAlphaCameraNo1.alphaSetShuterSpeed( h, static_cast<SCRSDK::CrCommandParam>g_currentList.ss );
					       std::cout << " shutter speed f value @= " << g_currentList.ss << std::endl;	
						   if (myCamSetUp->isParamError( CrError_fc )==0) 
					          g_currentList.fc = myCamSetUp->setFlashComp();
					       myAlphaCameraNo1.alphaSetFlashCompensation( h, static_cast<SCRSDK::CrCommandParam>g_currentList.fc );
					       std::cout << " flash comp value @= " << g_currentList.fc << std::endl;	
						   if ((myCamSetUp->isParamError( CrError_iso1 )==0)&&(myCamSetUp->isParamError( CrError_iso2 )==0)) 
							  g_currentList.iso = myCamSetUp->setIsoSens(); 						    
					       myAlphaCameraNo1.alphaSetISOSensitivity( h, static_cast<SCRSDK::CrCommandParam>g_currentList.iso.first, static_cast<SCRSDK::CrISOMode>g_currentList.iso.second  );
					       myAlphaCameraNo1.printCrISOMode(static_cast<SCRSDK::CrISOMode>g_currentList.iso.second);
					       std::cout << " iso value @= " << g_currentList.iso.first << " " << g_currentList.iso.second << std::endl;	
						   if (myCamSetUp->isParamError( CrError_imgsz )==0) 
							   g_currentList.imgsz = myCamSetUp->setImageSz(); 
					       myAlphaCameraNo1.alphaSetImageSize( h, static_cast<SCRSDK::CrImageSize>g_currentList.imgsz );
					       myAlphaCameraNo1.printCrImageSize:(static_cast<SCRSDK::CrImageSize>g_currentList.imgsz );						   
                           break;
						   
                           case Option_SetFromJsonFile:
						   if (readJSONFile(myJsonFileName, &g_JsonList)==true) myCamSetUp = &fileSavedSettings;
                           break;

                           case Option_WriteToJsonFile:
                           writeJSONFile(myJsonFileName, &g_currentList);						   
                           break;

                           case Option_DoDelay:
						   float waitTimeRequired = floatValArg.getValue();
						   std::int32_t t = clock();                                               // start the tick clock
						   while (((static_cast<float>t) / CLOCKS_PER_SEC) < waitTimeRequired);    // wait for the time specified in seconds CLOCKS_PER_SEC=1000000
                           break;
						   
                           default:
					       std::cout << "Inavlid option passed - parser error - check this case code!" << std::endl;
                           break;					   
   
				       }
                    }
				    // exit the iteration if we got a match
				    //
                    if (weGotMatch == true)
                    {
                       break;
                    }				  
                }
			} 
            // disconnect the camera
            //			 
		    bool b = myAlphaCameraNo1.alphaDisconnect(h);
	      }	
		  // terminate the session
		  //
          bool term = myAlphaCameraNo1.alphaTerminate();		  
        }
#endif
		
        // destruct the class instance
		//
        (&myAlphaCameraNo1)->~alphaSonyCam();
 
        std::exit(EXIT_SUCCESS); 
	    // for testing.....
        //		
	    //if ( setValue == true )
	    //{		
		//    std::reverse(userCommand.begin(),userCommand.end());
		//    std::cout << "User command (spelled backwards) is: " << userCommand << std::endl;
	    //}
	    //else
	    //{
		//    std::cout << "User command is: " << userCommand << std::endl;
        //}

	} 
	catch (TCLAP::ArgException &e)  // catch exceptions
	{ 
	    std::cerr << "error: " << e.error() << " for arg " << e.argId() << std::endl; 
		std::exit(EXIT_FAILURE); 
	}
}
