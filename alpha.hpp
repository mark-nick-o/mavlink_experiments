#ifndef CAMERAREMOTE_ALPHAWRAPPERS_H                              // include this library if we havent already in the toolchain
#define CAMERAREMOTE_ALPHAWRAPPERS_H                              // now only include it once

//
// ================================== Wrapper class for Sony Alpha 1 Series Camera  ===============================================
//

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


#include <iostream>
#include <string>
#include <tuple>

using namespace std;

/* ==============================================================================================================================

   Class Name : alphaSonyCam
   Purpose    : Communicate with Sony Alpha range cameras and perform control functionality
   Rev        : 1.0 (initial release)
   
   ============================================================================================================================= */

#pragma pack()
   
class alphaSonyCam
{

    public:

    SCRSDK::CrInt32u ratioNowFocusMag = 0;
    SCRSDK::CrInt16u xNowFocusMag = 0;
    SCRSDK::CrInt16u yNowFocusMag = 0;
    //std::uint32_t valCountFocusMag = 0;	
	
    bool writable_f_number_current = false;
    bool writable_iso_sensitivity_current = false;
    bool writable_shutter_speed_current = false;
    bool writable_position_key_setting_current = false;
    bool writable_exposure_program_mode_current = false;
    bool writable_still_capture_mode_current = false;
    bool writable_focus_mode_current = false;
    bool writable_focus_area_current = false;
    bool writable_live_view_image_quality_current = false;
    bool writable_live_view_status_current = false;  
    bool writable_media_slot1_full_format_enable_status_current = false;
    bool writable_media_slot2_full_format_enable_status_current = false;
    bool writable_media_slot1_quick_format_enable_status_current = false;
    bool writable_media_slot2_quick_format_enable_status_current = false;
    bool writable_white_balance_current = false;
    bool writable_customwb_capture_stanby_current = false;
    bool writable_customwb_capture_stanby_cancel_current = false;
    bool writable_customwb_capture_operation_current = false;
    bool writable_customwb_capture_execution_state_current = false;
    bool writable_zoom_operation_status_current = false;
    bool writable_zoom_setting_type_current = false;
    bool writable_zoom_types_status_current = false;
    bool writable_zoom_operation_current = false;

    std::uint16_t  f_number_current = 0;
    std::uint32_t  iso_sensitivity_current = 0;
    std::uint32_t  shutter_speed_current = 0;
    std::uint16_t  position_key_setting_current = 0;
    std::uint32_t  exposure_program_mode_current = 0;
    std::uint32_t  still_capture_mode_current = 0;
    std::uint16_t  focus_mode_current = 0;
    std::uint16_t  focus_area_current = 0;
    std::uint16_t  live_view_image_quality_current = 0;
    std::uint16_t  live_view_status_current = 0;
    std::uint8_t   media_slot1_full_format_enable_status_current = 0;
    std::uint8_t   media_slot2_full_format_enable_status_current = 0;
    std::uint8_t   media_slot1_quick_format_enable_status_current = 0;
    std::uint8_t   media_slot2_quick_format_enable_status_current = 0;
    std::uint16_t  white_balance_current = 0;
    std::uint16_t  customwb_capture_stanby_current = 0;
    std::uint16_t  customwb_capture_stanby_cancel_current = 0;
    std::uint16_t  customwb_capture_operation_current = 0;
    std::uint16_t  customwb_capture_execution_state_current = 0;
    std::uint8_t   zoom_operation_status_current = 0;
    std::uint8_t   zoom_setting_type_current = 0;
    std::uint8_t   zoom_types_status_current = 0;
    std::uint8_t   zoom_operation_current = 0;

    std::vector<std::uint64_t> parsed_mag_setting; 
    std::vector<std::uint16_t> parsed_f_number;
    std::vector<std::uint32_t> parsed_iso_sensitivity;
    std::vector<std::uint32_t> parsed_shutter_speed;
    std::vector<std::uint16_t> parsed_position_key_setting;
    std::vector<std::uint32_t> parsed_exposure_program_mode;
    std::vector<std::uint32_t> parsed_still_capture_mode;
    std::vector<std::uint16_t> parsed_focus_mode;
    std::vector<std::uint16_t> parsed_focus_area;
    std::vector<std::uint16_t> parsed_live_view_image_quality;
    std::vector<std::uint8_t> parsed_media_slot1_full_format_enable_status;
    std::vector<std::uint8_t> parsed_media_slot2_full_format_enable_status;
    std::vector<std::uint8_t> parsed_media_slot1_quick_format_enable_status;
    std::vector<std::uint8_t> parsed_media_slot2_quick_format_enable_status;
    std::vector<std::uint16_t> parsed_white_balance;
    std::vector<std::uint16_t> parsed_customwb_capture_stanby;
    std::vector<std::uint16_t> parsed_customwb_capture_stanby_cancel;
    std::vector<std::uint16_t> parsed_customwb_capture_operation;
    std::vector<std::uint16_t> parsed_customwb_capture_execution_state;
    std::vector<std::uint8_t> parsed_zoom_operation_status;
    std::vector<std::uint8_t> parsed_zoom_setting_type;
    std::vector<std::uint8_t> parsed_zoom_types_status;
    std::vector<std::uint8_t> parsed_zoom_operation;
  
    typedef std::shared_ptr<cli::CameraDevice> SCRSDK::CameraDevicePtr;
    typedef std::vector<SCRSDK::CameraDevicePtr> CameraDeviceList;
    CameraDeviceList cameraList; // gloabl list of all cameras for multi-connect mode

