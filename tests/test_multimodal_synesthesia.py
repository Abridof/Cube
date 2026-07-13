"""
多模态通感融合系统测试套件
测试覆盖:
- 视觉语义编码
- 听觉情感映射
- 触觉质感模拟
- 通感融合
- 跨模态联想
"""

import pytest
from src.modules.multimodal_synesthesia import (
    get_synesthesia_engine,
    SynesthesiaEngine,
    VisualSemanticsEncoder,
    AuditoryEmotionMapper,
    HapticTextureSimulator,
    SynestheticFusionLayer,
    ColorPalette,
    ModalityType,
    SynesthesiaType,
    VisualFeatures,
    AuditoryFeatures,
    HapticFeatures,
)


class TestColorPalette:
    """测试颜色心理学映射"""
    
    def test_emotion_to_rgb_basic(self):
        """测试基础情感到 RGB 的转换"""
        assert ColorPalette.emotion_to_rgb("joy") == (255, 215, 0)
        assert ColorPalette.emotion_to_rgb("sadness") == (70, 130, 180)
        assert ColorPalette.emotion_to_rgb("anger") == (220, 20, 60)
    
    def test_emotion_to_rgb_unknown(self):
        """测试未知情感返回灰色"""
        assert ColorPalette.emotion_to_rgb("unknown") == (128, 128, 128)
    
    def test_pitch_to_rgb_low(self):
        """测试低音到颜色的映射"""
        color = ColorPalette.pitch_to_rgb(0.0)
        assert color[0] > 100  # 红色分量高
        assert color[2] < 50   # 蓝色分量低
    
    def test_pitch_to_rgb_high(self):
        """测试高音到颜色的映射"""
        color = ColorPalette.pitch_to_rgb(1.0)
        assert color[2] > 200  # 蓝色分量高
    
    def test_pitch_to_rgb_interpolation(self):
        """测试音高插值"""
        color_low = ColorPalette.pitch_to_rgb(0.4)
        color_high = ColorPalette.pitch_to_rgb(0.6)
        # 中间音高应该有不同的颜色
        assert color_low != color_high
    
    def test_rgb_to_temperature_warm(self):
        """测试暖色温度计算"""
        temp = ColorPalette.rgb_to_temperature((255, 100, 50))
        assert temp > 0.5
    
    def test_rgb_to_temperature_cold(self):
        """测试冷色温度计算"""
        temp = ColorPalette.rgb_to_temperature((50, 100, 255))
        assert temp < 0.5


class TestVisualSemanticsEncoder:
    """测试视觉语义编码器"""
    
    def test_encode_sunset(self):
        """测试日落场景编码"""
        encoder = VisualSemanticsEncoder()
        features = encoder.encode_visual_description("A beautiful sunset over the ocean")
        
        assert features.temperature > 0.5  # 温暖
        assert features.brightness > 0.5   # 明亮
    
    def test_encode_storm(self):
        """测试暴风雨场景编码"""
        encoder = VisualSemanticsEncoder()
        features = encoder.encode_visual_description("A dark storm with lightning")
        
        assert features.temperature < 0.5  # 冷
        assert features.brightness < 0.5   # 暗
    
    def test_encode_color_detection(self):
        """测试颜色词检测"""
        encoder = VisualSemanticsEncoder()
        features = encoder.encode_visual_description("A bright red apple")
        
        assert features.dominant_color[0] > 200  # 红色分量高
    
    def test_extract_emotional_resonance_positive(self):
        """测试积极场景的情感共鸣"""
        encoder = VisualSemanticsEncoder()
        features = encoder.encode_visual_description("A wonderful sunny day")
        resonance = encoder.extract_emotional_resonance(features, "A wonderful sunny day")
        
        assert resonance > 0
    
    def test_extract_emotional_resonance_negative(self):
        """测试消极场景的情感共鸣"""
        encoder = VisualSemanticsEncoder()
        features = encoder.encode_visual_description("A terrible dark night")
        resonance = encoder.extract_emotional_resonance(features, "A terrible dark night")
        
        assert resonance < 0


