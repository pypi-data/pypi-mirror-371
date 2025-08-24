# SPDX-FileCopyrightText: 2025 Dan Peled
#
# SPDX-License-Identifier: GPL-3.0-or-later

import queue
import socket
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import cv2
import numpy as np
from cscore import (CameraServer, CvSink, UsbCamera, VideoCamera, VideoMode,
                    VideoSource)
from cv2.typing import Size
from ntcore import NetworkTable, NetworkTableEntry, NetworkTableInstance
from synapse.log import warn
from synapse_net.nt_client import NtClient
from synapse_net.proto.v1 import CalibrationDataProto, CameraProto
from wpimath import geometry

from ..stypes import CameraID, Frame, PipelineID, Resolution
from ..util import listToTransform3d, transform3dToList

PropName = str
PropertMetaDict = Dict[PropName, Dict[str, Union[int, float]]]
ResolutionString = str


class CameraPropKeys(Enum):
    kBrightness = "brightness"
    kContrast = "contrast"
    kSaturation = "saturation"
    kHue = "hue"
    kGain = "gain"
    kExposure = "exposure"
    kWhiteBalanceTemperature = "white_balance_temperature"
    kSharpness = "sharpness"
    kOrientation = "orientation"


CSCORE_TO_CV_PROPS = {
    "brightness": cv2.CAP_PROP_BRIGHTNESS,
    "contrast": cv2.CAP_PROP_CONTRAST,
    "saturation": cv2.CAP_PROP_SATURATION,
    "hue": cv2.CAP_PROP_HUE,
    "gain": cv2.CAP_PROP_GAIN,
    "exposure": cv2.CAP_PROP_EXPOSURE,
    "white_balance_temperature": cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,
    "sharpness": cv2.CAP_PROP_SHARPNESS,
}

CV_TO_CSCORE_PROPS = {v: k for k, v in CSCORE_TO_CV_PROPS.items()}


class CameraSettingsKeys(Enum):
    kViewID = "view_id"
    kRecord = "record"
    kPipeline = "pipeline"
    kPipelineType = "pipeline_t"


@dataclass
class CalibrationData:
    matrix: List[float]
    distCoeff: List[float]
    meanErr: float
    measuredRes: Resolution

    def toDict(self) -> Dict[str, Any]:
        return {
            CameraConfigKey.kMatrix.value: self.matrix,
            CameraConfigKey.kDistCoeff.value: self.distCoeff,
            CameraConfigKey.kMeasuredRes.value: self.measuredRes,
            CameraConfigKey.kMeanErr.value: self.meanErr,
        }

    @staticmethod
    def fromDict(data: Dict[str, Any]) -> "CalibrationData":
        return CalibrationData(
            matrix=data[CameraConfigKey.kMatrix.value],
            distCoeff=data[CameraConfigKey.kDistCoeff.value],
            measuredRes=data[CameraConfigKey.kMeasuredRes.value],
            meanErr=data[CameraConfigKey.kMeanErr.value],
        )

    def toProto(self, cameraIndex: CameraID) -> CalibrationDataProto:
        return CalibrationDataProto(
            camera_index=cameraIndex,
            mean_error=self.meanErr,
            resolution="x".join([str(dim) for dim in self.measuredRes]),
            camera_matrix=self.matrix,
            dist_coeffs=self.distCoeff,
        )


@dataclass
class CameraConfig:
    name: str
    id: str
    transform: geometry.Transform3d
    calibration: Dict[ResolutionString, CalibrationData]
    defaultPipeline: int
    streamRes: Resolution

    def toDict(self) -> Dict[str, Any]:
        return {
            CameraConfigKey.kName.value: self.name,
            CameraConfigKey.kPath.value: self.id,
            CameraConfigKey.kTransform.value: transform3dToList(self.transform),
            CameraConfigKey.kDefaultPipeline.value: self.defaultPipeline,
            CameraConfigKey.kStreamRes.value: list(self.streamRes),
            CameraConfigKey.kCalibration.value: {
                resolution: calib.toDict()
                for resolution, calib in self.calibration.items()
            },
        }

    @staticmethod
    def fromDict(data: Dict[str, Any]) -> "CameraConfig":
        calib = {
            key: CalibrationData.fromDict(calib)
            for key, calib in data.get(CameraConfigKey.kCalibration.value, {}).items()
        }

        return CameraConfig(
            name=data[CameraConfigKey.kName.value],
            id=data[CameraConfigKey.kPath.value],
            streamRes=data[CameraConfigKey.kStreamRes.value],
            transform=listToTransform3d(data[CameraConfigKey.kTransform.value]),
            defaultPipeline=data[CameraConfigKey.kDefaultPipeline.value],
            calibration=calib,
        )


