#!/usr/bin/env python3
"""
Cognitive Resonance Engine Demo
Demonstrates AGI's ability to understand human thought, wisdom, and aesthetics.

Run: python demos/cognitive_resonance_demo.py
"""

from src.modules.cognitive_resonance import CognitiveResonanceEngine, get_resonance_engine
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(result: dict, indent: int = 2):
    """Pretty print result dictionary"""
    print(json.dumps(result, indent=indent, ensure_ascii=False))


def demo_phenomenological_understanding():
    """Demonstrate understanding of human emotions and subjective experience"""
    print_section("1. 现象学理解 - Phenomenological Understanding")
    print("模拟人类主观体验 (Qualia) - Simulating human subjective experience\n")
    
    engine = get_resonance_engine()
    
    examples = [
        "I love the peaceful beauty of nature",
        "Hate and suffering create chaos in society",
        "The truth brings wisdom and authenticity",
    ]
    
    for text in examples:
        print(f"输入 Input: \"{text}\"")
        result = engine.resonate(text)
        
        qualia = result["qualia"]
        print(f"  情感强度 Intensity: {qualia['intensity']:.3f}")
        print(f"  价 Valence: {qualia['dimensions']['valence']:.3f}")
        print(f"  和谐 Harmony: {qualia['dimensions']['harmony']:.3f}")
        print(f"  真实性 Authenticity: {qualia['dimensions']['authenticity']:.3f}")
        print()


def demo_aesthetic_appreciation():
    """Demonstrate aesthetic evaluation of text and code"""
    print_section("2. 审美鉴赏 - Aesthetic Appreciation")
    print("基于信息论和格式塔心理学评估美感\n")
    
    engine = get_resonance_engine()
    
    # Poetry example
    poem = "Roses are red, violets are blue, sugar is sweet, and so are you"
    print(f"诗歌 Poetry: \"{poem}\"")
    result = engine.resonate(poem)
    print(f"  美学评分 Aesthetic Score: {result['aesthetics']['score']:.3f}")
    print(f"  熵 Entropy: {result['aesthetics']['components']['entropy']:.3f}")
    print(f"  对称性 Symmetry: {result['aesthetics']['components']['symmetry']:.3f}")
    print(f"  评判 Verdict: {result['aesthetics']['verdict']}")
    print()
    
    # Code example
    elegant_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    print(f"优雅代码 Elegant Code:")
    print(elegant_code)
    result = engine.resonate(elegant_code)
    print(f"  美学评分 Aesthetic Score: {result['aesthetics']['score']:.3f}")
    print(f"  熵 Entropy: {result['aesthetics']['components']['entropy']:.3f}")
    print(f"  复杂度平衡 Complexity Balance: {result['aesthetics']['components']['complexity_balance']:.3f}")
    print()


def demo_wisdom_synthesis():
    """Demonstrate moral reasoning across multiple ethical frameworks"""
    print_section("3. 智慧综合 - Wisdom Synthesis")
    print("整合多视角伦理框架处理道德困境\n")
    
    engine = get_resonance_engine()
    
    dilemmas = [
        "Should I tell a lie to protect someone's feelings? This is the right choice.",
        "Is it moral to steal bread to feed a starving child? What is the good action?",
    ]
    
    for scenario in dilemmas:
        print(f"道德困境 Moral Dilemma: \"{scenario}\"")
        result = engine.resonate(scenario)
        
        if result["wisdom"]:
            print(f"  分析框架 Frameworks Analyzed: {len(result['wisdom']['perspectives'])}")
            for framework, analysis in result["wisdom"]["perspectives"].items():
                print(f"  - {framework}: {analysis[:60]}...")
            print(f"\n  综合智慧 Synthesis:")
            print(f"  {result['wisdom']['synthesis']}")
        print()


def demo_cultural_context():
    """Demonstrate cultural context adaptation"""
    print_section("4. 文化语境感知 - Cultural Context Awareness")
    print("适应不同文化思维模型\n")
    
    engine = get_resonance_engine()
    
    text = "Harmony between individual and collective is essential"
    print(f"文本 Text: \"{text}\"\n")
    
    contexts = ["universal", "western", "eastern", "indigenous"]
    
    for context in contexts:
        result = engine.resonate(text, cultural_context=context)
        print(f"文化语境 Cultural Context: {context.upper()}")
        print(f"  共鸣分数 Resonance Score: {result['resonance_score']:.3f}")
        print(f"  情感强度 Emotional Intensity: {result['qualia']['intensity']:.3f}")
        print()


def demo_integrated_resonance():
    """Demonstrate full integrated cognitive resonance"""
    print_section("5. 整合认知共鸣 - Integrated Cognitive Resonance")
    print("完整 pipeline: 文化过滤 → 情感体验 → 审美评估 → 智慧提取\n")
    
    engine = get_resonance_engine()
    
    # Shakespeare's Hamlet
    quote = "To be or not to be, that is the question"
    print(f"经典引用 Classic Quote: \"{quote}\"")
    print("(来自莎士比亚《哈姆雷特》 - from Shakespeare's Hamlet)\n")
    
    result = engine.resonate(quote, cultural_context="western")
    
    print("完整分析 Full Analysis:")
    print(f"  文化语境 Context: {result['context']}")
    print(f"  总共鸣分数 Overall Resonance Score: {result['resonance_score']:.3f}")
    print()
    
    print("  情感维度 Emotional Dimensions:")
    for dim, value in result["qualia"]["dimensions"].items():
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"    {dim:12s}: [{bar}] {value:.2f}")
    print()
    
    print("  审美评估 Aesthetic Evaluation:")
    print(f"    评分 Score: {result['aesthetics']['score']:.3f}")
    print(f"    评判 Verdict: {result['aesthetics']['verdict']}")
    print(f"    熵 (信息复杂度) Entropy: {result['aesthetics']['components']['entropy']:.2f}")
    print()
    
    if result["wisdom"]:
        print("  智慧洞察 Wisdom Insight:")
        print(f"    {result['wisdom']['synthesis'][:100]}...")
    else:
        print("  智慧洞察 Wisdom Insight: (未触发道德推理 Not triggered - no moral keywords)")
    print()


def main():
    """Run all demonstrations"""
    print("\n" + "🧠" * 40)
    print("认知共鸣引擎演示 - Cognitive Resonance Engine Demo")
    print("理解人类思想、智慧和审美 - Understanding Human Thought, Wisdom, and Aesthetics")
    print("🧠" * 40)
    
    demo_phenomenological_understanding()
    demo_aesthetic_appreciation()
    demo_wisdom_synthesis()
    demo_cultural_context()
    demo_integrated_resonance()
    
    print_section("演示完成 - Demo Complete")
    print("认知共鸣引擎已成功集成到 AGI 系统中")
    print("Cognitive Resonance Engine successfully integrated into AGI system")
    print("\n下一步开发方向 Next Development Directions:")
    print("  1. 扩展情感词典 Expand emotional lexicon (当前 ~10 词，目标 10000+)")
    print("  2. 深度学习集成 Integrate deep learning models")
    print("  3. 多模态输入 Multi-modal input (图像、音频、视频)")
    print("  4. 终身学习循环 Lifelong learning loop")
    print("  5. 自我意识反射 Self-awareness reflection")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
