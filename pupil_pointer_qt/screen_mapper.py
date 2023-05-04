import os
import sys
import uuid
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Tuple

import cv2
import msgpack
import numpy as np
import numpy.typing as npt
import pupil_apriltags
from pupil_labs.realtime_api import GazeData

from surface_tracker import (
    CoordinateSpace,
    CornerId,
    Marker,
    MarkerId,
    Surface,
    SurfaceId,
    SurfaceLocation,
    SurfaceOrientation,
    SurfaceTracker,
    marker,
)

from camera_models import Dummy_Camera, Radial_Dist_Camera

class ScreenMapper:
    def __init__(
        self,
        camera: Optional["Radial_Dist_Camera"],
        surfaces: Iterable[Surface] = (),
    ) -> None:
        self._camera: Optional[Radial_Dist_Camera]
        self._detector: Optional[ApriltagDetector]
        self._tracker = SurfaceTracker()

        self.camera = camera
        self._surfaces: List[Surface] = list(surfaces)
        self._recent_result: Optional[MarkerMapperResult] = None

    def process_frame(self, frame, gaze):
        """
        1. Detect markers
        2. Locate defined surfaces
        3. (Optional) Map gaze to each located surface
        """
        if not all((self._camera, self._detector)):
            return

        markers = self._detector.detect_from_image(frame.bgr_pixels)

        surface_locations = {
            surface.uid: self._tracker.locate_surface(
                surface=surface,
                markers=markers,
            )
            for surface in self._surfaces
        }

        gaze_undistorted = self._camera.undistort_points_on_image_plane([[gaze.x, gaze.y]])

        gaze_mapped_norm: npt.NDArray[np.float32]
        mapped_gaze: Dict[SurfaceId, List[MarkerMappedGaze]] = {}
        for surface_uid, location in surface_locations.items():
            if location is None:
                mapped_gaze[surface_uid] = []
                continue

            gaze_mapped_norm = location._map_from_image_to_surface(gaze_undistorted)

            mapped_gaze[location.surface_uid] = [
                MarkerMappedGaze.from_norm_pos(surface_uid, norm, base)
                for base, norm in zip(gaze, gaze_mapped_norm.tolist())
            ]

        return MarkerMapperResult(markers, surface_locations, mapped_gaze)

    def set_screen_surface(self, marker_size, surface_size):
        print('Set screen surface', marker_size, surface_size)
        marker_verts = np.array([
            [0, marker_size],
            [0, 0],
            [marker_size, 0],
            [marker_size, marker_size]
        ])

        markers = [
            Marker.from_vertices(
                create_apriltag_marker_uid('tag36h11', 0),
                marker_verts,
                CornerId.TOP_LEFT,
                False
            ),
            Marker.from_vertices(
                create_apriltag_marker_uid('tag36h11', 1),
                marker_verts + [surface_size[0]-marker_size, 0],
                CornerId.TOP_LEFT,
                False
            ),
            Marker.from_vertices(
                create_apriltag_marker_uid('tag36h11', 2),
                marker_verts + [surface_size[0]-marker_size, surface_size[1]],
                CornerId.TOP_LEFT,
                False
            ),
            Marker.from_vertices(
                create_apriltag_marker_uid('tag36h11', 3),
                marker_verts + [0, surface_size[1]],
                CornerId.TOP_LEFT,
                False
            ),
        ]

        surface = self._tracker.define_surface('Screen 0', markers)
        self._surfaces = [surface]

        return surface

    @property
    def camera(self) -> Optional["Radial_Dist_Camera"]:
        return self._camera

    @camera.setter
    def camera(self, camera: Optional["Radial_Dist_Camera"]) -> None:
        self._camera = camera
        if camera is None:
            self._detector = None
        else:
            self._detector = ApriltagDetector(camera)

    @property
    def surfaces(self) -> Tuple[Surface]:
        return tuple(self._surfaces)


class MarkerMappedGaze(NamedTuple):
    aoi_id: SurfaceId
    x: float
    y: float
    is_on_aoi: bool
    base_datum: GazeData

    @classmethod
    def from_norm_pos(
        cls, aoi_id: SurfaceId, norm_pos: Tuple[float, float], base_datum: GazeData
    ):
        on_surface = (0.0 <= norm_pos[0] <= 1.0) and (0.0 <= norm_pos[1] <= 1.0)
        return cls(aoi_id, *norm_pos, on_surface, base_datum)


class MarkerMapperResult(NamedTuple):
    markers: List[Marker]
    located_aois: Dict[SurfaceId, Optional[SurfaceLocation]]
    mapped_gaze: Dict[SurfaceId, List[MarkerMappedGaze]]


def create_apriltag_marker_uid(tag_family: str, tag_id: int) -> MarkerId:
    # Construct the UID by concatinating the tag family and the tag id
    return MarkerId(f"{tag_family}:{tag_id}")

