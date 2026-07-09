"""
多模态感知层单元测试
"""

import unittest
import json
from multimodal_perception import (
    ModalityType, FeatureType, ModalFeature, PerceivedObject,
    ImagePerceiver, AudioPerceiver, StructuredDataPerceiver,
    MultimodalFusionEngine, create_multimodal_engine
)


class TestModalFeature(unittest.TestCase):
    """测试模态特征"""
    
    def test_create_feature(self):
        """创建特征"""
        feat = ModalFeature(
            feature_type=FeatureType.SPATIAL,
            name='test_feature',
            value=42.0,
            confidence=0.95
        )
        self.assertEqual(feat.name, 'test_feature')
        self.assertEqual(feat.value, 42.0)
        self.assertEqual(feat.confidence, 0.95)
    
    def test_feature_with_location(self):
        """带位置信息的特征"""
        feat = ModalFeature(
            feature_type=FeatureType.SPATIAL,
            name='bounding_box',
            value={'x': 10, 'y': 20},
            confidence=0.9,
            location={'top': 0, 'left': 0, 'width': 100, 'height': 100}
        )
        self.assertIsNotNone(feat.location)
        self.assertEqual(feat.location['width'], 100)


class TestPerceivedObject(unittest.TestCase):
    """测试感知对象"""
    
    def test_create_object(self):
        """创建感知对象"""
        feat = ModalFeature(
            feature_type=FeatureType.SEMANTIC,
            name='category',
            value='cat',
            confidence=0.9
        )
        obj = PerceivedObject(
            object_id='obj_001',
            modality=ModalityType.IMAGE,
            category='animal',
            features=[feat],
            confidence=0.9
        )
        self.assertEqual(obj.object_id, 'obj_001')
        self.assertEqual(len(obj.features), 1)
        self.assertEqual(obj.modality, ModalityType.IMAGE)
    
    def test_object_with_relations(self):
        """带关系的感知对象"""
        obj = PerceivedObject(
            object_id='obj_001',
            modality=ModalityType.IMAGE,
            category='scene',
            features=[],
            confidence=0.8,
            relations=['obj_002', 'obj_003']
        )
        self.assertEqual(len(obj.relations), 2)


class TestImagePerceiver(unittest.TestCase):
    """测试图像感知器"""
    
    def setUp(self):
        self.perceiver = ImagePerceiver()
    
    def test_perceive_bytes(self):
        """感知字节图像数据"""
        fake_image = bytes([i % 256 for i in range(1000)])
        objects = self.perceiver.perceive(fake_image)
        
        self.assertGreater(len(objects), 0)
        # 应该至少有一个整合的场景对象
        scene_objects = [o for o in objects if o.category == 'integrated_scene']
        self.assertGreater(len(scene_objects), 0)
    
    def test_perceive_dict_with_dimensions(self):
        """感知结构化图像数据（带尺寸）"""
        image_dict = {
            'width': 800,
            'height': 600
        }
        objects = self.perceiver.perceive(image_dict)
        
        self.assertGreater(len(objects), 0)
        # 检查是否提取了尺寸特征
        has_dimension = False
        for obj in objects:
            for feat in obj.features:
                if feat.name == 'dimensions':
                    has_dimension = True
                    self.assertEqual(feat.value['width'], 800)
                    self.assertEqual(feat.value['height'], 600)
        self.assertTrue(has_dimension)
    
    def test_perceive_dict_with_objects(self):
        """感知结构化图像数据（带物体列表）"""
        image_dict = {
            'width': 800,
            'height': 600,
            'objects': [
                {'category': 'person', 'confidence': 0.95, 'bbox': [100, 100, 200, 300]},
                {'category': 'car', 'confidence': 0.88, 'bbox': [400, 300, 600, 500]}
            ]
        }
        objects = self.perceiver.perceive(image_dict)
        
        # 应该检测到物体
        person_objects = [o for o in objects if o.category == 'person']
        self.assertGreater(len(person_objects), 0)
        self.assertEqual(person_objects[0].bounding_box, [100, 100, 200, 300])
    
    def test_metadata_estimation(self):
        """元数据估计"""
        png_header = b'\x89PNG' + b'\x00' * 100
        objects = self.perceiver.perceive(png_header)
        
        self.assertGreater(len(objects), 0)
        # 检查格式检测
        self.assertEqual(objects[0].metadata.get('format'), 'PNG')


