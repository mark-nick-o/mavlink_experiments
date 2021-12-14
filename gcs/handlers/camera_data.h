#ifndef CAMERA_DATA_LIB
#define CAMERA_DATA_LIB

#include <iostream>
#include <vector>

#include <mavlink.h>
#include <mavlink_types.h>

using namespace std;

struct cam_config_t
{
  std::uint8_t mode;
  std::uint8_t shutterSpeed;   
  std::uint8_t aperture;
  std::uint8_t iso;   
  std::uint8_t exposure;
  std::uint8_t identity;     
  std::uint8_t engCutOff;
};

struct cam_control_t
{
  std::uint8_t SessionControl;
  std::uint8_t ZoomAbsolute;	
  std::uint8_t ZoomRelative;
  std::uint8_t Focus;
  std::uint8_t Shoot;
  std::uint8_t CommandId;
  std::uint8_t ShotID;
};

struct vid_control_t
{
  std::uint8_t ID;
  std::uint8_t Transmission;	
  std::uint8_t Interval;
  std::uint8_t Recording;
};

/* ======================== read back structures of camera information ================================================= */

struct cameraMountOrietation_t
{
  std::uint32_t time_boot_ms;		              // ms	Timestamp (time since system boot).
  std::float roll;		                        // deg	Roll in global frame (set to NaN for invalid).
  std::float pitch;		                        // deg	Pitch in global frame (set to NaN for invalid).
  std::float yaw;		                          // deg	Yaw relative to vehicle (set to NaN for invalid).
  std::float yaw_absolute; 		                // deg	Yaw in absolute frame relative to Earth's North, north is 0 (set to NaN for invalid).
};

struct cameraInformation_t
{
	std::uint32_t time_boot_ms;		              // ms		Timestamp (time since system boot).
    std::uint8_t[32] vendor_name;	            // Name of the camera vendor
    std::uint8_t[32] model_name;	            // Name of the camera model
    std::uint32_t firmware_version;	          // Version of the camera firmware, encoded as: (Dev & 0xff) << 24 | (Patch & 0xff) << 16 | (Minor & 0xff) << 8 | (Major & 0xff)
    std::float focal_length;		              // mm		Focal length
    std::float sensor_size_h;		              // mm		Image sensor size horizontal
    std::float sensor_size_v;		              // mm		Image sensor size vertical
    std::uint16_t resolution_h;		            // pix		Horizontal image resolution
    std::uint16_t resolution_v;		            // pix		Vertical image resolution
    std::uint8_t lens_id;			                // Reserved for a lens ID
    std::uint32_t flags;			                // CAMERA_CAP_FLAGS	Bitmap of camera capability flags.
    std::uint16_t cam_definition_version;			// Camera definition version (iteration)
    std::char[140] cam_definition_uri;				// Camera definition URI (if any, otherwise only basic functions will be available). HTTP- (http://) and MAVLink FTP- (mavlinkftp://) formatted URIs are allowed (and both must be supported by any GCS that implements the Camera Protocol). The definition file may be xz compressed, which will be indicated by the file extension .xml.xz (a GCS that implements the protocol must support decompressing the file).
};

struct cameraImageSet_t
{
  std::uint32_t time_boot_ms;		       // ms Timestamp (time since system boot).
  std::uint8_t mode_id;			           // CAMERA_MODE	Camera mode
  std::float zoomLevel; 			         // Current zoom level (0.0 to 100.0, NaN if not known)
  std::float focusLevel; 	             // Current focus level (0.0 to 100.0, NaN if not known)
};

struct storageInfo_t
{
   std::uint8_t storage_id;				      // Storage ID (1 for first, 2 for second, etc.)
   std::uint8_t storage_count;			    // Number of storage devices
   std::uint8_t status;			            // STORAGE_STATUS	Status of storage
   std::float total_capacity;	          // MiB	Total capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
   std::float used_capacity;		        // MiB	Used capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
   std::float available_capacity;		    // MiB	Available storage capacity. If storage is not ready (STORAGE_STATUS_READY) value will be ignored.
   std::float read_speed;	              // MiB/s Read speed.
   std::float write_speed;	            // MiB/s Write speed.
   std::uint8_t type; 	                // STORAGE_TYPE	Type of storage
   std::char[32] name; 			            // Textual storage name to be used in UI (microSD 1, Internal Memory, etc.) This is a NULL terminated string. If it is exactly 32 characters long, add a terminating NULL. If this string is empty, the generic type is shown to the user.
   std::uint8_t storage_usage; 	 	      // STORAGE_USAGE_FLAG	Flags indicating whether this instance is preferred storage for photos, videos, etc. Note: Implementations should initially set the flags on the system-default storage id used for saving media (if possible/supported). This setting can then be overridden using `MAV_CMD_SET_STORAGE_USAGE`. If the media usage flags are not set, a GCS may assume storage ID 1 is the default storage for all media types.
};

struct camCapture_t
{
   std::uint32_t time_boot_ms;		       // ms	Timestamp (time since system boot).
   std::uint8_t	image_status;		         //Current status of image capturing (0: idle, 1: capture in progress, 2: interval set but idle, 3: interval set and capture in progress)
   std::uint8_t video_status;			       //Current status of video capturing (0: idle, 1: capture in progress)
   std::float image_interval;			       //Image capture interval
   std::uint32_t recording_time_ms;		   //ms	Elapsed time since recording started (0: Not supported/available). A GCS should compute recording time and use non-zero values of this field to correct any discrepancy.
   std::float available_capacity;		     //MiB	Available storage capacity.
   std::int32_t image_count; 			       //Total number of images captured ('forever', or until reset using MAV_CMD_STORAGE_FORMAT).
};

