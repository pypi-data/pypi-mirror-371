from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
from datetime import datetime, timezone

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..utils import (
    filter_by_confidence,
    apply_category_mapping,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure,
    bbox_smoothing,
    BBoxSmoothingConfig,
    BBoxSmoothingTracker
)
from ..core.config import BaseConfig, AlertConfig
from ..utils.geometry_utils import get_bbox_bottom25_center, point_in_polygon

@dataclass
class DwellConfig(BaseConfig):
    """Configuration for dwell time use case."""
    enable_smoothing: bool = True
    smoothing_algorithm: str = "observability"
    smoothing_window_size: int = 20
    smoothing_cooldown_frames: int = 5
    smoothing_confidence_range_factor: float = 0.5
    confidence_threshold: float = 0.6
    dwell_threshold: float = 30.0  # in seconds
    zone_config: Optional[Dict[str, List[List[float]]]] = None
    usecase_categories: List[str] = field(default_factory=lambda: ["person"])
    target_categories: List[str] = field(default_factory=lambda: ["person"])
    alert_config: Optional[AlertConfig] = None
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {0: "person"})

class DwellUseCase(BaseProcessor):
    CATEGORY_DISPLAY = {"person": "Person"}

    def __init__(self):
        super().__init__("dwell")
        self.category = "general"
        self.CASE_TYPE: str = 'dwell'
        self.CASE_VERSION: str = '1.0'
        self.target_categories = ['person']
        self.smoothing_tracker = None
        self.tracker = None
        self._total_frame_counter = 0
        self._track_aliases: Dict[Any, Any] = {}
        self._canonical_tracks: Dict[Any, Dict[str, Any]] = {}
        self._track_merge_iou_threshold: float = 0.05
        self._track_merge_time_window: float = 7.0
        self._ascending_alert_list: List[int] = []
        self.current_incident_end_timestamp: str = "N/A"
        self.start_timer = None
        self._total_track_ids = set()
        self._current_frame_track_ids = set()
        self._total_count = 0
        self._last_update_time = time.time()
        self._total_count_list = []
        self._zone_current_track_ids = {}
        self._zone_total_track_ids = {}
        self._zone_current_counts = {}
        self._zone_total_counts = {}
        self._track_start_times: Dict[Any, float] = {}
        self._dwelling_tracks: set[Any] = set()

    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None,
                stream_info: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        processing_start = time.time()
        if not isinstance(config, DwellConfig):
            return self.create_error_result("Invalid config type", usecase=self.name, category=self.category, context=context)
        if context is None:
            context = ProcessingContext()

        data = self._normalize_yolo_results(data, config.index_to_category)
        input_format = match_results_structure(data)
        context.input_format = input_format
        context.confidence_threshold = config.confidence_threshold

        processed_data = filter_by_confidence(data, config.confidence_threshold) if config.confidence_threshold else data
        processed_data = apply_category_mapping(processed_data, config.index_to_category) if config.index_to_category else processed_data
        processed_data = [d for d in processed_data if d.get('category') in self.target_categories]

        if config.enable_smoothing:
            if self.smoothing_tracker is None:
                smoothing_config = BBoxSmoothingConfig(
                    smoothing_algorithm=config.smoothing_algorithm,
                    window_size=config.smoothing_window_size,
                    cooldown_frames=config.smoothing_cooldown_frames,
                    confidence_threshold=config.confidence_threshold,
                    confidence_range_factor=config.smoothing_confidence_range_factor,
                    enable_smoothing=True
                )
                self.smoothing_tracker = BBoxSmoothingTracker(smoothing_config)
            processed_data = bbox_smoothing(processed_data, self.smoothing_tracker.config, self.smoothing_tracker)

        try:
            from ..advanced_tracker import AdvancedTracker, TrackerConfig
            if self.tracker is None:
                self.tracker = AdvancedTracker(TrackerConfig())
            processed_data = self.tracker.update(processed_data)
        except Exception as e:
            self.logger.warning(f"AdvancedTracker failed: {e}")

        self._update_tracking_state(processed_data)
        self._total_frame_counter += 1

        current_time = self._get_current_time_float(stream_info)
        for det in processed_data:
            tid = det.get("track_id")
            if tid and tid not in self._track_start_times:
                self._track_start_times[tid] = current_time
            if tid and (current_time - self._track_start_times[tid]) > config.dwell_threshold:
                self._dwelling_tracks.add(tid)

        frame_number = stream_info.get("input_settings", {}).get("start_frame") if stream_info and stream_info.get("input_settings", {}).get("start_frame") == stream_info.get("input_settings", {}).get("end_frame") else None

        counting_summary = self._count_categories(processed_data, config)
        counting_summary['total_counts'] = self.get_total_counts()
        counting_summary['categories'] = {det.get("category", "unknown"): counting_summary["categories"].get(det.get("category", "unknown"), 0) + 1 for det in processed_data}

        zone_analysis = {}
        if config.zone_config and config.zone_config['zones']:
            zone_analysis = count_objects_in_zones(processed_data, config.zone_config['zones'])
            if zone_analysis:
                zone_analysis = self._update_zone_tracking(zone_analysis, processed_data, config)

        alerts = self._check_alerts(counting_summary, zone_analysis, frame_number, config)
        predictions = self._extract_predictions(processed_data)
        incidents_list = []
        tracking_stats_list = self._generate_tracking_stats(counting_summary, zone_analysis, alerts, config, frame_number, stream_info)
        business_analytics_list = self._generate_business_analytics(counting_summary, zone_analysis, alerts, config, stream_info, is_empty=True)
        summary_list = self._generate_summary(counting_summary, zone_analysis, incidents_list, tracking_stats_list, business_analytics_list, alerts)

        agg_summary = {str(frame_number): {
            "incidents": incidents_list[0] if incidents_list else {},
            "tracking_stats": tracking_stats_list[0] if tracking_stats_list else {},
            "business_analytics": business_analytics_list[0] if business_analytics_list else {},
            "alerts": alerts,
            "zone_analysis": zone_analysis,
            "human_text": summary_list[0] if summary_list else {}
        }}

        context.mark_completed()
        result = self.create_result(data={"agg_summary": agg_summary}, usecase=self.name, category=self.category, context=context)
        proc_time = time.time() - processing_start
        print(f"latency in ms: {proc_time * 1000.0:.2f} | Throughput fps: {(1.0 / proc_time) if proc_time > 0 else None:.2f} | Frame_Number: {self._total_frame_counter}")
        return result

    def _update_zone_tracking(self, zone_analysis: Dict[str, Dict[str, int]], detections: List[Dict], config: DwellConfig) -> Dict[str, Dict[str, Any]]:
        if not zone_analysis or not config.zone_config or not config.zone_config['zones']:
            return {}
        
        enhanced_zone_analysis = {}
        zones = config.zone_config['zones']
        current_frame_zone_tracks = {zone_name: set() for zone_name in zones.keys()}
        
        for zone_name in zones.keys():
            self._zone_current_track_ids.setdefault(zone_name, set())
            self._zone_total_track_ids.setdefault(zone_name, set())
        
        for detection in detections:
            track_id = detection.get("track_id")
            if not track_id:
                continue
            bbox = detection.get("bounding_box") or detection.get("bbox")
            if not bbox:
                continue
            center_point = get_bbox_bottom25_center(bbox)
            for zone_name, zone_polygon in zones.items():
                polygon_points = [(point[0], point[1]) for point in zone_polygon]
                if point_in_polygon(center_point, polygon_points):
                    current_frame_zone_tracks[zone_name].add(track_id)
                    if track_id not in self._total_count_list:
                        self._total_count_list.append(track_id)
        
        for zone_name, zone_counts in zone_analysis.items():
            current_tracks = current_frame_zone_tracks.get(zone_name, set())
            self._zone_current_track_ids[zone_name] = current_tracks
            self._zone_total_track_ids[zone_name].update(current_tracks)
            self._zone_current_counts[zone_name] = len(current_tracks)
            self._zone_total_counts[zone_name] = len(self._zone_total_track_ids[zone_name])
            enhanced_zone_analysis[zone_name] = {
                "current_count": self._zone_current_counts[zone_name],
                "total_count": self._zone_total_counts[zone_name],
                "current_track_ids": list(current_tracks),
                "total_track_ids": list(self._zone_total_track_ids[zone_name]),
                "original_counts": zone_counts
            }
        return enhanced_zone_analysis

    def _normalize_yolo_results(self, data: Any, index_to_category: Optional[Dict[int, str]] = None) -> Any:
        def to_bbox_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            if "bounding_box" in d and isinstance(d["bounding_box"], dict):
                return d["bounding_box"]
            if "bbox" in d:
                bbox = d["bbox"]
                if isinstance(bbox, dict):
                    return bbox
                if len(bbox) >= 4:
                    return {"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]}
            if "xyxy" in d and len(d["xyxy"]) >= 4:
                return {"x1": d["xyxy"][0], "y1": d["xyxy"][1], "x2": d["xyxy"][2], "y2": d["xyxy"][3]}
            if "xywh" in d and len(d["xywh"]) >= 4:
                cx, cy, w, h = d["xywh"]
                return {"x1": cx - w / 2, "y1": cy - h / 2, "x2": cx + w / 2, "y2": cy + h / 2}
            return {}

        def resolve_category(d: Dict[str, Any]) -> Tuple[str, Optional[int]]:
            raw_cls = d.get("category", d.get("category_id", d.get("class", d.get("cls"))))
            label_name = d.get("name")
            if isinstance(raw_cls, int) and index_to_category and raw_cls in index_to_category:
                return index_to_category[raw_cls], raw_cls
            if isinstance(raw_cls, str):
                return raw_cls, None
            if label_name:
                return str(label_name), None
            return "unknown", None

        def normalize_det(det: Dict[str, Any]) -> Dict[str, Any]:
            category_name, category_id = resolve_category(det)
            confidence = det.get("confidence", det.get("conf", det.get("score", 0.0)))
            bbox = to_bbox_dict(det)
            normalized = {"category": category_name, "confidence": confidence, "bounding_box": bbox}
            if category_id is not None:
                normalized["category_id"] = category_id
            for key in ("track_id", "frame_id", "masks", "segmentation"):
                if key in det:
                    normalized[key] = det[key]
            return normalized

        if isinstance(data, list):
            return [normalize_det(d) if isinstance(d, dict) else d for d in data]
        if isinstance(data, dict):
            return {k: [normalize_det(d) if isinstance(d, dict) else d for d in v] if isinstance(v, list) else normalize_det(v) if isinstance(v, dict) else v for k, v in data.items()}
        return data

    def _check_alerts(self, summary: dict, zone_analysis: Dict, frame_number: Any, config: DwellConfig) -> List[Dict]:
        def get_trend(data, lookback=900, threshold=0.6):
            window = data[-lookback:] if len(data) >= lookback else data
            if len(window) < 2:
                return True
            increasing = sum(1 for i in range(1, len(window)) if window[i] >= window[i - 1])
            return increasing / (len(window) - 1) >= threshold

        alerts = []
        frame_key = str(frame_number) if frame_number is not None else "current_frame"
        total_detections = summary.get("total_count", 0)
        per_category_count = summary.get("per_category_count", {})

        if config.alert_config and hasattr(config.alert_config, 'count_thresholds') and config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total_detections > threshold:
                    alerts.append({
                        "alert_type": getattr(config.alert_config, 'alert_type', ['Default']),
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": threshold,
                        "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                        "settings": dict(zip(getattr(config.alert_config, 'alert_type', ['Default']), getattr(config.alert_config, 'alert_value', ['JSON'])))
                    })
                elif category in per_category_count and per_category_count[category] > threshold:
                    alerts.append({
                        "alert_type": getattr(config.alert_config, 'alert_type', ['Default']),
                        "alert_id": f"alert_{category}_{frame_key}",
                        "incident_category": self.CASE_TYPE,
                        "threshold_level": threshold,
                        "ascending": get_trend(self._ascending_alert_list, lookback=900, threshold=0.8),
                        "settings": dict(zip(getattr(config.alert_config, 'alert_type', ['Default']), getattr(config.alert_config, 'alert_value', ['JSON'])))
                    })
        return alerts

    def _generate_tracking_stats(self, counting_summary: Dict, zone_analysis: Dict, alerts: List, config: DwellConfig,
                                frame_number: Optional[int] = None, stream_info: Optional[Dict[str, Any]] = None) -> List[Dict]:
        camera_info = self.get_camera_info_from_stream(stream_info)
        tracking_stats = []
        total_detections = counting_summary.get("total_count", 0)
        total_counts_dict = counting_summary.get("total_counts", {})
        per_category_count = counting_summary.get("per_category_count", {})
        current_timestamp = self._get_current_timestamp_str(stream_info)
        start_timestamp = self._get_start_timestamp_str(stream_info)
        high_precision_start_timestamp = self._get_current_timestamp_str(stream_info, precision=True)
        high_precision_reset_timestamp = self._get_start_timestamp_str(stream_info, precision=True)

        total_counts = [{"category": cat, "count": count} for cat, count in total_counts_dict.items() if count > 0]
        current_counts = [{"category": cat, "count": count} for cat, count in per_category_count.items() if count > 0 or total_detections > 0]

        detections = [self.create_detection_object(det.get("category", "person"), det.get("bounding_box", {}), 
                      segmentation=det.get("masks") or det.get("segmentation") or det.get("mask")) 
                      for det in counting_summary.get("detections", [])]

        alert_settings = [{
            "alert_type": getattr(config.alert_config, 'alert_type', ['Default']),
            "incident_category": self.CASE_TYPE,
            "threshold_level": config.alert_config.count_thresholds if hasattr(config.alert_config, 'count_thresholds') else {},
            "ascending": True,
            "settings": dict(zip(getattr(config.alert_config, 'alert_type', ['Default']), getattr(config.alert_config, 'alert_value', ['JSON'])))
        }] if config.alert_config and hasattr(config.alert_config, 'alert_type') else []

        human_text_lines = [f"Tracking Statistics:", f"CURRENT FRAME @ {current_timestamp}"]
        person_count = per_category_count.get("person", 0)
        human_text_lines.append(f"\tDetected {person_count} persons" if person_count > 0 else "\tNo persons detected")
        
        if zone_analysis:
            human_text_lines.append("\tZones (current):")
            for zone_name, zone_data in zone_analysis.items():
                current_count = zone_data.get("current_count", sum(v for v in zone_data.values() if isinstance(v, (int, float))) if isinstance(zone_data, dict) else 0)
                human_text_lines.append(f"\t{zone_name}: {int(current_count)}")
        
        human_text_lines.append(f"TOTAL SINCE {start_timestamp}")
        dwelling_count = len(self._dwelling_tracks)
        human_text_lines.append(f"\tPersons dwelled > {config.dwell_threshold}s: {dwelling_count}" if dwelling_count > 0 else f"\tNo persons dwelled > {config.dwell_threshold}s")
        
        if zone_analysis:
            human_text_lines.append("\tZones (total):")
            for zone_name, zone_data in zone_analysis.items():
                total_count = zone_data.get("total_count", len(zone_data.get("total_track_ids", [])) if isinstance(zone_data.get("total_track_ids"), list) else sum(v for v in zone_data.values() if isinstance(v, (int, float))))
                human_text_lines.append(f"\t{zone_name}: {int(total_count)}")
        else:
            total_persons = total_counts_dict.get("person", 0)
            human_text_lines.append(f"\tTotal unique persons: {total_persons}")
        
        human_text_lines.append(f"Alerts: {alerts[0].get('settings', {})} sent @ {current_timestamp}" if alerts else "Alerts: None")
        human_text = "\n".join(human_text_lines)

        reset_settings = [{"interval_type": "daily", "reset_time": {"value": 9, "time_unit": "hour"}}]
        tracking_stats.append(self.create_tracking_stats(
            total_counts=total_counts,
            current_counts=current_counts,
            detections=detections,
            human_text=human_text,
            camera_info=camera_info,
            alerts=alerts,
            alert_settings=alert_settings,
            reset_settings=reset_settings,
            start_time=high_precision_start_timestamp,
            reset_time=high_precision_reset_timestamp
        ))
        return tracking_stats

    def _generate_business_analytics(self, counting_summary: Dict, zone_analysis: Dict, alerts: Any, config: DwellConfig,
                                    stream_info: Optional[Dict[str, Any]] = None, is_empty=False) -> List[Dict]:
        return [] if is_empty else []

    def _generate_summary(self, summary: dict, zone_analysis: Dict, incidents: List, tracking_stats: List, business_analytics: List, alerts: List) -> List[str]:
        lines = [f"Application Name: {self.CASE_TYPE}", f"Application Version: {self.CASE_VERSION}"]
        if incidents:
            lines.append(f"Incidents:\n\t{incidents[0].get('human_text', 'No incidents detected')}")
        if tracking_stats:
            lines.append(f"Tracking Statistics:\n\t{tracking_stats[0].get('human_text', 'No tracking statistics detected')}")
        if business_analytics:
            lines.append(f"Business Analytics:\n\t{business_analytics[0].get('human_text', 'No business analytics detected')}")
        if not (incidents or tracking_stats or business_analytics):
            lines.append("Summary: No Summary Data")
        return ["\n".join(lines)]

    def _get_track_ids_info(self, detections: list) -> Dict[str, Any]:
        frame_track_ids = {det.get('track_id') for det in detections if det.get('track_id') is not None}
        total_track_ids = set().union(*(s for s in getattr(self, '_per_category_total_track_ids', {}).values()))
        return {
            "total_count": len(total_track_ids),
            "current_frame_count": len(frame_track_ids),
            "total_unique_track_ids": len(total_track_ids),
            "current_frame_track_ids": list(frame_track_ids),
            "last_update_time": time.time(),
            "total_frames_processed": self._total_frame_counter
        }

    def _update_tracking_state(self, detections: list):
        self._per_category_total_track_ids = getattr(self, '_per_category_total_track_ids', {cat: set() for cat in self.target_categories})
        self._current_frame_track_ids = {cat: set() for cat in self.target_categories}
        for det in detections:
            cat, raw_track_id = det.get("category"), det.get("track_id")
            if cat not in self.target_categories or raw_track_id is None:
                continue
            bbox = det.get("bounding_box", det.get("bbox"))
            canonical_id = self._merge_or_register_track(raw_track_id, bbox)
            det["track_id"] = canonical_id
            self._per_category_total_track_ids[cat].add(canonical_id)
            self._current_frame_track_ids[cat].add(canonical_id)

    def get_total_counts(self):
        return {cat: len(ids) for cat, ids in getattr(self, '_per_category_total_track_ids', {}).items()}

    def _format_timestamp_for_stream(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y:%m:%d %H:%M:%S')

    def _format_timestamp_for_video(self, timestamp: float) -> str:
        hours, minutes = int(timestamp // 3600), int((timestamp % 3600) // 60)
        seconds = round(timestamp % 60, 2)
        return f"{hours:02d}:{minutes:02d}:{seconds:.1f}"

    def _get_current_time_float(self, stream_info: Optional[Dict[str, Any]]) -> float:
        if not stream_info:
            return time.time()
        input_settings = stream_info.get("input_settings", {})
        if input_settings.get("start_frame") is not None:
            return input_settings.get("start_frame", 0) / input_settings.get("original_fps", 30)
        stream_time_str = input_settings.get("stream_info", {}).get("stream_time", "")
        if stream_time_str:
            try:
                return datetime.strptime(stream_time_str.replace(" UTC", ""), "%Y-%m-%d-%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp()
            except:
                return time.time()
        return time.time()

    def _get_current_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False, frame_id: Optional[str]=None) -> str:
        if not stream_info:
            return "00:00:00.00"
        input_settings = stream_info.get("input_settings", {})
        if precision and input_settings.get("start_frame", "na") != "na":
            start_time = (int(frame_id) if frame_id else input_settings.get("start_frame", 30)) / input_settings.get("original_fps", 30)
            return self._format_timestamp(input_settings.get("stream_time", "NA"))
        if input_settings.get("start_frame", "na") != "na":
            start_time = (int(frame_id) if frame_id else input_settings.get("start_frame", 30)) / input_settings.get("original_fps", 30)
            return self._format_timestamp(input_settings.get("stream_time", "NA"))
        stream_time_str = input_settings.get("stream_info", {}).get("stream_time", "")
        if stream_time_str:
            try:
                timestamp = datetime.strptime(stream_time_str.replace(" UTC", ""), "%Y-%m-%d-%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp()
                return self._format_timestamp_for_stream(timestamp)
            except:
                return self._format_timestamp_for_stream(time.time())
        return self._format_timestamp_for_stream(time.time())

    def _get_start_timestamp_str(self, stream_info: Optional[Dict[str, Any]], precision=False) -> str:
        if not stream_info:
            return "00:00:00"
        if precision:
            if self.start_timer is None or stream_info.get("input_settings", {}).get("start_frame", "na") == 1:
                self.start_timer = stream_info.get("input_settings", {}).get("stream_time", "NA")
            return self._format_timestamp(self.start_timer)
        if self.start_timer is None or stream_info.get("input_settings", {}).get("start_frame", "na") == 1:
            self.start_timer = stream_info.get("input_settings", {}).get("stream_time", "NA")
            return self._format_timestamp(self.start_timer)
        if self._tracking_start_time is None:
            stream_time_str = stream_info.get("input_settings", {}).get("stream_info", {}).get("stream_time", "")
            self._tracking_start_time = (datetime.strptime(stream_time_str.replace(" UTC", ""), "%Y-%m-%d-%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp() 
                                        if stream_time_str else time.time())
        dt = datetime.fromtimestamp(self._tracking_start_time, tz=timezone.utc).replace(minute=0, second=0, microsecond=0)
        return dt.strftime('%Y:%m:%d %H:%M:%S')

    def _format_timestamp(self, timestamp: Any) -> str:
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d-%H:%M:%S.%f UTC')
        if not isinstance(timestamp, str):
            return str(timestamp)
        if '.' not in timestamp:
            return timestamp
        main_part, fractional_and_suffix = timestamp.split('.', 1)
        fractional_part, suffix = (fractional_and_suffix.split(' ', 1) if ' ' in fractional_and_suffix else (fractional_and_suffix, ''))[0], ' ' + fractional_and_suffix.split(' ', 1)[1] if ' ' in fractional_and_suffix else ''
        return f"{main_part}.{fractional_part[:2]}{suffix}"

    def _count_categories(self, detections: list, config: DwellConfig) -> dict:
        counts = {}
        for det in detections:
            cat = det.get('category', 'unknown')
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [{"bounding_box": det.get("bounding_box"), "category": det.get("category"), "confidence": det.get("confidence"), "track_id": det.get("track_id"), "frame_id": det.get("frame_id")} for det in detections]
        }

    def _extract_predictions(self, detections: list) -> List[Dict[str, Any]]:
        return [{"category": det.get("category", "unknown"), "confidence": det.get("confidence", 0.0), "bounding_box": det.get("bounding_box", {})} for det in detections]

    def _compute_iou(self, box1: Any, box2: Any) -> float:
        def _bbox_to_list(bbox):
            if not bbox:
                return []
            if isinstance(bbox, list) and len(bbox) >= 4:
                return bbox[:4]
            if isinstance(bbox, dict):
                return [bbox.get(k) for k in ("xmin", "ymin", "xmax", "ymax") if "xmin" in bbox] or [bbox.get(k) for k in ("x1", "y1", "x2", "y2") if "x1" in bbox] or [v for v in bbox.values() if isinstance(v, (int, float))][:4]
            return []
        
        l1, l2 = _bbox_to_list(box1), _bbox_to_list(box2)
        if len(l1) < 4 or len(l2) < 4:
            return 0.0
        x1_min, y1_min, x1_max, y1_max = min(l1[0], l1[2]), l1[1], max(l1[0], l1[2]), l1[3]
        x2_min, y2_min, x2_max, y2_max = min(l2[0], l2[2]), l2[1], max(l2[0], l2[2]), l2[3]
        inter_x_min, inter_y_min = max(x1_min, x2_min), max(y1_min, y2_min)
        inter_x_max, inter_y_max = min(x1_max, x2_max), min(y1_max, y2_max)
        inter_area = max(0.0, inter_x_max - inter_x_min) * max(0.0, inter_y_max - inter_y_min)
        area1, area2 = (x1_max - x1_min) * (y1_max - y1_min), (x2_max - x2_min) * (y2_max - y2_min)
        return inter_area / (area1 + area2 - inter_area) if (area1 + area2 - inter_area) > 0 else 0.0

    def _merge_or_register_track(self, raw_id: Any, bbox: Any) -> Any:
        if raw_id is None or bbox is None:
            return raw_id
        now = time.time()
        if raw_id in self._track_aliases:
            canonical_id = self._track_aliases[raw_id]
            if canonical_id in self._canonical_tracks:
                self._canonical_tracks[canonical_id]["last_bbox"] = bbox
                self._canonical_tracks[canonical_id]["last_update"] = now
                self._canonical_tracks[canonical_id]["raw_ids"].add(raw_id)
            return canonical_id
        for canonical_id, info in self._canonical_tracks.items():
            if now - info["last_update"] > self._track_merge_time_window:
                continue
            if self._compute_iou(bbox, info["last_bbox"]) >= self._track_merge_iou_threshold:
                self._track_aliases[raw_id] = canonical_id
                info["last_bbox"] = bbox
                info["last_update"] = now
                info["raw_ids"].add(raw_id)
                return canonical_id
        self._track_aliases[raw_id] = raw_id
        self._canonical_tracks[raw_id] = {"last_bbox": bbox, "last_update": now, "raw_ids": {raw_id}}
        return raw_id

    def _get_tracking_start_time(self) -> str:
        return self._format_timestamp(self._tracking_start_time) if self._tracking_start_time is not None else "N/A"

    def _set_tracking_start_time(self) -> None:
        self._tracking_start_time = time.time()