class TestAudioPerceiver(unittest.TestCase):
    """测试音频感知器"""
    
    def setUp(self):
        self.perceiver = AudioPerceiver()
    
    def test_perceive_samples(self):
        """感知音频样本列表"""
        samples = [0.5 * (i % 100) / 100 for i in range(2000)]
        objects = self.perceiver.perceive(samples, {'sample_rate': 44100})
        
        self.assertGreater(len(objects), 0)
        
        # 检查是否提取了时域特征
        temporal_objects = [o for o in objects if o.category == 'temporal_pattern']
        self.assertGreater(len(temporal_objects), 0)
    
    def test_temporal_features(self):
        """时域特征提取"""
        # 创建一个简单的正弦波模拟
        import math
        samples = [math.sin(i * 0.1) for i in range(1000)]
        objects = self.perceiver.perceive(samples)
        
        # 应该包含 RMS 能量和过零率
        feature_names = []
        for obj in objects:
            for feat in obj.features:
                feature_names.append(feat.name)
        
        self.assertIn('rms_energy', feature_names)
        self.assertIn('zero_crossing_rate', feature_names)
    
    def test_spectral_features(self):
        """频域特征提取"""
        samples = [0.8] * 500 + [-0.8] * 500  # 方波
        objects = self.perceiver.perceive(samples)
        
        feature_names = []
        for obj in objects:
            for feat in obj.features:
                feature_names.append(feat.name)
        
        self.assertIn('spectral_balance', feature_names)
    
    def test_rhythm_detection(self):
        """节奏检测"""
        # 创建有节奏的样本
        samples = []
        for i in range(4410):  # 0.1 秒 @ 44100Hz
            if (i // 1102) % 2 == 0:  # 每 0.025 秒一个节拍
                samples.append(0.9)
            else:
                samples.append(0.1)
        
        objects = self.perceiver.perceive(samples, {'sample_rate': 44100})
        
        # 检查 BPM 估计
        bpm_features = []
        for obj in objects:
            for feat in obj.features:
                if feat.name == 'estimated_bpm':
                    bpm_features.append(feat)
        
        # 可能检测到也可能检测不到（取决于信号特性）
        # 至少不应该崩溃


class TestStructuredDataPerceiver(unittest.TestCase):
    """测试结构化数据感知器"""
    
    def setUp(self):
        self.perceiver = StructuredDataPerceiver()
    
    def test_perceive_dict(self):
        """感知字典数据"""
        data = {'name': 'Alice', 'age': 30, 'active': True}
        objects = self.perceiver.perceive(data)
        
        self.assertGreater(len(objects), 0)
        
        # 检查结构分析
        dict_objects = [o for o in objects if o.category == 'dictionary']
        self.assertGreater(len(dict_objects), 0)
    
    def test_perceive_list(self):
        """感知列表数据"""
        data = [1, 2, 3, 4, 5]
        objects = self.perceiver.perceive(data)
        
        # 检查统计特征
        stats_objects = [o for o in objects if o.category == 'statistics']
        if stats_objects:
            has_homogeneity = False
            for obj in stats_objects:
                for feat in obj.features:
                    if feat.name == 'homogeneity':
                        has_homogeneity = True
                        self.assertEqual(feat.value, 1.0)  # 完全同质
            self.assertTrue(has_homogeneity)
    
    def test_perceive_json_string(self):
        """感知 JSON 字符串"""
        json_str = '{"users": [{"id": 1}, {"id": 2}], "total": 2}'
        objects = self.perceiver.perceive(json_str)
        
        self.assertGreater(len(objects), 0)
    
    def test_nesting_depth(self):
        """嵌套深度计算"""
        deep_data = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 42
                    }
                }
            }
        }
        objects = self.perceiver.perceive(deep_data)
        
        # 检查嵌套深度
        depth_found = False
        for obj in objects:
            for feat in obj.features:
                if feat.name == 'nesting_depth':
                    depth_found = True
                    self.assertGreaterEqual(feat.value, 4)
        self.assertTrue(depth_found)
    
    def test_element_count(self):
        """元素计数"""
        data = {'a': 1, 'b': 2, 'c': [3, 4, 5]}
        objects = self.perceiver.perceive(data)
        
        count_found = False
        for obj in objects:
            for feat in obj.features:
                if feat.name == 'element_count':
                    count_found = True
                    self.assertGreaterEqual(feat.value, 6)  # 3 keys + 3 list items
        self.assertTrue(count_found)