    // This will reset CAMERA_CAPTURE_STATUS.image_count and CAMERA_IMAGE_CAPTURED
    std::uint64_t camera_image_count = 0;
	std::uint64_t recording_time_ms = 0;
	std::float available_capacity = 0.0;
	std::uint8_t image_status = 0;
	std::uint8_t video_status = 0;
    std::uint64_t time_utc;		                      //us	Timestamp (time since UNIX epoch) in UTC. 0 for unknown.
    std::int32_t lat;	                              //degE7	Latitude where image was taken
    std::int32_t lon;	                              //degE7	Longitude where capture was taken
    std::int32_t alt;		                          //mm	Altitude (MSL) where image was taken
    std::int32_t relative_alt;		                  //mm	Altitude above ground
    std::float[4] q;		                          //Quaternion of camera orientation (w, x, y, z order, zero-rotation is 1, 0, 0, 0)
    std::int32_t image_index;			              //Zero based index of this image (i.e. a new image will have index CAMERA_CAPTURE_STATUS.image count -1)
    std::int8_t capture_result;			              //Boolean indicating success (1) or failure (0) while capturing this image.
    std::string file_url;			                  //URL of image taken. Either local storage or http://foo.jpg if camera provides an HTTP interface.	
    // std::uint8_t   zoom_operation_current = 0;
	
/* =========================================== Class constructor/destructor ===================================================== */
    alphaSonyCam();
   ~alphaSonyCam();

/* =========================================== Function Definitions ============================================================= */
    bool alphaInit();
    bool alphaTerminate();
    alphaSonyCam::localeInit();
    SCRSDK::ICrCameraObjectInfo** Enumerate_Cameras();
    SCRSDK::ICrCameraObjectInfo* Enumerate_Camera_USB();
    auto alpahGetSDKVersion();
    SCRSDK::CameraDevicePtr alphaCreateUSBCameraConnectionWithDevicePtr();
    SCRSDK::CrDeviceHandle alphaConnectCamera(SCRSDK::ICrCameraObjectInfo *pcamera);
    bool alphaDisconnect(SCRSDK::CrDeviceHandle handle);
    bool alphaGetProperties(SCRSDK::CrDeviceHandle handle);
    void alphaGetLiveViewProperties(SCRSDK::CrDeviceHandle handle);
    void alphaStartStopMovie(SCRSDK::CrDeviceHandle handle);
    void alphaReleaseShutterShoot(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32 TimeMs);
    void alphaMediaFormatSlot1(SCRSDK::CrDeviceHandle handle);
    void alphaMediaFormatSlot2(SCRSDK::CrDeviceHandle handle);
    void alphaMediaQuickFormatSlot1(SCRSDK::CrDeviceHandle handle);
    void alphaMediaQuickFormatSlot2(SCRSDK::CrDeviceHandle handle);
    void alphaCancelMediaFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32 TimeMs);
    void alphaSetShutterHalfReleaseUnlock(SCRSDK::CrDeviceHandle handle);
    void alphaSetShutterHalfReleaseLock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAELUnlock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAELLock(SCRSDK::CrDeviceHandle handle);
    void alphaSetFELUnlock(SCRSDK::CrDeviceHandle handle);
    void alphaSetFELLock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAWBLUnlock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAWBLLock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAFLUnlock(SCRSDK::CrDeviceHandle handle);
    void alphaSetAFLLock(SCRSDK::CrDeviceHandle handle);
    void alphaSetApertureFNum(SCRSDK::CrDeviceHandle handle, CrCommandParam fVal);
    void alphaSetExposureBiasCompensation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal);
    void alphaSetFlashCompensation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal);
    void alphaSetShuterSpeed(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal);
    void alphaSetISOSensitivity(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32u fVal, SCRSDK::CrISOMode mode);
    void alphaSetFocusArea(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFocusArea mode);
    void alphaSetExposureProgramMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDeviceProperty::CrExposureProgram mode);
    void alphaSetStillFileCompressionFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCompressionFileFormat mode);
    void alphaSetStillFileFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFileType mode);
    void alphaSetStillJpegQuality(SCRSDK::CrDeviceHandle handle, SCRSDK::CrJpegQuality mode);
    void alphaSetWhiteBalance(SCRSDK::CrDeviceHandle handle, SCRSDK::CrWhiteBalanceSetting  mode);
    void alphaSetFocusMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFocusMode mode);
    void alphaSetExposureMeteringMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrMeteringMode mode);
    void alphaSetFlashMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFlashMode mode);
    void alphaSetWirelessFlashMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrWirelessFlash mode);
    void alphaSetRedEyeRed(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRedEyeReduction mode);
    void alphaSetStillCaptureMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDriveMode mode);
    void alphaSetDynamicRangeOperator(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDRangeOptimizer mode);
    void alphaSetImageSize(SCRSDK::CrDeviceHandle handle, SCRSDK::CrImageSize mode);
    void alphaSetAspectRatio(SCRSDK::CrDeviceHandle handle, SCRSDK::CrAspectRatioIndex mode);
    void alphaSetPictureEffect(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPictureEffect mode);
    void alphaSetColorTemp(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColortemp col);
    void alphaSetBiaxialFineTuneDirAB(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColorTuning v);
    void alphaSetBiaxialFineTuneDirGM(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColorTuning v);
    void alphaSetLiveViewDisplayEffect(SCRSDK::CrDeviceHandle handle, SCRSDK::CrLiveViewDisplayEffect v);
    void alphaSetStillImageStoreDestination(SCRSDK::CrDeviceHandle handle, SCRSDK::CrStillImageStoreDestination v)
    void alphaSetPositionKeySetting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPriorityKeySettings v);
    void alphaSetDateTime(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    void alphaSetFocusMagnifierSetting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    void alphaSetNearFarEnable(SCRSDK::CrDeviceHandle handle, SCRSDK::CrNearFarEnableStatus v);
    void alphaSetAFAreaPosition(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt16u x, SCRSDK::CrInt16u y);
    SCRSDK::CrCommandParam alphaSetZoomScale(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    void alphaSetZoom(SCRSDK::CrDeviceHandle handle, SCRSDK::CrZoomSettingType v);
    void alphaSetZoomOperation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrZoomOperation v);
    void alphaSetFileFormatMovie(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRecordingSettingMovie v);
    void alphaSetMovieFrameRate(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRecordingFrameRateSettingMovie v);
    void alphaIntervalRecModeEnable(SCRSDK::CrDeviceHandle handle, SCRSDK::CrIntervalRecMode v);
    void alphaSetStillImageTransSize(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyStillImageTransSize v);
    void alphaSetRawJPCSaveImage(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyRAWJPCSaveImage v);
    void alphaSetLiveViewImageQuality(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyLiveViewImageQuality v);
    void alphaSetStandbyCaptureWBOperation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyCustomWBOperation v);
    void alphaSetStandbyCaptureWBCapButton(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyCustomWBCaptureButton v);
    void alphaSetCaptureStandbyCancel(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    void alphaSetCustomWBCapture(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt16u x, SCRSDK::CrInt16u y);
    SCRSDK::CrInt32u alphaGetSnapshotInfo(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt16u alphaGetBatteryRemain(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrBatteryLevel alphaGetBatteryLevel(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrMovie_Recording_State alphaGetMoveRecordState(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrLiveViewStatus alphaGetLiveViewStatus(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetCustomWBCapturableArea(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrFocusIndicator alphaGetFocusIndication(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrSlotStatus alphaGetMediaSlot1Status(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetMediaSlot1RemainingNumber(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetMediaSlot1RemainingTime(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrMediaFormat alphaGetMediaSlot1FormatStatus(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrCommandParam alphaCancelShooting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    SCRSDK::CrSlotStatus alphaGetMediaSlot2Status(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetMediaSlot2RemainingNumber(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetMediaSlot2RemainingTime(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrMediaFormat alphaGetMediaSlot2FormatStatus(SCRSDK::CrDeviceHandle handle);
    float alphaGetMediaFormatProgressRatePercent(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrIntervalRecStatus alphaGetIntervalStatus(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrPropertyCustomWBExecutionState alphaGetCustomWBExecutionStatus(SCRSDK::CrDeviceHandle handle);
    std::pair alphaGetCustomWBCaptureAsPair(SCRSDK::CrDeviceHandle handle);
    auto alphaGetCustomWBCaptureAsTuple(SCRSDK::CrDeviceHandle handle);
    std::pair alphaGetCaptureFrameSizeAsPair(SCRSDK::CrDeviceHandle handle);
    auto alphaGetCaptureFrameSizeAsTuple(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrPropertyCustomWBOperation alphaGetCustomWBOperation(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrZoomOperationEnableStatus alphaGetZoomOperationStatus(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetZoomBarInfo(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrImageSize alphaGetEstimatePictureSize(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrFocusArea alphaGetFocalPosition(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrZoomTypeStatus alphaGetZoomTypeStatus(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrFileType alphaGetMediaSLOT1FileType(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrFileType alphaGetMediaSLOT2FileType(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrJpegQuality alphaGetMediaSLOT1JpegQuality(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrJpegQuality alphaGetMediaSLOT2JpegQuality(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrImageSize alphaGetMediaSLOT1ImageSize(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrImageSize alphaGetMediaSLOT2ImageSize(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrRAWFileCompressionType alphaGetRawCompressionType(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrRAWFileCompressionType alphaGetRawCompressionTypeSLOT1(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrRAWFileCompressionType alphaGetRawCompressionTypeSLOT2(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrMediaFormat alphaGetQuickFormatStatusSLOT1(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrMediaFormat alphaGetQuickFormatStatusSLOT2(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrCancelMediaFormat alphaGetQuickFormatStatusCancel(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetLiveViewArea(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrCommandParam alphaSnapShotInfo(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrInt32u alphaGetOnly(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrRecordingSettingMovie alphaMovieRecordingSetting(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrCommandParam alphaAFAreaPosition(SCRSDK::CrDeviceHandle handle);
    SCRSDK::CrCommandParam alphaSetParameterS2(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v);
    auto alphaGetSDKVersion();
    auto alphaGetSDKSerial();
    SCRSDK::CameraDevicePtr alphaCreateUSBCameraConnectionWithDevicePtr();
    SCRSDK::CrDeviceHandle alphaConnectCameraUSBwithHandle(SCRSDK::ICrCameraObjectInfo *camera_list);
    SCRSDK::CameraDevicePtr alphaCreateCameraConnectionWithDevicePtr(std::int32_t no);
    void alphaCheckCamConnectWithDevicePtr(SCRSDK::CameraDevicePtr camera);
    void alphaCapImage(SCRSDK::CameraDevicePtr camera);
    void alphaShootS1(SCRSDK::CameraDevicePtr camera);
    void alphaAFShutter(SCRSDK::CameraDevicePtr camera);
    void alphaContShoot(SCRSDK::CameraDevicePtr camera);
    void alphaAperture(SCRSDK::CameraDevicePtr camera);
    void alphaISO(SCRSDK::CameraDevicePtr camera);
    void alphaShutSpeed(SCRSDK::CameraDevicePtr camera);
    void alphaShutSpeed(SCRSDK::CameraDevicePtr camera);
    void alphaGetLiveView(SCRSDK::CameraDevicePtr camera);
    void alphaLiveViewImageQuality(SCRSDK::CameraDevicePtr camera);
    void alphaLiveViewImageQuality(SCRSDK::CameraDevicePtr camera);
    void alphaLiveViewImageStatus(SCRSDK::CameraDevicePtr camera);
    void alphaGetLiveViewImageStatus(SCRSDK::CameraDevicePtr camera);
    void alphaPositonKeySetting(SCRSDK::CameraDevicePtr camera);
    void alphaSetExposureProgramMode(SCRSDK::CameraDevicePtr camera);
    void alphaSetStillCaptureMode(SCRSDK::CameraDevicePtr camera);
    void alphaGetFocusMode(SCRSDK::CameraDevicePtr camera);
    void alphaGetFocusArea(SCRSDK::CameraDevicePtr camera);
    void alphaFELock(SCRSDK::CameraDevicePtr camera);
    void alphaAWBLock(SCRSDK::CameraDevicePtr camera);
    void alphaAFLLock(SCRSDK::CameraDevicePtr camera);
    void alphaSetAFAreaPos(SCRSDK::CameraDevicePtr camera);
    void alphaMediaFormat(SCRSDK::CameraDevicePtr camera);
    void alphaExecMovieRecord(SCRSDK::CameraDevicePtr camera);
    void alphaWhiteBal(SCRSDK::CameraDevicePtr camera);
    void alphaCustomWB(SCRSDK::CameraDevicePtr camera);
    void alphaZoomOp(SCRSDK::CameraDevicePtr camera);
	void alphaSonyCam::resetCameraData();
	
    void printBatteryLevel(SCRSDK::CrBatteryLevel retVal);
    void printCrLiveViewPropertyCode(SCRSDK::CrLiveViewPropertyCode retVal);
    void printCrLockIndicator(SCRSDK::CrLockIndicator retVal);
    void printCrPropValueSet(SCRSDK::CrPropValueSet retVal);
    void printCrFnumberSet(SCRSDK::CrFnumberSet retVal);
    void printCrShutterSpeedSet(SCRSDK::CrShutterSpeedSet retVal);
    void printCrISOMode(SCRSDK::CrISOMode retVal);
    void printCrExposureProgram(SCRSDK::CrExposureProgram retVal);
    void printCrFileType(SCRSDK::CrFileType retVal);
    void printCrJpegQuality(SCRSDK::CrJpegQuality retVal);
    void printCrWhiteBalanceSetting(SCRSDK::CrWhiteBalanceSetting retVal);
    void printCrFocusMode(SCRSDK::CrFocusMode retVal);
    void printCrMeteringMode(SCRSDK::CrMeteringMode retVal);
    void printCrFlashMode(SCRSDK::CrFlashMode retVal);
    void printCrWirelessFlash(SCRSDK::CrWirelessFlash retVal);
    void printCrRedEyeReduction(SCRSDK::CrRedEyeReduction retVal);
    void printCrMediaFormat(SCRSDK::CrMediaFormat retVal);
    void printCrCancelMediaFormat(SCRSDK::CrCancelMediaFormat retVal);
    void printCrDriveMode(SCRSDK::CrDriveMode retVal);
    void printCrDRangeOptimizer(SCRSDK::CrDRangeOptimizer retVal);
    void printCrImageSize:(SCRSDK::CrImageSize retVal);
    void printCrAspectRatioIndex(SCRSDK::CrAspectRatioIndex retVal);
    void printCrPictureEffect(SCRSDK::CrPictureEffect retVal);
    void printCrMovie_Recording_State(SCRSDK::CrMovie_Recording_State retVal);
    void printCrFocusArea(SCRSDK::CrFocusArea retVal);
    void printCrColortemp(SCRSDK::CrColortemp retVal);
    void printCrColorTuning(SCRSDK::CrColorTuning retVal);
    void printCrLiveViewDisplayEffect(SCRSDK::CrLiveViewDisplayEffect retVal);
    void printCrStillImageStoreDestination(SCRSDK::CrStillImageStoreDestination retVal);
    void printCrNearFarEnableStatus(SCRSDK::CrNearFarEnableStatus retVal);
    void printCrIntervalRecMode(SCRSDK::CrIntervalRecMode retVal);
    void printCrBatteryLevel(SCRSDK::CrBatteryLevel retVal);
    void printCrWhiteBalanceInitialize(SCRSDK::CrWhiteBalanceInitialize retVal);
    void printCrLiveViewStatus:(SCRSDK::CrLiveViewStatus retVal);
    void printCrIntervalRecStatus(SCRSDK::CrIntervalRecStatus retVal);
    void printCrFocusIndicator(SCRSDK::CrFocusIndicator retVal);
    void printCrSlotStatus(SCRSDK::CrSlotStatus retVal);
    void printCrPriorityKeySettings(SCRSDK::CrPriorityKeySettings retVal);
    void printCrFocusFrameType(SCRSDK::CrFocusFrameType retVal);
    void printCrFocusFrameState(SCRSDK::CrFocusFrameState retVal);
    void printCrFrameInfoType(SCRSDK::CrFrameInfoType retVal);
    void printCrPropertyEnableFlag(SCRSDK::CrPropertyEnableFlag retVal);
    void printCrPropertyVariableFlag(SCRSDK::CrPropertyVariableFlag retVal);
    void printCrPropertyStillImageTransSize(SCRSDK::CrPropertyStillImageTransSize retVal);
    void printCrPropertyRAWJPCSaveImage(SCRSDK::CrPropertyRAWJPCSaveImage retVal);
    void printCrPropertyLiveViewImageQuality(SCRSDK::CrPropertyLiveViewImageQuality retVal);
    void printCrPropertyCustomWBOperation(SCRSDK::CrPropertyCustomWBOperation retVal);
    void printCrPropertyCustomWBExecutionState(SCRSDK::CrPropertyCustomWBExecutionState retVal);
    void printCrPropertyCustomWBCaptureButton(SCRSDK::CrPropertyCustomWBCaptureButton retVal);
    void printCrFileFormatMovie(SCRSDK::CrFileFormatMovie retVal);
    void printCrRecordingSettingMovie(SCRSDK::CrRecordingSettingMovie retVal);
    void printCrRecordingFrameRateSettingMovie(SCRSDK::CrRecordingFrameRateSettingMovie retVal);
    void printCrCompressionFileFormat(SCRSDK::CrCompressionFileFormat retVal);
    void printCrZoomOperationEnableStatus(SCRSDK::CrZoomOperationEnableStatus retVal);
    void printCrZoomSettingType(SCRSDK::CrZoomSettingType retVal);
    void printCrZoomTypeStatus(SCRSDK::CrZoomTypeStatus retVal);
    void printCrZoomOperation(SCRSDK::CrZoomOperation retVal);
    void printCrRAWFileCompressionType(SCRSDK::CrRAWFileCompressionType retVal);
    void printCrCommandParam(SCRSDK::CrCommandParam retVal);
    void printCrCommandId(SCRSDK::CrCommandId retVal);
    void printCrError(SCRSDK::CrError retVal);
    std::vector<std::uint16_t> parse_mag_setting(unsigned char const* buf, std::uint32_t nval);
};
/* =========== end class alphaSonyCam ============ */

/* ------------------------------------ functions within this class --------------------------------------------------------------  */

/* Initialize and Release Camera Remote SDK */
bool alphaSonyCam::alphaInit() 
{
    return(SCRSDK::Init(0));
}

/* Release the memory from the SDK */
bool alphaSonyCam::alphaTerminate() 
{
    return(SCRSDK::Release());
}

SCRSDK::ICrCameraObjectInfo** alphaSonyCam::Enumerate_Cameras() 
{ 
   SCRSDK::ICrEnumCameraObjectInfo* pEnum = nullptr;
   SCRSDK::ICrCameraObjectInfo **pobj;
   
   SCRSDK::CrError err = SCRSDK::EnumCameraObjects(&pEnum); 
   //SCRSDK::CrError err = SCRSDK::EnumCameraObjects(*pEnum); 
   alphaSonyCam::printCrError(err);
   
   if (err == SCRSDK::CrError_Init)
   {
	 std::cout << "The SDK is not properly initialised" << std::endl;
	 pEnum->Release();
     return NULL; 	   
   }
   else if (err == SCRSDK::CrError_Adaptor_HandlePlugin)
   {
	 std::cout << "No plugin modules found" << std::endl;
	 pEnum->Release();
     return NULL; 		   
   }
   else if (pEnum == NULL) 
   { 
	 std::cout << "No cameras found" << std::endl;
	 pEnum->Release();
     return NULL; 
   } 
   
   auto cntOfCamera = pEnum->GetCount(); // get number of cameras 
   if ( cntOfCamera == 0 )
   {
	 std::cout << "Count of cameras was zero" << std::endl;	   
	 return NULL;
   }
   else if ( cntOfCamera != 0 )
   {
	 std::cout << "More than one camera founc" << std::endl;	   
	 return NULL;	   
   }
   // get connected camera information 
   for (SCRSDK::CrInt32 n = 0; n < cntOfCamera; n++) 
   { 
      pobj[n] = pEnum->GetCameraObjectInfo(n); 
      cli::text conn_type(pobj->GetConnectionTypeName());
      cli::text model(pobj->GetModel());
      cli::text id = TEXT("");
      if (TEXT("IP") == conn_type) 
	  {
            cli::NetworkInfo ni = cli::parse_ip_info(pobj->GetId(), pobj->GetIdSize());
            id = ni.mac_address;
      }	  
      else id = ((TCHAR*)pobj->GetId());
      std::cout << '[' << i + 1 << "] " << model.data() << " (" << id.data() << ")   :   " << conn_type << std::endl;
   } 

   pEnum->Release();  // use Release() function of ICrEnumCameraObjectInfo 
   return pobj;
}

SCRSDK::ICrCameraObjectInfo* alphaSonyCam::Enumerate_Camera_USB() 
{ 
   SCRSDK::ICrEnumCameraObjectInfo* pEnum = nullptr;
   //SCRSDK::CrError err = SCRSDK::EnumCameraObjects(*pEnum); 
   SCRSDK::CrError err = SCRSDK::EnumCameraObjects(&pEnum); 
   
   alphaSonyCam::printCrError(err);
   if (err == SCRSDK::CrError_Init)
   {
	 std::cout << "The SDK is not properly initialised" << std::endl;
	 pEnum->Release();
     return NULL; 	   
   }
   else if (err == SCRSDK::CrError_Adaptor_HandlePlugin)
   {
	 std::cout << "No plugin modules found" << std::endl;
	 pEnum->Release();
     return NULL; 		   
   }
   else if (pEnum == NULL) 
   { 
	 std::cout << "No cameras found" << std::endl;
	 pEnum->Release();
     return NULL; 
   } 
   auto cntOfCamera = pEnum->GetCount(); // get number of cameras 
   if ( cntOfCamera == 0 )
   {
	 std::cout << "Count of cameras was zero" << std::endl;	 
     pEnum->Release();	 
	 return NULL;
   }
   else if ( cntOfCamera != 1 )  // remove this for multi-cam
   {
	 std::cout << "More than one camera founc" << std::endl;	
     pEnum->Release();	 
	 return NULL;	   
   }
   // get connected camera information 
   for (SCRSDK::CrInt32 n = 0; n < cntOfCamera; n++) 
   { 
      SCRSDK::ICrCameraObjectInfo *pobj = pEnum->GetCameraObjectInfo(n); 
      cli::text conn_type(pobj->GetConnectionTypeName());
      cli::text model(pobj->GetModel());
      cli::text id = TEXT("");
	  if (TEXT("USB") == conn_type)
      {
		id = ((TCHAR*)pobj->GetId());
		std::cout << '[' << i + 1 << "] " << model.data() << " (" << id.data() << ")   :   " << conn_type << std::endl;
		pEnum->Release();  // use Release() function of ICrEnumCameraObjectInfo 
		return pobj;
	  }		        
   } 

   pEnum->Release();  //use Release() function of ICrEnumCameraObjectInfo as we did find the usb one
   return NULL;
}
			
SCRSDK::CrDeviceHandle alphaSonyCam::alphaConnectCamera(SCRSDK::ICrCameraObjectInfo *pcamera) 
{
   if (pcamera == NULL) return NULL;	
   SCRSDK::MyDeviceCallback *cb = new SCRSDK::MyDeviceCallback(); 
   SCRSDK::CrDeviceHandle hDev = NULL; 
   SCRSDK::CrError err = SCRSDK::Connect(pcamera, cb, &hDev); 
   
   alphaSonyCam::printCrError(err);
   if (err == SCRSDK::CrError_Init)
   {
	 std::cout << "The SDK is not properly initialised" << std::endl;
     return NULL; 	   
   }
   else if (err == SCRSDK::CrError_Generic_Unknown)
   {
	 std::cout << "The pCameraObjectInfo is NULL, and no valid deviceNumber is supplied" << std::endl;
     return NULL; 		   
   }
   return hDev;
}

bool alphaSonyCam::alphaDisconnect(SCRSDK::CrDeviceHandle handle) 
{
   SCRSDK::CrError err = SCRSDK::Disconnect(handle);
   
   alphaSonyCam::printCrError(err);
   if (err == SCRSDK::CrError_Init)
   {
	 std::cout << "The SDK is not properly initialised" << std::endl;
     return false; 	   
   }
   else if (err == SCRSDK::CrError_Generic_InvalidHandle)
   {
	 std::cout << "An invalid hamdle was supplied" << std::endl;
     return false; 		   
   }
   return true;
}

std::vector<std::uint16_t> alphaSonyCam::parse_mag_setting(unsigned char const* buf, std::uint32_t nval)
{
    using TargetType = std::uint64_t;
    constexpr std::size_t const type_size = sizeof(TargetType);
    TargetType const* source = reinterpret_cast<TargetType const*>(buf);
    std::vector<TargetType> result(nval);
    for (std::uint32_t i = 0; i < nval; ++i, ++source) 
	{
        std::memcpy(&result[i], source, type_size);
    }
    return result;
}

bool alphaSonyCam::alphaGetProperties(SCRSDK::CrDeviceHandle handle) 
{ 
  SCRSDK::CrDeviceProperty *pProperties; 
  SCRSDK::CrInt32 numofProperties = 0; 
  SCRSDK::CrError err = SCRSDK::GetDeviceProperties(handle, &pProperties, &numofProperties); 
  
  alphaSonyCam::printCrError(err);
  if (err == SCRSDK::CrError_Init)
  {
	 std::cout << "The SDK is not properly initialised" << std::endl;
     return false; 	   
  }
  else if (err == SCRSDK::CrError_Generic_InvalidHandle)
  {
	 std::cout << "An invalid hamdle was supplied for GetDeviceProperties" << std::endl;
     return false; 		   
  }
  else if (NULL == pProperties)
  {
	 std::cout << "No properties returned from GetDeviceProperties call" << std::endl;
     return false; 		   
  }
  else 
  { // the property list is received successfully 
    std::uint32_t nval = 0;
	
    for (SCRSDK::CrInt32 n = 0; n < numofProperties; n++) 
    {   
      switch (pProperties[n].code) 
  	  {
        case SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Magnifier_Setting:
	    SCRSDK::CrInt64u currentvalue = static_cast<SCRSDK::CrInt64u>(pProperties[n].CurrentValue);
        ratioNowFocusMag = (currentvalue >> 32);
        xNowFocusMag = ((currentvalue >> 16) & 0xFFFF);
        yNowFocusMag = (currentvalue & 0xFFFF);
        nval = pProperties[n].ValueSize / sizeof(SCRSDK::CrInt64u);
		auto parsed_values = alphaSonyCam::parse_mag_setting(pProperties[n].GetValues(), nval);
		parsed_mag_setting = parsed_values; 
        //SCRSDK::CrInt64u* ratioSetList = new SCRSDK::CrInt64u[valCountFocusMag];
        //memcpy(ratioSetList, &pProperties[n].Values,(size_t)pProperties[n].ValueSize);	
        std::cout << "Focus Magnifier setting xNow @= " << xNowFocusMag << " yNow @= " << yNowFocusMag << " valCount @= " << nval << std::endl;	   
        break;

        case SDK::CrDevicePropertyCode::CrDeviceProperty_FNumber:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_f_number_current = pProperties[n].IsSetEnableCurrentValue();
        f_number_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		auto parsed_values = cli::parse_f_number(pProperties[n].GetValues(), nval);
        //alphaCurrentStatus.f_number.possible.swap(parsed_values);
        parsed_f_number = parsed_values; 
        std::cout << "F-Num @= " << (f_number_current/100) << " writable @= " << writable_f_number_current << " valCount @= " << nval << std::endl;	 
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint32_t);
        writable_iso_sensitivity_current = pProperties[n].IsSetEnableCurrentValue();
        iso_sensitivity_current = static_cast<std::uint32_t>(pProperties[n].GetCurrentValue());
		SCRSDK::CrISOMode isoMode = (iso_sensitivity_current>>27);
		alphaSonyCam::printCrISOMode(isoMode);
        auto parsed_values = cli::parse_iso_sensitivity(pProperties[n].GetValues(), nval);
        parsed_iso_sensitivity = parsed_values;
        std::cout << "iso-sens @= " << (iso_sensitivity_current&0x0FFFFFFF) << " writable @= " << writable_iso_sensitivity_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint32_t);
        writable_shutter_speed_current = pProperties[n].IsSetEnableCurrentValue();
        shutter_speed_current = static_cast<std::uint32_t>(pProperties[n].GetCurrentValue());
        auto parsed_values = cli::parse_shutter_speed(pProperties[n].GetValues(), nval);
        parsed_shutter_speed = parsed_values;
        std::cout << "shutter-speed @= " << (shutter_speed_current/1000) << " writable @= " << writable_shutter_speed_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_PriorityKeySettings:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_position_key_setting_current = pProperties[n].IsSetEnableCurrentValue();
        position_key_setting_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrPriorityKeySettings(static_cast<SCRSDK::CrPriorityKeySettings> position_key_setting_current);
        auto parsed_values = cli::parse_position_key_setting(pProperties[n].GetValues(), nval);
        parsed_position_key_setting = parsed_values;
        std::cout << "position Key setting @= " << position_key_setting_current << " writable @= " << writable_position_key_setting_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_ExposureProgramMode:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint32_t);
        writable_exposure_program_mode_current = pProperties[n].IsSetEnableCurrentValue();
        exposure_program_mode_current = static_cast<std::uint32_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrExposureProgram(static_cast<SCRSDK::CrExposureProgram> exposure_program_mode_current);
        auto parsed_values = cli::parse_exposure_program_mode(pProperties[n].GetValues(), nval);
        parsed_exposure_program_mode = parsed_values;
        std::cout << "exposure program mode @= " << exposure_program_mode_current << " writable @= " << writable_exposure_program_mode_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_DriveMode:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint32_t);
        writable_still_capture_mode_current = pProperties[n].IsSetEnableCurrentValue();
        still_capture_mode_current = static_cast<std::uint32_t>(pProperties[n].GetCurrentValue());
        alphaSonyCam::printCrDriveMode(static_cast<SCRSDK::CrDriveMode> still_capture_mode_current);
        auto parsed_values = cli::parse_still_capture_mode(pProperties[n].GetValues(), nval);
        parsed_still_capture_mode = parsed_values;
        std::cout << "drive mode @= " << still_capture_mode_current << " writable @= " << writable_still_capture_mode_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_focus_mode_current = pProperties[n].IsSetEnableCurrentValue();
        focus_mode_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrFocusMode(static_cast<SCRSDK::CrFocusMode> focus_mode_current);
        auto parsed_values = cli::parse_focus_mode(pProperties[n].GetValues(), nval);
        parsed_focus_mode = parsed_values;
        std::cout << "focus mode @= " << focus_mode_current << " writable @= " << writable_focus_mode_current << " valCount @= " << nval << std::endl;
        break;
		
        case SDK::CrDevicePropertyCode::CrDeviceProperty_FocusArea:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_focus_area_current = pProperties[n].IsSetEnableCurrentValue();
        focus_area_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrFocusArea(static_cast<SCRSDK::CrFocusArea> focus_area_current);
        auto parsed_values = cli::parse_focus_area(pProperties[n].GetValues(), nval);
        parsed_focus_area = parsed_values;
        std::cout << "focus area @= " << focus_area_current << " writable @= " << writable_focus_area_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Image_Quality:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_live_view_image_quality_current = pProperties[n].IsSetEnableCurrentValue();
        live_view_image_quality_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrPropertyLiveViewImageQuality(static_cast<SCRSDK::CrPropertyLiveViewImageQuality> live_view_image_quality_current);
        parsed_live_view_image_quality  = parse_live_view_image_quality(pProperties[n].GetValues(), nval);
        std::cout << "live view image quality @= " << live_view_image_quality_current << " writable @= " << writable_live_view_image_quality_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_LiveViewStatus:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_live_view_status_current = pProperties[n].IsSetEnableCurrentValue();
        live_view_status_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrLiveViewStatus:(static_cast<SCRSDK::CrLiveViewStatus> live_view_status_current);
        std::cout << "live view status @= " << live_view_status_current << " writable @= " << writable_live_view_status_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_FormatEnableStatus:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_media_slot1_full_format_enable_status_current = pProperties[n].IsSetEnableCurrentValue();
        media_slot1_full_format_enable_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrMediaFormat(static_cast<SCRSDK::CrMediaFormat> media_slot1_full_format_enable_status_current);
        parsed_media_slot1_full_format_enable_status = cli::parse_media_slotx_format_enable_status(pProperties[n].GetValues(), nval);
        std::cout << "media slot 1 full format status @= " << media_slot1_full_format_enable_status_current << " writable @= " << writable_media_slot1_full_format_enable_status_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_FormatEnableStatus:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_media_slot2_full_format_enable_status_current = pProperties[n].IsSetEnableCurrentValue();
        media_slot2_full_format_enable_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrMediaFormat(static_cast<SCRSDK::CrMediaFormat> media_slot2_full_format_enable_status_current);
        parsed_media_slot2_full_format_enable_status = cli::parse_media_slotx_format_enable_status(pProperties[n].GetValues(), nval);
        std::cout << "media slot 2 full format status @= " << media_slot2_full_format_enable_status_current << " writable @= " << writable_media_slot2_full_format_enable_status_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_QuickFormatEnableStatus:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_media_slot1_quick_format_enable_status_current = pProperties[n].IsSetEnableCurrentValue();
        media_slot1_quick_format_enable_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrMediaFormat(static_cast<SCRSDK::CrMediaFormat> media_slot1_quick_format_enable_status_current);
        std::vector<uint8_t> mode = cli::parse_media_slotx_format_enable_status(pProperties[n].GetValues(), nval);
        parsed_media_slot1_quick_format_enable_status = mode;
        std::cout << "media slot 1 quick format status @= " << media_slot1_quick_format_enable_status_current << " writable @= " << writable_media_slot1_quick_format_enable_status_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_QuickFormatEnableStatus:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_media_slot2_quick_format_enable_status_current = pProperties[n].IsSetEnableCurrentValue();
        media_slot2_quick_format_enable_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrMediaFormat(static_cast<SCRSDK::CrMediaFormat> media_slot2_quick_format_enable_status_current);
        std::vector<uint8_t> mode = cli::parse_media_slotx_format_enable_status(pProperties[n].GetValues(), nval);
        parsed_media_slot2_quick_format_enable_status = mode;
        std::cout << "media slot 2 quick format status @= " << media_slot2_quick_format_enable_status_current << " writable @= " << writable_media_slot2_quick_format_enable_status_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_WhiteBalance:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_white_balance_current = pProperties[n].IsSetEnableCurrentValue();
        white_balance_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrWhiteBalanceSetting(static_cast<SCRSDK::CrWhiteBalanceSetting> white_balance_current);
        std::vector<uint16_t> mode = cli::parse_white_balance(pProperties[n].GetValues(), nval);
        parsed_white_balance = mode;
        std::cout << "white balance @= " << white_balance_current << " writable @= " << writable_white_balance_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Standby:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_customwb_capture_stanby_current = pProperties[n].IsSetEnableCurrentValue();
        customwb_capture_stanby_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
        std::vector<uint16_t> mode = cli::parse_customwb_capture_stanby(pProperties[n].GetValues(), nval);
        parsed_customwb_capture_stanby = mode;
        std::cout << "custom wb @= " << customwb_capture_stanby_current << " writable @= " << writable_customwb_capture_stanby_current << " valCount @= " << nval << std::endl;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Standby_Cancel:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_customwb_capture_stanby_cancel_current = pProperties[n].IsSetEnableCurrentValue();
        customwb_capture_stanby_cancel_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
        std::vector<uint16_t> mode = cli::parse_customwb_capture_stanby_cancel(pProperties[n].GetValues(), nval);
        parsed_customwb_capture_stanby_cancel = mode;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Operation:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_customwb_capture_operation_current = pProperties[n].IsSetEnableCurrentValue();
        customwb_capture_operation_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrPropertyCustomWBOperation(static_cast<SCRSDK::CrPropertyCustomWBOperation> customwb_capture_operation_current);
        std::vector<uint16_t> mode = cli::parse_customwb_capture_operation(pProperties[n].GetValues(), nval);
        parsed_customwb_capture_operation = mode;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Execution_State:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint16_t);
        writable_customwb_capture_execution_state_current = pProperties[n].IsSetEnableCurrentValue();
        customwb_capture_execution_state_current = static_cast<std::uint16_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrPropertyCustomWBExecutionState(static_cast<SCRSDK::CrPropertyCustomWBExecutionState> customwb_capture_execution_state_current);
        std::vector<uint16_t> mode = cli::parse_customwb_capture_execution_state(pProperties[n].GetValues(), nval);
        parsed_customwb_capture_execution_state = mode;                  
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Operation_Status:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_zoom_operation_status_current = pProperties[n].IsSetEnableCurrentValue();
        zoom_operation_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrZoomOperationEnableStatus(static_cast<SCRSDK::CrZoomOperationEnableStatus> zoom_operation_status_current);
        std::vector<uint8_t> mode = cli::parse_zoom_operation_status(pProperties[n].GetValues(), nval);
        parsed_zoom_operation_status = mode;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Setting:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_zoom_setting_type_current = pProperties[n].IsSetEnableCurrentValue();
        zoom_setting_type_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrZoomSettingType(static_cast<SCRSDK::CrZoomSettingType> zoom_setting_type_current);
        std::vector<uint8_t> mode = cli::parse_zoom_setting_type(pProperties[n].GetValues(), nval);
        parsed_zoom_setting_type = mode;
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Type_Status:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_zoom_types_status_current = pProperties[n].IsSetEnableCurrentValue();
        zoom_types_status_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrZoomTypeStatus(static_cast<SCRSDK::CrZoomTypeStatus> zoom_types_status_current);
        std::vector<uint8_t> mode = cli::parse_zoom_types_status(pProperties[n].GetValues(), nval);
        alphaCurrentStatus.zoom_types_status.possible.swap(mode);
        break;
				
        case SDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Operation:
        nval = pProperties[n].GetValueSize() / sizeof(std::uint8_t);
        writable_zoom_operation_current = pProperties[n].IsSetEnableCurrentValue();
        zoom_operation_current = static_cast<std::uint8_t>(pProperties[n].GetCurrentValue());
		alphaSonyCam::printCrZoomOperation(static_cast<SCRSDK::CrZoomOperation> zoom_operation_current);
        std::vector<uint8_t> mode = cli::parse_zoom_operation(pProperties[n].GetValues(), nval);
        parsed_zoom_operation = mode;
        break; 	   
				
	    default:
	    break
      }
      err = SCRSDK::ReleaseDeviceProperties(handle, pProperties); 
      if (err == SCRSDK::CrError_Init)
      {
	     std::cout << "The SDK is not properly initialised" << std::endl;
         return false; 	   
      }
      else if (err == SCRSDK::CrError_Generic_InvalidHandle)
      {
	     std::cout << "An invalid hamdle was supplied for ReleaseDeviceProperties" << std::endl;
         return false; 		   
      }
    }
  }
  return true;
}

void alphaSonyCam::alphaGetLiveViewProperties(SCRSDK::CrDeviceHandle handle) 
{ 
   SCRSDK::CrLiveViewProperty *pProperties = NULL; 
   SCRSDK::CrInt32 numofProperties = 0; 
   SCRSDK::CrError err = SCRSDK::GetLiveViewProperties(handle, &pProperties, &numofProperties); 
   alphaSonyCam::printCrError(err);
   
   // the property list was received successfully
   //
   if (pProperties)                                                       
   {  
       for (SCRSDK::CrInt32 n = 0; n < numofProperties; n++) 
	   { 
           alphaSonyCam::printCrLiveViewPropertyCode(pProperties[n].code);
           //switch (pProperties[n].code) 
		   //{
           //    case CrLiveViewProperty_AF_Area_Position: 
           //   // code to parse the properties... 
           //   break;
		   //	  
		   //  default:
		   //  break;
           //}
        }
		SCRSDK::CrError err = SCRSDK::ReleaseLiveViewProperties(handle, pProperties); 
        alphaSonyCam::printCrError(err);		
		return;
   }
   std::cout << "No properties were returned" << std::endl;
}

void alphaSonyCam::alphaStartStopMovie(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_MovieRecord, CrCommandParam::CrCommandParam_Down);
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaReleaseShutterShoot(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32 TimeMs)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_Release, SCRSDK::CrCommandParam::CrCommandParam_Down); 
   alphaSonyCam::printCrError(err);
   Sleep(TimeMs);
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_Release, SCRSDK::CrCommandParam::CrCommandParam_Up); 
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaMediaFormatSlot1(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_MediaFormat, SCRSDK::CrCommandParam::CrCommandParam_Up);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaMediaFormatSlot2(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_MediaFormat, SCRSDK::CrCommandParam::CrCommandParam_Down);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaMediaQuickFormatSlot1(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_MediaQuickFormat, SCRSDK::CrCommandParam::CrCommandParam_Up);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaMediaQuickFormatSlot2(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_MediaQuickFormat, SCRSDK::CrCommandParam::CrCommandParam_Down);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaCancelMediaFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32 TimeMs)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_CancelMediaFormat, SCRSDK::CrCommandParam::CrCommandParam_Down); 
   alphaSonyCam::printCrError(err);
   Sleep(TimeMs);
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_CancelMediaFormat, SCRSDK::CrCommandParam::CrCommandParam_Up); 
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetShutterHalfReleaseUnlock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_S1, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetShutterHalfReleaseLock(SCRSDK::CrDeviceHandle handle)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_S1, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Locked);  
    alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAELUnlock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AEL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAELLock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AEL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Locked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetFELUnlock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FEL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetFELLock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FEL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Locked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAWBLUnlock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDeviceProperty_AWBL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAWBLLock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDeviceProperty_AWBL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Locked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAFLUnlock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDeviceProperty_AFL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetAFLLock(SCRSDK::CrDeviceHandle handle)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDeviceProperty_AFL, static_cast<SCRSDK::CrCommandParam>SCRSDK::CrLockIndicator::CrLockIndicator_Locked);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetApertureFNum(SCRSDK::CrDeviceHandle handle, CrCommandParam fVal)
{
   //SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FNumber, fVal*100);  
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FNumber, fVal);
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetExposureBiasCompensation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ExposureBiasCompensation, fVal*1000);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetFlashCompensation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FlashCompensation, fVal*1000);  
   alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetShuterSpeed(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam fVal)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed, fVal*1000);  
   alphaSonyCam::printCrError(err);
}

// TODO Check this because static_cast<SCRSDK::CrCommandParam> seems to be 16bit ????
//
/*
    allowable values for mode :-
	
	CrISO_Normal = 0x0,	// ISO setting Normal
	CrISO_MultiFrameNR = 0x1,	// Multi Frame NR
	CrISO_MultiFrameNR_High = 0x2,	// Multi Frame NR High
	CrISO_AUTO = 0xFFFFFF,
*/
void alphaSonyCam::alphaSetISOSensitivity(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt32u fVal, SCRSDK::CrISOMode mode)
{
   SCRSDK::CrCommandParam setVal = static_cast<SCRSDK::CrCommandParam>((mode & 0x0000000F) << 27) | static_cast<SCRSDK::CrCommandParam>(fVal & 0x0FFFFFFF);
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity, setVal);  
   alphaSonyCam::printCrError(err);
}

/*
  mode can be any of the following :-
  
  CrFocusArea_Wide Wide 
  CrFocusArea_Zone Zone
  CrFocusArea_Center Center
  CrFocusArea_Flexible_Spot_S Flexible spot S
  CrFocusArea_Flexible_Spot_M Flexible spot M
  CrFocusArea_Flexible_Spot_L Flexible spot L
  CrFocusArea_Expand_Flexible_Spot Expand flexible spot
  CrFocusArea_Flexible_Spot Flexible spot
  CrFocusArea_Tracking_Wide Tracking on AF wide
  CrFocusArea_Tracking_Zone Tracking on AF zone
  CrFocusArea_Tracking_Center Tracking on AF center
  CrFocusArea_Tracking_Flexible_Spot_S Tracking on AF flexible spot S
  CrFocusArea_Tracking_Flexible_Spot_M Tracking on AF flexible spot M
  CrFocusArea_Tracking_Flexible_Spot_L Tracking on AF flexible spot L
  CrFocusArea_Tracking_Expand_Flexible_Spot Tracking on expand flexible spot
  CrFocusArea_Tracking_Flexible_Spot Tracking on AF flexible spot
*/
void alphaSonyCam::alphaSetFocusArea(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFocusArea mode)
{
   SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FocusArea, static_cast<SCRSDK::CrCommandParam>mode);  
   alphaSonyCam::printCrError(err);
}

/*
  CrExposure_M_Manual Manual(M)
  CrExposure_P_Auto Automatic(P)
  CrExposure_A_AperturePriority Aperture Priority(A)
  CrExposure_S_ShutterSpeedPriority Shutter Priority(S)
  CrExposure_Program_Creative Program Creative(greater depth of field)
  CrExposure_Program_Action Program Action(faster shutter speed)
  CrExposure_Portrait Portrait
  CrExposure_Auto Auto
  CrExposure_Auto_Plus Auto+
  CrExposure_P_A P_A
  CrExposure_P_S P_S
  CrExposure_Sports_Action Sports Action
  CrExposure_Sunset Sunset
  CrExposure_Night Night Scene
  CrExposure_Landscape Landscape
  CrExposure_Macro Macro
  CrExposure_HandheldTwilight Hand-held Twilight
  CrExposure_NightPortrait Night Portrait
  CrExposure_AntiMotionBlur Anti Motion Blur
  CrExposure_Pet Pet
  CrExposure_Gourmet Gourmet
  CrExposure_Fireworks Fireworks
  CrExposure_HighSensitivity High Sensitivity
  CrExposure_MemoryRecall MemoryRecall(MR)
  CrExposure_ContinuousPriority_AE_8pics Tele-Zoom Continuous Priority AE 8pics
  CrExposure_ContinuousPriority_AE_10pics Tele-Zoom Continuous Priority AE 10pics
  CrExposure_ContinuousPriority_AE_12pics Continuous Priority AE12pics
  CrExposure_3D_SweepPanorama 3D Sweep Panorama Shooting
  CrExposure_SweepPanorama Sweep Panorama Shooting
  CrExposure_Movie_P Movie Recording(P)
  CrExposure_Movie_A Movie Recording(A)
  CrExposure_Movie_S Movie Recording(S)
  CrExposure_Movie_M Movie Recording(M)
  CrExposure_Movie_Auto Movie Recording(AUTO)
  CrExposure_Movie_SQMotion_P Movie Recording(Slow&Quick Motion(P))
  CrExposure_Movie_SQMotion_A Movie Recording(Slow&Quick Motion(A))
  CrExposure_Movie_SQMotion_S Movie Recording(Slow&Quick Motion(S))
  CrExposure_Movie_SQMotion_M Movie Recording(Slow&Quick Motion(M))
  CrExposure_Flash_Off Flash Off
  CrExposure_PictureEffect PictureEffect
  CrExposure_HiFrameRate_P High Frame Rate(P)
  CrExposure_HiFrameRate_A High Frame Rate(A)
  CrExposure_HiFrameRate_S High Frame Rate(S)
  CrExposure_HiFrameRate_M High Frame Rate(M)
  CrExposure_SQMotion_P S&Q Motion(P)
  CrExposure_SQMotion_A S&Q Motion(A)
  CrExposure_SQMotion_S S&Q Motion(S)
  CrExposure_SQMotion_M S&Q Motion(M)
  CrExposure_MOVIE MOVIE
  CrExposure_STILL STILL
*/
void alphaSonyCam::alphaSetExposureProgramMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDeviceProperty::CrExposureProgram mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ExposureProgramMode, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrCompressionFileFormat_JPEG == JPEG
  CrCompressionFileFormat_HEIF_422 == HEIF (4:2:2)
  CrCompressionFileFormat_HEIF_420 == HEIF (4:2:0)
*/
void alphaSonyCam::alphaSetStillFileCompressionFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCompressionFileFormat mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CompressionFileFormatStill, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrFileType_RawJpeg RAW+JPEG
  CrFileType_Jpeg JPEG
  CrFileType_Raw RAW
  CrFileType_RawHeif RAW+HEIF
  CrFileType_Heif HEIF
*/
void alphaSonyCam::alphaSetStillFileFormat(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFileType mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FileType, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrJpegQuality_Light Light
  CrJpegQuality_Standard Standard
  CrJpegQuality_Fine Fine
  CrJpegQuality_ExFine Extra fine
*/
void alphaSonyCam::alphaSetStillJpegQuality(SCRSDK::CrDeviceHandle handle, SCRSDK::CrJpegQuality mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_JpegQuality, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrWhiteBalance_AWB AWB
  CrWhiteBalance_Underwater_Auto Underwater Auto
  CrWhiteBalance_Daylight Daylight
  CrWhiteBalance_Shadow Shade
  CrWhiteBalance_Cloudy Cloudy
  CrWhiteBalance_Tungsten Tungsten (Incandescent)
  CrWhiteBalance_Fluorescent Fluorescent
  CrWhiteBalance_Fluorescent_WarmWhite Fluor::Warm White(-1)
  CrWhiteBalance_Fluorescent_CoolWhite Fluor::Cool White(0)
  CrWhiteBalance_Fluorescent_DayWhite Fluor::Day White(+1)
  CrWhiteBalance_Fluorescent_Daylight Fluor::Daylight White(+2)
  CrWhiteBalance_Flush Flush
  CrWhiteBalance_ColorTemp C.Temp.
  CrWhiteBalance_Custom_1 Custom1
  CrWhiteBalance_Custom_2 Custom2
  CrWhiteBalance_Custom_3 Custom3
  CrWhiteBalance_Custom Custom
*/
void alphaSonyCam::alphaSetWhiteBalance(SCRSDK::CrDeviceHandle handle, SCRSDK::CrWhiteBalanceSetting  mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_WhiteBalance, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrFocus_MF Manual(MF)
  CrFocus_AF_S Automatic(AF_S)
  CrFocus_AF_C Continuous AF(AF_C)
  CrFocus_AF_A Auto(AF_A)
  CrFocus_AF_D (AF-D) 
  CrFocus_DMF Direct Manual Focus(DMF)
  CrFocus_PF Preset Focus(PF)
*/
void alphaSonyCam::alphaSetFocusMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFocusMode mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrMetering_Average Average
  CrMetering_CenterWeightedAverage Center-weighted-average
  CrMetering_MultiSpot Multi-spot
  CrMetering_CenterSpot Center-spot
  CrMetering_Multi Multi
  CrMetering_CenterWeighted Center-weighted
  CrMetering_EntireScreenAverage Entire Screen Avg.
  CrMetering_Spot_Standard Spot : Standard
  CrMetering_Spot_Large Spot : Large
  CrMetering_HighLightWeighted Highlight
*/
void alphaSonyCam::alphaSetExposureMeteringMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrMeteringMode mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MeteringMode, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrFlash_Auto Auto flash
  CrFlash_Off Flash off
  CrFlash_Fill Fill flash
  CrFlash_ExternalSync External Sync
  CrFlash_SlowSync Slow Sync
  CrFlash_RearSync Rear Syn
*/
void alphaSonyCam::alphaSetFlashMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrFlashMode mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FlashMode, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrWirelessFlash_Off Off
  CrWirelessFlash_On On
*/
void alphaSonyCam::alphaSetWirelessFlashMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrWirelessFlash mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_WirelessFlash, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrRedEye_Off Off
  CrRedEye_On On
*/
void alphaSonyCam::alphaSetRedEyeRed(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRedEyeReduction mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_RedEyeReduction, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrDrive_Single Normal
  CrDrive_Continuous_Hi Continuous Shot hi
  CrDrive_Continuous_Hi_Plus Cont. Shooting Hi+
  CrDrive_Continuous_Hi_Live Cont. Shooting Hi-Live
  CrDrive_Continuous_Lo Continuous Shot lo
  CrDrive_Continuous Continuous Shot
  CrDrive_Continuous_SpeedPriority Continuous Shot Speed Priority
  CrDrive_Continuous_Mid Continuous Shot mid
  CrDrive_Continuous_Mid_Live Cont. Shooting Mid-Live
  CrDrive_Continuous_Lo_Live Cont. Shooting Lo-Live
  CrDrive_Timelapse Timelapse
  CrDrive_Timer_5s Self Timer 5sec
  CrDrive_Timer_10s Self Timer 10sec
  CrDrive_Timer_2s Self Timer 2sec
  CrDrive_Continuous_Bracket_03Ev_3pics Continuous Bracket 0.3EV 3pics
  CrDrive_Continuous_Bracket_03Ev_5pics Continuous Bracket 0.3EV 5pics
  CrDrive_Continuous_Bracket_03Ev_9pics Continuous Bracket 0.3EV 9pics
  CrDrive_Continuous_Bracket_05Ev_3pics Continuous Bracket 0.5EV 3pics
  CrDrive_Continuous_Bracket_05Ev_5pics Continuous Bracket 0.5EV 5pics
  CrDrive_Continuous_Bracket_05Ev_9pics Continuous Bracket 0.5EV 9pics
  CrDrive_Continuous_Bracket_07Ev_3pics Continuous Bracket 0.7EV 3pics
  CrDrive_Continuous_Bracket_07Ev_5pics Continuous Bracket 0.7EV 5pics
  CrDrive_Continuous_Bracket_07Ev_9pics Continuous Bracket 0.7EV 9pics
  CrDrive_Continuous_Bracket_10Ev_3pics Continuous Bracket 1.0EV 3pics
  CrDrive_Continuous_Bracket_10Ev_5pics Continuous Bracket 1.0EV 5pics
  CrDrive_Continuous_Bracket_10Ev_9pics Continuous Bracket 1.0EV 9pics
  CrDrive_Continuous_Bracket_20Ev_3pics Continuous Bracket 2.0EV 3pics
  CrDrive_Continuous_Bracket_20Ev_5pics Continuous Bracket 2.0EV 5pics
  CrDrive_Continuous_Bracket_30Ev_3pics Continuous Bracket 3.0EV 3pics
  CrDrive_Continuous_Bracket_30Ev_5pics Continuous Bracket 3.0EV 5pics
  CrDrive_Single_Bracket_03Ev_3pics Single Bracket 0.3EV 3pics
  CrDrive_Single_Bracket_03Ev_5pics Single Bracket 0.3EV 5pics
  CrDrive_Single_Bracket_03Ev_9pics Single Bracket 0.3EV 9pics
  CrDrive_Single_Bracket_05Ev_3pics Single Bracket 0.5EV 3pics
  CrDrive_Single_Bracket_05Ev_5pics Single Bracket 0.5EV 5pics
  CrDrive_Single_Bracket_05Ev_9pics Single Bracket 0.5EV 9pics
  CrDrive_Single_Bracket_07Ev_3pics Single Bracket 0.7EV 3pics
  CrDrive_Single_Bracket_07Ev_5pics Single Bracket 0.7EV 5pics
  CrDrive_Single_Bracket_07Ev_9pics Single Bracket 0.7EV 9pics
  CrDrive_Single_Bracket_10Ev_3pics Single Bracket 1.0EV 3pics
  CrDrive_Single_Bracket_10Ev_5pics Single Bracket 1.0EV 5pics
  CrDrive_Single_Bracket_10Ev_9pics Single Bracket 1.0EV 9pics
  CrDrive_Single_Bracket_20Ev_3pics Single Bracket 2.0EV 3pics
  CrDrive_Single_Bracket_20Ev_5pics Single Bracket 2.0EV 5pics
  CrDrive_Single_Bracket_30Ev_3pics Single Bracket 3.0EV 3pics
  CrDrive_Single_Bracket_30Ev_5pics Single Bracket 3.0EV 5pics
  CrDrive_WB_Bracket_Lo WhiteBalance Bracket Lo
  CrDrive_WB_Bracket_Hi WhiteBalance Bracket Hi
  CrDrive_DRO_Bracket_Lo DRO Bracket Lo
  CrDrive_DRO_Bracket_Hi DRO Bracket Hi
  CrDrive_LPF_Bracket LPF Bracket
  CrDrive_RemoteCommander Remote Commander
  CrDrive_MirrorUp Mirror Up
  CrDrive_SelfPortrait_1 Self Portrait 1 Person
  CrDrive_SelfPortrait_2 Self Portrait 2people
  CrDrive_Continuous_Timer_3pics Continuous Self Timer 3pics
  CrDrive_Continuous_Timer_5pics Continuous Self Timer 5pics
  CrDrive_Continuous_Timer_5s_3pics Continuous Self Timer 3pics 5sec
  CrDrive_Continuous_Timer_5s_5pics Continuous Self Timer 5pics 5sec
  CrDrive_Continuous_Timer_2s_3pics Continuous Self Timer 3pics 2sec
  CrDrive_Continuous_Timer_2s_5pics Continuous Self Timer 5pics 2sec
  CrDrive_SingleBurstShooting_lo Spot Burst Shooting Lo
  CrDrive_SingleBurstShooting_mid Spot Burst Shooting Mid
  CrDrive_SingleBurstShooting_hi Spot Burst Shooting Hi
*/
void alphaSonyCam::alphaSetStillCaptureMode(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDriveMode mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_DriveMode, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrDRangeOptimizer_Off DRO OFF
  CrDRangeOptimizer_On DRO
  CrDRangeOptimizer_Plus DRO+
  CrDRangeOptimizer_Plus_Manual_1 DRO + Manual1
  CrDRangeOptimizer_Plus_Manual_2 DRO + Manual2
  CrDRangeOptimizer_Plus_Manual_3 DRO + Manual3
  CrDRangeOptimizer_Plus_Manual_4 DRO + Manual4
  CrDRangeOptimizer_Plus_Manual_5 DRO + Manual5
  CrDRangeOptimizer_Auto DRO AUTO
  CrDRangeOptimizer_HDR_Auto HDR AUTO
  CrDRangeOptimizer_HDR_10Ev HDR 1.0Ev
  CrDRangeOptimizer_HDR_20Ev HDR 2.0Ev
  CrDRangeOptimizer_HDR_30Ev HDR 3.0Ev
  CrDRangeOptimizer_HDR_40Ev HDR 4.0Ev
  CrDRangeOptimizer_HDR_50Ev HDR 5.0Ev
  CrDRangeOptimizer_HDR_60Ev HDR 6.0E
*/
void alphaSonyCam::alphaSetDynamicRangeOperator(SCRSDK::CrDeviceHandle handle, SCRSDK::CrDRangeOptimizer mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_DRO, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrImageSize_L L
  CrImageSize_M M
  CrImageSize_S S
  CrImageSize_VGA VGA
*/
void alphaSonyCam::alphaSetImageSize(SCRSDK::CrDeviceHandle handle, SCRSDK::CrImageSize mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ImageSize, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrAspectRatio_3_2 3:2
  CrAspectRatio_16_9 16:9
  CrAspectRatio_4_3 4:3
  CrAspectRatio_1_1 1:1
*/
void alphaSonyCam::alphaSetAspectRatio(SCRSDK::CrDeviceHandle handle, SCRSDK::CrAspectRatioIndex mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AspectRatio, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
  CrPictureEffect_Off OFF
  CrPictureEffect_ToyCameraNormal Toy Camera Normal
  CrPictureEffect_ToyCameraCool Toy Camera Cool
  CrPictureEffect_ToyCameraWarm Toy Camera Warm
  CrPictureEffect_ToyCameraGreen Toy Camera Green
  CrPictureEffect_ToyCameraMagenta Toy Camera Magenta
  CrPictureEffect_Pop Pop Color
  CrPictureEffect_PosterizationBW Posterization B/W
  CrPictureEffect_PosterizationColor Posterization Color
  CrPictureEffect_Retro Retro Photo
  CrPictureEffect_SoftHighkey Soft High-key
  CrPictureEffect_PartColorRed Partial Color Red
  CrPictureEffect_PartColorGreen Partial Color Green
  CrPictureEffect_PartColorBlue Partial Color Blue
  CrPictureEffect_PartColorYellow Partial Color Yellow
  CrPictureEffect_HighContrastMonochrome High Contrast Mono
  CrPictureEffect_SoftFocusLow Soft Focus Low
  CrPictureEffect_SoftFocusMid Soft Focus Mid
  CrPictureEffect_SoftFocusHigh Soft Focus High
  CrPictureEffect_HDRPaintingLow HDR Painting Low
  CrPictureEffect_HDRPaintingMid HDR Painting Mid
  CrPictureEffect_HDRPaintingHigh HDR Painting High
  CrPictureEffect_RichToneMonochrome Rich-tone Mono
  CrPictureEffect_MiniatureAuto Miniature Auto
  CrPictureEffect_MiniatureTop Miniature Top
  CrPictureEffect_MiniatureMidHorizontal Miniature Middle(Horizontal)
  CrPictureEffect_MiniatureBottom Miniature Bottom
  CrPictureEffect_MiniatureLeft Miniature Left
  CrPictureEffect_MiniatureMidVertical Miniature Middle(Vertical)
  CrPictureEffect_MiniatureRight Miniature Right
  CrPictureEffect_MiniatureWaterColor Miniature Wator Color
  CrPictureEffect_MiniatureIllustrationLow Miniature Illustration Low
  CrPictureEffect_MiniatureIllustrationMid Miniature Illustration Mid
  CrPictureEffect_MiniatureIllustrationHigh Miniature Illustration High
*/
void alphaSonyCam::alphaSetPictureEffect(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPictureEffect mode)
{
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_PictureEffect, static_cast<SCRSDK::CrCommandParam>mode);  
    alphaSonyCam::printCrError(err);
}

/*
    not as per manual but listed as 
   	CrColortemp_Min = 0x0000,
	CrColortemp_Max = 0xFFFF,
*/
void alphaSonyCam::alphaSetColorTemp(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColortemp col)
{
	if (col < 0x09C4) col = 0x09C4;
	if (col > 0x26AC) col = 0x26AC;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Colortemp, static_cast<SCRSDK::CrCommandParam>col);  
    alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetBiaxialFineTuneDirAB(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColorTuning v)
{
	if (v < 0x9C) v = 0x9C;
	if (v > 0xE4) v = 0xE4;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ColorTuningAB, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetBiaxialFineTuneDirGM(SCRSDK::CrDeviceHandle handle, SCRSDK::CrColorTuning v)
{
	if (v < 0x9C) v = 0x9C;
	if (v > 0xE4) v = 0xE4;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ColorTuningGM, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrLiveViewDisplayEffect_Unknown Unknown
  CrLiveViewDisplayEffect_ON Effect ON
  CrLiveViewDisplayEffect_OFF Effect OFF
*/
void alphaSonyCam::alphaSetLiveViewDisplayEffect(SCRSDK::CrDeviceHandle handle, SCRSDK::CrLiveViewDisplayEffect v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_LiveViewDisplayEffect, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrStillImageStoreDestination_HostPC Host Device (Ex. PC)
  CrStillImageStoreDestination_MemoryCard
  Camera(Memory Card)
  CrStillImageStoreDestination_HostPCAndMemoryCard
  Host Device & Camera(Memory Card)
*/
void alphaSonyCam::alphaSetStillImageStoreDestination(SCRSDK::CrDeviceHandle handle, SCRSDK::CrStillImageStoreDestination v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_StillImageStoreDestination, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrPriorityKey_CameraPosition Camera position priority
  CrPriorityKey_PCRemote PC Remote setting priority
*/
void alphaSonyCam::alphaSetPositionKeySetting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPriorityKeySettings v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_PriorityKeySettings, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetDateTime(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_DateTime_Settings, v);  
    alphaSonyCam::printCrError(err);
}

/*
   TODO Find out what the magnifier seeting should be ???
*/
void alphaSonyCam::alphaSetFocusMagnifierSetting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Magnifier_Setting, v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrNearFar_Disable Disable
  CrNearFar_Enable Enable
  -7 near +7 far
  1 step
*/
void alphaSonyCam::alphaSetNearFarEnable(SCRSDK::CrDeviceHandle handle, SCRSDK::CrNearFarEnableStatus v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_NearFar, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

// TODO Check as SCRSDK::CrCommandParam is 16 bit ??
//
void alphaSonyCam::alphaSetAFAreaPosition(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt16u x, SCRSDK::CrInt16u y)
{	
	//if (x > 0x027F) x = 0x027F;
	//if (y > 0x01DF) y = 0x01DF;
    //v = ((x&0xFFFF) << 16) | (y&0xFFFF);
    SCRSDK::CrCommandParam v = ((static_cast<SCRSDK::CrCommandParam>(x&0x027F) << 16)) | (static_cast<SCRSDK::CrCommandParam>(y&0x01DF));	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>CrDevicePropertyCode::CrDeviceProperty_NearFar, v);  
    alphaSonyCam::printCrError(err);
}

SCRSDK::CrCommandParam alphaSonyCam::alphaSetZoomScale(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{
	if (v < 1000) v = 1000;
	if (v > 8000) v = 8000;	
	if ((v % 200) != 0)
	{
		v -= (v % 200);
		if ((v % 200) > 100) v+=200;
	}
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Scale, v); 
    alphaSonyCam::printCrError(err);
    return v;	
}

/*
  CrZoomSetting_OpticalZoomOnly Optical zoom only
  CrZoomSetting_SmartZoomOnly Smart zoom only
  CrZoomSetting_On_ClearImageZoom Clear image zoom on
  CrZoomSetting_On_DigitalZoom Digital zoom (and Clear image zoom) on
*/
void alphaSonyCam::alphaSetZoom(SCRSDK::CrDeviceHandle handle, SCRSDK::CrZoomSettingType v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Setting, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrZoomOperation_Wide
  Zoom out (-)
  When you specify zoom out, the zoom out continues
  until it stops or until the lens or setting limit is 
  reached.
  CrZoomOperation_Stop Specifies when to stop zooming in / out.
  CrZoomOperation_Tele
  Zoom in (+)
  When you specify zoom in, the zoom in continues 
  until it stops or until the lens or setting limit is 
  reached
*/
void alphaSonyCam::alphaSetZoomOperation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrZoomOperation v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Operation, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrRecordingSettingMovie_60p_50M 60p 50M / XAVC S
  CrRecordingSettingMovie_30p_50M 30p 50M / XAVC S
  CrRecordingSettingMovie_24p_50M 24p 50M / XAVC S
  CrRecordingSettingMovie_50p_50M 50p 50M / XAVC S
  CrRecordingSettingMovie_25p_50M 25p 50M / XAVC S
  CrRecordingSettingMovie_60i_24M 60i 24M(FX) / AVCHD
  CrRecordingSettingMovie_50i_24M_FX 50i 24M(FX) / AVCHD
  CrRecordingSettingMovie_60i_17M_FH 60i 17M(FH) / AVCHD
  CrRecordingSettingMovie_50i_17M_FH 50i 17M(FH) / AVCHD
  CrRecordingSettingMovie_60p_28M_PS 60p 28M(PS) / AVCHD
  CrRecordingSettingMovie_50p_28M_PS 50p 28M(PS) / AVCHD
  CrRecordingSettingMovie_24p_24M_FX 24p 24M(FX) / AVCHD
  CrRecordingSettingMovie_25p_24M_FX 25p 24M(FX) / AVCHD
  CrRecordingSettingMovie_24p_17M_FH 24p 17M(FH) / AVCHD
  CrRecordingSettingMovie_25p_17M_FH 25p 17M(FH) / AVCHD
  CrRecordingSettingMovie_120p_50M_1280x720 120p 50M (1280x720) / XAVC S
  CrRecordingSettingMovie_100p_50M_1280x720 100p 50M (1280x720) / XAVC S
  CrRecordingSettingMovie_1920x1080_30p_16M 1920x1080 30p 16M / MP4
  CrRecordingSettingMovie_1920x1080_25p_16M 1920x1080 25p 16M / MP4
  CrRecordingSettingMovie_1280x720_30p_6M 1280x720 30p 6M / MP4
  CrRecordingSettingMovie_1280x720_25p_6M 1280x720 25p 6M / MP4
  CrRecordingSettingMovie_1920x1080_60p_28M 1920x1080 60p 28M / MP4
  CrRecordingSettingMovie_1920x1080_50p_28M 1920x1080 50p 28M / MP4
  CrRecordingSettingMovie_60p_25M_XAVC_S_HD 60p 25M / XAVC S HD
  CrRecordingSettingMovie_50p_25M_XAVC_S_HD 50p 25M / XAVC S HD
  CrRecordingSettingMovie_30p_16M_XAVC_S_HD 30p 16M / XAVC S HD
  CrRecordingSettingMovie_25p_16M_XAVC_S_HD 25p 16M / XAVC S HD
  CrRecordingSettingMovie_120p_100M_1920x 1080_XAVC_S_HD 120p 100M (1920x1080) / XAVC S HD
  CrRecordingSettingMovie_100p_100M_1920x 1080_XAVC_S_HD 100p 100M (1920x1080) / XAVC S HD CrRecordingSettingMovie_120p_60M_1920x 1080_XAVC_S_HD 120p 60M (1920x1080) / XAVC S HD
  CrRecordingSettingMovie_100p_60M_1920x 1080_XAVC_S_HD 100p 60M (1920x1080) / XAVC S HD
  CrRecordingSettingMovie_30p_100M_XAVC_S_4K 30p 100M / XAVC S 4K
  CrRecordingSettingMovie_25p_100M_XAVC_S_4K 25p 100M / XAVC S 4K
  CrRecordingSettingMovie_24p_100M_XAVC_S_4K 24p 100M / XAVC S 4K
  CrRecordingSettingMovie_30p_60M_XAVC_S_4K 30p 60M / XAVC S 4K
  CrRecordingSettingMovie_25p_60M_XAVC_S_4K 25p 60M / XAVC S 4K
  CrRecordingSettingMovie_24p_60M_XAVC_S_4K 24p 60M / XAVC S 4K
  CrRecordingSettingMovie_600M_422_10bit 600M 422 10bit
  CrRecordingSettingMovie_500M_422_10bit 500M 422 10bit
  CrRecordingSettingMovie_400M_420_10bit 400M 420 10bit
  CrRecordingSettingMovie_300M_422_10bit 300M 422 10bit
  CrRecordingSettingMovie_280M_422_10bit 280M 422 10bit
  CrRecordingSettingMovie_250M_422_10bit 250M 422 10bit
  CrRecordingSettingMovie_240M_422_10bit 240M 422 10bit
  CrRecordingSettingMovie_222M_422_10bit 222M 422 10bit
  CrRecordingSettingMovie_200M_422_10bit 200M 422 10bit
  CrRecordingSettingMovie_200M_420_10bit 200M 420 10bit
  CrRecordingSettingMovie_200M_420_8bit 200M 420 8bit
  CrRecordingSettingMovie_185M_422_10bit 185M 422 10bit
  CrRecordingSettingMovie_150M_420_10bit 150M 420 10bit
  CrRecordingSettingMovie_150M_420_8bit 150M 420 8bit
  CrRecordingSettingMovie_140M_422_10bit 140M 422 10bit
  CrRecordingSettingMovie_111M_422_10bit 111M 422 10bit
  CrRecordingSettingMovie_100M_422_10bit 100M 422 10bit
  CrRecordingSettingMovie_100M_420_10bit 100M 420 10bit
  CrRecordingSettingMovie_100M_420_8bit 100M 420 8bit
  CrRecordingSettingMovie_93M_422_10bit 93M 422 10bit
  CrRecordingSettingMovie_89M_422_10bit 89M 422 10bit
  CrRecordingSettingMovie_75M_420_10bit 75M 420 10bit
  CrRecordingSettingMovie_60M_420_8bit 60M 420 8bit
  CrRecordingSettingMovie_50M_422_10bit 50M 422 10bit
  CrRecordingSettingMovie_50M_420_10bit 50M 420 10bit
  CrRecordingSettingMovie_50M_420_8bit 50M 420 8bit
  CrRecordingSettingMovie_45M_420_10bit 45M 420 10bit
  CrRecordingSettingMovie_30M_420_10bit 30M 420 10bit
  CrRecordingSettingMovie_25M_420_8bit 25M 420 8bit
  CrRecordingSettingMovie_16M_420_8bit 16M 420 8bit
*/
void alphaSonyCam::alphaSetFileFormatMovie(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRecordingSettingMovie v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Movie_File_Format, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrRecordingFrameRateSettingMovie_120p 120p
  CrRecordingFrameRateSettingMovie_100p 100p
  CrRecordingFrameRateSettingMovie_60p 60p
  CrRecordingFrameRateSettingMovie_50p 50p
  CrRecordingFrameRateSettingMovie_30p 30p
  CrRecordingFrameRateSettingMovie_25p 25p
  CrRecordingFrameRateSettingMovie_24p 24p
*/
void alphaSonyCam::alphaSetMovieFrameRate(SCRSDK::CrDeviceHandle handle, SCRSDK::CrRecordingFrameRateSettingMovie v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Movie_Recording_FrameRateSetting, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrIntervalRecMode_OFF OFF
  CrIntervalRecMode_ON ON
*/
void alphaSonyCam::alphaIntervalRecModeEnable(SCRSDK::CrDeviceHandle handle, SCRSDK::CrIntervalRecMode v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Interval_Rec_Mode, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrPropertyStillImageTransSize_Original Original
  CrPropertyStillImageTransSize_SmallSizeJPEG Small Size JPEG
*/
void alphaSonyCam::alphaSetStillImageTransSize(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyStillImageTransSize v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Still_Image_Trans_Size, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrPropertyRAWJPCSaveImage_RAWAndJPEG RAW & JPEG
  CrPropertyRAWJPCSaveImage_JPEGOnly JPEG Only
  CrPropertyRAWJPCSaveImage_RAWOnly RAW Only
  CrPropertyRAWJPCSaveImage_RAWAndHEIF RAW & HEIF
  CrPropertyRAWJPCSaveImage_HEIFOnly HEIF Only
*/
void alphaSonyCam::alphaSetRawJPCSaveImage(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyRAWJPCSaveImage v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_RAW_J_PC_Save_Image, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
  CrPropertyLiveViewImageQuality_Low Low
  CrPropertyLiveViewImageQuality_High High
*/
void alphaSonyCam::alphaSetLiveViewImageQuality(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyLiveViewImageQuality v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Image_Quality, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
Get the Custom WB Capture Standby Operation
Parameter Code Explanation
  CrPropertyCustomWBOperation_Disable Disable
  CrPropertyCustomWBOperation_Enable Enable
*/
void alphaSonyCam::alphaSetStandbyCaptureWBOperation(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyCustomWBOperation v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Standby, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
Execute the Custom WB Capture Standby
Parameter Code Explanation
 CrPropertyCustomWBCapture_Up Up
 CrPropertyCustomWBCapture_Down Down
*/
void alphaSonyCam::alphaSetStandbyCaptureWBCapButton(SCRSDK::CrDeviceHandle handle, SCRSDK::CrPropertyCustomWBCaptureButton v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Standby, static_cast<SCRSDK::CrCommandParam>v);  
    alphaSonyCam::printCrError(err);
}

/*
Get the Custom WB Capture Standby Cancel Operation
   CrPropertyCustomWBOperation_Disable Disable
   CrPropertyCustomWBOperation_Enable Enable
Execute the Custom WB Capture Standby Cancel
   CrPropertyCustomWBCapture_Up Up
   CrPropertyCustomWBCapture_Down Down
*/
void alphaSonyCam::alphaSetCaptureStandbyCancel(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Standby_Cancel, v);  
    alphaSonyCam::printCrError(err);
}

void alphaSonyCam::alphaSetCustomWBCapture(SCRSDK::CrDeviceHandle handle, SCRSDK::CrInt16u x, SCRSDK::CrInt16u y)
{
    SCRSDK::CrCommandParam v = ((static_cast<SCRSDK::CrCommandParam>(x&0xFFFF)) << 16) | (static_cast<SCRSDK::CrCommandParam>(y&0xFFFF));	
	//if (v < 0) v = 0;
	//if (v > 0xFFFFFFFF) v = 0xFFFFFFFF;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture, v);  
    alphaSonyCam::printCrError(err);
}

SCRSDK::CrInt32u alphaSonyCam::alphaGetSnapshotInfo(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_SnapshotInfo, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

/*
  0xFF(untaken) min
  0x64(100%) max
*/
SCRSDK::CrInt16u alphaSonyCam::alphaGetBatteryRemain(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_BatteryRemain, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt16u>v;	
}

/*
  CrBatteryLevel_Fake Fake Battery
  CrBatteryLevel_PreEndBattery Pre-End Battery
  CrBatteryLevel_1_4 Battery Level 1/4
  CrBatteryLevel_2_4 Battery Level 2/4
  CrBatteryLevel_3_4 Battery Level 3/4
  CrBatteryLevel_4_4 Battery Level 4/4
  CrBatteryLevel_1_3 Battery Level 1/3
  CrBatteryLevel_2_3 Battery Level 2/3
  CrBatteryLevel_3_3 Battery Level 3/3
  CrBatteryLevel_PreEnd_PowerSupply Pre-End Battery with USB BusPower Supply
  CrBatteryLevel_1_4_PowerSupply Battery Level 1/4 with USB BusPower Supply
  CrBatteryLevel_2_4_PowerSupply Battery Level 2/4 with USB BusPower Supply
  CrBatteryLevel_3_4_PowerSupply Battery Level 3/4 with USB BusPower Supply
  CrBatteryLevel_4_4_PowerSupply Battery Level 4/4 with USB BusPower Supply
  CrBatteryLevel_USBPowerSupply USB BusPower Supply
*/
SCRSDK::CrBatteryLevel alphaSonyCam::alphaGetBatteryLevel(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_BatteryLevel, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrBatteryLevel>v;	
}

/*
  CrMovie_Recording_State_Not_Recording Not Recording
  CrMovie_Recording_State_Recording Recording
  CrMovie_Recording_State_Recording_Failed Recording Failed
*/
SCRSDK::CrMovie_Recording_State alphaSonyCam::alphaGetMoveRecordState(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_RecordingState, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrMovie_Recording_State>v;	
}

/*
  CrLiveView_Disable LiveView Support but Disable just now :If this value is set, the host should not get the LiveView Image.
  CrLiveView_Enable LiveView Support and Enable :The host can get the LiveView Image and activate LiveView button if have.
  CrLiveView_NotSupport LiveView Not Support :Just definition, If the camera doesn't support Liveview, the host can't get this property by any operation.
*/
SCRSDK::CrLiveViewStatus alphaSonyCam::alphaGetLiveViewStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_LiveViewStatus, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrLiveViewStatus>v;	
}


SCRSDK::CrInt32u alphaSonyCam::alphaGetCustomWBCapturableArea(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capturable_Area, v);
	alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

/*
  CrFocusIndicator_Unlocked Unlock
  CrFocusIndicator_Focused_AF_S [AF-S]Focussed, and AF Locked State
  CrFocusIndicator_NotFocused_AF_S [AF-S]Not focussed, and Low Contrast State
  CrFocusIndicator_TrackingSubject_AF_C [AF-C]Tracking Subject motion
  CrFocusIndicator_Focused_AF_C [AF-C]Focussed State
  CrFocusIndicator_NotFocused_AF_C [AF-C]Not focussed, and Low Contrast State
*/
SCRSDK::CrFocusIndicator alphaSonyCam::alphaGetFocusIndication(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FocusIndication, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrFocusIndicator>v;	
}

/*
  CrSlotStatus_OK OK
  CrSlotStatus_NoCard No card
  CrSlotStatus_CardError Card error
  CrSlotStatus_RecognizingOrLockedError
  Card recognizing/Card locked and DB error
*/
SCRSDK::CrSlotStatus alphaSonyCam::alphaGetMediaSlot1Status(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_Status, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrSlotStatus>v;	
}

/*

*/
SCRSDK::CrInt32u alphaSonyCam::alphaGetMediaSlot1RemainingNumber(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_RemainingNumber, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

/*

*/
SCRSDK::CrInt32u alphaSonyCam::alphaGetMediaSlot1RemainingTime(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_RemainingTime, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

SCRSDK::CrMediaFormat alphaSonyCam::alphaGetMediaSlot1FormatStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_FormatEnableStatus, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrMediaFormat>v;	
}

SCRSDK::CrCommandParam alphaSonyCam::alphaCancelShooting(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrCommandId::CrCommandId_CancelShooting, v);
    alphaSonyCam::printCrError(err);
    return v;	
}

/*
  CrSlotStatus_OK OK
  CrSlotStatus_NoCard No card
  CrSlotStatus_CardError Card error
  CrSlotStatus_RecognizingOrLockedError
  Card recognizing/Card locked and DB error
*/
SCRSDK::CrSlotStatus alphaSonyCam::alphaGetMediaSlot2Status(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_Status, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrSlotStatus>v;	
}

/*

*/
SCRSDK::CrInt32u alphaSonyCam::alphaGetMediaSlot2RemainingNumber(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_RemainingNumber, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

/*

*/
SCRSDK::CrInt32u alphaSonyCam::alphaGetMediaSlot2RemainingTime(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_RemainingTime, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

SCRSDK::CrMediaFormat alphaSonyCam::alphaGetMediaSlot2FormatStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_FormatEnableStatus, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrMediaFormat>v;	
}

/* TODO again check that SCRSDK::CrCommandParam */
float alphaSonyCam::alphaGetMediaFormatProgressRatePercent(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
	SCRSDK::CrInt16u a,b;
	float pRate;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Media_FormatProgressRate, v);
    alphaSonyCam::printCrError(err);
	b = static_cast<SCRSDK::CrInt16u>(v&0xFFFF);
	a = static_cast<SCRSDK::CrInt16u>((v>>16)&0xFFFF);	
	pRate = ((static_cast<float>a) / (static_cast<float>b)) * 100.0f;
    return pRate;	
}

/*
  CrIntervalRecStatus_WaitingStart Waiting Start
  CrIntervalRecStatus_IntervalShooting Interval Shooting
*/
SCRSDK::CrIntervalRecStatus alphaSonyCam::alphaGetIntervalStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Interval_Rec_Status, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrIntervalRecStatus>v;	
}

/*
  CrPropertyCustomWBExecutionState_Invalid Invalid
  CrPropertyCustomWBExecutionState_Standby Standby
  CrPropertyCustomWBExecutionState_Capturing Capturing
  CrPropertyCustomWBExecutionState_OperatingCamera Operating Camera
*/
SCRSDK::CrPropertyCustomWBExecutionState alphaSonyCam::alphaGetCustomWBExecutionStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Execution_State, v);
    alphaSonyCam::printCrError(err);
    return static_cast<CrPropertyCustomWBExecutionState>v;	
}

std::pair alphaSonyCam::alphaGetCustomWBCaptureAsPair(SCRSDK::CrDeviceHandle handle)
{
    SCRSDK::CrCommandParam v;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture, v);  
    alphaSonyCam::printCrError(err);
	std::pair<SCRSDK::CrInt16u, SCRSDK::CrInt16u> pairname;
	pairname.first = static_cast<SCRSDK::CrInt16u>((v&0xFFFF0000) >> 16);
	pairname.second = static_cast<SCRSDK::CrInt16u>(v&0000FFFF);
	return pairname;
}

auto alphaSonyCam::alphaGetCustomWBCaptureAsTuple(SCRSDK::CrDeviceHandle handle)
{
    SCRSDK::CrCommandParam v;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture, v);  
    alphaSonyCam::printCrError(err);
	return std::make_tuple(static_cast<SCRSDK::CrInt16u>((v&0xFFFF0000) >> 16),static_cast<SCRSDK::CrInt16u>(v&0000FFFF)); // x, y
}

std::pair alphaSonyCam::alphaGetCaptureFrameSizeAsPair(SCRSDK::CrDeviceHandle handle)
{
    SCRSDK::CrCommandParam v;	
	std::pair<SCRSDK::CrInt16u, SCRSDK::CrInt16u> pairname;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Frame_Size, v); 	
    alphaSonyCam::printCrError(err);
	pairname = std::make_pair(static_cast<SCRSDK::CrInt16u>((v&0x00400000) >> 16),static_cast<SCRSDK::CrInt16u>(v&00000040));  // w, h
	return pairname;
}

auto alphaSonyCam::alphaGetCaptureFrameSizeAsTuple(SCRSDK::CrDeviceHandle handle)
{
    SCRSDK::CrCommandParam v;	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Frame_Size, v); 	
    alphaSonyCam::printCrError(err);
	return std::make_tuple(static_cast<SCRSDK::CrInt16u>((v&0x00400000) >> 16),static_cast<SCRSDK::CrInt16u>(v&00000040));  // w, h
}

/*
  CrPropertyCustomWBOperation_Disable Disable
  CrPropertyCustomWBOperation_Enable Enable
*/
SCRSDK::CrPropertyCustomWBOperation alphaSonyCam::alphaGetCustomWBOperation(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDevicePropertyCode::CrDeviceProperty_CustomWB_Capture_Operation, v);
    alphaSonyCam::printCrError(err);
    return static_cast<CrPropertyCustomWBOperation>v;	
}

/*
  CrZoomOperationEnableStatus_Disable Disable
  CrZoomOperationEnableStatus_Enable Enable
*/
SCRSDK::CrZoomOperationEnableStatus alphaSonyCam::alphaGetZoomOperationStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDevicePropertyCode::CrDeviceProperty_Zoom_Operation_Status, v);
    alphaSonyCam::printCrError(err);
    return static_cast<CrZoomOperationEnableStatus>v;	
}

SCRSDK::CrInt32u alphaSonyCam::alphaGetZoomBarInfo(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Bar_Information, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

SCRSDK::CrImageSize alphaSonyCam::alphaGetEstimatePictureSize(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_EstimatePictureSize, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrImageSize>v;	
}

SCRSDK::CrFocusArea alphaSonyCam::alphaGetFocalPosition(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FocalPosition, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrFocusArea>v;	
}

/*
  CrZoomTypeStatus_OpticalZoom Optical zoom only
  CrZoomTypeStatus_SmartZoom Smart zoom only
  CrZoomTypeStatus_ClearImageZoom Clear image zoom
  CrZoomTypeStatus_DigitalZoom Digital zoom
*/
SCRSDK::CrZoomTypeStatus alphaSonyCam::alphaGetZoomTypeStatus(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Zoom_Type_Status, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrZoomTypeStatus>v;	
}

/*
  CrFileType_RawJpeg RAW+JPEG
  CrFileType_Jpeg JPEG
  CrFileType_Raw RAW
  CrFileType_RawHeif RAW+HEIF
  CrFileType_Heif HEIF
*/
SCRSDK::CrFileType alphaSonyCam::alphaGetMediaSLOT1FileType(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_FileType, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrFileType>v;	
}

/*
  CrFileType_RawJpeg RAW+JPEG
  CrFileType_Jpeg JPEG
  CrFileType_Raw RAW
  CrFileType_RawHeif RAW+HEIF
  CrFileType_Heif HEIF
*/
SCRSDK::CrFileType alphaSonyCam::alphaGetMediaSLOT2FileType(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_FileType, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK:::CrFileType>v;	
}

/*
  CrJpegQuality_Light Light
  CrJpegQuality_Standard Standard
  CrJpegQuality_Fine Fine
  CrJpegQuality_ExFine Extra fine
*/
SCRSDK::CrJpegQuality alphaSonyCam::alphaGetMediaSLOT1JpegQuality(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_JpegQuality, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrJpegQuality>v;	
}

/*
  CrJpegQuality_Light Light
  CrJpegQuality_Standard Standard
  CrJpegQuality_Fine Fine
  CrJpegQuality_ExFine Extra fine
*/
SCRSDK::CrJpegQuality alphaSonyCam::alphaGetMediaSLOT2JpegQuality(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_JpegQuality, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrJpegQuality>v;	
}

/*
  CrImageSize_L L
  CrImageSize_M M
  CrImageSize_S S
*/
SCRSDK::CrImageSize alphaSonyCam::alphaGetMediaSLOT1ImageSize(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_ImageSize, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrImageSize>v;	
}

/*
  CrImageSize_L L
  CrImageSize_M M
  CrImageSize_S S
*/
SCRSDK::CrImageSize alphaSonyCam::alphaGetMediaSLOT2ImageSize(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_ImageSize, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrImageSize>v;	
}

/*
  CrRAWFile_Uncompression Uncompression
  CrRAWFile_Compression Compression
  CrRAWFile_LossLess Lossless Compression
*/
SCRSDK::CrRAWFileCompressionType alphaSonyCam::alphaGetRawCompressionType(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_RAW_FileCompressionType, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrRAWFileCompressionType>v;	
}

/*
  CrRAWFile_Uncompression Uncompression
  CrRAWFile_Compression Compression
  CrRAWFile_LossLess Lossless Compression
*/
SCRSDK::CrRAWFileCompressionType alphaSonyCam::alphaGetRawCompressionTypeSLOT1(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_RAW_FileCompressionType, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrRAWFileCompressionType>v;	
}

/*
  CrRAWFile_Uncompression Uncompression
  CrRAWFile_Compression Compression
  CrRAWFile_LossLess Lossless Compression
*/
SCRSDK::CrRAWFileCompressionType alphaSonyCam::alphaGetRawCompressionTypeSLOT2(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_RAW_FileCompressionType, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrRAWFileCompressionType>v;	
}

/*
  CrMediaFormat_Disable Disable
  CrMediaFormat_Enable Enable
*/
SCRSDK::CrMediaFormat alphaSonyCam::alphaGetQuickFormatStatusSLOT1(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT1_QuickFormatEnableStatus, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrMediaFormat>Sv;	
}

/*
  CrMediaFormat_Disable Disable
  CrMediaFormat_Enable Enable
*/
SCRSDK::CrMediaFormat alphaSonyCam::alphaGetQuickFormatStatusSLOT2(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_MediaSLOT2_QuickFormatEnableStatus, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrMediaFormat>Sv;	
}

/*
  CrCancelMediaFormat_Disable Disable
  CrCancelMediaFormat_Enable Enable
*/
SCRSDK::CrCancelMediaFormat alphaSonyCam::alphaGetQuickFormatStatusCancel(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Cancel_Media_FormatEnableStatus, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrCancelMediaFormat>v;	
}

SCRSDK::CrInt32u alphaSonyCam::alphaGetLiveViewArea(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Area, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrInt32u>v;	
}

SCRSDK::CrCommandParam alphaSonyCam::alphaSnapShotInfo(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_SnapshotInfo, v);
    alphaSonyCam::printCrError(err);
    return v;	
}

SCRSDK::CrInt32u alphaSonyCam::alphaGetOnly(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_GetOnly, v);
    alphaSonyCam::printCrError(err);
    return static_cast<CrInt32u>v;	
}

SCRSDK::CrRecordingSettingMovie alphaSonyCam::alphaMovieRecordingSetting(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_Movie_Recording_Setting, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrRecordingSettingMovie>v;	
}

SCRSDK::CrFocusArea alphaSonyCam::alphaAFAreaPosition(SCRSDK::CrDeviceHandle handle)
{	
    SCRSDK::CrCommandParam v;
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AF_Area_Position, v);
    alphaSonyCam::printCrError(err);
    return static_cast<SCRSDK::CrFocusArea>v;	
}

// not sure what this one is but its in the enum file
SCRSDK::CrCommandParam alphaSonyCam::alphaSetParameterS2(SCRSDK::CrDeviceHandle handle, SCRSDK::CrCommandParam v)
{	
    SCRSDK::CrError err = SCRSDK::SendCommand(handle, static_cast<SCRSDK::CrInt32u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_S2, v);
    alphaSonyCam::printCrError(err);
	return v;
}

auto alphaSonyCam::alphaGetSDKVersion()
{
    SCRSDK::CrInt32u version = SCRSDK::GetSDKVersion();
    std::int32_t major = static_cast<std::int32_t>(version & 0xFF000000) >> 24;
    std::int32_t minor = static_cast<std::int32_t>(version & 0x00FF0000) >> 16;
    std::int32_t patch = static_cast<std::int32_t>(version & 0x0000FF00) >> 8;
	return (std::make_tuple(major, minor, patch));
}

auto alphaSonyCam::alphaGetSDKSerial()
{
    SCRSDK::CrInt32u version = SCRSDK::GetSDKSerial();
	return version;
}

SCRSDK::CameraDevicePtr alphaSonyCam::alphaCreateUSBCameraConnectionWithDevicePtr() 
{
    std::int32_t cameraNumUniq = 1;
    std::int32_t selectCamera = 1;
    SCRSDK::CameraDevicePtr camera = NULL;
   
    SCRSDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    // auto enum_status = cr_lib->EnumCameraObjects(&camera_list, 3);
    auto enum_status = SCRSDK::EnumCameraObjects(*camera_list);	
    //auto enum_status = SCRSDK::EnumCameraObjects(&camera_list);

    alphaSonyCam::printCrError(enum_status);	
    if (enum_status == SCRSDK::CrError::CrError_Init)
    {
	   std::cout << "The SDK is not properly initialised" << std::endl;
	   camera_list->Release();
       return NULL; 	   
    }
    else if (enum_status == SCRSDK::CrError::CrError_Adaptor_HandlePlugin)
    {
       std::cout << "No plugin modules found" << std::endl;
	   camera_list->Release();
       return NULL; 		   
    }
    else if (camera_list == NULL) 
    {  
	   std::cout << "No cameras found" << std::endl;
	   camera_list->Release();
       return NULL; 
    }  
    auto cntOfCamera = camera_list->GetCount(); // get number of cameras 
    if ( cntOfCamera == 0 )
    {
	   std::cout << "Count of cameras was zero" << std::endl;
       camera_list->Release();	   
	   return NULL;
    }
    // get connected camera information we iterate the cameras that have been found
	//
    for (SCRSDK::CrInt32 n = 0; n < cntOfCamera; n++) 
    { 
      SCRSDK::ICrCameraObjectInfo *pobj = camera_list->GetCameraObjectInfo(n); 
      cli::text conn_type(pobj->GetConnectionTypeName());
      cli::text model(pobj->GetModel());
      cli::text id = TEXT("");
	  if (TEXT("USB") == conn_type)
      {
         std::cout << "Connect to selected camera... " << n << std::endl;
         auto* camera_info = camera_list->GetCameraObjectInfo(n);

         std::cout << "Create camera SDK camera callback object.\n";
         camera = SCRSDK::CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));

         //std::cout << "Release enumerated camera list.\n";
         //camera_list->Release();

         auto connect_status = camera->connect();
         if (!connect_status) 
	     {
            std::cout << "Camera connection failed to initiate. Abort.\n";
            // cr_lib->Release();
            SCRSDK::Release();
            std::exit(EXIT_FAILURE);
         }
         std::cout << "Camera connection successfully initiated!\n\n";
		 n = ++cntOfCamera;  // break iteration we only have one usb camera
	  }		        
    } 
    std::cout << "Release enumerated camera list.\n";	
    camera_list->Release();
	return camera;
}

SCRSDK::CrDeviceHandle alphaSonyCam::alphaConnectCameraUSBwithHandle(SCRSDK::ICrCameraObjectInfo *camera_list) 
{
    if (camera_list == NULL) return NULL;	
    std::int32_t cameraNumUniq = 1;
    std::int32_t selectCamera = 1;   
    SCRSDK::CrDeviceHandle hDev = NULL;    
    SCRSDK::CameraDevicePtr camera = NULL;
	
    auto cntOfCamera = camera_list->GetCount(); // get number of cameras 
    if ( cntOfCamera == 0 )
    {
	   std::cout << "Count of cameras was zero" << std::endl;
       camera_list->Release();	   
	   return NULL;
    }
    // get connected camera information we iterate the cameras that have been found
	//
    for (SCRSDK::CrInt32 n = 0; n < cntOfCamera; n++) 
    { 
      SCRSDK::ICrCameraObjectInfo *pobj = camera_list->GetCameraObjectInfo(n); 
      cli::text conn_type(pobj->GetConnectionTypeName());
      cli::text model(pobj->GetModel());
      cli::text id = TEXT("");
	  if (TEXT("USB") == conn_type)
      {
         std::cout << "Connect to selected camera... " << n << std::endl;
         auto* camera_info = camera_list->GetCameraObjectInfo(n);

         std::cout << "Create camera SDK camera callback object.\n";
         camera = SCRSDK::CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));

         //std::cout << "Release enumerated camera list.\n";
         //camera_list->Release();

         SCRSDK::CrError err = SCRSDK::Connect(camera_list, static_cast<SCRSDK::MyDeviceCallback *>&camera, &hDev); 
         if (err == SCRSDK::CrError_Init)
         {
	       std::cout << "The SDK is not properly initialised" << std::endl;
		   camera_list->Release();
           return NULL; 	   
         }
         else if (err == SCRSDK::CrError_Generic_Unknown)
         {
	       std::cout << "The pCameraObjectInfo is NULL, and no valid deviceNumber is supplied" << std::endl;
           camera_list->Release();
           return NULL; 		   
         }
         std::cout << "Camera connection successfully initiated!\n\n";
		 n = ++cntOfCamera;  // break iteration we only have one usb camera
	  }		        
    } 
    std::cout << "Release enumerated camera list.\n";	
    camera_list->Release();

    return hDev;
}

SCRSDK::CameraDevicePtr alphaSonyCam::alphaCreateCameraConnectionWithDevicePtr(std::int32_t no) 
{
    std::int32_t cameraNumUniq = 1;
    std::int32_t selectCamera = 1;
    SCRSDK::CameraDevicePtr camera = NULL;
  
    SCRSDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
    // auto enum_status = cr_lib->EnumCameraObjects(&camera_list, 3);
    // auto enum_status = SCRSDK::EnumCameraObjects(&camera_list);
	auto enum_status = SCRSDK::EnumCameraObjects(*camera_list);
    if (enum_status == SCRSDK::CrError::CrError_Init)
    {
	   std::cout << "The SDK is not properly initialised" << std::endl;
	   camera_list->Release();
       return NULL; 	   
    }
    else if (enum_status == SCRSDK::CrError::CrError_Adaptor_HandlePlugin)
    {
       std::cout << "No plugin modules found" << std::endl;
	   camera_list->Release();
       return NULL; 		   
    }
    else if (camera_list == NULL) 
    {  
	   std::cout << "No cameras found" << std::endl;
	   camera_list->Release();
       return NULL; 
    }  
    auto cntOfCamera = camera_list->GetCount(); // get number of cameras 
    if ( cntOfCamera == 0 )
    {
	   std::cout << "Count of cameras was zero" << std::endl;
       camera_list->Release();	   
	   return NULL;
    }
 	
    std::cout << "Connect to selected camera...\n";
    auto* camera_info = camera_list->GetCameraObjectInfo(no - 1);

    std::cout << "Create camera SDK camera callback object.\n";
    camera = SCRSDK::CameraDevicePtr(new cli::CameraDevice(cameraNumUniq, nullptr, camera_info));

    std::cout << "Release enumerated camera list.\n";
    camera_list->Release();

    auto connect_status = camera->connect();
    if (!connect_status) 
	{
       std::cout << "Camera connection failed to initiate. Abort.\n";
       // cr_lib->Release();
       SCRSDK::Release();
       std::exit(EXIT_FAILURE);
    }
    std::cout << "Camera connection successfully initiated!\n\n";
	cameraList.push_back(camera);    	   // add each one to the global camera list if you need this
	return camera;
}

void alphaSonyCam::alphaCheckCamConnectWithDevicePtr(SCRSDK::CameraDevicePtr camera)
{
    if (camera->is_connected()) 
	{
        camera->disconnect();
    }
    else 
	{
        camera->connect();
    }
}

void alphaSonyCam::alphaCapImage(SCRSDK::CameraDevicePtr camera)
{
	camera->capture_image();
}

void alphaSonyCam::alphaShootS1(SCRSDK::CameraDevicePtr camera)
{
	camera->s1_shooting();
}

void alphaSonyCam::alphaAFShutter(SCRSDK::CameraDevicePtr camera)
{
	camera->af_shutter();
}

void alphaSonyCam::alphaContShoot(SCRSDK::CameraDevicePtr camera)
{
	camera->continuous_shooting();
}

void alphaSonyCam::alphaAperture(SCRSDK::CameraDevicePtr camera)
{
    camera->get_aperture();
    camera->set_aperture();
}

void alphaSonyCam::alphaISO(SCRSDK::CameraDevicePtr camera)
{
    camera->get_iso();
    camera->set_iso();
}

void alphaSonyCam::alphaShutSpeed(SCRSDK::CameraDevicePtr camera)
{
    camera->get_shutter_speed();
    camera->set_shutter_speed();
}

void alphaSonyCam::alphaShutSpeed(SCRSDK::CameraDevicePtr camera)
{
    camera->get_shutter_speed();
    camera->set_shutter_speed();
}

void alphaSonyCam::alphaGetLiveView(SCRSDK::CameraDevicePtr camera)
{
    camera->get_live_view();
}

void alphaSonyCam::alphaLiveViewImageQuality(SCRSDK::CameraDevicePtr camera)
{
    camera->get_live_view_image_quality();
    camera->set_live_view_image_quality();
}

void alphaSonyCam::alphaLiveViewImageQuality(SCRSDK::CameraDevicePtr camera)
{
    camera->get_live_view_image_quality();
    camera->set_live_view_image_quality();
}

void alphaSonyCam::alphaLiveViewImageStatus(SCRSDK::CameraDevicePtr camera)
{
    camera->get_live_view_status();
    camera->set_live_view_status();
}

void alphaSonyCam::alphaGetLiveViewImageStatus(SCRSDK::CameraDevicePtr camera)
{
    camera->get_live_view_status();
    camera->set_live_view_status();
}

void alphaSonyCam::alphaPositonKeySetting(SCRSDK::CameraDevicePtr camera)
{
    camera->get_position_key_setting();
    camera->set_position_key_setting();
}

void alphaSonyCam::alphaSetExposureProgramMode(SCRSDK::CameraDevicePtr camera)
{
    camera->get_exposure_program_mode();
    camera->set_exposure_program_mode();
}

void alphaSonyCam::alphaSetStillCaptureMode(SCRSDK::CameraDevicePtr camera)
{
    camera->get_still_capture_mode();
    camera->set_still_capture_mode();
}

void alphaSonyCam::alphaGetFocusMode(SCRSDK::CameraDevicePtr camera)
{
	camera->get_focus_mode();
    camera->set_focus_mode();
}

void alphaSonyCam::alphaGetFocusArea(SCRSDK::CameraDevicePtr camera)
{
    camera->get_focus_area();
    camera->set_focus_area();
}

void alphaSonyCam::alphaFELock(SCRSDK::CameraDevicePtr camera)
{
    camera->execute_lock_property(static_cast<SCRSDK::CrInt16u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_FEL);
}

void alphaSonyCam::alphaAWBLock(SCRSDK::CameraDevicePtr camera)
{
    camera->execute_lock_property(static_cast<SCRSDK::CrInt16u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AWBL);
}

void alphaSonyCam::alphaAFLLock(SCRSDK::CameraDevicePtr camera)
{
    camera->execute_lock_property(static_cast<SCRSDK::CrInt16u>SCRSDK::CrDevicePropertyCode::CrDeviceProperty_AFL);
}

void alphaSonyCam::alphaSetAFAreaPos(SCRSDK::CameraDevicePtr camera)
{
    camera->set_af_area_position();
}

void alphaSonyCam::alphaMediaFormat(SCRSDK::CameraDevicePtr camera)
{
    camera->get_select_media_format();
    camera->set_select_media_format();
}

void alphaSonyCam::alphaExecMovieRecord(SCRSDK::CameraDevicePtr camera)
{
    camera->execute_movie_rec();
}

void alphaSonyCam::alphaWhiteBal(SCRSDK::CameraDevicePtr camera)
{
    camera->get_white_balance();
    camera->set_white_balance();
}

void alphaSonyCam::alphaCustomWB(SCRSDK::CameraDevicePtr camera)
{
    camera->get_custom_wb();
    camera->set_custom_wb();
}

void alphaSonyCam::alphaZoomOp(SCRSDK::CameraDevicePtr camera)
{
    camera->get_zoom_operation();
    camera->set_zoom_operation();
}

void alphaSonyCam::resetCameraData()
{
	camera_image_count = 0;
	recording_time_ms = 0;
	lat - 0;
	lon = 0;
	alt = 0;
	relative_alt = 0;
	q[0] = 0;
	q[1] = 0;
	q[2] = 0;
	q[3] = 0;
	image_index = 0;
	capture_result = 0;
	file_url.clear();
}

// ------------------------- Print helpers ------------------------------------------------------------------------------
//
void alphaSonyCam::printBatteryLevel(SCRSDK::CrBatteryLevel retVal)
{
	switch (retVal)
	{
		case SCRSDK::CrBatteryLevel::CrBatteryLevel_PreEndBattery:
		std::cout << "battery level : PreEndBattery " << retval << std::endl;
		break;
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_4:								// Level 1/4
		std::cout << "battery level : 25% Battery " << retval << std::endl;
		break;
		
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_4:
		std::cout << "battery level : 50% Battery " << retval << std::endl;
		break;
						   
		case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_4:
		std::cout << "battery level : 75% Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_4_4:
		std::cout << "battery level : 100% Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_3:								// Level 1/3
		std::cout << "battery level : 33.3% Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_3:
		std::cout << "battery level : 66.7% Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_3:
		std::cout << "battery level : 100% Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_USBPowerSupply:	// USB Power Supply
		std::cout << "battery level : USB Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_PreEnd_PowerSupply:
		std::cout << "battery level : PreEndBattery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_4_PowerSupply:					// Level 1/4 with USB Power Supply
		std::cout << "battery level : 25% PSU Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_4_PowerSupply:
		std::cout << "battery level : 50% PSU Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_4_PowerSupply:
		std::cout << "battery level : 75% PSU Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_4_4_PowerSupply:
		std::cout << "battery level : 100% PSU Battery " << retval << std::endl;
		break;						   
						   
	    case SCRSDK::CrBatteryLevel::CrBatteryLevel_Fake:				// Fake
		std::cout << "battery level : Fake Battery " << retval << std::endl;
		break;						   

        default:
        std::cout << "not supported return value CrBatteryLevel " << retVal << std::endl;
        break;		
	}
}

// ........................... functions  which print the enumerated type that was sent or returned
//

void alphaSonyCam::printCrLiveViewPropertyCode(SCRSDK::CrLiveViewPropertyCode retVal)
{
	switch(retVal) 
	{ 
    case SCRSDK::CrLiveViewPropertyCode::CrLiveViewProperty_AF_Area_Position:
    std::cout << "enumeratedType returned was @= CrLiveViewProperty_AF_Area_Position" << std::endl;
    break;
    case SCRSDK::CrLiveViewPropertyCode::CrLiveViewProperty_Focus_Magnifier_Position:
    std::cout << "enumeratedType returned was @= CrLiveViewProperty_Focus_Magnifier_Position" << std::endl;
    break;
    case SCRSDK::CrLiveViewPropertyCode::CrLiveViewProperty_LiveViewUndefined:
    std::cout << "enumeratedType returned was @= CrLiveViewProperty_LiveViewUndefined" << std::endl;
    break;
    case SCRSDK::CrLiveViewPropertyCode::CrLiveViewProperty__LiveViewMaxVal:
    std::cout << "enumeratedType returned was @= CrLiveViewProperty__LiveViewMaxVal" << std::endl;
    break;
	default:
    std::cout << " unknown enum found CrLiveViewPropertyCode " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrLockIndicator(SCRSDK::CrLockIndicator retVal)
{
	switch(retVal) 
	{ 
    case SCRSDK::CrLockIndicator::CrLockIndicator_Unknown:
    std::cout << "enumeratedType returned was @= CrLockIndicator_Unknown" << std::endl;
    break;
    case SCRSDK::CrLockIndicator::CrLockIndicator_Unlocked:
    std::cout << "enumeratedType returned was @= CrLockIndicator_Unlocked" << std::endl;
    break;
    case SCRSDK::CrLockIndicator::CrLockIndicator_Locked:
    std::cout << "enumeratedType returned was @= CrLockIndicator_Locked" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found CrLockIndicator " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropValueSet(SCRSDK::CrPropValueSet retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropValueSet::CrPropValueMinus1:
    std::cout << "enumeratedType returned was @= CrPropValueMinus1" << std::endl;
    break;
    case SCRSDK::CrPropValueSet::CrPropValuePlus1:
    std::cout << "enumeratedType returned was @= CrPropValuePlus1" << std::endl;
    break;
    default:
    std::cout << " unknown enum found CrPropValueSet " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFnumberSet(SCRSDK::CrFnumberSet retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFnumberSet::CrFnumber_Unknown:
    std::cout << "enumeratedType returned was @= CrFnumber_Unknown" << std::endl;
    break;
    case SCRSDK::CrFnumberSet::CrFnumber_Nothing:
    std::cout << "enumeratedType returned was @= CrFnumber_Nothing" << std::endl;
    break;
    default:
    std::cout << " unknown enum found CrFnumberSet " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrShutterSpeedSet(SCRSDK::CrShutterSpeedSet retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrShutterSpeedSet::CrShutterSpeed_Bulb:
    std::cout << "enumeratedType returned was @= CrShutterSpeed_Bulb" << std::endl;
    break;
    case SCRSDK::CrShutterSpeedSet::CrShutterSpeed_Nothing:
    std::cout << "enumeratedType returned was @= CrShutterSpeed_Nothing" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found CrShutterSpeedSet " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrISOMode(SCRSDK::CrISOMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrISOMode::CrISO_Normal:
    std::cout << "enumeratedType returned was @= CrISO_Normal" << std::endl;
    break;
    case SCRSDK::CrISOMode::CrISO_MultiFrameNR:
    std::cout << "enumeratedType returned was @= CrISO_MultiFrameNR" << std::endl;
    break;
    case SCRSDK::CrISOMode::CrISO_MultiFrameNR_High:
    std::cout << "enumeratedType returned was @= CrISO_MultiFrameNR_High" << std::endl;
    break;
    case SCRSDK::CrISOMode::CrISO_AUTO:
    std::cout << "enumeratedType returned was @= CrISO_AUTO" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found CrISOMode " << retVal << std::endl;
    break;
	}
}

void alphaSonyCam::printCrExposureProgram(SCRSDK::CrExposureProgram retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrExposureProgram::CrExposure_M_Manual:
    std::cout << "enumeratedType returned was @= CrExposure_M_Manual" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_P_Auto:
    std::cout << "enumeratedType returned was @= CrExposure_P_Auto" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_A_AperturePriority:
    std::cout << "enumeratedType returned was @= CrExposure_A_AperturePriority" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_S_ShutterSpeedPriority:
    std::cout << "enumeratedType returned was @= CrExposure_S_ShutterSpeedPriority" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Program_Creative:
    std::cout << "enumeratedType returned was @= CrExposure_Program_Creative" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Program_Action:
    std::cout << "enumeratedType returned was @= CrExposure_Program_Action" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Portrait:
    std::cout << "enumeratedType returned was @= CrExposure_Portrait" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Auto:
    std::cout << "enumeratedType returned was @= CrExposure_Auto" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Auto_Plus:
    std::cout << "enumeratedType returned was @= CrExposure_Auto_Plus" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_P_A:
    std::cout << "enumeratedType returned was @= CrExposure_P_A" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_P_S:
    std::cout << "enumeratedType returned was @= CrExposure_P_S" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Sports_Action:
    std::cout << "enumeratedType returned was @= CrExposure_Sports_Action" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Sprots_Action:
    std::cout << "enumeratedType returned was @= CrExposure_Sprots_Action" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Sunset:
    std::cout << "enumeratedType returned was @= CrExposure_Sunset" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Night:
    std::cout << "enumeratedType returned was @= CrExposure_Night" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Landscape:
    std::cout << "enumeratedType returned was @= CrExposure_Landscape" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Macro:
    std::cout << "enumeratedType returned was @= CrExposure_Macro" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HandheldTwilight:
    std::cout << "enumeratedType returned was @= CrExposure_HandheldTwilight" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_NightPortrait:
    std::cout << "enumeratedType returned was @= CrExposure_NightPortrait" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_AntiMotionBlur:
    std::cout << "enumeratedType returned was @= CrExposure_AntiMotionBlur" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Pet:
    std::cout << "enumeratedType returned was @= CrExposure_Pet" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Gourmet:
    std::cout << "enumeratedType returned was @= CrExposure_Gourmet" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Fireworks:
    std::cout << "enumeratedType returned was @= CrExposure_Fireworks" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HighSensitivity:
    std::cout << "enumeratedType returned was @= CrExposure_HighSensitivity" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_MemoryRecall:
    std::cout << "enumeratedType returned was @= CrExposure_MemoryRecall" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_ContinuousPriority_AE_8pics:
    std::cout << "enumeratedType returned was @= CrExposure_ContinuousPriority_AE_8pics" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_ContinuousPriority_AE_10pics:
    std::cout << "enumeratedType returned was @= CrExposure_ContinuousPriority_AE_10pics" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_ContinuousPriority_AE_12pics:
    std::cout << "enumeratedType returned was @= CrExposure_ContinuousPriority_AE_12pics" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_3D_SweepPanorama:
    std::cout << "enumeratedType returned was @= CrExposure_3D_SweepPanorama" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_SweepPanorama:
    std::cout << "enumeratedType returned was @= CrExposure_SweepPanorama" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_P:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_P" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_A:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_A" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_S:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_S" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_M:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_M" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_Auto:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_Auto" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_SQMotion_P:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_SQMotion_P" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_SQMotion_A:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_SQMotion_A" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_SQMotion_S:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_SQMotion_S" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Movie_SQMotion_M:
    std::cout << "enumeratedType returned was @= CrExposure_Movie_SQMotion_M" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_Flash_Off:
    std::cout << "enumeratedType returned was @= CrExposure_Flash_Off" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_PictureEffect:
    std::cout << "enumeratedType returned was @= CrExposure_PictureEffect" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HiFrameRate_P:
    std::cout << "enumeratedType returned was @= CrExposure_HiFrameRate_P" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HiFrameRate_A:
    std::cout << "enumeratedType returned was @= CrExposure_HiFrameRate_A" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HiFrameRate_S:
    std::cout << "enumeratedType returned was @= CrExposure_HiFrameRate_S" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_HiFrameRate_M:
    std::cout << "enumeratedType returned was @= CrExposure_HiFrameRate_M" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_SQMotion_P:
    std::cout << "enumeratedType returned was @= CrExposure_SQMotion_P" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_SQMotion_A:
    std::cout << "enumeratedType returned was @= CrExposure_SQMotion_A" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_SQMotion_S:
    std::cout << "enumeratedType returned was @= CrExposure_SQMotion_S" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_SQMotion_M:
    std::cout << "enumeratedType returned was @= CrExposure_SQMotion_M" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_MOVIE:
    std::cout << "enumeratedType returned was @= CrExposure_MOVIE" << std::endl;
    break;
    case SCRSDK::CrExposureProgram::CrExposure_STILL:
    std::cout << "enumeratedType returned was @= CrExposure_STILL" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
    }
}

void alphaSonyCam::printCrFileType(SCRSDK::CrFileType retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFileType::CrFileType_Jpeg:
    std::cout << "enumeratedType returned was @= CrFileType_Jpeg" << std::endl;
    break;
    case SCRSDK::CrFileType::CrFileType_Raw:
    std::cout << "enumeratedType returned was @= CrFileType_Raw" << std::endl;
    break;
    case SCRSDK::CrFileType::CrFileType_RawJpeg:
    std::cout << "enumeratedType returned was @= CrFileType_RawJpeg" << std::endl;
    break;
    case SCRSDK::CrFileType::CrFileType_RawHeif:
    std::cout << "enumeratedType returned was @= CrFileType_RawHeif" << std::endl;
    break;
    case SCRSDK::CrFileType::CrFileType_Heif:
    std::cout << "enumeratedType returned was @= CrFileType_Heif" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrJpegQuality(SCRSDK::CrJpegQuality retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrJpegQuality::CrJpegQuality_Unknown:
    std::cout << "enumeratedType returned was @= CrJpegQuality_Unknown" << std::endl;
    break;
    case SCRSDK::CrJpegQuality::CrJpegQuality_Light:
    std::cout << "enumeratedType returned was @= CrJpegQuality_Light" << std::endl;
    break;
    case SCRSDK::CrJpegQuality::CrJpegQuality_Standard:
    std::cout << "enumeratedType returned was @= CrJpegQuality_Standard" << std::endl;
    break;
    case SCRSDK::CrJpegQuality::CrJpegQuality_Fine:
    std::cout << "enumeratedType returned was @= CrJpegQuality_Fine" << std::endl;
    break;
    case SCRSDK::CrJpegQuality::CrJpegQuality_ExFine:
    std::cout << "enumeratedType returned was @= CrJpegQuality_ExFine" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrWhiteBalanceSetting(SCRSDK::CrWhiteBalanceSetting retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_AWB:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_AWB" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Underwater_Auto:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Underwater_Auto" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Daylight:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Daylight" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Shadow:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Shadow" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Cloudy:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Cloudy" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Tungsten:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Tungsten" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Fluorescent:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Fluorescent" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Fluorescent_WarmWhite:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Fluorescent_WarmWhite" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Fluorescent_CoolWhite:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Fluorescent_CoolWhite" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Fluorescent_DayWhite:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Fluorescent_DayWhite" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Fluorescent_Daylight:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Fluorescent_Daylight" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Flush:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Flush" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_ColorTemp:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_ColorTemp" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Custom_1:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Custom_1" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Custom_2:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Custom_2" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Custom_3:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Custom_3" << std::endl;
    break;
    case SCRSDK::CrWhiteBalanceSetting::CrWhiteBalance_Custom:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Custom" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
    }
}

void alphaSonyCam::printCrFocusMode(SCRSDK::CrFocusMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFocusMode::CrFocus_MF:
    std::cout << "enumeratedType returned was @= CrFocus_MF" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_AF_S:
    std::cout << "enumeratedType returned was @= CrFocus_AF_S" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_AF_C:
    std::cout << "enumeratedType returned was @= CrFocus_AF_C" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_AF_A:
    std::cout << "enumeratedType returned was @= CrFocus_AF_A" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_AF_D:
    std::cout << "enumeratedType returned was @= CrFocus_AF_D" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_DMF:
    std::cout << "enumeratedType returned was @= CrFocus_DMF" << std::endl;
    break;
    case SCRSDK::CrFocusMode::CrFocus_PF:
    std::cout << "enumeratedType returned was @= CrFocus_PF" << std::endl;
    break;
	default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrMeteringMode(SCRSDK::CrMeteringMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrMeteringMode::CrMetering_Average:
    std::cout << "enumeratedType returned was @= CrMetering_Average" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_CenterWeightedAverage:
    std::cout << "enumeratedType returned was @= CrMetering_CenterWeightedAverage" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_MultiSpot:
    std::cout << "enumeratedType returned was @= CrMetering_MultiSpot" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_CenterSpot:
    std::cout << "enumeratedType returned was @= CrMetering_CenterSpot" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_Multi:
    std::cout << "enumeratedType returned was @= CrMetering_Multi" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_CenterWeighted:
    std::cout << "enumeratedType returned was @= CrMetering_CenterWeighted" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_EntireScreenAverage:
    std::cout << "enumeratedType returned was @= CrMetering_EntireScreenAverage" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_Spot_Standard:
    std::cout << "enumeratedType returned was @= CrMetering_Spot_Standard" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_Spot_Large:
    std::cout << "enumeratedType returned was @= CrMetering_Spot_Large" << std::endl;
    break;
    case SCRSDK::CrMeteringMode::CrMetering_HighLightWeighted:
    std::cout << "enumeratedType returned was @= CrMetering_HighLightWeighted" << std::endl;
    break;
	default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFlashMode(SCRSDK::CrFlashMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFlashMode::CrFlash_Auto:
    std::cout << "enumeratedType returned was @= CrFlash_Auto" << std::endl;
    break;
    case SCRSDK::CrFlashMode::CrFlash_Off:
    std::cout << "enumeratedType returned was @= CrFlash_Off" << std::endl;
    break;
    case SCRSDK::CrFlashMode::CrFlash_Fill:
    std::cout << "enumeratedType returned was @= CrFlash_Fill" << std::endl;
    break;
    case SCRSDK::CrFlashMode::CrFlash_ExternalSync:
    std::cout << "enumeratedType returned was @= CrFlash_ExternalSync" << std::endl;
    break;
    case SCRSDK::CrFlashMode::CrFlash_SlowSync:
    std::cout << "enumeratedType returned was @= CrFlash_SlowSync" << std::endl;
    break;
    case SCRSDK::CrFlashMode::CrFlash_RearSync:
    std::cout << "enumeratedType returned was @= CrFlash_RearSync" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrWirelessFlash(SCRSDK::CrWirelessFlash retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrWirelessFlash::CrWirelessFlash_Off:
    std::cout << "enumeratedType returned was @= CrWirelessFlash_Off" << std::endl;
    break;
    case SCRSDK::CrWirelessFlash::CrWirelessFlash_On:
    std::cout << "enumeratedType returned was @= CrWirelessFlash_On" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrRedEyeReduction(SCRSDK::CrRedEyeReduction retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrRedEyeReduction::CrRedEye_Off:
    std::cout << "enumeratedType returned was @= CrRedEye_Off" << std::endl;
    break;
    case SCRSDK::CrRedEyeReduction::CrRedEye_On:
    std::cout << "enumeratedType returned was @= CrRedEye_On" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrMediaFormat(SCRSDK::CrMediaFormat retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrMediaFormat::CrMediaFormat_Disable:
    std::cout << "enumeratedType returned was @= CrMediaFormat_Disable" << std::endl;
    break;
    case SCRSDK::CrMediaFormat::CrMediaFormat_Enable:
    std::cout << "enumeratedType returned was @= CrMediaFormat_Enable" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrCancelMediaFormat(SCRSDK::CrCancelMediaFormat retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrCancelMediaFormat::CrCancelMediaFormat_Disable:
    std::cout << "enumeratedType returned was @= CrCancelMediaFormat_Disable" << std::endl;
    break;
    case SCRSDK::CrCancelMediaFormat::CrCancelMediaFormat_Enable:
    std::cout << "enumeratedType returned was @= CrCancelMediaFormat_Enable" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrDriveMode(SCRSDK::CrDriveMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrDriveMode::CrDrive_Single:
    std::cout << "enumeratedType returned was @= CrDrive_Single" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Hi:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Hi" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Hi_Plus:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Hi_Plus" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Hi_Live:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Hi_Live" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Lo:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Lo" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_SpeedPriority:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_SpeedPriority" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Mid:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Mid" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Mid_Live:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Mid_Live" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Lo_Live:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Lo_Live" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_SingleBurstShooting_lo:
    std::cout << "enumeratedType returned was @= CrDrive_SingleBurstShooting_lo" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_SingleBurstShooting_mid:
    std::cout << "enumeratedType returned was @= CrDrive_SingleBurstShooting_mid" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_SingleBurstShooting_hi:
    std::cout << "enumeratedType returned was @= CrDrive_SingleBurstShooting_hi" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Timelapse:
    std::cout << "enumeratedType returned was @= CrDrive_Timelapse" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Timer_2s:
    std::cout << "enumeratedType returned was @= CrDrive_Timer_2s" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Timer_5s:
    std::cout << "enumeratedType returned was @= CrDrive_Timer_5s" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Timer_10s:
    std::cout << "enumeratedType returned was @= CrDrive_Timer_10s" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_03Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_03Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_03Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_03Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_03Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_03Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_05Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_05Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_05Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_05Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_05Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_05Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_07Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_07Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_07Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_07Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_07Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_07Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_10Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_10Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_10Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_10Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_10Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_10Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_20Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_20Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_20Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_20Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_30Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_30Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Bracket_30Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Bracket_30Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_03Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_03Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_03Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_03Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_03Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_03Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_05Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_05Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_05Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_05Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_05Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_05Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_07Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_07Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_07Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_07Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_07Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_07Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_10Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_10Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_10Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_10Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_10Ev_9pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_10Ev_9pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_20Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_20Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_20Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_20Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_30Ev_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_30Ev_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Single_Bracket_30Ev_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Single_Bracket_30Ev_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_WB_Bracket_Lo:
    std::cout << "enumeratedType returned was @= CrDrive_WB_Bracket_Lo" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_WB_Bracket_Hi:
    std::cout << "enumeratedType returned was @= CrDrive_WB_Bracket_Hi" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_DRO_Bracket_Lo:
    std::cout << "enumeratedType returned was @= CrDrive_DRO_Bracket_Lo" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_DRO_Bracket_Hi:
    std::cout << "enumeratedType returned was @= CrDrive_DRO_Bracket_Hi" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_2s_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_2s_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_2s_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_2s_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_5s_3pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_5s_3pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_Continuous_Timer_5s_5pics:
    std::cout << "enumeratedType returned was @= CrDrive_Continuous_Timer_5s_5pics" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_LPF_Bracket:
    std::cout << "enumeratedType returned was @= CrDrive_LPF_Bracket" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_RemoteCommander:
    std::cout << "enumeratedType returned was @= CrDrive_RemoteCommander" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_MirrorUp:
    std::cout << "enumeratedType returned was @= CrDrive_MirrorUp" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_SelfPortrait_1:
    std::cout << "enumeratedType returned was @= CrDrive_SelfPortrait_1" << std::endl;
    break;
    case SCRSDK::CrDriveMode::CrDrive_SelfPortrait_2:
    std::cout << "enumeratedType returned was @= CrDrive_SelfPortrait_2" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrDRangeOptimizer(SCRSDK::CrDRangeOptimizer retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Off:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Off" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_On:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_On" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus_Manual_1:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus_Manual_1" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus_Manual_2:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus_Manual_2" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus_Manual_3:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus_Manual_3" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus_Manual_4:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus_Manual_4" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Plus_Manual_5:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Plus_Manual_5" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_Auto:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_Auto" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_Auto:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_Auto" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_10Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_10Ev" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_20Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_20Ev" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_30Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_30Ev" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_40Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_40Ev" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_50Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_50Ev" << std::endl;
    break;
    case SCRSDK::CrDRangeOptimizer::CrDRangeOptimizer_HDR_60Ev:
    std::cout << "enumeratedType returned was @= CrDRangeOptimizer_HDR_60Ev" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrImageSize:(SCRSDK::CrImageSize retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrImageSize::CrImageSize_L:
    std::cout << "enumeratedType returned was @= CrImageSize_L" << std::endl;
    break;
    case SCRSDK::CrImageSize::CrImageSize_M:
    std::cout << "enumeratedType returned was @= CrImageSize_M" << std::endl;
    break;
    case SCRSDK::CrImageSize::CrImageSize_S:
    std::cout << "enumeratedType returned was @= CrImageSize_S" << std::endl;
    break;
    case SCRSDK::CrImageSize::CrImageSize_VGA:
    std::cout << "enumeratedType returned was @= CrImageSize_VGA" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrAspectRatioIndex(SCRSDK::CrAspectRatioIndex retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrAspectRatioIndex::CrAspectRatio_3_2:
    std::cout << "enumeratedType returned was @= CrAspectRatio_3_2" << std::endl;
    break;
    case SCRSDK::CrAspectRatioIndex::CrAspectRatio_16_9:
    std::cout << "enumeratedType returned was @= CrAspectRatio_16_9" << std::endl;
    break;
    case SCRSDK::CrAspectRatioIndex::CrAspectRatio_4_3:
    std::cout << "enumeratedType returned was @= CrAspectRatio_4_3" << std::endl;
    break;
    case SCRSDK::CrAspectRatioIndex::CrAspectRatio_1_1:
    std::cout << "enumeratedType returned was @= CrAspectRatio_1_1" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPictureEffect(SCRSDK::CrPictureEffect retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPictureEffect::CrPictureEffect_Off:
    std::cout << "enumeratedType returned was @= CrPictureEffect_Off" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_ToyCameraNormal:
    std::cout << "enumeratedType returned was @= CrPictureEffect_ToyCameraNormal" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_ToyCameraCool:
    std::cout << "enumeratedType returned was @= CrPictureEffect_ToyCameraCool" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_ToyCameraWarm:
    std::cout << "enumeratedType returned was @= CrPictureEffect_ToyCameraWarm" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_ToyCameraGreen:
    std::cout << "enumeratedType returned was @= CrPictureEffect_ToyCameraGreen" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_ToyCameraMagenta:
    std::cout << "enumeratedType returned was @= CrPictureEffect_ToyCameraMagenta" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_Pop:
    std::cout << "enumeratedType returned was @= CrPictureEffect_Pop" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PosterizationBW:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PosterizationBW" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PosterizationColor:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PosterizationColor" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_Retro:
    std::cout << "enumeratedType returned was @= CrPictureEffect_Retro" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_SoftHighkey:
    std::cout << "enumeratedType returned was @= CrPictureEffect_SoftHighkey" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PartColorRed:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PartColorRed" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PartColorGreen:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PartColorGreen" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PartColorBlue:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PartColorBlue" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_PartColorYellow:
    std::cout << "enumeratedType returned was @= CrPictureEffect_PartColorYellow" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_HighContrastMonochrome:
    std::cout << "enumeratedType returned was @= CrPictureEffect_HighContrastMonochrome" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_SoftFocusLow:
    std::cout << "enumeratedType returned was @= CrPictureEffect_SoftFocusLow" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_SoftFocusMid:
    std::cout << "enumeratedType returned was @= CrPictureEffect_SoftFocusMid" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_SoftFocusHigh:
    std::cout << "enumeratedType returned was @= CrPictureEffect_SoftFocusHigh" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_HDRPaintingLow:
    std::cout << "enumeratedType returned was @= CrPictureEffect_HDRPaintingLow" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_HDRPaintingMid:
    std::cout << "enumeratedType returned was @= CrPictureEffect_HDRPaintingMid" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_HDRPaintingHigh:
    std::cout << "enumeratedType returned was @= CrPictureEffect_HDRPaintingHigh" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_RichToneMonochrome:
    std::cout << "enumeratedType returned was @= CrPictureEffect_RichToneMonochrome" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureAuto:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureAuto" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureTop:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureTop" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureMidHorizontal:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureMidHorizontal" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureBottom:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureBottom" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureLeft:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureLeft" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureMidVertical:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureMidVertical" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureRight:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureRight" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureWaterColor:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureWaterColor" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureIllustrationLow:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureIllustrationLow" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureIllustrationMid:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureIllustrationMid" << std::endl;
    break;
    case SCRSDK::CrPictureEffect::CrPictureEffect_MiniatureIllustrationHigh:
    std::cout << "enumeratedType returned was @= CrPictureEffect_MiniatureIllustrationHigh" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrMovie_Recording_State(SCRSDK::CrMovie_Recording_State retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrMovie_Recording_State::CrMovie_Recording_State_Not_Recording:
    std::cout << "enumeratedType returned was @= CrMovie_Recording_State_Not_Recording" << std::endl;
    break;
    case SCRSDK::CrMovie_Recording_State::CrMovie_Recording_State_Recording:
    std::cout << "enumeratedType returned was @= CrMovie_Recording_State_Recording" << std::endl;
    break;
    case SCRSDK::CrMovie_Recording_State::CrMovie_Recording_State_Recording_Failed:
    std::cout << "enumeratedType returned was @= CrMovie_Recording_State_Recording_Failed" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFocusArea(SCRSDK::CrFocusArea retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFocusArea::CrFocusArea_Unknown:
    std::cout << "enumeratedType returned was @= CrFocusArea_Unknown" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Wide:
    std::cout << "enumeratedType returned was @= CrFocusArea_Wide" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Zone:
    std::cout << "enumeratedType returned was @= CrFocusArea_Zone" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Center:
    std::cout << "enumeratedType returned was @= CrFocusArea_Center" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Flexible_Spot_S:
    std::cout << "enumeratedType returned was @= CrFocusArea_Flexible_Spot_S" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Flexible_Spot_M:
    std::cout << "enumeratedType returned was @= CrFocusArea_Flexible_Spot_M" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Flexible_Spot_L:
    std::cout << "enumeratedType returned was @= CrFocusArea_Flexible_Spot_L" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Expand_Flexible_Spot:
    std::cout << "enumeratedType returned was @= CrFocusArea_Expand_Flexible_Spot" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Flexible_Spot:
    std::cout << "enumeratedType returned was @= CrFocusArea_Flexible_Spot" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Wide:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Wide" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Zone:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Zone" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Center:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Center" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Flexible_Spot_S:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Flexible_Spot_S" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Flexible_Spot_M:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Flexible_Spot_M" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Flexible_Spot_L:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Flexible_Spot_L" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Expand_Flexible_Spot:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Expand_Flexible_Spot" << std::endl;
    break;
    case SCRSDK::CrFocusArea::CrFocusArea_Tracking_Flexible_Spot:
    std::cout << "enumeratedType returned was @= CrFocusArea_Tracking_Flexible_Spot" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrColortemp(SCRSDK::CrColortemp retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrColortemp::CrColortemp_Min:
    std::cout << "enumeratedType returned was @= CrColortemp_Min" << std::endl;
    break;
    case SCRSDK::CrColortemp::CrColortemp_Max:
    std::cout << "enumeratedType returned was @= CrColortemp_Max" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrColorTuning(SCRSDK::CrColorTuning retVal)
{
#if defined(__cpp_using_enum) // c++20 feature testing
    switch (retVal) 
    {
        using SCRSDK::CrColorTuning;
        case CrColorTuning_Min: std::cout << "enumeratedType returned was @= CrColorTuning_Min" << std::endl; break;
        case CrColorTuning_Max: std::cout << "enumeratedType returned was @= CrColorTuning_Max" << std::endl; break;
        case default: 
        if (retVal < CrColorTuning::CrColorTuning_Min) std::cout << retVal << " is less than min " << SCRSDK::CrColorTuning::CrColorTuning_Min << std::endl; 
        if (retVal > CrColorTuning::CrColorTuning_Max) std::cout << retVal << " is greater than max " <<  SCRSDK::CrColorTuning::CrColorTuning_Max << std::endl;
        std::cout << " color tuning was set to @= " << retVal << std::endl;
        break;
    }
#else
	switch(retVal)
	{
       case SCRSDK::CrColorTuning::CrColorTuning_Min:
       std::cout << "enumeratedType returned was @= CrColorTuning_Min" << std::endl;
       break;
       
       case SCRSDK::CrColorTuning::CrColorTuning_Max:
       std::cout << "enumeratedType returned was @= CrColorTuning_Max" << std::endl;
       break;
	
       default:
	   if (retVal < SCRSDK::CrColorTuning::CrColorTuning_Min) std::cout << retVal << " is less than min " << SCRSDK::CrColorTuning::CrColorTuning_Min << std::endl;
	   if (retVal > SCRSDK::CrColorTuning::CrColorTuning_Max) std::cout << retVal << " is greater than max " <<  SCRSDK::CrColorTuning::CrColorTuning_Max << std::endl;
       std::cout << " color tuning was set to @= " << retVal << std::endl;
       break;
	}
#endif
}

void alphaSonyCam::printCrLiveViewDisplayEffect(SCRSDK::CrLiveViewDisplayEffect retVal)
{
#if defined(__cpp_using_enum) // c++20 feature testing
    switch (retVal) 
    {
        using SCRSDK::CrLiveViewDisplayEffect;
        case CrLiveViewDisplayEffect_Unknown:
        std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_Unknown" << std::endl;
        break;
        case CrLiveViewDisplayEffect_ON:
        std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_ON" << std::endl;
        break;
        case CrLiveViewDisplayEffect_OFF:
        std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_OFF" << std::endl;
        break;
	
        default:
        std::cout << " unknown enum found " << std::endl;
        break;
    }
#else
	switch(retVal)
	{
       case SCRSDK::CrLiveViewDisplayEffect::CrLiveViewDisplayEffect_Unknown:
       std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_Unknown" << std::endl;
       break;
       
       case SCRSDK::CrLiveViewDisplayEffect::CrLiveViewDisplayEffect_ON:
       std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_ON" << std::endl;
       break;
       
       case SCRSDK::CrLiveViewDisplayEffect::CrLiveViewDisplayEffect_OFF:
       std::cout << "enumeratedType returned was @= CrLiveViewDisplayEffect_OFF" << std::endl;
       break;
	
       default:
       std::cout << " unknown enum found " << std::endl;
       break;
	}
#endif
}

void alphaSonyCam::printCrStillImageStoreDestination(SCRSDK::CrStillImageStoreDestination retVal)
{
#if defined(__cpp_using_enum) // c++20 feature testing
    switch (retVal) 
    {
        using SCRSDK::CrStillImageStoreDestination;
        case CrStillImageStoreDestination_HostPC:
        std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_HostPC" << std::endl;
        break;
        case CrStillImageStoreDestination_MemoryCard:
        std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_MemoryCard" << std::endl;
        break;
        case CrStillImageStoreDestination_HostPCAndMemoryCard:
        std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_HostPCAndMemoryCard" << std::endl;
        break;
	
        default:
        std::cout << " unknown enum found " << std::endl;
        break;
    }
#else
	switch(retVal)
	{
    case SCRSDK::CrStillImageStoreDestination::CrStillImageStoreDestination_HostPC:
    std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_HostPC" << std::endl;
    break;
    case SCRSDK::CrStillImageStoreDestination::CrStillImageStoreDestination_MemoryCard:
    std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_MemoryCard" << std::endl;
    break;
    case SCRSDK::CrStillImageStoreDestination::CrStillImageStoreDestination_HostPCAndMemoryCard:
    std::cout << "enumeratedType returned was @= CrStillImageStoreDestination_HostPCAndMemoryCard" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
#endif
}

void alphaSonyCam::printCrNearFarEnableStatus(SCRSDK::CrNearFarEnableStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrNearFarEnableStatus::CrNearFar_Disable:
    std::cout << "enumeratedType returned was @= CrNearFar_Disable" << std::endl;
    break;
    case SCRSDK::CrNearFarEnableStatus::CrNearFar_Enable:
    std::cout << "enumeratedType returned was @= CrNearFar_Enable" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrIntervalRecMode(SCRSDK::CrIntervalRecMode retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrIntervalRecMode::CrIntervalRecMode_OFF:
    std::cout << "enumeratedType returned was @= CrIntervalRecMode_OFF" << std::endl;
    break;
    case SCRSDK::CrIntervalRecMode::CrIntervalRecMode_ON:
    std::cout << "enumeratedType returned was @= CrIntervalRecMode_ON" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrBatteryLevel(SCRSDK::CrBatteryLevel retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_PreEndBattery:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_PreEndBattery" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_4:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_1_4" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_4:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_2_4" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_4:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_3_4" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_4_4:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_4_4" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_3:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_1_3" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_3:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_2_3" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_3:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_3_3" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_USBPowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_USBPowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_PreEnd_PowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_PreEnd_PowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_1_4_PowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_1_4_PowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_2_4_PowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_2_4_PowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_3_4_PowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_3_4_PowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_4_4_PowerSupply:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_4_4_PowerSupply" << std::endl;
    break;
    case SCRSDK::CrBatteryLevel::CrBatteryLevel_Fake:
    std::cout << "enumeratedType returned was @= CrBatteryLevel_Fake" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrWhiteBalanceInitialize(SCRSDK::CrWhiteBalanceInitialize retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrWhiteBalanceInitialize::CrWhiteBalance_Initialized:
    std::cout << "enumeratedType returned was @= CrWhiteBalance_Initialized" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrLiveViewStatus:(SCRSDK::CrLiveViewStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrLiveViewStatus::CrLiveView_NotSupport:
    std::cout << "enumeratedType returned was @= CrLiveView_NotSupport" << std::endl;
    break;
    case SCRSDK::CrLiveViewStatus::CrLiveView_Disable:
    std::cout << "enumeratedType returned was @= CrLiveView_Disable" << std::endl;
    break;
    case SCRSDK::CrLiveViewStatus::CrLiveView_Enable:
    std::cout << "enumeratedType returned was @= CrLiveView_Enable" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrIntervalRecStatus(SCRSDK::CrIntervalRecStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrIntervalRecStatus::CrIntervalRecStatus_WaitingStart:
    std::cout << "enumeratedType returned was @= CrIntervalRecStatus_WaitingStart" << std::endl;
    break;
    case SCRSDK::CrIntervalRecStatus::CrIntervalRecStatus_IntervalShooting:
    std::cout << "enumeratedType returned was @= CrIntervalRecStatus_IntervalShooting" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFocusIndicator(SCRSDK::CrFocusIndicator retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_Unlocked:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_Unlocked" << std::endl;
    break;
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_Focused_AF_S:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_Focused_AF_S" << std::endl;
    break;
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_NotFocused_AF_S:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_NotFocused_AF_S" << std::endl;
    break;
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_Focused_AF_C:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_Focused_AF_C" << std::endl;
    break;
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_NotFocused_AF_C:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_NotFocused_AF_C" << std::endl;
    break;
    case SCRSDK::CrFocusIndicator::CrFocusIndicator_TrackingSubject_AF_C:
    std::cout << "enumeratedType returned was @= CrFocusIndicator_TrackingSubject_AF_C" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrSlotStatus(SCRSDK::CrSlotStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrSlotStatus::CrSlotStatus_OK:
    std::cout << "enumeratedType returned was @= CrSlotStatus_OK" << std::endl;
    break;
    case SCRSDK::CrSlotStatus::CrSlotStatus_NoCard:
    std::cout << "enumeratedType returned was @= CrSlotStatus_NoCard" << std::endl;
    break;
    case SCRSDK::CrSlotStatus::CrSlotStatus_CardError:
    std::cout << "enumeratedType returned was @= CrSlotStatus_CardError" << std::endl;
    break;
    case SCRSDK::CrSlotStatus::CrSlotStatus_RecognizingOrLockedError:
    std::cout << "enumeratedType returned was @= CrSlotStatus_RecognizingOrLockedError" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPriorityKeySettings(SCRSDK::CrPriorityKeySettings retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPriorityKeySettings::CrPriorityKey_CameraPosition:
    std::cout << "enumeratedType returned was @= CrPriorityKey_CameraPosition" << std::endl;
    break;
    case SCRSDK::CrPriorityKeySettings::CrPriorityKey_PCRemote:
    std::cout << "enumeratedType returned was @= CrPriorityKey_PCRemote" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFocusFrameType(SCRSDK::CrFocusFrameType retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFocusFrameType::CrFocusFrameType_Unknown:
    std::cout << "enumeratedType returned was @= CrFocusFrameType_Unknown" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFocusFrameState(SCRSDK::CrFocusFrameState retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFocusFrameState::CrFocusFrameState_Unknown:
    std::cout << "enumeratedType returned was @= CrFocusFrameState_Unknown" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFrameInfoType(SCRSDK::CrFrameInfoType retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFrameInfoType::CrFrameInfoType_Unknown:
    std::cout << "enumeratedType returned was @= CrFrameInfoType_Unknown" << std::endl;
    break;
    case SCRSDK::CrFrameInfoType::CrFrameInfoType_FocusFrameInfo:
    std::cout << "enumeratedType returned was @= CrFrameInfoType_FocusFrameInfo" << std::endl;
    break;
    case SCRSDK::CrFrameInfoType::CrFrameInfoType_Magnifier_Position:
    std::cout << "enumeratedType returned was @= CrFrameInfoType_Magnifier_Position" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyEnableFlag(SCRSDK::CrPropertyEnableFlag retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyEnableFlag::CrEnableValue_NotSupported:
    std::cout << "enumeratedType returned was @= CrEnableValue_NotSupported" << std::endl;
    break;
    case SCRSDK::CrPropertyEnableFlag::CrEnableValue_False:
    std::cout << "enumeratedType returned was @= CrEnableValue_False" << std::endl;
    break;
    case SCRSDK::CrPropertyEnableFlag::CrEnableValue_True:
    std::cout << "enumeratedType returned was @= CrEnableValue_True" << std::endl;
    break;
    case SCRSDK::CrPropertyEnableFlag::CrEnableValue_DisplayOnly:
    std::cout << "enumeratedType returned was @= CrEnableValue_DisplayOnly" << std::endl;
    break;
    case SCRSDK::CrPropertyEnableFlag::CrEnableValue_SetOnly:
    std::cout << "enumeratedType returned was @= CrEnableValue_SetOnly" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyVariableFlag(SCRSDK::CrPropertyVariableFlag retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyVariableFlag::CrEnableValue_Invalid:
    std::cout << "enumeratedType returned was @= CrEnableValue_Invalid" << std::endl;
    break;
    case SCRSDK::CrPropertyVariableFlag::CrEnableValue_Invariable:
    std::cout << "enumeratedType returned was @= CrEnableValue_Invariable" << std::endl;
    break;
    case SCRSDK::CrPropertyVariableFlag::CrEnableValue_Variable:
    std::cout << "enumeratedType returned was @= CrEnableValue_Variable" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyStillImageTransSize(SCRSDK::CrPropertyStillImageTransSize retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyStillImageTransSize::CrPropertyStillImageTransSize_Original:
    std::cout << "enumeratedType returned was @= CrPropertyStillImageTransSize_Original" << std::endl;
    break;
    case SCRSDK::CrPropertyStillImageTransSize::CrPropertyStillImageTransSize_SmallSizeJPEG:
    std::cout << "enumeratedType returned was @= CrPropertyStillImageTransSize_SmallSizeJPEG" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyRAWJPCSaveImage(SCRSDK::CrPropertyRAWJPCSaveImage retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyRAWJPCSaveImage::CrPropertyRAWJPCSaveImage_RAWAndJPEG:
    std::cout << "enumeratedType returned was @= CrPropertyRAWJPCSaveImage_RAWAndJPEG" << std::endl;
    break;
    case SCRSDK::CrPropertyRAWJPCSaveImage::CrPropertyRAWJPCSaveImage_JPEGOnly:
    std::cout << "enumeratedType returned was @= CrPropertyRAWJPCSaveImage_JPEGOnly" << std::endl;
    break;
    case SCRSDK::CrPropertyRAWJPCSaveImage::CrPropertyRAWJPCSaveImage_RAWOnly:
    std::cout << "enumeratedType returned was @= CrPropertyRAWJPCSaveImage_RAWOnly" << std::endl;
    break;
    case SCRSDK::CrPropertyRAWJPCSaveImage::CrPropertyRAWJPCSaveImage_RAWAndHEIF:
    std::cout << "enumeratedType returned was @= CrPropertyRAWJPCSaveImage_RAWAndHEIF" << std::endl;
    break;
    case SCRSDK::CrPropertyRAWJPCSaveImage::CrPropertyRAWJPCSaveImage_HEIFOnly:
    std::cout << "enumeratedType returned was @= CrPropertyRAWJPCSaveImage_HEIFOnly" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyLiveViewImageQuality(SCRSDK::CrPropertyLiveViewImageQuality retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyLiveViewImageQuality::CrPropertyLiveViewImageQuality_Low:
    std::cout << "enumeratedType returned was @= CrPropertyLiveViewImageQuality_Low" << std::endl;
    break;
    case SCRSDK::CrPropertyLiveViewImageQuality::CrPropertyLiveViewImageQuality_High:
    std::cout << "enumeratedType returned was @= CrPropertyLiveViewImageQuality_High" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyCustomWBOperation(SCRSDK::CrPropertyCustomWBOperation retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyCustomWBOperation::CrPropertyCustomWBOperation_Disable:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBOperation_Disable" << std::endl;
    break;
    case SCRSDK::CrPropertyCustomWBOperation::CrPropertyCustomWBOperation_Enable:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBOperation_Enable" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyCustomWBExecutionState(SCRSDK::CrPropertyCustomWBExecutionState retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyCustomWBExecutionState::CrPropertyCustomWBExecutionState_Invalid:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBExecutionState_Invalid" << std::endl;
    break;
    case SCRSDK::CrPropertyCustomWBExecutionState::CrPropertyCustomWBExecutionState_Standby:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBExecutionState_Standby" << std::endl;
    break;
    case SCRSDK::CrPropertyCustomWBExecutionState::CrPropertyCustomWBExecutionState_Capturing:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBExecutionState_Capturing" << std::endl;
    break;
    case SCRSDK::CrPropertyCustomWBExecutionState::CrPropertyCustomWBExecutionState_OperatingCamera:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBExecutionState_OperatingCamera" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrPropertyCustomWBCaptureButton(SCRSDK::CrPropertyCustomWBCaptureButton retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrPropertyCustomWBCaptureButton::CrPropertyCustomWBCapture_Up:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBCapture_Up" << std::endl;
    break;
    case SCRSDK::CrPropertyCustomWBCaptureButton::CrPropertyCustomWBCapture_Down:
    std::cout << "enumeratedType returned was @= CrPropertyCustomWBCapture_Down" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrFileFormatMovie(SCRSDK::CrFileFormatMovie retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_AVCHD:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_AVCHD" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_MP4:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_MP4" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_HS_8K:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_HS_8K" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_HS_4K:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_HS_4K" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_L_4K:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_L_4K" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_L_HD:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_L_HD" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_I_4K:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_I_4K" << std::endl;
    break;
    case SCRSDK::CrFileFormatMovie::CrFileFormatMovie_XAVC_S_I_HD:
    std::cout << "enumeratedType returned was @= CrFileFormatMovie_XAVC_S_I_HD" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrRecordingSettingMovie(SCRSDK::CrRecordingSettingMovie retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60p_50M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60p_50M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_30p_50M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_30p_50M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_24p_50M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_24p_50M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50p_50M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50p_50M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_50M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_50M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60i_24M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60i_24M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50i_24M_FX:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50i_24M_FX" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60i_17M_FH:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60i_17M_FH" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50i_17M_FH:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50i_17M_FH" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60p_28M_PS:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60p_28M_PS" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50p_28M_PS:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50p_28M_PS" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_24p_24M_FX:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_24p_24M_FX" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_24M_FX:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_24M_FX" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_24p_17M_FH:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_24p_17M_FH" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_17M_FH:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_17M_FH" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_120p_50M_1280x720:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_120p_50M_1280x720" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100p_50M_1280x720:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100p_50M_1280x720" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1920x1080_30p_16M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1920x1080_30p_16M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1920x1080_25p_16M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1920x1080_25p_16M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1280x720_30p_6M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1280x720_30p_6M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1280x720_25p_6M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1280x720_25p_6M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1920x1080_60p_28M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1920x1080_60p_28M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_1920x1080_50p_28M:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_1920x1080_50p_28M" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60p_25M_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60p_25M_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50p_25M_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50p_25M_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_30p_16M_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_30p_16M_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_16M_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_16M_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_120p_100M_1920x1080_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_120p_100M_1920x1080_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100p_100M_1920x1080_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100p_100M_1920x1080_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_120p_60M_1920x1080_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_120p_60M_1920x1080_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100p_60M_1920x1080_XAVC_S_HD:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100p_60M_1920x1080_XAVC_S_HD" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_30p_100M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_30p_100M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_100M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_100M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_24p_100M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_24p_100M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_30p_60M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_30p_60M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25p_60M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25p_60M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_24p_60M_XAVC_S_4K:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_24p_60M_XAVC_S_4K" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_600M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_600M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_500M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_500M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_400M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_400M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_300M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_300M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_280M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_280M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_250M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_250M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_240M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_240M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_222M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_222M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_200M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_200M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_200M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_200M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_200M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_200M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_185M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_185M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_150M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_150M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_150M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_150M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_140M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_140M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_111M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_111M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_100M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_100M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_93M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_93M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_89M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_89M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_75M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_75M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_60M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_60M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50M_422_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50M_422_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_50M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_50M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_45M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_45M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_30M_420_10bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_30M_420_10bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_25M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_25M_420_8bit" << std::endl;
    break;
    case SCRSDK::CrRecordingSettingMovie::CrRecordingSettingMovie_16M_420_8bit:
    std::cout << "enumeratedType returned was @= CrRecordingSettingMovie_16M_420_8bit" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrRecordingFrameRateSettingMovie(SCRSDK::CrRecordingFrameRateSettingMovie retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_120p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_120p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_100p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_100p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_60p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_60p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_50p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_50p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_30p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_30p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_25p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_25p" << std::endl;
    break;
    case SCRSDK::CrRecordingFrameRateSettingMovie::CrRecordingFrameRateSettingMovie_24p:
    std::cout << "enumeratedType returned was @= CrRecordingFrameRateSettingMovie_24p" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrCompressionFileFormat(SCRSDK::CrCompressionFileFormat retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrCompressionFileFormat::CrCompressionFileFormat_JPEG:
    std::cout << "enumeratedType returned was @= CrCompressionFileFormat_JPEG" << std::endl;
    break;
    case SCRSDK::CrCompressionFileFormat::CrCompressionFileFormat_HEIF_422:
    std::cout << "enumeratedType returned was @= CrCompressionFileFormat_HEIF_422" << std::endl;
    break;
    case SCRSDK::CrCompressionFileFormat::CrCompressionFileFormat_HEIF_420:
    std::cout << "enumeratedType returned was @= CrCompressionFileFormat_HEIF_420" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrZoomOperationEnableStatus(SCRSDK::CrZoomOperationEnableStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrZoomOperationEnableStatus::CrZoomOperationEnableStatus_Default:
    std::cout << "enumeratedType returned was @= CrZoomOperationEnableStatus_Default" << std::endl;
    break;
    case SCRSDK::CrZoomOperationEnableStatus::CrZoomOperationEnableStatus_Disable:
    std::cout << "enumeratedType returned was @= CrZoomOperationEnableStatus_Disable" << std::endl;
    break;
    case SCRSDK::CrZoomOperationEnableStatus::CrZoomOperationEnableStatus_Enable:
    std::cout << "enumeratedType returned was @= CrZoomOperationEnableStatus_Enable" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrZoomSettingType(SCRSDK::CrZoomSettingType retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrZoomSettingType::CrZoomSetting_OpticalZoomOnly:
    std::cout << "enumeratedType returned was @= CrZoomSetting_OpticalZoomOnly" << std::endl;
    break;
    case SCRSDK::CrZoomSettingType::CrZoomSetting_SmartZoomOnly:
    std::cout << "enumeratedType returned was @= CrZoomSetting_SmartZoomOnly" << std::endl;
    break;
    case SCRSDK::CrZoomSettingType::CrZoomSetting_On_ClearImageZoom:
    std::cout << "enumeratedType returned was @= CrZoomSetting_On_ClearImageZoom" << std::endl;
    break;
    case SCRSDK::CrZoomSettingType::CrZoomSetting_On_DigitalZoom:
    std::cout << "enumeratedType returned was @= CrZoomSetting_On_DigitalZoom" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrZoomTypeStatus(SCRSDK::CrZoomTypeStatus retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrZoomTypeStatus::CrZoomTypeStatus_OpticalZoom:
    std::cout << "enumeratedType returned was @= CrZoomTypeStatus_OpticalZoom" << std::endl;
    break;
    case SCRSDK::CrZoomTypeStatus::CrZoomTypeStatus_SmartZoom:
    std::cout << "enumeratedType returned was @= CrZoomTypeStatus_SmartZoom" << std::endl;
    break;
    case SCRSDK::CrZoomTypeStatus::CrZoomTypeStatus_ClearImageZoom:
    std::cout << "enumeratedType returned was @= CrZoomTypeStatus_ClearImageZoom" << std::endl;
    break;
    case SCRSDK::CrZoomTypeStatus::CrZoomTypeStatus_DigitalZoom:
    std::cout << "enumeratedType returned was @= CrZoomTypeStatus_DigitalZoom" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrZoomOperation(SCRSDK::CrZoomOperation retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrZoomOperation::CrZoomOperation_Wide:
    std::cout << "enumeratedType returned was @= CrZoomOperation_Wide" << std::endl;
    break;
    case SCRSDK::CrZoomOperation::CrZoomOperation_Stop:
    std::cout << "enumeratedType returned was @= CrZoomOperation_Stop" << std::endl;
    break;
    case SCRSDK::CrZoomOperation::CrZoomOperation_Tele:
    std::cout << "enumeratedType returned was @= CrZoomOperation_Tele" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrRAWFileCompressionType(SCRSDK::CrRAWFileCompressionType retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrRAWFileCompressionType::CrRAWFile_Uncompression:
    std::cout << "enumeratedType returned was @= CrRAWFile_Uncompression" << std::endl;
    break;
    case SCRSDK::CrRAWFileCompressionType::CrRAWFile_Compression:
    std::cout << "enumeratedType returned was @= CrRAWFile_Compression" << std::endl;
    break;
    case SCRSDK::CrRAWFileCompressionType::CrRAWFile_LossLess:
    std::cout << "enumeratedType returned was @= CrRAWFile_LossLess" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrCommandParam(SCRSDK::CrCommandParam retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrCommandParam::CrCommandParam_Up:
    std::cout << "enumeratedType returned was @= CrCommandParam_Up" << std::endl;
    break;
    case SCRSDK::CrCommandParam::CrCommandParam_Down:
    std::cout << "enumeratedType returned was @= CrCommandParam_Down" << std::endl;
    break;

    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrCommandId(SCRSDK::CrCommandId retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrCommandId::CrCommandId_Release:
    std::cout << "enumeratedType returned was @= CrCommandId_Release" << std::endl;
    break;
    case SCRSDK::CrCommandId::CrCommandId_MovieRecord:
    std::cout << "enumeratedType returned was @= CrCommandId_MovieRecord" << std::endl;
    break;
    case SCRSDK::CrCommandId::CrCommandId_CancelShooting:
    std::cout << "enumeratedType returned was @= CrCommandId_CancelShooting" << std::endl;
    break;
    case SCRSDK::CrCommandId::CrCommandId_MediaFormat:
    std::cout << "enumeratedType returned was @= CrCommandId_MediaFormat" << std::endl;
    break;
    case SCRSDK::CrCommandId::CrCommandId_MediaQuickFormat:
    std::cout << "enumeratedType returned was @= CrCommandId_MediaQuickFormat" << std::endl;
    break;
    case SCRSDK::CrCommandId::CrCommandId_CancelMediaFormat:
    std::cout << "enumeratedType returned was @= CrCommandId_CancelMediaFormat" << std::endl;
    break;	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	}
}

void alphaSonyCam::printCrError(SCRSDK::CrError retVal)
{
	switch(retVal)
	{
    case SCRSDK::CrError::CrError_None:
    std::cout << "enumeratedType returned was @= CrError_None" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic:
    std::cout << "enumeratedType returned was @= CrError_Generic" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric:
    std::cout << "enumeratedType returned was @= CrError_Genric" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File:
    std::cout << "enumeratedType returned was @= CrError_File" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect:
    std::cout << "enumeratedType returned was @= CrError_Connect" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Memory:
    std::cout << "enumeratedType returned was @= CrError_Memory" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Api:
    std::cout << "enumeratedType returned was @= CrError_Api" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Init:
    std::cout << "enumeratedType returned was @= CrError_Init" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Polling:
    std::cout << "enumeratedType returned was @= CrError_Polling" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor:
    std::cout << "enumeratedType returned was @= CrError_Adaptor" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Device:
    std::cout << "enumeratedType returned was @= CrError_Device" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Application:
    std::cout << "enumeratedType returned was @= CrError_Application" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Generic_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_Notimpl:
    std::cout << "enumeratedType returned was @= CrError_Generic_Notimpl" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_Abort:
    std::cout << "enumeratedType returned was @= CrError_Generic_Abort" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_NotSupported:
    std::cout << "enumeratedType returned was @= CrError_Generic_NotSupported" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_SeriousErrorNotSupported:
    std::cout << "enumeratedType returned was @= CrError_Generic_SeriousErrorNotSupported" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_InvalidHandle:
    std::cout << "enumeratedType returned was @= CrError_Generic_InvalidHandle" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Generic_InvalidParameter:
    std::cout << "enumeratedType returned was @= CrError_Generic_InvalidParameter" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Genric_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_Notimpl:
    std::cout << "enumeratedType returned was @= CrError_Genric_Notimpl" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_Abort:
    std::cout << "enumeratedType returned was @= CrError_Genric_Abort" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_NotSupported:
    std::cout << "enumeratedType returned was @= CrError_Genric_NotSupported" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_SeriousErrorNotSupported:
    std::cout << "enumeratedType returned was @= CrError_Genric_SeriousErrorNotSupported" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_InvalidHandle:
    std::cout << "enumeratedType returned was @= CrError_Genric_InvalidHandle" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Genric_InvalidParameter:
    std::cout << "enumeratedType returned was @= CrError_Genric_InvalidParameter" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_Unknown:
    std::cout << "enumeratedType returned was @= CrError_File_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_IllegalOperation:
    std::cout << "enumeratedType returned was @= CrError_File_IllegalOperation" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_IllegalParameter:
    std::cout << "enumeratedType returned was @= CrError_File_IllegalParameter" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_EOF:
    std::cout << "enumeratedType returned was @= CrError_File_EOF" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_OutOfRange:
    std::cout << "enumeratedType returned was @= CrError_File_OutOfRange" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_NotFound:
    std::cout << "enumeratedType returned was @= CrError_File_NotFound" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_DirNotFound:
    std::cout << "enumeratedType returned was @= CrError_File_DirNotFound" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_AlreadyOpened:
    std::cout << "enumeratedType returned was @= CrError_File_AlreadyOpened" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_PermissionDenied:
    std::cout << "enumeratedType returned was @= CrError_File_PermissionDenied" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_StorageFull:
    std::cout << "enumeratedType returned was @= CrError_File_StorageFull" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_AlreadyExists:
    std::cout << "enumeratedType returned was @= CrError_File_AlreadyExists" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_TooManyOpenedFiles:
    std::cout << "enumeratedType returned was @= CrError_File_TooManyOpenedFiles" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_ReadOnly:
    std::cout << "enumeratedType returned was @= CrError_File_ReadOnly" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantOpen:
    std::cout << "enumeratedType returned was @= CrError_File_CantOpen" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantClose:
    std::cout << "enumeratedType returned was @= CrError_File_CantClose" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantDelete:
    std::cout << "enumeratedType returned was @= CrError_File_CantDelete" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantRead:
    std::cout << "enumeratedType returned was @= CrError_File_CantRead" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantWrite:
    std::cout << "enumeratedType returned was @= CrError_File_CantWrite" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_CantCreateDir:
    std::cout << "enumeratedType returned was @= CrError_File_CantCreateDir" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_OperationAbortedByUser:
    std::cout << "enumeratedType returned was @= CrError_File_OperationAbortedByUser" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_UnsupportedOperation:
    std::cout << "enumeratedType returned was @= CrError_File_UnsupportedOperation" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_NotYetCompleted:
    std::cout << "enumeratedType returned was @= CrError_File_NotYetCompleted" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_Invalid:
    std::cout << "enumeratedType returned was @= CrError_File_Invalid" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_StorageNotExist:
    std::cout << "enumeratedType returned was @= CrError_File_StorageNotExist" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_SharingViolation:
    std::cout << "enumeratedType returned was @= CrError_File_SharingViolation" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_Rotation:
    std::cout << "enumeratedType returned was @= CrError_File_Rotation" << std::endl;
    break;
    case SCRSDK::CrError::CrError_File_SameNameFull:
    std::cout << "enumeratedType returned was @= CrError_File_SameNameFull" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Connect_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Connect:
    std::cout << "enumeratedType returned was @= CrError_Connect_Connect" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Reserved1:
    std::cout << "enumeratedType returned was @= CrError_Connect_Reserved1" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Release:
    std::cout << "enumeratedType returned was @= CrError_Connect_Release" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_GetProperty:
    std::cout << "enumeratedType returned was @= CrError_Connect_GetProperty" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_SendCommand:
    std::cout << "enumeratedType returned was @= CrError_Connect_SendCommand" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_HandlePlugin:
    std::cout << "enumeratedType returned was @= CrError_Connect_HandlePlugin" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Disconnected:
    std::cout << "enumeratedType returned was @= CrError_Connect_Disconnected" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_TimeOut:
    std::cout << "enumeratedType returned was @= CrError_Connect_TimeOut" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Reconnect_TimeOut:
    std::cout << "enumeratedType returned was @= CrError_Reconnect_TimeOut" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_FailRejected:
    std::cout << "enumeratedType returned was @= CrError_Connect_FailRejected" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_FailBusy:
    std::cout << "enumeratedType returned was @= CrError_Connect_FailBusy" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_FailUnspecified:
    std::cout << "enumeratedType returned was @= CrError_Connect_FailUnspecified" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Connect_Cancel:
    std::cout << "enumeratedType returned was @= CrError_Connect_Cancel" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Memory_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Memory_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Memory_OutOfMemory:
    std::cout << "enumeratedType returned was @= CrError_Memory_OutOfMemory" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Memory_InvalidPointer:
    std::cout << "enumeratedType returned was @= CrError_Memory_InvalidPointer" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Memory_Insufficient:
    std::cout << "enumeratedType returned was @= CrError_Memory_Insufficient" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Api_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Api_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Api_Insufficient:
    std::cout << "enumeratedType returned was @= CrError_Api_Insufficient" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Api_InvalidCalled:
    std::cout << "enumeratedType returned was @= CrError_Api_InvalidCalled" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Polling_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Polling_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Polling_InvalidVal_Intervals:
    std::cout << "enumeratedType returned was @= CrError_Polling_InvalidVal_Intervals" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_InvaildProperty:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_InvaildProperty" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_GetInfo:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_GetInfo" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Create:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Create" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_SendCommand:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_SendCommand" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_HandlePlugin:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_HandlePlugin" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_CreateDevice:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_CreateDevice" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_EnumDecvice:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_EnumDecvice" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Reset:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Reset" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Read:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Read" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Phase:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Phase" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_DataToWiaItem:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_DataToWiaItem" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_DeviceBusy:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_DeviceBusy" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Adaptor_Escape:
    std::cout << "enumeratedType returned was @= CrError_Adaptor_Escape" << std::endl;
    break;
    case SCRSDK::CrError::CrError_Device_Unknown:
    std::cout << "enumeratedType returned was @= CrError_Device_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Unknown:
    std::cout << "enumeratedType returned was @= CrWarning_Unknown" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Connect_Reconnected:
    std::cout << "enumeratedType returned was @= CrWarning_Connect_Reconnected" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Connect_Reconnecting:
    std::cout << "enumeratedType returned was @= CrWarning_Connect_Reconnecting" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_File_StorageFull:
    std::cout << "enumeratedType returned was @= CrWarning_File_StorageFull" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_SetFileName_Failed:
    std::cout << "enumeratedType returned was @= CrWarning_SetFileName_Failed" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_GetImage_Failed:
    std::cout << "enumeratedType returned was @= CrWarning_GetImage_Failed" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_FailedToSetCWB:
    std::cout << "enumeratedType returned was @= CrWarning_FailedToSetCWB" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_NetworkErrorOccurred:
    std::cout << "enumeratedType returned was @= CrWarning_NetworkErrorOccurred" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_NetworkErrorRecovered:
    std::cout << "enumeratedType returned was @= CrWarning_NetworkErrorRecovered" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Format_Failed:
    std::cout << "enumeratedType returned was @= CrWarning_Format_Failed" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Format_Invalid:
    std::cout << "enumeratedType returned was @= CrWarning_Format_Invalid" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Format_Complete:
    std::cout << "enumeratedType returned was @= CrWarning_Format_Complete" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Reserved1:
    std::cout << "enumeratedType returned was @= CrWarning_Reserved1" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Reserved2:
    std::cout << "enumeratedType returned was @= CrWarning_Reserved2" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Reserved3:
    std::cout << "enumeratedType returned was @= CrWarning_Reserved3" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Reserved4:
    std::cout << "enumeratedType returned was @= CrWarning_Reserved4" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Reserved5:
    std::cout << "enumeratedType returned was @= CrWarning_Reserved5" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Exposure_Started:
    std::cout << "enumeratedType returned was @= CrWarning_Exposure_Started" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_DateTime_Setting_Result_Invalid:
    std::cout << "enumeratedType returned was @= CrWarning_DateTime_Setting_Result_Invalid" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_DateTime_Setting_Result_OK:
    std::cout << "enumeratedType returned was @= CrWarning_DateTime_Setting_Result_OK" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_DateTime_Setting_Result_Parameter_Error:
    std::cout << "enumeratedType returned was @= CrWarning_DateTime_Setting_Result_Parameter_Error" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_DateTime_Setting_Result_Exclusion_Error:
    std::cout << "enumeratedType returned was @= CrWarning_DateTime_Setting_Result_Exclusion_Error" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_DateTime_Setting_Result_System_Error:
    std::cout << "enumeratedType returned was @= CrWarning_DateTime_Setting_Result_System_Error" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Frame_NotUpdated:
    std::cout << "enumeratedType returned was @= CrWarning_Frame_NotUpdated" << std::endl;
    break;
    case SCRSDK::CrError::CrNotify_All_Download_Complete:
    std::cout << "enumeratedType returned was @= CrNotify_All_Download_Complete" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Connect_Already:
    std::cout << "enumeratedType returned was @= CrWarning_Connect_Already" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Connect_OverLimitOfDevice:
    std::cout << "enumeratedType returned was @= CrWarning_Connect_OverLimitOfDevice" << std::endl;
    break;
    case SCRSDK::CrError::CrWarning_Format_Canceled:
    std::cout << "enumeratedType returned was @= CrWarning_Format_Canceled" << std::endl;
    break;
	
    default:
    std::cout << " unknown enum found " << std::endl;
    break;
	
    }
}

void alphaSonyCam::localeInit()
{
	// Change global locale to native locale
    std::locale::global(std::locale(""));

    // Make the stream's locale the same as the current global locale
    cli::tin.imbue(std::locale());
    cli::tout.imbue(std::locale());
}
#pragma warning (pop)

// ------------------------- Main Program example of use of sony alpha camera class -------------------------------------
//
//  #define TEST_THIS_CLASS
//
#if defined(TEST_THIS_CLASS)
int main(int argc, char** argv)
{
   // create camera class instance
   alphaSonyCam myAlphaCameraNo1;
   if (myAlphaCameraNo1.alphaInit() == true)
   {
	  SCRSDK::ICrCameraObjectInfo* e = myAlphaCameraNo1.Enumerate_Cameras();
      if ( e != NULL)
      {
		 SCRSDK::CrDeviceHandle h = myAlphaCameraNo1.alphaConnectCamera(e); 

         myAlphaCameraNo1.alphaReleaseShutterShoot(h, 1000);
		 
		 bool b = myAlphaCameraNo1.alphaDisconnect(h);
	  }		  
   }
   // destruct the class instance
   (&myAlphaCameraNo1)->~alphaSonyCam();
}
#endif

#endif // <------- end of the library 