class ApriltagDetector:
    def __init__(self, camera_model: Radial_Dist_Camera):
        families = "tag36h11"
        self._camera_model = camera_model
        self._detector = pupil_apriltags.Detector(
            families=families, nthreads=2, quad_decimate=2.0, decode_sharpening=1.0
        )

    def detect_from_image(self, image: npt.NDArray[np.uint8]) -> List[Marker]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.detect_from_gray(gray)

    def detect_from_gray(self, gray: npt.NDArray[np.uint8]) -> List[Marker]:
        # Detect apriltag markers from the gray image
        markers = self._detector.detect(gray)

        # Ensure detected markers are unique
        # TODO: Between deplicate markers, pick the one with higher confidence
        uid_fn = self.__apiltag_marker_uid
        markers = {uid_fn(m): m for m in markers}.values()

        # Convert apriltag markers into surface tracker markers
        marker_fn = self.__apriltag_marker_to_surface_marker
        markers = [marker_fn(m) for m in markers]

        return markers

    @staticmethod
    def __apiltag_marker_uid(
        apriltag_marker: pupil_apriltags.Detection,
    ) -> MarkerId:
        family = apriltag_marker.tag_family.decode("utf-8")
        tag_id = int(apriltag_marker.tag_id)
        return create_apriltag_marker_uid(family, tag_id)

    def __apriltag_marker_to_surface_marker(
        self, apriltag_marker: pupil_apriltags.Detection
    ) -> Marker:

        # Construct the surface tracker marker UID
        uid = ApriltagDetector.__apiltag_marker_uid(apriltag_marker)

        # Extract vertices in the correct format form apriltag marker
        vertices = [[point] for point in apriltag_marker.corners]
        vertices = self._camera_model.undistort_points_on_image_plane(vertices)

        # TODO: Verify this is correct...
        starting_with = CornerId.TOP_LEFT
        clockwise = True

        return Marker.from_vertices(
            uid=uid,
            undistorted_image_space_vertices=vertices,
            starting_with=starting_with,
            clockwise=clockwise,
        )


class _CoreSurface(Surface):
    version = 1

    @property
    def uid(self) -> SurfaceId:
        return self.__uid

    @property
    def name(self) -> str:
        return self.__name

    @property
    def _registered_markers_by_uid_undistorted(self) -> Mapping[MarkerId, Marker]:
        return self.__registered_markers_by_uid_undistorted

    @_registered_markers_by_uid_undistorted.setter
    def _registered_markers_by_uid_undistorted(self, value: Mapping[MarkerId, Marker]):
        self.__registered_markers_by_uid_undistorted = value

    @property
    def orientation(self) -> SurfaceOrientation:
        return self.__orientation

    @orientation.setter
    def orientation(self, value: SurfaceOrientation):
        self.__orientation = value

    def as_dict(self) -> dict:
        registered_markers_undistorted = self._registered_markers_by_uid_undistorted
        registered_markers_undistorted = {
            k: v.as_dict() for k, v in registered_markers_undistorted.items()
        }
        return {
            "version": self.version,
            "uid": str(self.uid),
            "name": self.name,
            "reg_markers": registered_markers_undistorted,
            "orientation": self.orientation.as_dict(),
        }

    @staticmethod
    def from_dict(value: dict) -> "Surface":
        try:
            actual_version = value["version"]
            expected_version = _CoreSurface.version
            assert (
                expected_version == actual_version
            ), f"Surface version missmatch; expected {expected_version}, but got {actual_version}"

            for m in value["reg_markers"]:
                m["uid"] = m["uid"].replace("apriltag_v3:", "")

            registered_markers_undistorted = {
                m["uid"]: _CoreMarker.from_dict(m) for m in value["reg_markers"]
            }

            orientation_dict = value.get("orientation", None)
            if orientation_dict:
                orientation = SurfaceOrientation.from_dict(orientation_dict)
            else:
                # use default if surface was saved as dict before this change
                orientation = SurfaceOrientation()

            return _CoreSurface(
                uid=SurfaceId(value.get("uid", str(uuid.uuid4()))),
                name=value["name"],
                registered_markers_undistorted=registered_markers_undistorted,
                orientation=orientation,
            )
        except Exception as err:
            raise ValueError(err)

    def __init__(
        self,
        uid: SurfaceId,
        name: str,
        registered_markers_undistorted: Mapping[MarkerId, Marker],
        orientation: SurfaceOrientation,
    ):
        self.__uid = uid
        self.__name = name
        self.__registered_markers_by_uid_undistorted = registered_markers_undistorted
        self.__orientation = orientation
        assert all(
            m.coordinate_space == CoordinateSpace.SURFACE_UNDISTORTED
            for m in registered_markers_undistorted.values()
        )


class _CoreMarker(Marker):
    @property
    def uid(self) -> MarkerId:
        return self.__uid

    @property
    def coordinate_space(self) -> CoordinateSpace:
        return self.__coordinate_space

    def _vertices_in_order(self, order: List[CornerId]) -> List[Tuple[float, float]]:
        mapping = self.__vertices_by_corner_id
        return [mapping[c] for c in order]

    @staticmethod
    def from_dict(value: dict) -> "Marker":
        try:
            return _CoreMarker(
                uid=value["uid"],
                coordinate_space=CoordinateSpace.SURFACE_UNDISTORTED,
                vertices_by_corner_id=dict(zip(CornerId, value["verts_uv"])),
            )
        except Exception as err:
            raise ValueError(err)

    def as_dict(self) -> dict:
        return {
            "uid": self.__uid,
            "space": self.__coordinate_space,
            "vertices": self.__vertices_by_corner_id,
        }

    def __init__(
        self,
        uid: MarkerId,
        coordinate_space: CoordinateSpace,
        vertices_by_corner_id: Mapping[CornerId, Tuple[float, float]],
    ):
        self.__uid = uid
        self.__coordinate_space = coordinate_space
        self.__vertices_by_corner_id = vertices_by_corner_id


marker._Marker = _CoreMarker