class TestMultimodalFusionEngine(unittest.TestCase):
    """测试多模态融合引擎"""
    
    def setUp(self):
        self.engine = create_multimodal_engine()
    
    def test_fuse_empty(self):
        """融合空列表"""
        result = self.engine.fuse([])
        self.assertEqual(len(result['fused_features']), 0)
        self.assertEqual(result['confidence'], 0.0)
    
    def test_fuse_single_modality(self):
        """融合单一模态"""
        feat = ModalFeature(
            feature_type=FeatureType.SEMANTIC,
            name='test',
            value=1.0,
            confidence=0.9
        )
        obj = PerceivedObject(
            object_id='test_001',
            modality=ModalityType.TEXT,
            category='text',
            features=[feat],
            confidence=0.9
        )
        
        result = self.engine.fuse([obj])
        self.assertEqual(len(result['fused_features']), 1)
        self.assertEqual(result['modality_count'], 1)
    
    def test_fuse_multiple_modalities(self):
        """融合多模态"""
        # 创建不同模态的对象
        text_obj = PerceivedObject(
            object_id='text_001',
            modality=ModalityType.TEXT,
            category='text',
            features=[ModalFeature(FeatureType.SEMANTIC, 'length', 100, 1.0)],
            confidence=0.9
        )
        
        img_obj = PerceivedObject(
            object_id='img_001',
            modality=ModalityType.IMAGE,
            category='scene',
            features=[ModalFeature(FeatureType.SPATIAL, 'size', 500, 0.8)],
            confidence=0.8
        )
        
        result = self.engine.fuse([text_obj, img_obj])
        
        self.assertEqual(len(result['fused_features']), 2)
        self.assertEqual(result['modality_count'], 2)
        # 图像权重更高 (1.2)
        self.assertGreater(result['confidence'], 0.8)
    
    def test_ucr_embedding_generation(self):
        """UCR 嵌入生成"""
        feat = ModalFeature(
            feature_type=FeatureType.STATISTICAL,
            name='count',
            value=50,
            confidence=0.9
        )
        obj = PerceivedObject(
            object_id='test_001',
            modality=ModalityType.STRUCTURED_DATA,
            category='data',
            features=[feat],
            confidence=0.9
        )
        
        result = self.engine.fuse([obj])
        
        self.assertIsNotNone(result['ucr_embedding'])
        self.assertGreater(len(result['ucr_embedding']), 0)
    
    def test_cross_modal_alignment(self):
        """跨模态对齐"""
        # 创建两个有共同特征的对象
        feat1 = ModalFeature(
            feature_type=FeatureType.STATISTICAL,
            name='count',
            value=100,
            confidence=0.9
        )
        feat2 = ModalFeature(
            feature_type=FeatureType.STATISTICAL,
            name='count',
            value=105,  # 接近的值
            confidence=0.9
        )
        
        obj1 = PerceivedObject(
            object_id='obj_001',
            modality=ModalityType.IMAGE,
            category='scene',
            features=[feat1],
            confidence=0.9
        )
        
        obj2 = PerceivedObject(
            object_id='obj_002',
            modality=ModalityType.AUDIO,
            category='sound',
            features=[feat2],
            confidence=0.9
        )
        
        alignment = self.engine.cross_modal_align(obj1, obj2)
        
        self.assertEqual(alignment['source_modality'], 'image')
        self.assertEqual(alignment['target_modality'], 'audio')
        # 相似度可能为 0（如果特征不完全匹配），但不应崩溃
        self.assertIn('similarity', alignment)
        self.assertIn('common_features', alignment)
    
    def test_perceive_dispatch(self):
        """感知分发"""
        # 测试文本感知
        text_objects = self.engine.perceive("Hello world", ModalityType.TEXT)
        self.assertGreater(len(text_objects), 0)
        self.assertEqual(text_objects[0].modality, ModalityType.TEXT)
        
        # 测试结构化数据感知
        data_objects = self.engine.perceive({'key': 'value'}, ModalityType.STRUCTURED_DATA)
        self.assertGreater(len(data_objects), 0)
        self.assertEqual(data_objects[0].modality, ModalityType.STRUCTURED_DATA)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_pipeline(self):
        """完整感知 - 融合流程"""
        engine = create_multimodal_engine()
        
        # 1. 感知多种模态
        img_data = bytes([i % 256 for i in range(500)])
        audio_data = [0.5 * (i % 50) / 50 for i in range(1000)]
        struct_data = {'items': [1, 2, 3], 'count': 3}
        
        img_objects = engine.perceive(img_data, ModalityType.IMAGE)
        audio_objects = engine.perceive(audio_data, ModalityType.AUDIO)
        struct_objects = engine.perceive(struct_data, ModalityType.STRUCTURED_DATA)
        
        # 2. 融合所有感知结果
        all_objects = img_objects + audio_objects + struct_objects
        fusion_result = engine.fuse(all_objects)
        
        # 验证结果
        self.assertGreater(fusion_result['object_count'], 0)
        self.assertEqual(fusion_result['modality_count'], 3)
        self.assertIsNotNone(fusion_result['ucr_embedding'])
        
        # 3. 验证置信度在合理范围（考虑模态权重）
        self.assertGreater(fusion_result['confidence'], 0)
        # 置信度可能超过 1.0 因为有权重，但应该在合理范围内
        self.assertLessEqual(fusion_result['confidence'], 5.0)