struct camImageCaptured_t
{
   std::uint32_t time_boot_ms;		        // ms	Timestamp (time since system boot).
   std::uint64_t time_utc;		            // us	Timestamp (time since UNIX epoch) in UTC. 0 for unknown.
   std::uint8_t camera_id;			          // Deprecated/unused. Component IDs are used to differentiate multiple cameras.
   std::int32_t lat;			                // Latitude where image was taken degE7
   std::int32_t lon;			                // Longitude where capture was taken
   std::int32_t alt;		                  // mm	Altitude (MSL) where image was taken
   std::int32_t relative_alt;		          // mm	Altitude above ground
   std::float[4] q;			                  // Quaternion of camera orientation (w, x, y, z order, zero-rotation is 1, 0, 0, 0)
   std::int32_t image_index;			        // Zero based index of this image (i.e. a new image will have index CAMERA_CAPTURE_STATUS.image count -1)
   std::int8_t capture_result;		        // Boolean indicating success (1) or failure (0) while capturing this image.
   char[205] file_url;			              // URL of image taken. Either local storage or http://foo.jpg if camera provides an HTTP interface.
};

// ==== state of mavlink send engine =====

// i.e. allowbale states of m_substate

enum mavSendState_e : std::int32_t
{
    DO_CMD_SEND_CAM_INFO,            //CAMERA_INFORMATION
    DO_CMD_SENT_CAM_INFO,
    DO_CMD_CONF_CAM_INFO,
    DO_CMD_SEND_CAM_SET,             //CAMERA_SETTINGS
    DO_CMD_SENT_CAM_SET,
    DO_CMD_CONF_CAM_SET,
    DO_CMD_SEND_STO_INFO,            //STORAGE_INFORMATION
    DO_CMD_SENT_STO_INFO,
    DO_CMD_CONF_STO_INFO,
    DO_CMD_SEND_VIDEO_STREAM_REQ,    //269
    DO_CMD_SENT_VIDEO_STREAM_REQ,
    DO_CMD_CONF_VIDEO_STREAM_REQ,
    DO_CMD_SEND_CAP_STA,             //CAMERA_CAPTURE_STATUS
    DO_CMD_SENT_CAP_STA,
    DO_CMD_CONF_CAP_STA,
    DO_CAM_SEND_MODE_CHANGE,
    DO_CAM_SENT_MODE_CHANGE,
    DO_CAM_CONF_MODE_CHANGE,
    DO_CAM_SEND_VC_START,
    DO_CAM_SENT_VC_START,
    DO_CAM_CONF_VC_START,
    DO_CAM_SEND_VC_STOP,
    DO_CAM_SENT_VC_STOP,
    DO_CAM_CONF_VC_STOP,
    DO_CAM_SEND_IM_START,
    DO_CAM_SENT_IM_START,
    DO_CAM_CONF_IM_START,
    DO_CAM_SEND_IM_STOP,
    DO_CAM_SENT_IM_STOP,
    DO_CAM_CONF_IM_STOP,
    DO_CAM_SEND_VIDEOST_START,
    DO_CAM_SENT_VIDEOST_START,
    DO_CAM_CONF_VIDEOST_START,
    DO_CAM_SEND_VIDEOST_STOP,
    DO_CAM_SENT_VIDEOST_STOP,
    DO_CAM_CONF_VIDEOST_STOP,
    DO_CAM_SEND_MODE,
    DO_CAM_SENT_MODE,
    DO_CAM_CONF_MODE,
    DO_CAM_SEND_ZOOM,
    DO_CAM_SENT_ZOOM,
    DO_CAM_CONF_ZOOM,
    DO_CAM_SEND_FOCUS,
    DO_CAM_SENT_FOCUS,
    DO_CAM_CONF_FOCUS,
    DO_CAM_SEND_CONFIG,
    DO_CAM_SENT_CONFIG,
    DO_CAM_CONF_CONFIG,
    DO_CAM_SEND_CONTROL,
    DO_CAM_SENT_CONTROL,
    DO_CAM_CONF_CONTROL,
    DO_VID_SEND_CONTROL,
    DO_VID_SENT_CONTROL,
    DO_VID_CONF_CONTROL,
    DO_MEDIA_SEND_FORMAT,
    DO_MEDIA_SENT_FORMAT,
    DO_MEDIA_CONF_FORMAT,
    DO_CAM_SEND_TRIGI,
    DO_CAM_SENT_TRIGI,
    DO_CAM_CONF_TRIGI,
    DO_CAM_SEND_RESET,
    DO_CAM_SENT_RESET,
    DO_CAM_CONF_RESET,
    DO_GIM_SEND_ROTAT,
    DO_GIM_SENT_ROTAT,
    DO_GIM_CONF_ROTAT,
    DO_GIM_SEND_RESET,
    DO_GIM_SENT_RESET,
    DO_GIM_CONF_RESET,
    DO_GIM_SEND_QUAT,
    DO_GIM_SENT_QUAT,
    DO_GIM_CONF_QUAT,
    DO_PI_SEND_RELAY1_ON,
    DO_PI_SENT_RELAY1_ON,
    DO_PI_SEND_RELAY1_OFF,
    DO_PI_SENT_RELAY1_OFF,
    DO_PI_SEND_RELAY2_ON,
    DO_PI_SENT_RELAY2_ON,
    DO_PI_SEND_RELAY2_OFF,
    DO_PI_SENT_RELAY2_OFF
};

// ==== heartbeat pulses determine our system health =====

// i.e. allowbale states of m_sendState

enum mavHealthState_e : std::int32_t
{
    GO_IDLE,
    HEART_RCV
};
#endif
