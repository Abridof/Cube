"""
多模态感知层 - 第三阶段核心模块

支持：
- 图像感知（结构分析、特征提取）
- 音频感知（节奏、模式识别）
- 结构化数据感知（表格、JSON、XML）
- 跨模态对齐与融合
- 统一认知表示转换
"""

import base64
import hashlib
import json
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from collections import defaultdict


class ModalityType(Enum):
    """模态类型"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    STRUCTURED_DATA = "structured_data"
    CODE = "code"
    SENSOR = "sensor"


class FeatureType(Enum):
    """特征类型"""

    SPATIAL = "spatial"  # 空间特征
    TEMPORAL = "temporal"  # 时间特征
    SPECTRAL = "spectral"  # 频谱特征
    SEMANTIC = "semantic"  # 语义特征
    STRUCTURAL = "structural"  # 结构特征
    STATISTICAL = "statistical"  # 统计特征


@dataclass
class ModalFeature:
    """模态特征"""

    feature_type: FeatureType
    name: str
    value: Any
    confidence: float
    location: Optional[Dict[str, int]] = None  # 空间/时间位置
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerceivedObject:
    """感知对象"""

    object_id: str
    modality: ModalityType
    category: str
    features: List[ModalFeature]
    confidence: float
    bounding_box: Optional[Dict[str, int]] = None  # 边界框
    temporal_span: Optional[Tuple[int, int]] = None  # 时间跨度
    relations: List[str] = field(default_factory=list)  # 与其他对象的关系
    ucr_embedding: Optional[Dict[str, float]] = None  # UCR 向量表示
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据


class ImagePerceiver:
    """图像感知器

    功能：
    - 结构分析（边缘、角点、区域）
    - 颜色直方图
    - 纹理特征
    - 简单物体检测（基于规则）
    """

    def __init__(self):
        self.feature_extractors = {
            "structure": self._extract_structure,
            "color": self._extract_color,
            "texture": self._extract_texture,
            "edges": self._extract_edges,
        }

    def perceive(
        self, image_data: Union[str, bytes, Dict], metadata: Optional[Dict] = None
    ) -> List[PerceivedObject]:
        """
        感知图像

        Args:
            image_data: 图像数据（base64、字节或字典格式）
            metadata: 元数据（尺寸、格式等）

        Returns:
            感知对象列表
        """
        # 解析图像数据
        if isinstance(image_data, str):
            try:
                # 尝试 base64 解码
                image_bytes = base64.b64decode(image_data)
            except:
                # 可能是文件路径或 URL，这里简化处理
                image_bytes = image_data.encode("utf-8")
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        elif isinstance(image_data, dict):
            # 已经是结构化格式
            return self._perceive_structured_image(image_data, metadata)
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")

        # 提取元数据
        if metadata is None:
            metadata = self._estimate_metadata(image_bytes)

        # 提取特征
        objects = []
        for feature_name, extractor in self.feature_extractors.items():
            features = extractor(image_bytes, metadata)
            for feat in features:
                obj = PerceivedObject(
                    object_id=f"img_{feature_name}_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                    modality=ModalityType.IMAGE,
                    category=feature_name,
                    features=[feat],
                    confidence=feat.confidence,
                    metadata=metadata,
                )
                objects.append(obj)

        # 整合为高级对象
        integrated_objects = self._integrate_image_objects(objects, metadata)

        return integrated_objects

    def _estimate_metadata(self, image_bytes: bytes) -> Dict:
        """估计图像元数据"""
        # 简单的格式检测
        if image_bytes.startswith(b"\x89PNG"):
            fmt = "PNG"
        elif image_bytes.startswith(b"\xff\xd8\xff"):
            fmt = "JPEG"
        elif image_bytes.startswith(b"GIF"):
            fmt = "GIF"
        else:
            fmt = "UNKNOWN"

        # 估计尺寸（简化）
        size = len(image_bytes)

        return {"format": fmt, "size_bytes": size, "estimated": True}

    def _perceive_structured_image(
        self, image_dict: Dict, metadata: Optional[Dict]
    ) -> List[PerceivedObject]:
        """处理结构化图像数据（如已解析的像素矩阵）"""
        objects = []

        # 检查是否包含预定义的结构
        if "width" in image_dict and "height" in image_dict:
            width = image_dict["width"]
            height = image_dict["height"]

            # 创建整体图像对象
            obj = PerceivedObject(
                object_id=f"img_struct_{hashlib.md5(str(image_dict).encode()).hexdigest()[:8]}",
                modality=ModalityType.IMAGE,
                category="scene",
                features=[
                    ModalFeature(
                        feature_type=FeatureType.SPATIAL,
                        name="dimensions",
                        value={"width": width, "height": height},
                        confidence=1.0,
                    )
                ],
                confidence=1.0,
                metadata=metadata or {},
            )
            objects.append(obj)

        # 检查是否包含物体列表
        if "objects" in image_dict:
            for idx, obj_data in enumerate(image_dict["objects"]):
                features = [
                    ModalFeature(
                        feature_type=FeatureType.SEMANTIC,
                        name="category",
                        value=obj_data.get("category", "unknown"),
                        confidence=obj_data.get("confidence", 0.8),
                    )
                ]

                if "bbox" in obj_data:
                    features.append(
                        ModalFeature(
                            feature_type=FeatureType.SPATIAL,
                            name="bounding_box",
                            value=obj_data["bbox"],
                            confidence=0.9,
                        )
                    )

                obj = PerceivedObject(
                    object_id=f"img_obj_{idx}",
                    modality=ModalityType.IMAGE,
                    category=obj_data.get("category", "object"),
                    features=features,
                    confidence=obj_data.get("confidence", 0.8),
                    bounding_box=obj_data.get("bbox"),
                    metadata=metadata or {},
                )
                objects.append(obj)

        return objects

    def _extract_structure(self, image_bytes: bytes, metadata: Dict) -> List[ModalFeature]:
        """提取结构特征（简化版）"""
        features = []

        # 基于字节分布的结构分析
        byte_counts = defaultdict(int)
        for b in image_bytes[:10000]:  # 限制处理长度
            byte_counts[b] += 1

        # 计算熵（复杂度指标）
        total = sum(byte_counts.values())
        entropy = 0.0
        if total > 0:
            for count in byte_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * (p if p == 1 else (p * 0.01))  # 简化熵计算

        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="complexity_entropy",
                value=entropy,
                confidence=0.7,
                metadata={"sample_size": min(10000, len(image_bytes))},
            )
        )

        # 检测重复模式
        pattern_score = self._detect_pattern(image_bytes[:1000])
        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="pattern_regularity",
                value=pattern_score,
                confidence=0.6,
            )
        )

        return features

    def _extract_color(self, image_bytes: bytes, metadata: Dict) -> List[ModalFeature]:
        """提取颜色特征（简化版）"""
        features = []

        # 简化的颜色分析（统计 RGB 分布）
        if len(image_bytes) >= 3:
            # 采样字节作为颜色代理
            r_sum = g_sum = b_sum = 0
            count = 0

            for i in range(0, min(3000, len(image_bytes) - 2), 3):
                r_sum += image_bytes[i]
                g_sum += image_bytes[i + 1]
                b_sum += image_bytes[i + 2]
                count += 1

            if count > 0:
                avg_color = {"r": r_sum / count, "g": g_sum / count, "b": b_sum / count}

                features.append(
                    ModalFeature(
                        feature_type=FeatureType.SPECTRAL,
                        name="dominant_color",
                        value=avg_color,
                        confidence=0.65,
                        metadata={"sample_count": count},
                    )
                )

        return features

    def _extract_texture(self, image_bytes: bytes, metadata: Dict) -> List[ModalFeature]:
        """提取纹理特征（简化版）"""
        features = []

        # 基于局部变化的纹理分析
        if len(image_bytes) > 100:
            variations = []
            for i in range(0, min(500, len(image_bytes) - 10), 10):
                chunk = image_bytes[i : i + 10]
                if len(chunk) >= 2:
                    var = max(chunk) - min(chunk)
                    variations.append(var)

            if variations:
                avg_variation = sum(variations) / len(variations)
                texture_type = (
                    "smooth"
                    if avg_variation < 50
                    else "rough" if avg_variation > 150 else "moderate"
                )

                features.append(
                    ModalFeature(
                        feature_type=FeatureType.SPATIAL,
                        name="texture_type",
                        value=texture_type,
                        confidence=0.55,
                        metadata={"avg_variation": avg_variation},
                    )
                )

        return features

    def _extract_edges(self, image_bytes: bytes, metadata: Dict) -> List[ModalFeature]:
        """提取边缘特征（简化版）"""
        features = []

        # 基于梯度变化的边缘检测
        if len(image_bytes) > 100:
            edge_strength = 0
            edge_count = 0

            for i in range(0, min(500, len(image_bytes) - 1), 2):
                diff = abs(image_bytes[i + 1] - image_bytes[i])
                if diff > 50:
                    edge_strength += diff
                    edge_count += 1

            if edge_count > 0:
                features.append(
                    ModalFeature(
                        feature_type=FeatureType.SPATIAL,
                        name="edge_density",
                        value=edge_count / 250.0,  # 归一化
                        confidence=0.6,
                        metadata={"edge_strength": edge_strength},
                    )
                )

        return features

    def _detect_pattern(self, data: bytes) -> float:
        """检测重复模式（返回 0-1 的规则性分数）"""
        if len(data) < 10:
            return 0.0

        # 检测周期性
        pattern_scores = []
        for period in range(2, min(50, len(data) // 2)):
            matches = 0
            comparisons = 0
            for i in range(0, len(data) - period, period):
                if data[i] == data[i + period]:
                    matches += 1
                comparisons += 1

            if comparisons > 0:
                pattern_scores.append(matches / comparisons)

        return max(pattern_scores) if pattern_scores else 0.0

    def _integrate_image_objects(
        self, objects: List[PerceivedObject], metadata: Dict
    ) -> List[PerceivedObject]:
        """整合低级特征为高级对象"""
        if not objects:
            return []

        # 创建一个综合场景对象
        all_confidences = [obj.confidence for obj in objects]
        avg_confidence = sum(all_confidences) / len(all_confidences)

        scene_features = []
        for obj in objects:
            scene_features.extend(obj.features)

        scene = PerceivedObject(
            object_id=f"img_scene_{hashlib.md5(str(metadata).encode()).hexdigest()[:8]}",
            modality=ModalityType.IMAGE,
            category="integrated_scene",
            features=scene_features,
            confidence=avg_confidence,
            metadata=metadata,
            relations=[obj.object_id for obj in objects],
        )

        return [scene] + objects  # 保留低级对象


class AudioPerceiver:
    """音频感知器

    功能：
    - 时域分析（振幅、过零率）
    - 频域分析（简化 FFT 模拟）
    - 节奏检测
    - 音色特征
    """

    def __init__(self):
        self.window_size = 1024
        self.sample_rate = 44100  # 默认采样率

    def perceive(
        self, audio_data: Union[str, bytes, List[float]], metadata: Optional[Dict] = None
    ) -> List[PerceivedObject]:
        """
        感知音频

        Args:
            audio_data: 音频数据（base64、字节或浮点样本列表）
            metadata: 元数据（采样率、位深度等）

        Returns:
            感知对象列表
        """
        # 解析音频数据
        if isinstance(audio_data, str):
            try:
                audio_bytes = base64.b64decode(audio_data)
            except:
                audio_bytes = audio_data.encode("utf-8")

            # 转换为样本（假设为 16-bit PCM）
            samples = self._bytes_to_samples(audio_bytes)
        elif isinstance(audio_data, bytes):
            samples = self._bytes_to_samples(audio_data)
        elif isinstance(audio_data, list):
            samples = audio_data
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")

        # 更新元数据
        if metadata is None:
            metadata = {}
        metadata["sample_count"] = len(samples)
        metadata["sample_rate"] = metadata.get("sample_rate", self.sample_rate)

        # 提取特征
        objects = []

        # 时域特征
        temporal_features = self._extract_temporal_features(samples, metadata)
        for feat in temporal_features:
            obj = PerceivedObject(
                object_id=f"aud_temporal_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                modality=ModalityType.AUDIO,
                category="temporal_pattern",
                features=[feat],
                confidence=feat.confidence,
                metadata=metadata,
            )
            objects.append(obj)

        # 频域特征（简化）
        spectral_features = self._extract_spectral_features(samples, metadata)
        for feat in spectral_features:
            obj = PerceivedObject(
                object_id=f"aud_spectral_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                modality=ModalityType.AUDIO,
                category="spectral_pattern",
                features=[feat],
                confidence=feat.confidence,
                metadata=metadata,
            )
            objects.append(obj)

        # 节奏特征
        rhythm_features = self._extract_rhythm_features(samples, metadata)
        for feat in rhythm_features:
            obj = PerceivedObject(
                object_id=f"aud_rhythm_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                modality=ModalityType.AUDIO,
                category="rhythm_pattern",
                features=[feat],
                confidence=feat.confidence,
                temporal_span=(0, len(samples)),
                metadata=metadata,
            )
            objects.append(obj)

        return objects

    def _bytes_to_samples(self, audio_bytes: bytes) -> List[float]:
        """将字节转换为浮点样本"""
        samples = []

        # 假设为 16-bit 小端 PCM
        if len(audio_bytes) >= 2:
            for i in range(0, min(len(audio_bytes) - 1, 44100), 2):
                sample = struct.unpack("<h", audio_bytes[i : i + 2])[0]
                samples.append(sample / 32768.0)  # 归一化到 [-1, 1]

        return samples

    def _extract_temporal_features(
        self, samples: List[float], metadata: Dict
    ) -> List[ModalFeature]:
        """提取时域特征"""
        features = []

        if not samples:
            return features

        # RMS 能量
        rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
        features.append(
            ModalFeature(
                feature_type=FeatureType.TEMPORAL, name="rms_energy", value=rms, confidence=0.95
            )
        )

        # 过零率
        zero_crossings = 0
        for i in range(1, len(samples)):
            if (samples[i - 1] >= 0) != (samples[i] >= 0):
                zero_crossings += 1

        zcr = zero_crossings / len(samples) if samples else 0
        features.append(
            ModalFeature(
                feature_type=FeatureType.TEMPORAL,
                name="zero_crossing_rate",
                value=zcr,
                confidence=0.9,
            )
        )

        # 动态范围
        if samples:
            dynamic_range = max(samples) - min(samples)
            features.append(
                ModalFeature(
                    feature_type=FeatureType.STATISTICAL,
                    name="dynamic_range",
                    value=dynamic_range,
                    confidence=0.95,
                )
            )

        return features

    def _extract_spectral_features(
        self, samples: List[float], metadata: Dict
    ) -> List[ModalFeature]:
        """提取频域特征（简化 DCT 近似）"""
        features = []

        if len(samples) < 100:
            return features

        # 简化的频谱分析（使用差分近似高频成分）
        high_freq_energy = 0
        low_freq_energy = 0

        for i in range(1, min(1000, len(samples))):
            diff = abs(samples[i] - samples[i - 1])
            high_freq_energy += diff**2

        low_freq_energy = sum(s**2 for s in samples[: min(500, len(samples))])

        if low_freq_energy > 0:
            spectral_ratio = high_freq_energy / low_freq_energy
            features.append(
                ModalFeature(
                    feature_type=FeatureType.SPECTRAL,
                    name="spectral_balance",
                    value=spectral_ratio,
                    confidence=0.7,
                )
            )

        # 估计主频（简化）
        # 通过自相关估计周期
        if len(samples) > 200:
            best_period = self._estimate_period(samples[:500])
            if best_period > 0:
                sample_rate = metadata.get("sample_rate", 44100)
                estimated_freq = sample_rate / best_period
                features.append(
                    ModalFeature(
                        feature_type=FeatureType.SPECTRAL,
                        name="estimated_dominant_frequency",
                        value=estimated_freq,
                        confidence=0.5,
                    )
                )

        return features

    def _estimate_period(self, samples: List[float]) -> int:
        """通过自相关估计周期"""
        n = len(samples)
        if n < 50:
            return 0

        best_period = 0
        best_correlation = 0

        for period in range(10, min(200, n // 2)):
            correlation = 0
            count = 0
            for i in range(n - period):
                correlation += samples[i] * samples[i + period]
                count += 1

            if count > 0:
                correlation /= count
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_period = period

        return best_period

    def _extract_rhythm_features(self, samples: List[float], metadata: Dict) -> List[ModalFeature]:
        """提取节奏特征"""
        features = []

        if len(samples) < 1000:
            return features

        # 计算包络
        window_size = 512
        envelope = []

        for i in range(0, len(samples) - window_size, window_size):
            window = samples[i : i + window_size]
            energy = sum(s**2 for s in window) / len(window)
            envelope.append(energy)

        if len(envelope) > 2:
            # 检测包络变化（节拍）
            beats = 0
            threshold = sum(envelope) / len(envelope) * 1.5

            for i in range(1, len(envelope)):
                if envelope[i] > threshold and envelope[i - 1] <= threshold:
                    beats += 1

            # 估计 BPM
            sample_rate = metadata.get("sample_rate", 44100)
            duration = len(samples) / sample_rate
            bpm = (beats / duration) * 60 if duration > 0 else 0

            features.append(
                ModalFeature(
                    feature_type=FeatureType.TEMPORAL,
                    name="estimated_bpm",
                    value=bpm,
                    confidence=0.6,
                    metadata={"beat_count": beats, "duration": duration},
                )
            )

        return features


class StructuredDataPerceiver:
    """结构化数据感知器

    支持：
    - JSON/XML 解析
    - 表格数据分析
    - 层级结构提取
    - 统计特征计算
    """

    def perceive(
        self, data: Union[str, Dict, List], format_type: Optional[str] = None
    ) -> List[PerceivedObject]:
        """
        感知结构化数据

        Args:
            data: 数据（字符串、字典或列表）
            format_type: 格式类型（json, xml, csv, table）

        Returns:
            感知对象列表
        """
        objects = []

        # 解析数据
        if isinstance(data, str):
            if (
                format_type == "json"
                or data.strip().startswith("{")
                or data.strip().startswith("[")
            ):
                parsed_data = json.loads(data)
            else:
                # 尝试自动检测
                try:
                    parsed_data = json.loads(data)
                except:
                    parsed_data = {"raw": data}
        else:
            parsed_data = data

        # 分析结构
        structure_features = self._analyze_structure(parsed_data)
        for feat in structure_features:
            obj = PerceivedObject(
                object_id=f"struct_{feat.name}_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                modality=ModalityType.STRUCTURED_DATA,
                category="structure",
                features=[feat],
                confidence=0.9,
            )
            objects.append(obj)

        # 提取统计特征
        if isinstance(parsed_data, list):
            stats_features = self._analyze_list_statistics(parsed_data)
            for feat in stats_features:
                obj = PerceivedObject(
                    object_id=f"struct_stats_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                    modality=ModalityType.STRUCTURED_DATA,
                    category="statistics",
                    features=[feat],
                    confidence=0.85,
                )
                objects.append(obj)

        elif isinstance(parsed_data, dict):
            dict_features = self._analyze_dict_structure(parsed_data)
            for feat in dict_features:
                obj = PerceivedObject(
                    object_id=f"struct_dict_{hashlib.md5(str(feat.value).encode()).hexdigest()[:8]}",
                    modality=ModalityType.STRUCTURED_DATA,
                    category="dictionary",
                    features=[feat],
                    confidence=0.85,
                )
                objects.append(obj)

        return objects

    def _analyze_structure(self, data: Any) -> List[ModalFeature]:
        """分析数据结构"""
        features = []

        # 类型信息
        data_type = type(data).__name__
        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="data_type",
                value=data_type,
                confidence=1.0,
            )
        )

        # 嵌套深度
        max_depth = self._calculate_depth(data)
        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="nesting_depth",
                value=max_depth,
                confidence=1.0,
            )
        )

        # 元素数量
        element_count = self._count_elements(data)
        features.append(
            ModalFeature(
                feature_type=FeatureType.STATISTICAL,
                name="element_count",
                value=element_count,
                confidence=1.0,
            )
        )

        return features

    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """计算嵌套深度"""
        if isinstance(data, dict):
            if not data:
                return current_depth + 1
            return max(self._calculate_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth + 1
            return max(self._calculate_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth

    def _count_elements(self, data: Any) -> int:
        """递归计算元素总数"""
        if isinstance(data, dict):
            return len(data) + sum(self._count_elements(v) for v in data.values())
        elif isinstance(data, list):
            return len(data) + sum(self._count_elements(item) for item in data)
        else:
            return 1

    def _analyze_list_statistics(self, data: List) -> List[ModalFeature]:
        """分析列表统计特征"""
        features = []

        if not data:
            return features

        # 同质性检查
        types = set(type(item).__name__ for item in data)
        homogeneity = 1.0 if len(types) == 1 else len(types) / len(data)

        features.append(
            ModalFeature(
                feature_type=FeatureType.STATISTICAL,
                name="homogeneity",
                value=homogeneity,
                confidence=0.95,
                metadata={"unique_types": list(types)},
            )
        )

        # 数值统计（如果适用）
        numeric_items = [x for x in data if isinstance(x, (int, float))]
        if numeric_items and len(numeric_items) > len(data) * 0.5:
            mean_val = sum(numeric_items) / len(numeric_items)
            min_val = min(numeric_items)
            max_val = max(numeric_items)

            features.append(
                ModalFeature(
                    feature_type=FeatureType.STATISTICAL,
                    name="numeric_summary",
                    value={"mean": mean_val, "min": min_val, "max": max_val},
                    confidence=0.9,
                )
            )

        return features

    def _analyze_dict_structure(self, data: Dict) -> List[ModalFeature]:
        """分析字典结构"""
        features = []

        if not data:
            return features

        # 键分析
        keys = list(data.keys())
        key_types = set(type(k).__name__ for k in keys)

        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="key_types",
                value=list(key_types),
                confidence=1.0,
            )
        )

        # 值类型分布
        value_types = defaultdict(int)
        for v in data.values():
            value_types[type(v).__name__] += 1

        features.append(
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="value_type_distribution",
                value=dict(value_types),
                confidence=1.0,
            )
        )

        return features


class MultimodalFusionEngine:
    """多模态融合引擎

    功能：
    - 跨模态对齐
    - 特征融合
    - 冲突解决
    - 统一 UCR 表示生成
    """

    def __init__(self):
        self.image_perceiver = ImagePerceiver()
        self.audio_perceiver = AudioPerceiver()
        self.struct_perceiver = StructuredDataPerceiver()
        self.modality_weights = {
            ModalityType.TEXT: 1.0,
            ModalityType.IMAGE: 1.2,
            ModalityType.AUDIO: 1.0,
            ModalityType.VIDEO: 1.5,
            ModalityType.STRUCTURED_DATA: 1.1,
            ModalityType.CODE: 1.0,
            ModalityType.SENSOR: 0.9,
        }

    def perceive(
        self, data: Any, modality: ModalityType, metadata: Optional[Dict] = None
    ) -> List[PerceivedObject]:
        """根据模态类型分发到相应的感知器"""
        if modality == ModalityType.IMAGE:
            return self.image_perceiver.perceive(data, metadata)
        elif modality == ModalityType.AUDIO:
            return self.audio_perceiver.perceive(data, metadata)
        elif modality == ModalityType.STRUCTURED_DATA:
            return self.struct_perceiver.perceive(
                data, metadata.get("format") if metadata else None
            )
        elif modality == ModalityType.TEXT:
            # 文本处理在 UCR 层中完成
            return self._perceive_text(data, metadata)
        else:
            raise NotImplementedError(f"Perceiver for {modality} not implemented")

    def _perceive_text(self, text: str, metadata: Optional[Dict]) -> List[PerceivedObject]:
        """文本感知（简化版，完整功能在 UCR 层）"""
        features = [
            ModalFeature(
                feature_type=FeatureType.SEMANTIC, name="length", value=len(text), confidence=1.0
            ),
            ModalFeature(
                feature_type=FeatureType.STRUCTURAL,
                name="word_count",
                value=len(text.split()),
                confidence=1.0,
            ),
        ]

        obj = PerceivedObject(
            object_id=f"text_{hashlib.md5(text.encode()).hexdigest()[:8]}",
            modality=ModalityType.TEXT,
            category="text_segment",
            features=features,
            confidence=1.0,
            metadata=metadata or {},
        )

        return [obj]

    def fuse(
        self, objects: List[PerceivedObject], alignment_strategy: str = "semantic"
    ) -> Dict[str, Any]:
        """
        融合多个感知对象

        Args:
            objects: 感知对象列表
            alignment_strategy: 对齐策略（semantic, temporal, spatial）

        Returns:
            融合结果
        """
        if not objects:
            return {"fused_features": [], "confidence": 0.0}

        # 按模态分组
        by_modality = defaultdict(list)
        for obj in objects:
            by_modality[obj.modality].append(obj)

        # 加权融合
        fused_features = []
        total_weight = 0
        weighted_confidence = 0

        for modality, mod_objects in by_modality.items():
            weight = self.modality_weights.get(modality, 1.0)
            total_weight += weight

            for obj in mod_objects:
                for feature in obj.features:
                    fused_features.append(
                        {
                            "modality": modality.value,
                            "feature": feature.name,
                            "type": feature.feature_type.value,
                            "value": feature.value,
                            "confidence": feature.confidence * weight,
                        }
                    )

                weighted_confidence += obj.confidence * weight

        # 计算总体置信度
        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0

        # 生成 UCR 嵌入（简化）
        ucr_embedding = self._generate_ucr_embedding(fused_features)

        return {
            "fused_features": fused_features,
            "confidence": avg_confidence,
            "modality_count": len(by_modality),
            "object_count": len(objects),
            "ucr_embedding": ucr_embedding,
            "alignment_strategy": alignment_strategy,
        }

    def _generate_ucr_embedding(self, features: List[Dict]) -> Dict[str, float]:
        """生成简化的 UCR 向量表示"""
        embedding = {}

        # 基于特征类型和值创建向量维度
        for idx, feat in enumerate(features[:20]):  # 限制维度
            key = f"{feat['type']}_{feat['feature']}"
            # 将值映射到 [-1, 1] 范围
            value = feat["value"]
            if isinstance(value, (int, float)):
                normalized = max(-1, min(1, value / 100))  # 简单归一化
            elif isinstance(value, dict):
                normalized = len(value) / 10
            else:
                normalized = hash(str(value)) % 100 / 100 - 0.5

            embedding[key] = normalized * feat["confidence"]

        return embedding

    def cross_modal_align(self, source: PerceivedObject, target: PerceivedObject) -> Dict[str, Any]:
        """
        跨模态对齐两个对象

        Returns:
            对齐结果（相似度、对应关系等）
        """
        # 基于特征名称和类型的相似度
        source_features = {(f.feature_type.value, f.name): f.value for f in source.features}
        target_features = {(f.feature_type.value, f.name): f.value for f in target.features}

        common_keys = set(source_features.keys()) & set(target_features.values())

        similarity_scores = []
        for key in common_keys:
            src_val = source_features[key]
            tgt_val = target_features[key]

            if isinstance(src_val, (int, float)) and isinstance(tgt_val, (int, float)):
                # 数值相似度
                diff = abs(src_val - tgt_val)
                sim = 1 / (1 + diff)
            else:
                # 类别相似度
                sim = 1.0 if src_val == tgt_val else 0.0

            similarity_scores.append(sim)

        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0

        return {
            "source_modality": source.modality.value,
            "target_modality": target.modality.value,
            "similarity": avg_similarity,
            "common_features": list(common_keys),
            "aligned": avg_similarity > 0.7,
        }


# 便捷函数
def create_multimodal_engine() -> MultimodalFusionEngine:
    """创建多模态融合引擎实例"""
    return MultimodalFusionEngine()


if __name__ == "__main__":
    print("=== 多模态感知层自测试 ===\n")

    engine = create_multimodal_engine()

    # 测试图像感知
    print("1. 测试图像感知...")
    fake_image = bytes([i % 256 for i in range(1000)])
    img_objects = engine.perceive(fake_image, ModalityType.IMAGE)
    print(f"   检测到 {len(img_objects)} 个图像对象")
    for obj in img_objects[:2]:
        print(f"   - {obj.category}: {len(obj.features)} 个特征")

    # 测试音频感知
    print("\n2. 测试音频感知...")
    fake_audio = [0.5 * (i % 100) / 100 for i in range(2000)]
    aud_objects = engine.perceive(fake_audio, ModalityType.AUDIO, {"sample_rate": 44100})
    print(f"   检测到 {len(aud_objects)} 个音频对象")
    for obj in aud_objects[:2]:
        print(f"   - {obj.category}: {len(obj.features)} 个特征")

    # 测试结构化数据感知
    print("\n3. 测试结构化数据感知...")
    test_data = {"users": [{"name": "Alice"}, {"name": "Bob"}], "count": 2}
    struct_objects = engine.perceive(test_data, ModalityType.STRUCTURED_DATA)
    print(f"   检测到 {len(struct_objects)} 个结构化对象")

    # 测试多模态融合
    print("\n4. 测试多模态融合...")
    all_objects = img_objects + aud_objects + struct_objects
    fusion_result = engine.fuse(all_objects)
    print(f"   融合特征数：{len(fusion_result['fused_features'])}")
    print(f"   总体置信度：{fusion_result['confidence']:.3f}")
    print(f"   模态种类：{fusion_result['modality_count']}")

    # 测试跨模态对齐
    print("\n5. 测试跨模态对齐...")
    if len(img_objects) > 0 and len(aud_objects) > 0:
        alignment = engine.cross_modal_align(img_objects[0], aud_objects[0])
        print(f"   相似度：{alignment['similarity']:.3f}")
        print(f"   是否对齐：{alignment['aligned']}")

    print("\n✅ 多模态感知层测试完成！")


# ============================================================================
# 导出别名（用于兼容其他模块的导入）
# ============================================================================

# Modality 是 ModalityType 的别名，用于保持接口一致性
Modality = ModalityType