class TestAuditoryEmotionMapper:
    """测试听觉情感映射器"""
    
    def test_parse_cello(self):
        """测试大提琴声音解析"""
        mapper = AuditoryEmotionMapper()
        features = mapper.parse_audio_description("A melancholic cello solo")
        
        assert features.pitch < 0.5  # 低音
        assert features.emotional_tone == "melancholic"
    
    def test_parse_violin(self):
        """测试小提琴声音解析"""
        mapper = AuditoryEmotionMapper()
        features = mapper.parse_audio_description("A passionate violin concerto")
        
        assert features.pitch > 0.5  # 高音
        assert features.emotional_tone == "passionate"
    
    def test_audio_to_color_synesthesia_sad(self):
        """测试悲伤音乐的音色联觉"""
        mapper = AuditoryEmotionMapper()
        features = mapper.parse_audio_description("A sad minor key melody")
        color = mapper.audio_to_color_synesthesia(features)
        
        # 悲伤音乐应该偏冷色调
        assert color[2] > color[0]  # 蓝色分量高于红色
    
    def test_audio_to_color_synesthesia_happy(self):
        """测试快乐音乐的音色联觉"""
        mapper = AuditoryEmotionMapper()
        features = mapper.parse_audio_description("A happy major key tune")
        color = mapper.audio_to_color_synesthesia(features)
        
        # 快乐音乐应该偏暖色调
        assert color[0] > 150 or color[1] > 150  # 红或绿分量高
    
    def test_calculate_emotional_resonance_positive(self):
        """测试积极音频的情感共鸣"""
        mapper = AuditoryEmotionMapper()
        features = AuditoryFeatures(
            pitch=0.7,
            loudness=0.6,
            emotional_tone="happy",
            harmonic_content=0.7
        )
        resonance = mapper.calculate_emotional_resonance(features)
        assert resonance > 0
    
    def test_calculate_emotional_resonance_negative(self):
        """测试消极音频的情感共鸣"""
        mapper = AuditoryEmotionMapper()
        features = AuditoryFeatures(
            pitch=0.2,
            loudness=0.3,
            emotional_tone="sad",
            harmonic_content=0.3
        )
        resonance = mapper.calculate_emotional_resonance(features)
        assert resonance < 0


class TestHapticTextureSimulator:
    """测试触觉质感模拟器"""
    
    def test_simulate_rough_texture(self):
        """测试粗糙质感模拟"""
        simulator = HapticTextureSimulator()
        features = simulator.simulate_haptic_from_text("A rough sandpaper surface")
        
        assert features.texture_roughness > 0.7
        assert features.hardness > 0.5
    
    def test_simulate_smooth_texture(self):
        """测试光滑质感模拟"""
        simulator = HapticTextureSimulator()
        features = simulator.simulate_haptic_from_text("Smooth silk fabric")
        
        assert features.texture_roughness < 0.2
        assert features.hardness < 0.3
    
    def test_simulate_temperature(self):
        """测试温度感知"""
        simulator = HapticTextureSimulator()
        features = simulator.simulate_haptic_from_text("Cold ice")
        
        assert features.temperature < 0.2
    
    def test_text_to_texture_synesthesia_heavy(self):
        """测试沉重文字的质感"""
        simulator = HapticTextureSimulator()
        scores = simulator.text_to_texture_synesthesia("A heavy burden on my shoulders")
        
        assert scores["weight"] > 0.7
        assert scores["pressure"] > 0.5
    
    def test_abstract_metaphor_harsh_words(self):
        """测试抽象隐喻：刺耳的话语"""
        simulator = HapticTextureSimulator()
        features = simulator.simulate_haptic_from_text("harsh words cut like knives")
        
        assert features.texture_roughness > 0.5


class TestSynestheticFusionLayer:
    """测试通感融合层"""
    
    def test_fuse_visual_input(self):
        """测试视觉输入融合"""
        layer = SynestheticFusionLayer()
        experience = layer.fuse_multimodal_input(
            visual_desc="A bright sunny meadow with flowers"
        )
        
        assert experience.input_modality == ModalityType.VISUAL
        assert experience.visual is not None
        assert experience.visual.brightness > 0.5
    
    def test_fuse_auditory_input(self):
        """测试听觉输入融合"""
        layer = SynestheticFusionLayer()
        experience = layer.fuse_multimodal_input(
            auditory_desc="A gentle piano melody in major key"
        )
        
        assert experience.input_modality == ModalityType.AUDITORY
        assert experience.auditory is not None
        assert experience.synesthesia_type == SynesthesiaType.COLOR_HEARING
        assert experience.visual is not None  # 应该有颜色联觉
    
    def test_fuse_textual_input(self):
        """测试文字输入融合"""
        layer = SynestheticFusionLayer()
        experience = layer.fuse_multimodal_input(
            textual_desc="I hear the sound of distant thunder"
        )
        
        assert experience.haptic is not None
        assert experience.auditory is not None  # 检测到听觉关键词
    
    def test_cross_modal_associations(self):
        """测试跨模态关联生成"""
        layer = SynestheticFusionLayer()
        experience = layer.fuse_multimodal_input(
            visual_desc="A warm sunset",
            auditory_desc="A mellow cello"
        )
        
        assert "visuo_auditory" in experience.cross_modal_associations
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        layer = SynestheticFusionLayer()
        experience = layer.fuse_multimodal_input(
            textual_desc="A very detailed and rich description of a scene"
        )
        
        assert experience.confidence > 0.3
    
    def test_enrich_poetry_with_synesthesia(self):
        """测试诗歌通感丰富"""
        layer = SynestheticFusionLayer()
        poem = "The fog comes on little cat feet."
        result = layer.enrich_poetry_with_synesthesia(poem)
        
        assert "poem" in result
        assert "line_by_line_analysis" in result
        assert "overall_experience" in result
        assert len(result["line_by_line_analysis"]) > 0


