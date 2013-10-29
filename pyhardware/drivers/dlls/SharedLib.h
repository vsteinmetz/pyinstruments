#include "extcode.h"
#pragma pack(push)
#pragma pack(1)

#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
	int32_t dimSize;
	LStrHandle String[1];
	} LStrHandleArrayBase;
typedef LStrHandleArrayBase **LStrHandleArray;
typedef struct {
	double CoeffA;
	double CoeffB;
	double CoeffC;
	double MaxWl;
	double MinWl;
} Cluster;
typedef struct {
	int32_t dimSize;
	LStrHandle elt[1];
	} LStrHandleArray1Base;
typedef LStrHandleArray1Base **LStrHandleArray1;
typedef struct {
	LVBoolean status;
	uint32_t code;
	LStrHandle source;
} Cluster1;

/*!
 * MC_Add_Status_String
 */
void __stdcall MC_Add_Status_String(LVRefNum *reference, char StringToAdd[], 
	LVRefNum *referenceOut);
/*!
 * MC_Add_Waypoint_GUI
 */
void __stdcall MC_Add_Waypoint_GUI(LVBoolean IsNew, 
	LStrHandleArray *WaypointDataIn, Cluster *CalcParameters, uint32_t KeyHandle, 
	double ActWavelength, LStrHandleArray1 *WaypointData, LVBoolean *Canceled);
/*!
 * MC_Calibrate
 */
void __stdcall MC_Calibrate(double actualWavelength, Cluster *CalcParameters, 
	LVBoolean *CancelOut, double *actualWavelengthOut);
/*!
 * MC_Connect
 */
int32_t __stdcall MC_Connect(char RingTextText[], 
	int32_t *StoredPositionOffset, LVBoolean *Connected, uint32_t *KeyHandleOut, 
	Cluster *CalcParameters, double *Wavelength, int32_t *pPositionIs);
/*!
 * MC_Disconnect
 */
int32_t __stdcall MC_Disconnect(int32_t PositionOld, int32_t OffsetPosition, 
	uint32_t KeyHandle, Cluster1 *errorIn, int32_t *newOldPosition, 
	int32_t *newOffsetPosition);
/*!
 * MC_GetProfile
 */
int32_t __stdcall MC_GetProfile(uint32_t KeyHandle, Cluster *CalcParameters, 
	Cluster1 *errorIn, double *MaxSpeed, double *SpeedNmS, 
	double *accelerationNmS, double *decelerationNmS);
/*!
 * MC_Info
 */
void __stdcall MC_Info(void);
/*!
 * MC_MoveToWavelength_101
 */
int32_t __stdcall MC_MoveToWavelength_101(LVBoolean HPMDefF, 
	Cluster *CalcParametersIn, double WavelengthToGo, uint32_t KeyHandle, 
	double *NewWavelength, LVBoolean *MoveStoppedByUser, uint32_t *KeyHandleOut);
/*!
 * MC_Move_to_Wavelength
 */
int32_t __stdcall MC_Move_to_Wavelength(double WavelengthToGo, 
	int32_t OffsetPosition, Cluster *CalcParameters, uint32_t KeyHandle, 
	LVBoolean Modus, Cluster1 *errorIn, int32_t OldPosition, 
	uint32_t *KeyHandleOut, double *Wavelength, int32_t *NewPosition);
/*!
 * MC_Patrol_Waypoints_GUI
 */
void __stdcall MC_Patrol_Waypoints_GUI(uint32_t KeyHandle, 
	Cluster *CalcParameters, double CurrWavelengthIn);
/*!
 * MC_SetProfile
 */
int32_t __stdcall MC_SetProfile(uint32_t KeyHandle, Cluster *CalcParameters, 
	double SpeedNmS, Cluster1 *errorIn, double accelerationNmS, 
	double decelerationNmS, uint32_t *KeyHandleOut);
/*!
 * MC_System_Info
 */
void __stdcall MC_System_Info(double actualMotorPosition, 
	double actualWavelength, Cluster *CalcParameters);
/*!
 * MC_Watch
 */
int32_t __stdcall MC_Watch(uint32_t KeyHandle, int32_t PositionOld, 
	Cluster *CalcParameters, int32_t OffsetPosition, Cluster1 *errorIn, 
	int32_t *aktMotorposition, double *Wavelength, int32_t *Offset);

long __cdecl LVDLLStatus(char *errStr, int errStrLen, void *module);

/*
* Memory Allocation/Resize/Deallocation APIs for type 'LStrHandleArray'
*/
LStrHandleArray __cdecl AllocateLStrHandleArray (int32 elmtCount);
MgErr __cdecl ResizeLStrHandleArray (LStrHandleArray *hdlPtr, int32 elmtCount);
MgErr __cdecl DeAllocateLStrHandleArray (LStrHandleArray *hdlPtr);

/*
* Memory Allocation/Resize/Deallocation APIs for type 'LStrHandleArray1'
*/
LStrHandleArray1 __cdecl AllocateLStrHandleArray1 (int32 elmtCount);
MgErr __cdecl ResizeLStrHandleArray1 (LStrHandleArray1 *hdlPtr, int32 elmtCount);
MgErr __cdecl DeAllocateLStrHandleArray1 (LStrHandleArray1 *hdlPtr);

#ifdef __cplusplus
} // extern "C"
#endif

#pragma pack(pop)

