"""
多模态感知与通感融合系统 (Multimodal Perception & Synesthesia Fusion)

实现 AGI 突破纯文本限制，具备跨模态联想（通感）能力。
像人类一样：听到颜色、看到旋律、感受文字温度。

核心能力:
1. 视觉语义编码 (Visual Semantics Encoding)
2. 听觉情感映射 (Auditory Emotion Mapping)
3. 通感融合层 (Synesthetic Fusion Layer)
4. 触觉质感模拟 (Haptic Texture Simulation)

理论基础:
- 联觉神经科学 (Synesthesia Neuroscience)
- 跨模态注意力机制 (Cross-Modal Attention)
- 具身认知理论 (Embodied Cognition)
- 格式塔心理学 (Gestalt Psychology)
"""

import math
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re


class ModalityType(Enum):
    """感知模态类型"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    HAPTIC = "haptic"
    OLFACTORY = "olfactory"
    GUSTATORY = "gustatory"
    TEXTUAL = "textual"


class SynesthesiaType(Enum):
    """通感类型"""
    COLOR_HEARING = "color_hearing"  # 听音见色
    SOUND_SEEING = "sound_seeing"    # 见形听声
    TEXTURE_SOUND = "texture_sound"  # 触质发声
    EMOTION_COLOR = "emotion_color"  # 情感着色
    CONCEPT_TEMPERATURE = "concept_temperature"  # 概念温度


@dataclass
class VisualFeatures:
    """视觉特征向量"""
    dominant_color: Tuple[int, int, int] = (128, 128, 128)
    brightness: float = 0.5  # 0-1
    saturation: float = 0.5  # 0-1
    temperature: float = 0.5  # 冷-暖 0-1
    complexity: float = 0.5  # 简单-复杂 0-1
    harmony: float = 0.5  # 和谐度 0-1
    motion_vector: Optional[Tuple[float, float]] = None
    depth_perception: float = 0.5  # 深度感知 0-1


@dataclass
class AuditoryFeatures:
    """听觉特征向量"""
    pitch: float = 0.5  # 音调 0-1 (低-高)
    loudness: float = 0.5  # 响度 0-1
    timbre_complexity: float = 0.5  # 音色复杂度 0-1
    rhythm_regularity: float = 0.5  # 节奏规律性 0-1
    tempo: float = 0.5  # 速度 0-1 (慢-快)
    harmonic_content: float = 0.5  # 和声内容 0-1
    spatial_location: Tuple[float, float] = (0.5, 0.5)  # 空间位置 (方位，距离)
    emotional_tone: str = "neutral"


@dataclass
class HapticFeatures:
    """触觉特征向量"""
    temperature: float = 0.5  # 冷-暖 0-1
    texture_roughness: float = 0.5  # 粗糙度 0-1 (光滑-粗糙)
    hardness: float = 0.5  # 硬度 0-1 (软-硬)
    weight: float = 0.5  # 重量感 0-1 (轻-重)
    moisture: float = 0.5  # 湿度 0-1 (干-湿)
    vibration: float = 0.0  # 振动强度 0-1
    pressure: float = 0.0  # 压力 0-1


@dataclass
class SynestheticExperience:
    """通感体验数据结构"""
    input_modality: ModalityType
    input_description: str
    visual: Optional[VisualFeatures] = None
    auditory: Optional[AuditoryFeatures] = None
    haptic: Optional[HapticFeatures] = None
    emotional_resonance: float = 0.0  # 情感共鸣强度 -1到1
    synesthesia_type: Optional[SynesthesiaType] = None
    cross_modal_associations: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ColorPalette:
    """颜色心理学映射"""
    
    # 基础颜色情感关联
    EMOTION_COLORS = {
        "joy": (255, 215, 0),      # 金色
        "sadness": (70, 130, 180), # 钢蓝
        "anger": (220, 20, 60),    # 深红
        "fear": (75, 0, 130),      # 靛蓝
        "surprise": (255, 165, 0), # 橙色
        "disgust": (85, 107, 47),  # 橄榄绿
        "trust": (34, 139, 34),    # 森林绿
        "anticipation": (218, 112, 214), # 兰花紫
        "calm": (176, 224, 230),   # 粉蓝
        "energy": (255, 69, 0),    # 橙红
        "mystery": (148, 0, 211),  # 深紫
        "warmth": (255, 160, 122), # 浅鲑肉色
        "cold": (176, 196, 222),   # 淡蓝灰
    }
    
    # 音高到颜色映射 (基于联觉研究)
    PITCH_COLORS = {
        0.0: (139, 69, 19),    # 低音 - 深棕
        0.2: (178, 34, 34),    # 中低 - 火砖红
        0.4: (255, 215, 0),    # 中 - 金色
        0.6: (50, 205, 50),    # 中高 - 石灰绿
        0.8: (0, 191, 255),    # 高音 - 深天蓝
        1.0: (230, 230, 250),  # 极高 - 淡紫
    }
    
    @classmethod
    def emotion_to_rgb(cls, emotion: str) -> Tuple[int, int, int]:
        """将情感转换为 RGB 颜色"""
        emotion_lower = emotion.lower()
        if emotion_lower in cls.EMOTION_COLORS:
            return cls.EMOTION_COLORS[emotion_lower]
        # 默认返回灰色
        return (128, 128, 128)
    
    @classmethod
    def pitch_to_rgb(cls, pitch: float) -> Tuple[int, int, int]:
        """将音高转换为 RGB 颜色"""
        pitch = max(0.0, min(1.0, pitch))
        
        # 找到最近的两个关键点
        pitches = sorted(cls.PITCH_COLORS.keys())
        lower_pitch = max([p for p in pitches if p <= pitch], default=0.0)
        upper_pitch = min([p for p in pitches if p >= pitch], default=1.0)
        
        if lower_pitch == upper_pitch:
            return cls.PITCH_COLORS[lower_pitch]
        
        # 线性插值
        ratio = (pitch - lower_pitch) / (upper_pitch - lower_pitch)
        lower_color = cls.PITCH_COLORS[lower_pitch]
        upper_color = cls.PITCH_COLORS[upper_pitch]
        
        r = int(lower_color[0] + (upper_color[0] - lower_color[0]) * ratio)
        g = int(lower_color[1] + (upper_color[1] - lower_color[1]) * ratio)
        b = int(lower_color[2] + (upper_color[2] - lower_color[2]) * ratio)
        
        return (r, g, b)
    
    @classmethod
    def rgb_to_temperature(cls, rgb: Tuple[int, int, int]) -> float:
        """从 RGB 估算色温 (0=冷，1=暖)"""
        r, g, b = rgb
        # 简化算法：红色分量高=暖，蓝色分量高=冷
        warmth = (r - b) / 255.0
        return max(0.0, min(1.0, 0.5 + warmth * 0.5))


class VisualSemanticsEncoder:
    """
    视觉语义编码器
    将图像描述或视觉概念映射到情感和概念空间
    """
    
    # 视觉元素情感关联词典
    VISUAL_EMOTION_MAP = {
        "sunset": {"emotion": "melancholy", "temperature": 0.8, "brightness": 0.6},
        "sunrise": {"emotion": "hope", "temperature": 0.7, "brightness": 0.7},
        "storm": {"emotion": "turbulence", "temperature": 0.3, "brightness": 0.3},
        "ocean": {"emotion": "calm", "temperature": 0.4, "brightness": 0.5},
        "mountain": {"emotion": "stability", "temperature": 0.3, "brightness": 0.5},
        "fire": {"emotion": "passion", "temperature": 0.95, "brightness": 0.8},
        "ice": {"emotion": "detachment", "temperature": 0.05, "brightness": 0.7},
        "forest": {"emotion": "growth", "temperature": 0.5, "brightness": 0.4},
        "desert": {"emotion": "isolation", "temperature": 0.85, "brightness": 0.9},
        "night": {"emotion": "mystery", "temperature": 0.2, "brightness": 0.1},
        "day": {"emotion": "clarity", "temperature": 0.6, "brightness": 0.9},
        "rain": {"emotion": "sadness", "temperature": 0.3, "brightness": 0.4},
        "snow": {"emotion": "purity", "temperature": 0.1, "brightness": 0.95},
    }
    
    # 颜色情感映射
    COLOR_EMOTIONS = {
        "red": {"emotion": "passion", "arousal": 0.8},
        "blue": {"emotion": "calm", "arousal": 0.3},
        "green": {"emotion": "balance", "arousal": 0.4},
        "yellow": {"emotion": "joy", "arousal": 0.7},
        "purple": {"emotion": "mystery", "arousal": 0.5},
        "orange": {"emotion": "energy", "arousal": 0.75},
        "black": {"emotion": "sophistication", "arousal": 0.2},
        "white": {"emotion": "purity", "arousal": 0.3},
    }
    
    def encode_visual_description(self, description: str) -> VisualFeatures:
        """
        编码视觉描述为特征向量
        
        Args:
            description: 视觉场景的文字描述
            
        Returns:
            VisualFeatures: 视觉特征向量
        """
        desc_lower = description.lower()
        
        # 初始化特征
        features = VisualFeatures()
        
        # 检测关键视觉元素
        detected_elements = []
        for element, props in self.VISUAL_EMOTION_MAP.items():
            if element in desc_lower:
                detected_elements.append((element, props))
        
        if detected_elements:
            # 综合多个元素的特征
            avg_temp = sum(props["temperature"] for _, props in detected_elements) / len(detected_elements)
            avg_brightness = sum(props["brightness"] for _, props in detected_elements) / len(detected_elements)
            
            features.temperature = avg_temp
            features.brightness = avg_brightness
            
            # 设置主色调
            if any("sunset" in elem or "fire" in elem for elem, _ in detected_elements):
                features.dominant_color = (255, 140, 0)  # 橙红
            elif any("ocean" in elem or "sky" in elem for elem, _ in detected_elements):
                features.dominant_color = (70, 130, 180)  # 钢蓝
            elif any("forest" in elem or "grass" in elem for elem, _ in detected_elements):
                features.dominant_color = (34, 139, 34)  # 森林绿
            elif any("snow" in elem or "ice" in elem for elem, _ in detected_elements):
                features.dominant_color = (240, 248, 255)  # 爱丽丝蓝
            elif any("night" in elem or "dark" in elem for elem, _ in detected_elements):
                features.dominant_color = (25, 25, 112)  # 午夜蓝
            else:
                features.dominant_color = (128, 128, 128)  # 灰色
        
        # 检测颜色词
        for color, props in self.COLOR_EMOTIONS.items():
            if color in desc_lower:
                features.dominant_color = ColorPalette.emotion_to_rgb(props["emotion"])
                break
        
        # 特殊处理"red"等直接颜色词
        if "red" in desc_lower:
            features.dominant_color = (255, 0, 0)
        elif "blue" in desc_lower:
            features.dominant_color = (0, 0, 255)
        elif "green" in desc_lower:
            features.dominant_color = (0, 255, 0)
        elif "yellow" in desc_lower:
            features.dominant_color = (255, 255, 0)
        elif "orange" in desc_lower:
            features.dominant_color = (255, 165, 0)
        elif "purple" in desc_lower or "violet" in desc_lower:
            features.dominant_color = (128, 0, 128)
        elif "white" in desc_lower:
            features.dominant_color = (255, 255, 255)
        elif "black" in desc_lower:
            features.dominant_color = (0, 0, 0)
        
        # 计算复杂度 (基于描述长度和词汇多样性)
        word_count = len(description.split())
        unique_words = len(set(description.lower().split()))
        features.complexity = min(1.0, (word_count / 20) * 0.5 + (unique_words / word_count if word_count > 0 else 0) * 0.5)
        
        # 估算和谐度 (基于情感一致性)
        if len(detected_elements) > 1:
            emotions = [props["emotion"] for _, props in detected_elements]
            # 简化：如果情感相似则和谐度高
            features.harmony = 0.8 if len(set(emotions)) == 1 else 0.5
        else:
            features.harmony = 0.7
        
        return features
    
    def extract_emotional_resonance(self, features: VisualFeatures, description: str) -> float:
        """
        提取视觉场景的情感共鸣强度
        
        Args:
            features: 视觉特征
            description: 原始描述
            
        Returns:
            float: 情感共鸣强度 (-1 到 1)
        """
        resonance = 0.0
        
        # 基于温度的情感倾向
        if features.temperature > 0.7:
            resonance += 0.3  # 温暖场景通常更积极
        elif features.temperature < 0.3:
            resonance -= 0.2  # 寒冷场景可能更消极
        
        # 基于亮度的情感倾向
        if features.brightness > 0.7:
            resonance += 0.2
        elif features.brightness < 0.3:
            resonance -= 0.3
        
        # 基于和谐度
        resonance += (features.harmony - 0.5) * 0.4
        
        # 关键词增强
        positive_words = ["beautiful", "lovely", "wonderful", "amazing", "gorgeous"]
        negative_words = ["terrible", "ugly", "horrible", "dark", "scary"]
        
        desc_lower = description.lower()
        for word in positive_words:
            if word in desc_lower:
                resonance += 0.1
        for word in negative_words:
            if word in desc_lower:
                resonance -= 0.1
        
        return max(-1.0, min(1.0, resonance))


class AuditoryEmotionMapper:
    """
    听觉情感映射器
    解析声音特征并转化为情绪向量和跨模态关联
    """
    
    # 乐器情感特征
    INSTRUMENT_PROFILES = {
        "violin": {"pitch_range": (0.4, 0.9), "emotion": "passionate", "color_temp": 0.6},
        "cello": {"pitch_range": (0.1, 0.5), "emotion": "melancholic", "color_temp": 0.3},
        "piano": {"pitch_range": (0.1, 0.9), "emotion": "versatile", "color_temp": 0.5},
        "flute": {"pitch_range": (0.5, 0.95), "emotion": "ethereal", "color_temp": 0.4},
        "trumpet": {"pitch_range": (0.3, 0.8), "emotion": "triumphant", "color_temp": 0.7},
        "drum": {"pitch_range": (0.0, 0.3), "emotion": "primal", "color_temp": 0.6},
        "guitar": {"pitch_range": (0.2, 0.7), "emotion": "intimate", "color_temp": 0.55},
    }
    
    # 调式情感映射
    MODE_EMOTIONS = {
        "major": {"emotion": "happy", "brightness": 0.7, "color_shift": (20, 20, 0)},
        "minor": {"emotion": "sad", "brightness": 0.4, "color_shift": (-20, 0, 20)},
        "dorian": {"emotion": "mysterious", "brightness": 0.5, "color_shift": (0, 10, 20)},
        "phrygian": {"emotion": "exotic", "brightness": 0.45, "color_shift": (-10, -10, 10)},
    }
    
    def parse_audio_description(self, description: str) -> AuditoryFeatures:
        """
        解析音频描述为特征向量
        
        Args:
            description: 声音的文字描述
            
        Returns:
            AuditoryFeatures: 听觉特征向量
        """
        desc_lower = description.lower()
        features = AuditoryFeatures()
        
        # 检测乐器
        for instrument, profile in self.INSTRUMENT_PROFILES.items():
            if instrument in desc_lower:
                pitch_min, pitch_max = profile["pitch_range"]
                features.pitch = (pitch_min + pitch_max) / 2
                features.emotional_tone = profile["emotion"]
                break
        
        # 检测调式
        for mode, props in self.MODE_EMOTIONS.items():
            if mode in desc_lower:
                features.emotional_tone = props["emotion"]
                features.loudness = props["brightness"]
                break
        
        # 特殊处理"sad"和"minor"关键词
        if "sad" in desc_lower or ("minor" in desc_lower and features.emotional_tone == "neutral"):
            features.emotional_tone = "melancholic"
            features.pitch = 0.3
            features.loudness = 0.4
        elif "happy" in desc_lower or ("major" in desc_lower and features.emotional_tone == "neutral"):
            features.emotional_tone = "happy"
            features.pitch = 0.6
            features.loudness = 0.7
        
        # 检测音高描述
        if any(word in desc_lower for word in ["high", "treble", "soprano"]):
            features.pitch = 0.8
        elif any(word in desc_lower for word in ["low", "bass", "deep"]):
            features.pitch = 0.2
        
        # 检测响度描述
        if any(word in desc_lower for word in ["loud", "forte", "powerful"]):
            features.loudness = 0.8
        elif any(word in desc_lower for word in ["quiet", "piano", "soft", "whisper"]):
            features.loudness = 0.2
        
        # 检测节奏描述
        if any(word in desc_lower for word in ["fast", "allegro", "rapid", "quick"]):
            features.tempo = 0.8
            features.rhythm_regularity = 0.7
        elif any(word in desc_lower for word in ["slow", "adagio", "leisurely"]):
            features.tempo = 0.3
            features.rhythm_regularity = 0.6
        
        # 检测和声描述
        if any(word in desc_lower for word in ["harmonic", "chord", "polyphonic"]):
            features.harmonic_content = 0.8
            features.timbre_complexity = 0.7
        elif any(word in desc_lower for word in ["monophonic", "single tone", "plain"]):
            features.harmonic_content = 0.2
            features.timbre_complexity = 0.3
        
        # 默认值处理
        if features.emotional_tone == "neutral":
            # 基于音高和响度推断情感
            if features.pitch > 0.7 and features.loudness > 0.6:
                features.emotional_tone = "excited"
            elif features.pitch < 0.3 and features.loudness < 0.4:
                features.emotional_tone = "melancholic"
            elif features.pitch > 0.5 and features.loudness < 0.4:
                features.emotional_tone = "gentle"
        
        return features
    
    def audio_to_color_synesthesia(self, features: AuditoryFeatures) -> Tuple[int, int, int]:
        """
        将听觉特征转换为颜色 (音 - 色联觉)
        
        Args:
            features: 听觉特征
            
        Returns:
            Tuple[int, int, int]: RGB 颜色值
        """
        # 基于音高的基础颜色
        base_color = ColorPalette.pitch_to_rgb(features.pitch)
        
        # 根据情感调整
        emotion_adjustment = {
            "happy": (20, 20, -10),
            "sad": (-10, -10, 20),
            "passionate": (30, -10, -10),
            "melancholic": (-15, -5, 15),
            "ethereal": (10, 10, 30),
            "triumphant": (25, 15, -5),
            "primal": (15, 5, -5),
            "intimate": (10, 5, 5),
            "excited": (25, 20, -10),
            "gentle": (5, 10, 15),
            "bright": (15, 15, -5),
            "neutral": (0, 0, 0),
        }
        
        adj = emotion_adjustment.get(features.emotional_tone, (0, 0, 0))
        
        r = max(0, min(255, base_color[0] + adj[0]))
        g = max(0, min(255, base_color[1] + adj[1]))
        b = max(0, min(255, base_color[2] + adj[2]))
        
        return (int(r), int(g), int(b))
    
    def map_audio_to_visual(self, description: str) -> VisualFeatures:
        """
        将音频描述直接映射为视觉特征
        
        Args:
            description: 音频描述
            
        Returns:
            VisualFeatures: 视觉特征
        """
        features = self.parse_audio_description(description)
        color = self.audio_to_color_synesthesia(features)
        
        return VisualFeatures(
            dominant_color=color,
            brightness=features.loudness * 0.7 + 0.15,
            temperature=ColorPalette.rgb_to_temperature(color),
            saturation=features.timbre_complexity,
            harmony=features.harmonic_content,
            complexity=features.timbre_complexity
        )
    
    def calculate_emotional_resonance(self, features: AuditoryFeatures) -> float:
        """
        计算音频的情感共鸣强度
        
        Args:
            features: 听觉特征
            
        Returns:
            float: 情感共鸣强度 (-1 到 1)
        """
        resonance = 0.0
        
        # 基于情感基调
        positive_emotions = ["happy", "triumphant", "excited", "ethereal", "gentle"]
        negative_emotions = ["sad", "melancholic", "primal"]
        
        if features.emotional_tone in positive_emotions:
            resonance += 0.4
        elif features.emotional_tone in negative_emotions:
            resonance -= 0.3
        
        # 基于音高和响度的组合
        if features.pitch > 0.6 and features.loudness > 0.5:
            resonance += 0.2  # 高亢明亮
        elif features.pitch < 0.4 and features.loudness < 0.4:
            resonance -= 0.2  # 低沉轻柔
        
        # 基于和声丰富度
        resonance += (features.harmonic_content - 0.5) * 0.3
        
        return max(-1.0, min(1.0, resonance))


class HapticTextureSimulator:
    """
    触觉质感模拟器
    模拟文字或概念带来的触觉感受
    """
    
    # 文字质感映射
    TEXTURE_WORDS = {
        "rough": {"roughness": 0.8, "hardness": 0.6, "temperature": 0.4},
        "smooth": {"roughness": 0.1, "hardness": 0.3, "temperature": 0.5},
        "soft": {"roughness": 0.2, "hardness": 0.1, "temperature": 0.6},
        "hard": {"roughness": 0.4, "hardness": 0.9, "temperature": 0.3},
        "cold": {"temperature": 0.1, "roughness": 0.3, "hardness": 0.7},
        "warm": {"temperature": 0.8, "roughness": 0.3, "hardness": 0.4},
        "wet": {"moisture": 0.9, "temperature": 0.4, "roughness": 0.2},
        "dry": {"moisture": 0.1, "temperature": 0.6, "roughness": 0.5},
        "heavy": {"weight": 0.9, "pressure": 0.7, "hardness": 0.8},
        "light": {"weight": 0.1, "pressure": 0.1, "hardness": 0.2},
        "sharp": {"roughness": 0.8, "hardness": 0.8, "pressure": 0.6},
        "blunt": {"roughness": 0.5, "hardness": 0.6, "pressure": 0.4},
        "harsh": {"roughness": 0.85, "hardness": 0.7, "pressure": 0.6},
        "gentle": {"roughness": 0.1, "hardness": 0.15, "temperature": 0.7},
    }
    
    # 材质触感档案
    MATERIAL_PROFILES = {
        "silk": {"roughness": 0.05, "hardness": 0.2, "temperature": 0.5, "moisture": 0.3},
        "sandpaper": {"roughness": 0.95, "hardness": 0.7, "temperature": 0.5, "moisture": 0.1},
        "metal": {"roughness": 0.2, "hardness": 0.95, "temperature": 0.2, "moisture": 0.0},
        "wood": {"roughness": 0.4, "hardness": 0.6, "temperature": 0.5, "moisture": 0.2},
        "water": {"roughness": 0.0, "hardness": 0.0, "temperature": 0.4, "moisture": 1.0},
        "stone": {"roughness": 0.6, "hardness": 0.9, "temperature": 0.3, "moisture": 0.1},
        "fur": {"roughness": 0.3, "hardness": 0.2, "temperature": 0.7, "moisture": 0.2},
        "glass": {"roughness": 0.05, "hardness": 0.85, "temperature": 0.3, "moisture": 0.0},
    }
    
    def simulate_haptic_from_text(self, text: str) -> HapticFeatures:
        """
        从文本描述模拟触觉感受
        
        Args:
            text: 文字描述
            
        Returns:
            HapticFeatures: 触觉特征向量
        """
        text_lower = text.lower()
        features = HapticFeatures()
        
        # 检测质感形容词
        for word, props in self.TEXTURE_WORDS.items():
            if word in text_lower:
                if "roughness" in props:
                    features.texture_roughness = props["roughness"]
                if "hardness" in props:
                    features.hardness = props["hardness"]
                if "temperature" in props:
                    features.temperature = props["temperature"]
                if "moisture" in props:
                    features.moisture = props["moisture"]
                if "weight" in props:
                    features.weight = props["weight"]
                if "pressure" in props:
                    features.pressure = props["pressure"]
                break
        
        # 检测材质名词
        for material, props in self.MATERIAL_PROFILES.items():
            if material in text_lower:
                features.texture_roughness = props["roughness"]
                features.hardness = props["hardness"]
                features.temperature = props["temperature"]
                features.moisture = props["moisture"]
                break
        
        # 隐喻性触觉 (抽象概念的质感)
        abstract_mappings = {
            "harsh words": {"roughness": 0.8, "sharpness": 0.7},
            "gentle touch": {"roughness": 0.1, "softness": 0.9},
            "cold personality": {"temperature": 0.1, "hardness": 0.7},
            "warm smile": {"temperature": 0.8, "softness": 0.6},
            "heavy heart": {"weight": 0.9, "pressure": 0.8},
            "light mood": {"weight": 0.1, "pressure": 0.1},
        }
        
        for phrase, props in abstract_mappings.items():
            if phrase in text_lower:
                if "roughness" in props:
                    features.texture_roughness = props["roughness"]
                if "temperature" in props:
                    features.temperature = props["temperature"]
                if "weight" in props:
                    features.weight = props["weight"]
                if "pressure" in props:
                    features.pressure = props["pressure"]
                break
        
        return features
    
    def text_to_texture_synesthesia(self, text: str) -> Dict[str, float]:
        """
        将文字转换为触觉质感评分
        
        Args:
            text: 输入文字
            
        Returns:
            Dict[str, float]: 各维度触觉评分
        """
        features = self.simulate_haptic_from_text(text)
        
        return {
            "roughness": features.texture_roughness,
            "hardness": features.hardness,
            "temperature": features.temperature,
            "moisture": features.moisture,
            "weight": features.weight,
            "pressure": features.pressure,
            "overall_intensity": (
                features.texture_roughness * 0.2 +
                features.hardness * 0.2 +
                abs(features.temperature - 0.5) * 0.2 +
                features.moisture * 0.15 +
                features.weight * 0.15 +
                features.pressure * 0.1
            )
        }


class SynestheticFusionLayer:
    """
    通感融合层
    整合多模态特征，生成跨模态联想和通感体验
    """
    
    def __init__(self):
        self.visual_encoder = VisualSemanticsEncoder()
        self.auditory_mapper = AuditoryEmotionMapper()
        self.haptic_simulator = HapticTextureSimulator()
    
    def fuse_multimodal_input(
        self,
        visual_desc: Optional[str] = None,
        auditory_desc: Optional[str] = None,
        textual_desc: Optional[str] = None
    ) -> SynestheticExperience:
        """
        融合多模态输入生成通感体验
        
        Args:
            visual_desc: 视觉描述 (可选)
            auditory_desc: 听觉描述 (可选)
            textual_desc: 文字描述 (可选)
            
        Returns:
            SynestheticExperience: 融合后的通感体验
        """
        experience = SynestheticExperience(
            input_modality=ModalityType.TEXTUAL,
            input_description=textual_desc or visual_desc or auditory_desc or ""
        )
        
        # 处理视觉输入
        if visual_desc:
            experience.input_modality = ModalityType.VISUAL
            experience.visual = self.visual_encoder.encode_visual_description(visual_desc)
            experience.emotional_resonance = self.visual_encoder.extract_emotional_resonance(
                experience.visual, visual_desc
            )
            
            # 视觉→听觉联觉
            if experience.visual:
                if experience.visual.brightness > 0.7:
                    experience.auditory = AuditoryFeatures(
                        pitch=0.7,
                        loudness=0.5,
                        emotional_tone="bright",
                        timbre_complexity=0.6
                    )
                    experience.synesthesia_type = SynesthesiaType.SOUND_SEEING
        
        # 处理听觉输入
        if auditory_desc:
            experience.input_modality = ModalityType.AUDITORY
            experience.auditory = self.auditory_mapper.parse_audio_description(auditory_desc)
            experience.emotional_resonance = self.auditory_mapper.calculate_emotional_resonance(
                experience.auditory
            )
            
            # 听觉→视觉联觉 (音 - 色联觉)
            if experience.auditory:
                color = self.auditory_mapper.audio_to_color_synesthesia(experience.auditory)
                experience.visual = VisualFeatures(
                    dominant_color=color,
                    brightness=experience.auditory.loudness * 0.7 + 0.15,
                    temperature=ColorPalette.rgb_to_temperature(color),
                    saturation=experience.auditory.timbre_complexity
                )
                experience.synesthesia_type = SynesthesiaType.COLOR_HEARING
        
        # 处理文字输入 (可能包含多模态隐喻)
        if textual_desc:
            experience.haptic = self.haptic_simulator.simulate_haptic_from_text(textual_desc)
            
            # 文字中的视觉隐喻
            visual_keywords = ["see", "look", "bright", "dark", "color", "image"]
            if any(kw in textual_desc.lower() for kw in visual_keywords):
                experience.visual = self.visual_encoder.encode_visual_description(textual_desc)
            
            # 文字中的听觉隐喻
            auditory_keywords = ["hear", "sound", "loud", "quiet", "music", "voice"]
            if any(kw in textual_desc.lower() for kw in auditory_keywords):
                experience.auditory = self.auditory_mapper.parse_audio_description(textual_desc)
        
        # 跨模态关联
        experience.cross_modal_associations = self._generate_cross_modal_associations(experience)
        
        # 计算置信度
        experience.confidence = self._calculate_confidence(experience)
        
        return experience
    
    def _generate_cross_modal_associations(self, experience: SynestheticExperience) -> Dict[str, Any]:
        """生成跨模态关联"""
        associations = {}
        
        if experience.visual and experience.auditory:
            # 视觉 - 听觉对应
            associations["visuo_auditory"] = {
                "brightness_pitch_correlation": abs(experience.visual.brightness - experience.auditory.pitch),
                "color_emotion_match": experience.visual.temperature - (
                    0.5 if experience.auditory.emotional_tone in ["happy", "excited"] else 0.3
                )
            }
        
        if experience.haptic and experience.visual:
            # 触觉 - 视觉对应
            associations["haptic_visual"] = {
                "temperature_color_consistency": abs(experience.haptic.temperature - experience.visual.temperature),
                "texture_complexity_match": abs(experience.haptic.texture_roughness - experience.visual.complexity)
            }
        
        if experience.haptic and experience.auditory:
            # 触觉 - 听觉对应
            associations["haptic_auditory"] = {
                "vibration_rhythm_relation": experience.haptic.vibration - experience.auditory.rhythm_regularity * 0.5
            }
        
        return associations
    
    def _calculate_confidence(self, experience: SynestheticExperience) -> float:
        """计算通感体验的置信度"""
        confidence_factors = []
        
        # 基于输入质量
        if experience.input_description:
            word_count = len(experience.input_description.split())
            confidence_factors.append(min(1.0, word_count / 10))
        
        # 基于模态一致性
        if experience.cross_modal_associations:
            consistency_scores = []
            for mod_pair, values in experience.cross_modal_associations.items():
                for metric, value in values.items():
                    # 差异越小越一致
                    consistency_scores.append(1.0 - abs(value))
            if consistency_scores:
                confidence_factors.append(sum(consistency_scores) / len(consistency_scores))
        
        # 基于情感共鸣强度
        confidence_factors.append(abs(experience.emotional_resonance))
        
        if not confidence_factors:
            return 0.5
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def enrich_poetry_with_synesthesia(self, poem: str) -> Dict[str, Any]:
        """
        用通感体验丰富诗歌理解
        
        Args:
            poem: 诗歌文本
            
        Returns:
            Dict[str, Any]: 包含多模态解读的结果
        """
        lines = poem.strip().split('\n')
        line_experiences = []
        
        for line in lines:
            if not line.strip():
                continue
            
            experience = self.fuse_multimodal_input(textual_desc=line)
            line_experiences.append({
                "line": line,
                "synesthetic_experience": experience
            })
        
        # 整体分析
        overall_experience = self.fuse_multimodal_input(textual_desc=poem)
        
        return {
            "poem": poem,
            "line_by_line_analysis": line_experiences,
            "overall_experience": overall_experience,
            "dominant_synesthesia": overall_experience.synesthesia_type.value if overall_experience.synesthesia_type else "none",
            "emotional_arc": [exp["synesthetic_experience"].emotional_resonance for exp in line_experiences]
        }


class SynesthesiaEngine:
    """
    通感引擎主类
    整合所有通感组件，提供统一接口
    """
    
    def __init__(self):
        self.fusion_layer = SynestheticFusionLayer()
        self.visual_encoder = VisualSemanticsEncoder()
        self.auditory_mapper = AuditoryEmotionMapper()
        self.haptic_simulator = HapticTextureSimulator()
    
    def generate_synesthetic_experience(
        self,
        description: str,
        modality_hint: Optional[ModalityType] = None
    ) -> SynestheticExperience:
        """
        生成通感体验
        
        Args:
            description: 输入描述
            modality_hint: 模态提示 (可选)
            
        Returns:
            SynestheticExperience: 通感体验
        """
        # 自动检测模态
        if modality_hint is None:
            desc_lower = description.lower()
            # 增强听觉关键词检测
            auditory_keywords = ["hear", "listen", "sound", "music", "audio", 
                                "melody", "symphony", "song", "tune", "note",
                                "instrument", "piano", "violin", "cello", "guitar",
                                "drum", "flute", "trumpet", "bass", "treble",
                                "major", "minor", "key", "chord", "harmony"]
            # 增强视觉关键词检测
            visual_keywords = ["see", "look", "view", "image", "picture", "visual",
                              "scene", "landscape", "color", "bright", "dark",
                              "light", "shadow", "painting", "art"]
            
            if any(kw in desc_lower for kw in auditory_keywords):
                modality_hint = ModalityType.AUDITORY
            elif any(kw in desc_lower for kw in visual_keywords):
                modality_hint = ModalityType.VISUAL
            else:
                modality_hint = ModalityType.TEXTUAL
        
        # 根据模态调用不同处理流程
        if modality_hint == ModalityType.VISUAL:
            return self.fusion_layer.fuse_multimodal_input(visual_desc=description)
        elif modality_hint == ModalityType.AUDITORY:
            return self.fusion_layer.fuse_multimodal_input(auditory_desc=description)
        else:
            return self.fusion_layer.fuse_multimodal_input(textual_desc=description)
    
    def analyze_artwork(self, artwork_description: str) -> Dict[str, Any]:
        """
        分析艺术作品的多模态体验
        
        Args:
            artwork_description: 艺术作品描述
            
        Returns:
            Dict[str, Any]: 多模态分析结果
        """
        experience = self.generate_synesthetic_experience(artwork_description)
        
        return {
            "visual_features": {
                "dominant_color": experience.visual.dominant_color if experience.visual else None,
                "brightness": experience.visual.brightness if experience.visual else None,
                "temperature": experience.visual.temperature if experience.visual else None,
                "harmony": experience.visual.harmony if experience.visual else None,
            } if experience.visual else {},
            "evoked_sounds": {
                "pitch": experience.auditory.pitch if experience.auditory else None,
                "emotional_tone": experience.auditory.emotional_tone if experience.auditory else None,
                "suggested_color": self.auditory_mapper.audio_to_color_synesthesia(experience.auditory) if experience.auditory else None,
            } if experience.auditory else {},
            "tactile_qualities": {
                "texture": experience.haptic.texture_roughness if experience.haptic else None,
                "temperature": experience.haptic.temperature if experience.haptic else None,
                "weight": experience.haptic.weight if experience.haptic else None,
            } if experience.haptic else {},
            "emotional_resonance": experience.emotional_resonance,
            "synesthesia_type": experience.synesthesia_type.value if experience.synesthesia_type else None,
            "confidence": experience.confidence
        }
    
    def describe_music_as_colors(self, music_description: str) -> str:
        """
        将音乐描述为颜色
        
        Args:
            music_description: 音乐描述
            
        Returns:
            str: 颜色描述
        """
        auditory_features = self.auditory_mapper.parse_audio_description(music_description)
        color = self.auditory_mapper.audio_to_color_synesthesia(auditory_features)
        
        color_names = {
            (255, 0, 0): "炽热的红色",
            (0, 255, 0): "生机的绿色",
            (0, 0, 255): "深邃的蓝色",
            (255, 255, 0): "明亮的黄色",
            (255, 165, 0): "温暖的橙色",
            (128, 0, 128): "神秘的紫色",
            (255, 192, 203): "柔和的粉色",
            (70, 130, 180): "忧郁的钢蓝色",
            (255, 215, 0): "辉煌的金色",
            (25, 25, 112): "深沉的午夜蓝",
        }
        
        # 查找最接近的颜色名称
        closest_name = "复杂的混合色"
        min_distance = float('inf')
        
        for rgb, name in color_names.items():
            distance = sum((a - b) ** 2 for a, b in zip(color, rgb))
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        
        emotion = auditory_features.emotional_tone
        pitch_desc = "高音" if auditory_features.pitch > 0.6 else "低音" if auditory_features.pitch < 0.4 else "中音"
        
        return f"这段{emotion}的{pitch_desc}音乐呈现出{closest_name} (RGB: {color})"
    
    def feel_text_texture(self, text: str) -> str:
        """
        感受文字的触觉质感
        
        Args:
            text: 文字
            
        Returns:
            str: 质感描述
        """
        haptic = self.haptic_simulator.simulate_haptic_from_text(text)
        texture_scores = self.haptic_simulator.text_to_texture_synesthesia(text)
        
        descriptions = []
        
        if haptic.texture_roughness > 0.7:
            descriptions.append("粗糙如砂纸")
        elif haptic.texture_roughness < 0.2:
            descriptions.append("光滑如丝绸")
        
        if haptic.temperature < 0.2:
            descriptions.append("冰冷刺骨")
        elif haptic.temperature > 0.8:
            descriptions.append("温暖如阳光")
        
        if haptic.hardness > 0.8:
            descriptions.append("坚硬如石")
        elif haptic.hardness < 0.2:
            descriptions.append("柔软如棉")
        
        if haptic.weight > 0.8:
            descriptions.append("沉重压抑")
        elif haptic.weight < 0.2:
            descriptions.append("轻盈飘逸")
        
        if not descriptions:
            descriptions.append("质感中性")
        
        return f"这段文字给人的触感是：{', '.join(descriptions)}。综合质感强度：{texture_scores['overall_intensity']:.2f}"


# 全局引擎实例
_engine: Optional[SynesthesiaEngine] = None


def get_synesthesia_engine() -> SynesthesiaEngine:
    """获取通感引擎单例"""
    global _engine
    if _engine is None:
        _engine = SynesthesiaEngine()
    return _engine


if __name__ == "__main__":
    # 演示用法
    engine = get_synesthesia_engine()
    
    print("=" * 60)
    print("多模态通感融合系统演示")
    print("=" * 60)
    
    # 示例 1: 音乐→颜色
    music_desc = "一段悲伤的大提琴独奏，缓慢而低沉"
    print(f"\n🎵 音乐描述：{music_desc}")
    color_desc = engine.describe_music_as_colors(music_desc)
    print(f"🎨 颜色描述：{color_desc}")
    
    # 示例 2: 文字→触觉
    text = " harsh words cut like knives"
    print(f"\n📝 文字：{text}")
    texture = engine.feel_text_texture(text)
    print(f"✋ 触感：{texture}")
    
    # 示例 3: 艺术作品分析
    artwork = "夕阳下的海面，金色的波光粼粼，远处有朦胧的山影"
    print(f"\n🎨 艺术作品：{artwork}")
    analysis = engine.analyze_artwork(artwork)
    print(f"情感共鸣：{analysis['emotional_resonance']:.2f}")
    if analysis.get('visual_features', {}).get('dominant_color'):
        print(f"主色调：{analysis['visual_features']['dominant_color']}")
    print(f"通感类型：{analysis['synesthesia_type']}")
    
    # 示例 4: 诗歌通感分析
    poem = """
    The fog comes on little cat feet.
    It sits looking over harbor and city
    on silent haunches and then moves on.
    """
    print(f"\n📜 诗歌分析:")
    poetry_analysis = engine.fusion_layer.enrich_poetry_with_synesthesia(poem)
    print(f"主导通感：{poetry_analysis['dominant_synesthesia']}")
    print(f"情感弧线：{poetry_analysis['emotional_arc']}")
    
    print("\n" + "=" * 60)