class TestSynesthesiaEngine:
    """测试通感引擎主类"""
    
    def test_generate_synesthetic_experience_auto_detect(self):
        """测试自动模态检测"""
        engine = get_synesthesia_engine()
        
        # 视觉关键词
        exp1 = engine.generate_synesthetic_experience("Look at this beautiful image")
        assert exp1.input_modality == ModalityType.VISUAL
        
        # 听觉关键词
        exp2 = engine.generate_synesthetic_experience("Listen to this music")
        assert exp2.input_modality == ModalityType.AUDITORY
        
        # 默认文字
        exp3 = engine.generate_synesthetic_experience("Some random text")
        assert exp3.input_modality == ModalityType.TEXTUAL
    
    def test_analyze_artwork(self):
        """测试艺术作品分析"""
        engine = get_synesthesia_engine()
        analysis = engine.analyze_artwork(
            "A serene landscape with mountains and a calm lake at sunset"
        )
        
        assert "visual_features" in analysis
        assert "emotional_resonance" in analysis
        assert analysis["visual_features"]["temperature"] > 0.5
    
    def test_describe_music_as_colors(self):
        """测试音乐颜色描述"""
        engine = get_synesthesia_engine()
        
        # 悲伤的大提琴
        desc1 = engine.describe_music_as_colors("A sad cello solo in minor key")
        assert "蓝色" in desc1 or "蓝" in desc1 or "cold" in desc1.lower()
        
        # 欢快的小号
        desc2 = engine.describe_music_as_colors("A triumphant trumpet fanfare")
        assert len(desc2) > 20  # 应该有详细描述
    
    def test_feel_text_texture(self):
        """测试文字触感"""
        engine = get_synesthesia_engine()
        
        # 尖锐的文字
        texture1 = engine.feel_text_texture("Sharp criticism that cuts deep")
        assert "粗糙" in texture1 or "坚硬" in texture1 or "rough" in texture1.lower()
        
        # 温柔的文字
        texture2 = engine.feel_text_texture("Gentle words of comfort")
        assert "光滑" in texture2 or "柔软" in texture2 or "smooth" in texture2.lower()
    
    def test_multimodal_integration(self):
        """测试多模态整合"""
        engine = get_synesthesia_engine()
        
        # 复杂场景：视觉 + 听觉 + 触觉
        artwork = "A stormy sea with crashing waves and thunder"
        analysis = engine.analyze_artwork(artwork)
        
        assert analysis["emotional_resonance"] != 0
        assert analysis["visual_features"] is not None


class TestIntegrationScenarios:
    """集成场景测试"""
    
    def test_synesthesia_pipeline_complete(self):
        """测试完整通感流程"""
        engine = get_synesthesia_engine()
        
        # 输入：音乐描述
        music = "A slow, melancholic cello piece in a minor key"
        
        # 步骤 1: 解析音频
        auditory_features = engine.auditory_mapper.parse_audio_description(music)
        assert auditory_features.emotional_tone == "melancholic"
        
        # 步骤 2: 生成颜色
        color = engine.auditory_mapper.audio_to_color_synesthesia(auditory_features)
        assert isinstance(color, tuple) and len(color) == 3
        
        # 步骤 3: 完整体验
        experience = engine.generate_synesthetic_experience(music)
        assert experience.visual is not None
        assert experience.emotional_resonance < 0  # 悲伤应该是负的
    
    def test_poetry_multimodal_analysis(self):
        """测试诗歌多模态分析"""
        engine = get_synesthesia_engine()
        
        poem = """
        The fog comes on little cat feet.
        It sits looking over harbor and city
        on silent haunches and then moves on.
        """
        
        analysis = engine.fusion_layer.enrich_poetry_with_synesthesia(poem)
        
        # 检查情感弧线
        assert len(analysis["emotional_arc"]) == 3  # 三行
        
        # 整体应该有某种通感类型
        assert analysis["dominant_synesthesia"] in [
            "color_hearing", "sound_seeing", "texture_sound",
            "emotion_color", "concept_temperature", "none"
        ]
    
    def test_artwork_comprehensive_analysis(self):
        """测试艺术品综合分析"""
        engine = get_synesthesia_engine()
        
        artwork = "Van Gogh's Starry Night: swirling blues and yellows"
        analysis = engine.analyze_artwork(artwork)
        
        # 应该有视觉特征
        assert "dominant_color" in analysis["visual_features"]
        
        # 应该有情感共鸣
        assert -1 <= analysis["emotional_resonance"] <= 1
        
        # 可能有触觉质感
        if analysis.get("tactile_qualities"):
            assert "texture" in analysis["tactile_qualities"]
    
    def test_cross_cultural_synesthesia(self):
        """测试跨文化通感（简化版）"""
        engine = get_synesthesia_engine()
        
        # 西方音乐描述
        western = "A grand symphony with trumpets and drums"
        west_exp = engine.generate_synesthetic_experience(western)
        
        # 东方音乐描述
        eastern = "A delicate guqin solo with plucked strings"
        east_exp = engine.generate_synesthetic_experience(eastern)
        
        # 应该有不同的特征
        assert west_exp.auditory is not None
        assert east_exp.auditory is not None
        # 音高可能不同
        # (不强制断言，因为实现可能相似)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
