"""
Intent Analyzer
Analyzes natural language intent descriptions for legitimacy indicators
"""

import re
from typing import Dict, List, Tuple


class IntentAnalyzer:
    """Analyzer for evaluating intent descriptions in access requests"""
    
    # Keyword categories with associated keywords
    KEYWORD_CATEGORIES = {
        'academic': [
            'research', 'study', 'assignment', 'project', 'thesis',
            'coursework', 'homework', 'lab', 'experiment', 'analysis',
            'dissertation', 'paper', 'report', 'presentation', 'learning',
            'education', 'academic', 'course', 'class', 'lecture',
            'seminar', 'workshop', 'tutorial', 'exam', 'test'
        ],
        'legitimate': [
            'work', 'official', 'authorized', 'required', 'approved',
            'necessary', 'needed', 'essential', 'important', 'critical',
            'scheduled', 'planned', 'assigned', 'designated', 'allocated'
        ],
        'suspicious': [
            'urgent', 'emergency', 'testing', 'temporary', 'quick',
            'just', 'trying', 'check', 'test', 'asap', 'immediately',
            'hurry', 'fast', 'now', 'right now', 'quickly'
        ],
        'administrative': [
            'configuration', 'setup', 'maintenance', 'deployment',
            'installation', 'update', 'upgrade', 'administration',
            'management', 'monitoring', 'backup', 'restore'
        ]
    }
    
    # Scoring weights
    SCORE_BASE = 50
    SCORE_ACADEMIC = 20
    SCORE_LEGITIMATE = 15
    SCORE_SUSPICIOUS = -15
    SCORE_ADMINISTRATIVE = 10
    SCORE_LENGTH_PENALTY = -20
    SCORE_WORD_COUNT_PENALTY = -20
    SCORE_COHERENCE_BONUS = 10
    SCORE_CONTRADICTION_PENALTY = -25
    
    # Validation thresholds
    MIN_CHARACTERS = 20
    MIN_WORDS = 5
    
    def analyze_intent(self, intent_text: str) -> float:
        """
        Analyze intent description and return clarity score
        
        Args:
            intent_text (str): The intent description to analyze
        
        Returns:
            float: Intent clarity score (0-100)
        """
        if not intent_text or not isinstance(intent_text, str):
            return 0
        
        # Start with base score
        score = self.SCORE_BASE
        
        # Validate minimum requirements
        if len(intent_text) < self.MIN_CHARACTERS:
            score += self.SCORE_LENGTH_PENALTY
        
        words = self._extract_words(intent_text)
        if len(words) < self.MIN_WORDS:
            score += self.SCORE_WORD_COUNT_PENALTY
        
        # Extract and categorize keywords
        keywords = self.extract_keywords(intent_text)
        categorized = self.categorize_keywords(keywords)
        
        # Apply scoring based on keyword categories
        if categorized['academic']:
            # Cap academic bonus at SCORE_ACADEMIC
            academic_bonus = min(len(categorized['academic']) * 10, self.SCORE_ACADEMIC)
            score += academic_bonus
        
        if categorized['legitimate']:
            # Cap legitimate bonus at SCORE_LEGITIMATE
            legitimate_bonus = min(len(categorized['legitimate']) * 8, self.SCORE_LEGITIMATE)
            score += legitimate_bonus
        
        if categorized['suspicious']:
            # Apply suspicious penalty
            suspicious_penalty = min(len(categorized['suspicious']) * 8, abs(self.SCORE_SUSPICIOUS))
            score -= suspicious_penalty
        
        if categorized['administrative']:
            # Small bonus for administrative keywords
            admin_bonus = min(len(categorized['administrative']) * 5, self.SCORE_ADMINISTRATIVE)
            score += admin_bonus
        
        # Check for coherence indicators
        if self._has_coherence_indicators(intent_text):
            score += self.SCORE_COHERENCE_BONUS
        
        # Check for contradictions
        if self._detect_contradictions(intent_text, categorized):
            score += self.SCORE_CONTRADICTION_PENALTY
        
        # Ensure score is within valid range
        return max(0, min(100, score))
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text using regex tokenization
        
        Args:
            text (str): Text to extract keywords from
        
        Returns:
            list: List of extracted keywords (lowercase)
        """
        if not text:
            return []
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Tokenize using regex: extract words (alphanumeric sequences)
        # Pattern matches words with optional hyphens and apostrophes
        pattern = r'\b[a-z]+(?:[-\'][a-z]+)*\b'
        tokens = re.findall(pattern, text_lower)
        
        # Remove very short tokens (less than 2 characters)
        keywords = [token for token in tokens if len(token) >= 2]
        
        return keywords
    
    def categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Map keywords to their respective categories
        
        Args:
            keywords (list): List of keywords to categorize
        
        Returns:
            dict: Dictionary mapping category names to matched keywords
        """
        categorized = {
            'academic': [],
            'legitimate': [],
            'suspicious': [],
            'administrative': []
        }
        
        if not keywords:
            return categorized
        
        # Create a set of keywords for faster lookup
        keyword_set = set(keywords)
        
        # Check each category
        for category, category_keywords in self.KEYWORD_CATEGORIES.items():
            for keyword in category_keywords:
                # Check for exact match or if keyword appears in the text
                if keyword in keyword_set:
                    categorized[category].append(keyword)
                else:
                    # Check for partial matches (e.g., "researching" contains "research")
                    for kw in keywords:
                        if keyword in kw or kw in keyword:
                            if keyword not in categorized[category]:
                                categorized[category].append(keyword)
                            break
        
        return categorized
    
    def _extract_words(self, text: str) -> List[str]:
        """
        Extract words from text for word count validation
        
        Args:
            text (str): Text to extract words from
        
        Returns:
            list: List of words
        """
        if not text:
            return []
        
        # Split by whitespace and filter out empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        return words
    
    def _has_coherence_indicators(self, text: str) -> bool:
        """
        Check if text has indicators of coherent, well-structured writing
        
        Args:
            text (str): Text to analyze
        
        Returns:
            bool: True if text appears coherent
        """
        if not text:
            return False
        
        coherence_indicators = 0
        
        # Check for proper punctuation
        if '.' in text or ',' in text:
            coherence_indicators += 1
        
        # Check for proper sentence structure (capital letter at start)
        if text[0].isupper():
            coherence_indicators += 1
        
        # Check for reasonable sentence length (not just one long run-on)
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 1:
            coherence_indicators += 1
        
        # Check for connecting words that indicate structured thought
        connecting_words = ['because', 'therefore', 'however', 'additionally', 
                          'furthermore', 'moreover', 'thus', 'hence', 'so that',
                          'in order to', 'for', 'to']
        text_lower = text.lower()
        if any(word in text_lower for word in connecting_words):
            coherence_indicators += 1
        
        # Consider text coherent if it has at least 2 indicators
        return coherence_indicators >= 2
    
    def _detect_contradictions(
        self, 
        text: str, 
        categorized: Dict[str, List[str]]
    ) -> bool:
        """
        Detect contradictory information in the intent description
        
        Args:
            text (str): Intent text
            categorized (dict): Categorized keywords
        
        Returns:
            bool: True if contradictions detected
        """
        if not text:
            return False
        
        # Check for contradictory keyword combinations
        # Suspicious + Academic might indicate false legitimacy
        has_suspicious = len(categorized.get('suspicious', [])) > 0
        has_academic = len(categorized.get('academic', [])) > 0
        
        # If both suspicious and academic keywords are present in high numbers
        if has_suspicious and has_academic:
            if len(categorized['suspicious']) >= 2 and len(categorized['academic']) >= 2:
                return True
        
        # Check for contradictory phrases
        text_lower = text.lower()
        contradictory_patterns = [
            ('urgent', 'planned'),
            ('emergency', 'scheduled'),
            ('temporary', 'long-term'),
            ('testing', 'production'),
            ('just checking', 'critical'),
            ('quick test', 'important project')
        ]
        
        for pattern1, pattern2 in contradictory_patterns:
            if pattern1 in text_lower and pattern2 in text_lower:
                return True
        
        # Check for vague + urgent combination (red flag)
        vague_indicators = ['just', 'trying', 'check', 'test', 'see']
        urgent_indicators = ['urgent', 'emergency', 'asap', 'immediately', 'now']
        
        has_vague = any(indicator in text_lower for indicator in vague_indicators)
        has_urgent = any(indicator in text_lower for indicator in urgent_indicators)
        
        if has_vague and has_urgent:
            return True
        
        return False


# Singleton instance
intent_analyzer = IntentAnalyzer()
