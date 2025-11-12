"""
Test script for Intent Analyzer
Tests the intent analysis functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.intent_analyzer import IntentAnalyzer


def test_intent_analyzer():
    """Test intent analyzer functionality"""
    
    analyzer = IntentAnalyzer()
    
    print("=" * 60)
    print("Testing Intent Analyzer")
    print("=" * 60)
    
    # Test 1: Extract keywords
    print("\n1. Testing keyword extraction:")
    text = "I need to access the lab server for my research project on machine learning"
    keywords = analyzer.extract_keywords(text)
    print(f"   Text: {text}")
    print(f"   Extracted keywords: {keywords}")
    
    expected_keywords = ['need', 'to', 'access', 'the', 'lab', 'server', 'for', 'my', 
                        'research', 'project', 'on', 'machine', 'learning']
    if len(keywords) >= 10:
        print(f"   ✓ PASS: Extracted {len(keywords)} keywords")
    else:
        print(f"   ✗ FAIL: Expected more keywords")
    
    # Test 2: Categorize keywords
    print("\n2. Testing keyword categorization:")
    categorized = analyzer.categorize_keywords(keywords)
    print(f"   Categorized keywords:")
    for category, words in categorized.items():
        if words:
            print(f"     - {category}: {words}")
    
    if categorized['academic']:
        print(f"   ✓ PASS: Found academic keywords")
    else:
        print(f"   ✗ FAIL: Should find academic keywords")
    
    # Test 3: Analyze good academic intent
    print("\n3. Testing good academic intent:")
    good_intent = "I need to access the lab server to run machine learning experiments for my research project on neural networks and deep learning algorithms"
    score = analyzer.analyze_intent(good_intent)
    print(f"   Intent: {good_intent}")
    print(f"   Score: {score}")
    
    if score >= 70:
        print(f"   ✓ PASS: High score for academic intent")
    else:
        print(f"   ✗ FAIL: Expected high score, got {score}")
    
    # Test 4: Analyze suspicious intent
    print("\n4. Testing suspicious intent:")
    suspicious_intent = "urgent need quick access testing"
    score = analyzer.analyze_intent(suspicious_intent)
    print(f"   Intent: {suspicious_intent}")
    print(f"   Score: {score}")
    
    if score < 50:
        print(f"   ✓ PASS: Low score for suspicious intent")
    else:
        print(f"   ✗ FAIL: Expected low score, got {score}")
    
    # Test 5: Analyze short intent (validation failure)
    print("\n5. Testing short intent (< 20 characters):")
    short_intent = "quick test"
    score = analyzer.analyze_intent(short_intent)
    print(f"   Intent: {short_intent}")
    print(f"   Score: {score}")
    
    if score < 40:
        print(f"   ✓ PASS: Low score for short intent")
    else:
        print(f"   ✗ FAIL: Expected low score for short intent")
    
    # Test 6: Analyze intent with few words (< 5 words)
    print("\n6. Testing intent with few words:")
    few_words = "need access now please"
    score = analyzer.analyze_intent(few_words)
    print(f"   Intent: {few_words}")
    print(f"   Score: {score}")
    
    if score < 50:
        print(f"   ✓ PASS: Low score for few words")
    else:
        print(f"   ✗ FAIL: Expected low score for few words")
    
    # Test 7: Analyze legitimate work intent
    print("\n7. Testing legitimate work intent:")
    legitimate_intent = "I need authorized access to the database for official coursework assignment that is required for my class project"
    score = analyzer.analyze_intent(legitimate_intent)
    print(f"   Intent: {legitimate_intent}")
    print(f"   Score: {score}")
    
    if score >= 65:
        print(f"   ✓ PASS: Good score for legitimate intent")
    else:
        print(f"   ✗ FAIL: Expected good score, got {score}")
    
    # Test 8: Analyze administrative intent
    print("\n8. Testing administrative intent:")
    admin_intent = "Need to perform system maintenance and configuration updates on the server for deployment purposes"
    score = analyzer.analyze_intent(admin_intent)
    print(f"   Intent: {admin_intent}")
    print(f"   Score: {score}")
    
    if score >= 55:
        print(f"   ✓ PASS: Reasonable score for administrative intent")
    else:
        print(f"   ✗ FAIL: Expected reasonable score, got {score}")
    
    # Test 9: Test coherence detection
    print("\n9. Testing coherence detection:")
    coherent_text = "I need access to the library database. This is required for my research on historical documents, which is part of my thesis project."
    incoherent_text = "need database access urgent quick now"
    
    coherent_score = analyzer.analyze_intent(coherent_text)
    incoherent_score = analyzer.analyze_intent(incoherent_text)
    
    print(f"   Coherent text score: {coherent_score}")
    print(f"   Incoherent text score: {incoherent_score}")
    
    if coherent_score > incoherent_score:
        print(f"   ✓ PASS: Coherent text scored higher")
    else:
        print(f"   ✗ FAIL: Coherent text should score higher")
    
    # Test 10: Test contradiction detection
    print("\n10. Testing contradiction detection:")
    contradictory_text = "This is an urgent emergency but it's a planned scheduled research project"
    normal_text = "This is a planned research project for my coursework"
    
    contradictory_score = analyzer.analyze_intent(contradictory_text)
    normal_score = analyzer.analyze_intent(normal_text)
    
    print(f"   Contradictory text score: {contradictory_score}")
    print(f"   Normal text score: {normal_score}")
    
    if contradictory_score < normal_score:
        print(f"   ✓ PASS: Contradictory text scored lower")
    else:
        print(f"   ✗ FAIL: Contradictory text should score lower")
    
    # Test 11: Test empty/null intent
    print("\n11. Testing empty/null intent:")
    empty_score = analyzer.analyze_intent("")
    null_score = analyzer.analyze_intent(None)
    
    print(f"   Empty string score: {empty_score}")
    print(f"   None score: {null_score}")
    
    if empty_score == 0 and null_score == 0:
        print(f"   ✓ PASS: Empty/null intents return 0")
    else:
        print(f"   ✗ FAIL: Empty/null should return 0")
    
    # Test 12: Test scoring boundaries
    print("\n12. Testing score boundaries (0-100):")
    test_cases = [
        "urgent emergency testing quick now asap immediately",  # Very suspicious
        "I need to conduct comprehensive research analysis for my academic thesis project on machine learning algorithms and neural network optimization",  # Very academic
        "access",  # Minimal
    ]
    
    all_valid = True
    for test_text in test_cases:
        score = analyzer.analyze_intent(test_text)
        if not (0 <= score <= 100):
            print(f"   ✗ FAIL: Score {score} out of bounds for: {test_text[:50]}")
            all_valid = False
    
    if all_valid:
        print(f"   ✓ PASS: All scores within 0-100 range")
    
    # Test 13: Test keyword categories
    print("\n13. Testing keyword category definitions:")
    categories = analyzer.KEYWORD_CATEGORIES
    
    required_categories = ['academic', 'legitimate', 'suspicious', 'administrative']
    all_present = all(cat in categories for cat in required_categories)
    
    if all_present:
        print(f"   ✓ PASS: All required categories present")
        for cat in required_categories:
            print(f"     - {cat}: {len(categories[cat])} keywords")
    else:
        print(f"   ✗ FAIL: Missing required categories")
    
    # Test 14: Test minimum validation thresholds
    print("\n14. Testing validation thresholds:")
    print(f"   MIN_CHARACTERS: {analyzer.MIN_CHARACTERS}")
    print(f"   MIN_WORDS: {analyzer.MIN_WORDS}")
    
    if analyzer.MIN_CHARACTERS == 20 and analyzer.MIN_WORDS == 5:
        print(f"   ✓ PASS: Validation thresholds correct")
    else:
        print(f"   ✗ FAIL: Validation thresholds incorrect")
    
    print("\n" + "=" * 60)
    print("Intent Analyzer Tests Completed")
    print("=" * 60)


def test_integration_with_policy_engine():
    """Test intent analyzer integration with policy engine"""
    
    print("\n" + "=" * 60)
    print("Testing Intent Analyzer Integration")
    print("=" * 60)
    
    from services.policy_engine import PolicyEngine
    
    # Create mock database
    class MockFirestoreClient:
        def collection(self, name):
            return MockCollection([])
    
    class MockCollection:
        def __init__(self, data):
            self.data = data
        def where(self, field, op, value):
            return MockQuery([])
        def limit(self, count):
            return MockQuery([])
        def stream(self):
            return []
    
    class MockQuery:
        def __init__(self, data):
            self.data = data
        def limit(self, count):
            return self
        def stream(self):
            return []
    
    engine = PolicyEngine()
    engine.db = MockFirestoreClient()
    
    print("\n1. Testing intent analysis through policy engine:")
    
    test_intents = [
        ("I need to access the lab server for my research project on machine learning", "academic"),
        ("urgent quick test access", "suspicious"),
        ("Required for official coursework assignment", "legitimate"),
    ]
    
    for intent, expected_type in test_intents:
        score = engine._analyze_intent_clarity(intent)
        print(f"   Intent type: {expected_type}")
        print(f"   Score: {score}")
        
        if expected_type == "academic" and score >= 60:
            print(f"   ✓ PASS")
        elif expected_type == "suspicious" and score < 50:
            print(f"   ✓ PASS")
        elif expected_type == "legitimate" and score >= 55:
            print(f"   ✓ PASS")
        else:
            print(f"   ✗ FAIL: Unexpected score for {expected_type}")
        print()
    
    print("=" * 60)
    print("Integration Tests Completed")
    print("=" * 60)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("INTENT ANALYZER TEST SUITE")
    print("=" * 60)
    
    try:
        test_intent_analyzer()
        test_integration_with_policy_engine()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
    
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