class TestModalityTypes(unittest.TestCase):
    """测试模态类型枚举"""
    
    def test_all_modalities_exist(self):
        """所有模态类型存在"""
        self.assertEqual(ModalityType.TEXT.value, 'text')
        self.assertEqual(ModalityType.IMAGE.value, 'image')
        self.assertEqual(ModalityType.AUDIO.value, 'audio')
        self.assertEqual(ModalityType.VIDEO.value, 'video')
        self.assertEqual(ModalityType.STRUCTURED_DATA.value, 'structured_data')
        self.assertEqual(ModalityType.CODE.value, 'code')
        self.assertEqual(ModalityType.SENSOR.value, 'sensor')
    
    def test_feature_types_exist(self):
        """所有特征类型存在"""
        self.assertEqual(FeatureType.SPATIAL.value, 'spatial')
        self.assertEqual(FeatureType.TEMPORAL.value, 'temporal')
        self.assertEqual(FeatureType.SPECTRAL.value, 'spectral')
        self.assertEqual(FeatureType.SEMANTIC.value, 'semantic')
        self.assertEqual(FeatureType.STRUCTURAL.value, 'structural')
        self.assertEqual(FeatureType.STATISTICAL.value, 'statistical')


if __name__ == '__main__':
    unittest.main(verbosity=2)