class CameraConfigKey(Enum):
    kName = "name"
    kPath = "id"
    kDefaultPipeline = "default_pipeline"
    kMatrix = "matrix"
    kDistCoeff = "distCoeffs"
    kMeasuredRes = "measured_res"
    kStreamRes = "stream_res"
    kTransform = "transform"
    kCalibration = "calibration"
    kMeanErr = "mean_err"


def cscoreToOpenCVProp(prop: str) -> Optional[int]:
    return CSCORE_TO_CV_PROPS.get(prop)


def opencvToCscoreProp(prop: int) -> Optional[str]:
    return CV_TO_CSCORE_PROPS.get(prop)


class SynapseCamera(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.stream: str = ""

    @classmethod
    @abstractmethod
    def create(
        cls,
        *_,
        path: Union[str, int],
        name: str = "",
        index: CameraID,
    ) -> "SynapseCamera": ...

    def setIndex(self, cameraIndex: CameraID) -> None:
        self.cameraIndex: CameraID = cameraIndex
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        self.stream = f"http://{ip}:{1181 + cameraIndex}/?action=stream/stream.mjpeg"

    @abstractmethod
    def grabFrame(self) -> Tuple[bool, Optional[Frame]]: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def isConnected(self) -> bool: ...

    @abstractmethod
    def setProperty(self, prop: str, value: Union[int, float]) -> None: ...

    @abstractmethod
    def getProperty(self, prop: str) -> Union[int, float, None]: ...

    @abstractmethod
    def setVideoMode(self, fps: int, width: int, height: int) -> None: ...

    @abstractmethod
    def getResolution(self) -> Size: ...

    @abstractmethod
    def getSupportedResolutions(self) -> List[Size]: ...

    @abstractmethod
    def getPropertyMeta(self) -> Optional[PropertMetaDict]: ...

    @abstractmethod
    def getMaxFPS(self) -> float: ...

    def getSettingEntry(self, key: str) -> Optional[NetworkTableEntry]:
        if hasattr(self, "cameraIndex"):
            table: NetworkTable = getCameraTable(self)
            entry: NetworkTableEntry = table.getEntry(key)
            return entry
        return None

    def getSetting(self, key: str, defaultValue: Any) -> Any:
        if hasattr(self, "cameraIndex"):
            table: NetworkTable = getCameraTable(self)
            entry: NetworkTableEntry = table.getEntry(key)
            if not entry.exists():
                entry.setValue(defaultValue)
            return entry.getValue()
        return None

    def setSetting(self, key: str, value: Any) -> None:
        if hasattr(self, "cameraIndex"):
            table: NetworkTable = getCameraTable(self)
            entry: NetworkTableEntry = table.getEntry(key)
            entry.setValue(value)


class OpenCvCamera(SynapseCamera):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.cap: cv2.VideoCapture

    @classmethod
    def create(
        cls,
        *_,
        name: str = "",
        path: Union[str, int],
        index: CameraID,
    ) -> "OpenCvCamera":
        inst = OpenCvCamera(name)
        assert isinstance(path, int) or isinstance(path, str), (
            f"No valid path for camera {index}"
        )

        if isinstance(path, int):
            inst.cap = cv2.VideoCapture(path)
        if isinstance(path, str):
            inst.cap = cv2.VideoCapture(path, cv2.CAP_V4L2)

        return inst

    def getSupportedResolutions(self) -> List[Size]:
        return [self.getResolution()]

    def getPropertyMeta(self) -> Optional[PropertMetaDict]:
        return None

    def grabFrame(self) -> Tuple[bool, Optional[Frame]]:
        return self.cap.read()

    def isConnected(self) -> bool:
        return self.cap.isOpened()

    def close(self) -> None:
        self.cap.release()

    def setProperty(self, prop: str, value: Union[int, float]) -> None:
        if isinstance(prop, int) and self.cap:
            propInt = cscoreToOpenCVProp(prop)
            if propInt is not None:
                self.cap.set(propInt, value)

    def getProperty(self, prop: str) -> Union[int, float, None]:
        if isinstance(prop, int) and self.cap:
            propInt = cscoreToOpenCVProp(prop)
            if propInt is not None:
                return self.cap.get(propInt)
            else:
                return None
        return None

    def setVideoMode(self, fps: int, width: int, height: int) -> None:
        if self.cap:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def getResolution(self) -> Size:
        return (
            int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def getMaxFPS(self) -> float:
        desired_fps = 120
        self.cap.set(cv2.CAP_PROP_FPS, desired_fps)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        return actual_fps


class CsCoreCamera(SynapseCamera):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.camera: VideoCamera
        self.frameBuffer: np.ndarray
        self.sink: CvSink
        self.propertyMeta: PropertMetaDict = {}
        self._properties: Dict[str, Any] = {}
        self._videoModes: List[Any] = []
        self._validVideoModes: List[VideoMode] = []

        self._frameQueue: queue.Queue[Tuple[bool, Optional[np.ndarray]]] = queue.Queue(
            maxsize=5
        )
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()  # Add this

    @classmethod
    def create(
        cls,
        *_,
        path: Union[str, int],
        name: str = "",
        index: CameraID,
    ) -> "CsCoreCamera":
        inst = CsCoreCamera(name)

        if isinstance(path, int):
            inst.camera = UsbCamera(f"USB Camera {index}", path)
        elif isinstance(path, str):
            inst.camera = UsbCamera(f"USB Camera {index}", path)

        inst.sink = CameraServer.getVideo(inst.camera)
        inst.sink.getProperty("auto_exposure").set(0)

        # Cache properties and metadata
        props = inst.camera.enumerateProperties()
        inst._properties = {prop.getName(): prop for prop in props}
        inst.propertyMeta = {
            name: {
                "min": prop.getMin(),
                "max": prop.getMax(),
                "default": prop.getDefault(),
            }
            for name, prop in inst._properties.items()
        }

        # Cache video modes and valid resolutions
        inst._videoModes = inst.camera.enumerateVideoModes()
        inst._validVideoModes = [mode for mode in inst._videoModes]
        inst.setVideoMode(1000, 1920, 1080)

        # Initialize frame buffer to current resolution
        mode = inst.camera.getVideoMode()
        inst.frameBuffer = np.zeros((mode.height, mode.width, 3), dtype=np.uint8)

        # Start background frame grabbing thread
        inst._startFrameThread()

        return inst

    def getPropertyMeta(self) -> Optional[PropertMetaDict]:
        return self.propertyMeta

    def _startFrameThread(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._frameGrabberLoop, daemon=True)
        self._thread.start()

    def _frameGrabberLoop(self) -> None:
        while not self.isConnected():
            time.sleep(0.1)
        while self._running:
            with self._lock:  # Protect frame operations
                result = self.sink.grabFrame(self.frameBuffer)
            if len(result) > 0:
                ret, frame = result
                hasFrame = ret != 0
                if hasFrame:
                    frame_copy = frame.copy()  # no lock needed here; copying is safe
                    try:
                        self._frameQueue.put_nowait((hasFrame, frame_copy))
                    except queue.Full:
                        try:
                            self._frameQueue.get_nowait()
                        except queue.Empty:
                            pass
                        self._frameQueue.put_nowait((hasFrame, frame_copy))
                else:
                    self._waitForNextFrame()
            self._waitForNextFrame()

    def _waitForNextFrame(self):
        if self.isConnected():
            if self.camera.getVideoMode().fps > 0:
                time.sleep(
                    1.0 / self.camera.getVideoMode().fps / 2.0
                )  # Half the expected frame interval

    def grabFrame(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self._lock:  # Protect frame buffer access
            try:
                return self._frameQueue.get_nowait()
            except queue.Empty:
                return False, None

    def isConnected(self) -> bool:
        return self.camera.isConnected()

    def close(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        # Properly close camera connection
        self.camera.setConnectionStrategy(
            VideoSource.ConnectionStrategy.kConnectionForceClose
        )

    def setProperty(self, prop: str, value: Union[int, float, str]) -> None:
        if prop == "resolution" and isinstance(value, str):
            resolution = value.split("x")
            width = int(resolution[0])
            height = int(resolution[1])
            self.setVideoMode(int(self.getMaxFPS()), width, height)
        elif prop in self._properties:
            meta = self.propertyMeta[prop]
            value = int(np.clip(value, meta["min"], meta["max"]))
            self._properties[prop].set(value)

    def getProperty(self, prop: str) -> Union[int, float, None]:
        if prop in self._properties:
            return self._properties[prop].get()
        return None

    def setVideoMode(self, fps: int, width: int, height: int, _fallback=False) -> None:
        pixelFormat = VideoMode.PixelFormat.kMJPEG

        for mode in self._validVideoModes:
            if (
                width == mode.width
                and height == mode.height
                and mode.pixelFormat == pixelFormat
            ):
                self.camera.setVideoMode(
                    width=width,
                    height=height,
                    fps=mode.fps,
                    pixelFormat=pixelFormat,
                )
                self.frameBuffer = np.zeros((height, width, 3), dtype=np.uint8)
                return

        if not _fallback:
            # Find the largest available resolution and try again
            largest_mode = max(
                (m for m in self._validVideoModes if m.pixelFormat == pixelFormat),
                key=lambda m: m.width * m.height,
                default=None,
            )

            if largest_mode:
                warn(
                    f"Invalid video mode (width={width}, height={height}). "
                    f"Falling back to largest available mode ({largest_mode.width}x{largest_mode.height})."
                )
                self.setVideoMode(
                    fps, largest_mode.width, largest_mode.height, _fallback=True
                )
                return

        warn(
            f"No valid video modes found for pixelFormat={pixelFormat}. "
            f"Camera default settings will be used."
        )

    def getResolution(self) -> Resolution:
        videoMode = self.camera.getVideoMode()
        return (videoMode.width, videoMode.height)

    def getMaxFPS(self) -> float:
        return self.camera.getVideoMode().fps

    def getSupportedResolutions(self) -> List[Size]:
        resolutions = []
        for videomode in self._validVideoModes:
            resolutions.append((videomode.width, videomode.height))
        return resolutions


class CameraFactory:
    kOpenCV: Type[SynapseCamera] = OpenCvCamera
    kCameraServer: Type[SynapseCamera] = CsCoreCamera
    kDefault: Type[SynapseCamera] = kCameraServer

    @classmethod
    def create(
        cls,
        *_,
        cameraType: Type[SynapseCamera] = kDefault,
        cameraIndex: CameraID,
        path: Union[str, int],
        name: str = "",
    ) -> "SynapseCamera":
        cam: SynapseCamera = cameraType.create(
            path=path,
            name=name,
            index=cameraIndex,
        )
        cam.setIndex(cameraIndex)
        return cam


def cameraToProto(
    camid: CameraID,
    name: str,
    camera: SynapseCamera,
    pipelineIndex: PipelineID,
    defaultPipeline: PipelineID,
    kind: str,
) -> CameraProto:
    return CameraProto(
        name=name,
        index=camid,
        stream_path=camera.stream,
        kind=kind,
        pipeline_index=pipelineIndex,
        default_pipeline=defaultPipeline,
        max_fps=int(camera.getMaxFPS()),
    )


@cache
def getCameraTable(camera: SynapseCamera) -> NetworkTable:
    return (
        NetworkTableInstance.getDefault()
        .getTable(NtClient.NT_TABLE)
        .getSubTable(getCameraTableName(camera))
    )


def getCameraTableName(camera: SynapseCamera) -> str:
    return camera.name
