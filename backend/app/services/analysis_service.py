# file: app/services/analysis_service.py

import re
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from functools import lru_cache, wraps
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, Counter
import time

logger = logging.getLogger(__name__)

class SentimentType(Enum):
    """Enum for sentiment types with numeric values for processing."""
    POSITIVE = "Positive"
    NEGATIVE = "Negative" 
    NEUTRAL = "Neutral"
    MIXED = "Mixed"

class ComplexityLevel(Enum):
    """Enum for complexity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXPERT = "Expert"

@dataclass
class AnalysisResult:
    """Enhanced structured result container with semantic meaning and metadata."""
    sentiment: SentimentType
    confidence: float
    keywords: List[str]
    complexity_score: float
    semantic_density: float
    cognitive_load: int
    linguistic_features: Dict[str, Any]
    reasoning_cues: List[str]
    
    # Enhanced fields for layered reasoning
    conceptual_clusters: List[Dict[str, Any]] = field(default_factory=list)
    argumentation_structure: Dict[str, Any] = field(default_factory=dict)
    coherence_metrics: Dict[str, float] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize results after initialization."""
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.complexity_score = max(0.0, min(1.0, self.complexity_score))
        self.semantic_density = max(0.0, min(1.0, self.semantic_density))
        self.cognitive_load = max(1, min(10, self.cognitive_load))

def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        execution_time = time.time() - start_time
        if hasattr(self, '_performance_metrics'):
            self._performance_metrics[func.__name__] = execution_time
        return result
    return wrapper

class IntelligentTextAnalyzer:
    """
    Enhanced sophisticated text analysis engine with improved efficiency,
    robustness, and intelligence for layered reasoning systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with configurable parameters for flexibility."""
        config = config or {}
        
        # Performance tracking
        self._performance_metrics = {}
        self._cache_stats = defaultdict(int)
        self._thread_local = threading.local()
        
        # Enhanced core analyzers with better configuration
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Configurable TF-IDF parameters
        tfidf_config = config.get('tfidf', {})
        self.keyword_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=tfidf_config.get('max_features', 100),
            ngram_range=tfidf_config.get('ngram_range', (1, 3)),  # Include trigrams
            min_df=tfidf_config.get('min_df', 1),
            max_df=tfidf_config.get('max_df', 0.8),
            sublinear_tf=True,  # Use log scaling for better performance
            smooth_idf=True     # Smooth IDF weights
        )
        
        # Enhanced reasoning pattern matchers with scoring
        self.reasoning_patterns = {
            'causal': {
                'patterns': [
                    r'\b(because|since|due to|as a result|therefore|thus|hence|consequently|leads to|causes?|results? in)\b',
                    r'\b(stems from|originates from|attributable to|owes to)\b'
                ],
                'weight': 1.0
            },
            'conditional': {
                'patterns': [
                    r'\b(if|unless|provided|assuming|given that|suppose|in case|should)\b',
                    r'\b(contingent upon|depends on|conditional on)\b'
                ],
                'weight': 0.9
            },
            'comparative': {
                'patterns': [
                    r'\b(better|worse|more|less|compared to|versus|rather than|instead of|superior|inferior)\b',
                    r'\b(in contrast|on the other hand|alternatively|conversely)\b'
                ],
                'weight': 0.8
            },
            'temporal': {
                'patterns': [
                    r'\b(before|after|during|while|when|then|next|finally|subsequently|previously|initially)\b',
                    r'\b(simultaneously|concurrently|thereafter|beforehand)\b'
                ],
                'weight': 0.7
            },
            'evidential': {
                'patterns': [
                    r'\b(evidence|proof|data|research|studies|findings|demonstrates?|shows?|indicates?|suggests?)\b',
                    r'\b(according to|based on|research shows|studies indicate)\b'
                ],
                'weight': 1.2  # Higher weight for evidence-based reasoning
            },
            'uncertainty': {
                'patterns': [
                    r'\b(might|could|possibly|perhaps|likely|probably|seems?|appears?|presumably|allegedly)\b',
                    r'\b(potentially|conceivably|ostensibly|supposedly)\b'
                ],
                'weight': 0.6
            },
            'emphasis': {
                'patterns': [
                    r'\b(crucial|critical|essential|vital|important|significant|fundamental|paramount)\b',
                    r'\b(notably|particularly|especially|remarkably|strikingly)\b'
                ],
                'weight': 0.9
            },
            'logical_structure': {
                'patterns': [
                    r'\b(furthermore|moreover|additionally|also|likewise|similarly)\b',
                    r'\b(however|nevertheless|nonetheless|although|despite|whereas)\b',
                    r'\b(first|second|third|finally|in conclusion|to summarize)\b'
                ],
                'weight': 1.0
            }
        }
        
        # Enhanced complexity indicators with weights
        self.complexity_indicators = [
            (r'\b\w{10,}\b', 2.0),  # Very long words
            (r'\b\w{8,9}\b', 1.5),  # Long words
            (r'[;:]', 1.2),         # Complex punctuation
            (r'\b(however|nevertheless|furthermore|moreover|consequently|notwithstanding)\b', 1.8),
            (r'\([^)]{10,}\)', 1.5), # Long parenthetical information
            (r'\"[^\"]{20,}\"', 1.3), # Long quoted material
            (r'\b(which|that|who|whom|whose|where|when|why)\b.*?\b(which|that|who|whom|whose|where|when|why)\b', 2.0), # Nested relative clauses
        ]
        
        # Conceptual clustering keywords for enhanced analysis
        self.concept_categories = {
            'technical': ['algorithm', 'system', 'process', 'method', 'technique', 'implementation', 'framework', 'architecture'],
            'analytical': ['analysis', 'evaluation', 'assessment', 'examination', 'investigation', 'study', 'research'],
            'emotional': ['feeling', 'emotion', 'sentiment', 'mood', 'attitude', 'reaction', 'response'],
            'logical': ['logic', 'reasoning', 'argument', 'conclusion', 'inference', 'deduction', 'proof'],
            'temporal': ['time', 'sequence', 'order', 'progression', 'timeline', 'chronology', 'duration'],
            'causal': ['cause', 'effect', 'reason', 'result', 'consequence', 'outcome', 'impact']
        }

    @timing_decorator
    @lru_cache(maxsize=256)
    def _calculate_semantic_density(self, text: str) -> float:
        """
        Enhanced semantic density calculation with better linguistic understanding.
        """
        if not text.strip():
            return 0.0
            
        # Tokenize with better word boundary detection
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        if not words:
            return 0.0
        
        # Expanded function words set with linguistic categories
        function_words = {
            # Articles
            'the', 'a', 'an',
            # Conjunctions
            'and', 'or', 'but', 'nor', 'for', 'so', 'yet',
            # Prepositions
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'who', 'what', 'where', 'when', 'why', 'how',
            # Auxiliary verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            # Common adverbs
            'not', 'no', 'yes', 'very', 'too', 'also', 'just', 'only', 'even', 'still', 'well', 'quite', 'rather', 'really', 'much', 'many', 'more', 'most', 'less', 'least', 'all', 'any', 'some', 'few', 'little', 'each', 'every', 'both', 'either', 'neither', 'other', 'another', 'such', 'same', 'different'
        }
        
        # Calculate content word ratio with length weighting
        content_words = []
        for word in words:
            if word not in function_words:
                # Weight longer words more heavily (they typically carry more semantic content)
                weight = min(len(word) / 6, 2.0)  # Cap weight at 2.0
                content_words.extend([word] * int(weight))
        
        return len(content_words) / len(words) if words else 0.0

    @timing_decorator
    def _extract_reasoning_cues(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """
        Enhanced reasoning cue extraction with confidence scoring.
        Returns both cue types and their confidence scores.
        """
        cues = []
        cue_scores = {}
        text_lower = text.lower()
        
        for pattern_type, pattern_data in self.reasoning_patterns.items():
            patterns = pattern_data['patterns']
            weight = pattern_data['weight']
            
            total_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                total_matches += matches
            
            if total_matches > 0:
                cues.append(pattern_type)
                # Normalize score based on text length and pattern frequency
                text_length = len(text.split())
                normalized_score = min((total_matches / max(text_length / 20, 1)) * weight, 1.0)
                cue_scores[pattern_type] = round(normalized_score, 3)
        
        return cues, cue_scores

    @timing_decorator
    def _calculate_complexity_score(self, text: str) -> float:
        """
        Enhanced multi-dimensional complexity scoring with better normalization.
        """
        if not text.strip():
            return 0.0
        
        # Sentence analysis
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if not sentences:
            return 0.0
        
        # Enhanced sentence complexity metrics
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = np.mean(sentence_lengths)
        sentence_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        # Vocabulary sophistication with better handling
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
            
        avg_word_length = np.mean([len(w) for w in words])
        unique_word_ratio = len(set(words)) / len(words)
        
        # Weighted syntactic complexity
        total_complexity = 0
        text_length = len(words)
        
        for pattern, weight in self.complexity_indicators:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                complexity_contribution = (matches / text_length) * weight
                total_complexity += complexity_contribution
        
        # Normalize components
        sentence_complexity = min(avg_sentence_length / 25, 1.0) * 0.3
        variance_complexity = min(sentence_variance / 50, 1.0) * 0.2
        vocab_complexity = min((avg_word_length - 3) / 7, 1.0) * 0.2
        diversity_complexity = unique_word_ratio * 0.1
        syntax_complexity = min(total_complexity, 1.0) * 0.2
        
        final_score = sentence_complexity + variance_complexity + vocab_complexity + diversity_complexity + syntax_complexity
        return min(final_score, 1.0)

    @timing_decorator
    def _calculate_cognitive_load(self, text: str, complexity_score: float, reasoning_cues: List[str]) -> int:
        """
        Enhanced cognitive load calculation considering multiple factors.
        """
        word_count = len(text.split())
        sentence_count = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        
        # Base load from text metrics
        if word_count < 15:
            base_load = 1
        elif word_count < 40:
            base_load = 2
        elif word_count < 80:
            base_load = 4
        elif word_count < 150:
            base_load = 6
        elif word_count < 250:
            base_load = 8
        else:
            base_load = 9
        
        # Adjustments
        complexity_adjustment = complexity_score * 2
        reasoning_adjustment = len(reasoning_cues) * 0.3
        sentence_density = word_count / max(sentence_count, 1)
        density_adjustment = min(sentence_density / 20, 1.0)
        
        total_load = base_load + complexity_adjustment + reasoning_adjustment + density_adjustment
        return max(1, min(int(round(total_load)), 10))

    @timing_decorator
    def _extract_enhanced_keywords(self, text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Enhanced keyword extraction with conceptual clustering.
        Returns both keywords and conceptual clusters.
        """
        try:
            # Advanced text preprocessing
            cleaned_text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
            cleaned_text = re.sub(r'[^\w\s]', ' ', cleaned_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            if not cleaned_text or len(cleaned_text.split()) < 3:
                return [], []
            
            # TF-IDF extraction
            tfidf_matrix = self.keyword_vectorizer.fit_transform([cleaned_text])
            feature_names = self.keyword_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Enhanced keyword scoring
            keyword_data = []
            for feature, score in zip(feature_names, tfidf_scores):
                if score > 0.1:  # Threshold for meaningful keywords
                    # Additional scoring factors
                    word_length_bonus = min(len(feature) / 10, 0.3)
                    frequency = cleaned_text.lower().count(feature.lower())
                    frequency_bonus = min(frequency * 0.1, 0.2)
                    
                    final_score = score + word_length_bonus + frequency_bonus
                    keyword_data.append({
                        'term': feature,
                        'tfidf_score': score,
                        'final_score': final_score,
                        'frequency': frequency
                    })
            
            # Sort and extract top keywords
            keyword_data.sort(key=lambda x: x['final_score'], reverse=True)
            top_keywords = [kw['term'] for kw in keyword_data[:8]]
            
            # Conceptual clustering
            clusters = self._create_conceptual_clusters(keyword_data)
            
            return top_keywords, clusters
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Enhanced keyword extraction failed: {e}")
            return [], []

    def _create_conceptual_clusters(self, keyword_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create conceptual clusters from keywords."""
        clusters = []
        
        for category, category_terms in self.concept_categories.items():
            cluster_keywords = []
            total_score = 0
            
            for kw_data in keyword_data:
                keyword = kw_data['term'].lower()
                if any(cat_term in keyword or keyword in cat_term for cat_term in category_terms):
                    cluster_keywords.append(kw_data['term'])
                    total_score += kw_data['final_score']
            
            if cluster_keywords:
                clusters.append({
                    'category': category,
                    'keywords': cluster_keywords,
                    'strength': round(total_score, 3),
                    'keyword_count': len(cluster_keywords)
                })
        
        return sorted(clusters, key=lambda x: x['strength'], reverse=True)

    @timing_decorator
    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Enhanced linguistic feature extraction."""
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Basic metrics
        features = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / max(len(sentences), 1),
            'question_count': text.count('?'),
            'exclamation_count': text.count('!'),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'punctuation_density': sum(1 for c in text if c in '.,;:!?-()[]{}') / max(len(text), 1)
        }
        
        # Advanced metrics
        if words:
            features.update({
                'avg_word_length': np.mean([len(w) for w in words]),
                'unique_word_ratio': len(set(words)) / len(words),
                'long_word_ratio': sum(1 for w in words if len(w) > 6) / len(words),
                'short_word_ratio': sum(1 for w in words if len(w) <= 3) / len(words)
            })
        
        # Readability approximation
        if sentences and words:
            avg_sentence_len = len(words) / len(sentences)
            avg_word_len = np.mean([len(w) for w in words])
            features['readability_estimate'] = max(1, min(10, (avg_sentence_len * 0.4 + avg_word_len * 2) / 3))
        
        return features

    def _analyze_argumentation_structure(self, text: str, reasoning_cues: List[str]) -> Dict[str, Any]:
        """Analyze the argumentation structure of the text."""
        structure = {
            'has_premises': any(cue in ['evidential', 'causal'] for cue in reasoning_cues),
            'has_conclusions': any(cue in ['causal', 'logical_structure'] for cue in reasoning_cues),
            'reasoning_chain_length': len(reasoning_cues),
            'argumentation_type': 'deductive' if 'causal' in reasoning_cues else 'inductive' if 'evidential' in reasoning_cues else 'descriptive'
        }
        
        # Check for counterarguments
        counter_patterns = [r'\b(however|but|although|despite|nevertheless)\b']
        has_counterarguments = any(re.search(pattern, text, re.IGNORECASE) for pattern in counter_patterns)
        structure['has_counterarguments'] = has_counterarguments
        
        return structure

    def _calculate_coherence_metrics(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate text coherence metrics."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 2:
            return {'coherence_score': 1.0, 'topic_consistency': 1.0}
        
        # Simple keyword-based coherence
        keyword_appearances = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            appearances = sum(1 for keyword in keywords if keyword.lower() in sentence_lower)
            keyword_appearances.append(appearances)
        
        # Coherence based on consistent keyword usage
        if keyword_appearances:
            coherence_variance = np.var(keyword_appearances)
            max_variance = max(keyword_appearances) ** 2 if keyword_appearances else 1
            coherence_score = 1 - (coherence_variance / max(max_variance, 1))
        else:
            coherence_score = 0.5
        
        # Topic consistency (simplified)
        topic_consistency = min(len(set(keywords)) / max(len(keywords), 1), 1.0) if keywords else 0.0
        
        return {
            'coherence_score': round(max(0, min(1, coherence_score)), 3),
            'topic_consistency': round(topic_consistency, 3)
        }

    def analyze_text(self, text: str) -> AnalysisResult:
        """
        Comprehensive enhanced text analysis with improved error handling and performance.
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return AnalysisResult(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                keywords=[],
                complexity_score=0.0,
                semantic_density=0.0,
                cognitive_load=1,
                linguistic_features={},
                reasoning_cues=[],
                processing_metadata={'processing_time': 0.0, 'text_length': 0}
            )
        
        try:
            # Core sentiment analysis with enhanced confidence
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
            compound_score = sentiment_scores['compound']
            
            # Enhanced sentiment classification
            if compound_score >= 0.1:
                sentiment = SentimentType.POSITIVE
                confidence = min(compound_score * 1.2, 1.0)
            elif compound_score <= -0.1:
                sentiment = SentimentType.NEGATIVE
                confidence = min(abs(compound_score) * 1.2, 1.0)
            elif abs(compound_score) < 0.02:
                sentiment = SentimentType.NEUTRAL
                confidence = 0.9  # High confidence for true neutral
            else:
                # Check for mixed sentiment
                pos_neg_diff = abs(sentiment_scores['pos'] - sentiment_scores['neg'])
                if pos_neg_diff < 0.3 and sentiment_scores['pos'] > 0.2 and sentiment_scores['neg'] > 0.2:
                    sentiment = SentimentType.MIXED
                    confidence = 0.7
                else:
                    sentiment = SentimentType.NEUTRAL
                    confidence = 1.0 - abs(compound_score) * 2
            
            # Enhanced feature extraction with parallel processing potential
            keywords, conceptual_clusters = self._extract_enhanced_keywords(text)
            complexity_score = self._calculate_complexity_score(text)
            semantic_density = self._calculate_semantic_density(text)
            reasoning_cues, reasoning_scores = self._extract_reasoning_cues(text)
            cognitive_load = self._calculate_cognitive_load(text, complexity_score, reasoning_cues)
            linguistic_features = self._extract_linguistic_features(text)
            
            # Advanced analysis components
            argumentation_structure = self._analyze_argumentation_structure(text, reasoning_cues)
            coherence_metrics = self._calculate_coherence_metrics(text, keywords)
            
            processing_time = time.time() - start_time
            
            return AnalysisResult(
                sentiment=sentiment,
                confidence=round(confidence, 3),
                keywords=keywords,
                complexity_score=round(complexity_score, 3),
                semantic_density=round(semantic_density, 3),
                cognitive_load=cognitive_load,
                linguistic_features=linguistic_features,
                reasoning_cues=reasoning_cues,
                conceptual_clusters=conceptual_clusters,
                argumentation_structure=argumentation_structure,
                coherence_metrics=coherence_metrics,
                processing_metadata={
                    'processing_time': round(processing_time, 4),
                    'text_length': len(text),
                    'reasoning_scores': reasoning_scores,
                    'performance_metrics': dict(self._performance_metrics)
                }
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return safe fallback result
            return AnalysisResult(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                keywords=[],
                complexity_score=0.0,
                semantic_density=0.0,
                cognitive_load=1,
                linguistic_features={},
                reasoning_cues=[],
                processing_metadata={'error': str(e), 'processing_time': time.time() - start_time}
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring and optimization."""
        return {
            'performance_metrics': dict(self._performance_metrics),
            'cache_stats': dict(self._cache_stats),
            'cache_info': self._calculate_semantic_density.cache_info()._asdict()
        }

# Thread-safe singleton with better lifecycle management
class AnalyzerSingleton:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, config: Optional[Dict[str, Any]] = None) -> IntelligentTextAnalyzer:
        """Thread-safe singleton with configuration support."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = IntelligentTextAnalyzer(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton for testing or reconfiguration."""
        with cls._lock:
            cls._instance = None

def get_analyzer(config: Optional[Dict[str, Any]] = None) -> IntelligentTextAnalyzer:
    """Get analyzer instance with optional configuration."""
    return AnalyzerSingleton.get_instance(config)

def analyze_user_input(text: str, include_metadata: bool = False) -> Dict[str, Any]:
    """
    Enhanced main analysis function with comprehensive results and backward compatibility.
    """
    analyzer = get_analyzer()
    result = analyzer.analyze_text(text)
    
    # Determine complexity level for easier interpretation
    if result.complexity_score >= 0.75:
        complexity_level = ComplexityLevel.EXPERT.value
    elif result.complexity_score >= 0.5:
        complexity_level = ComplexityLevel.HIGH.value
    elif result.complexity_score >= 0.25:
        complexity_level = ComplexityLevel.MEDIUM.value
    else:
        complexity_level = ComplexityLevel.LOW.value
    
    # Build enhanced response
    response = {
        # Core backward-compatible fields
        "sentiment": result.sentiment.value,
        "keywords": result.keywords,
        
        # Enhanced analysis fields
        "confidence": result.confidence,
        "complexity_score": result.complexity_score,
        "complexity_level": complexity_level,
        "semantic_density": result.semantic_density,
        "cognitive_load": result.cognitive_load,
        "reasoning_cues": result.reasoning_cues,
        "linguistic_features": result.linguistic_features,
        
        # Advanced layered reasoning fields
        "conceptual_clusters": result.conceptual_clusters,
        "argumentation_structure": result.argumentation_structure,
        "coherence_metrics": result.coherence_metrics,
        
        # Enhanced computed insights
        "analysis_summary": {
            "text_sophistication": complexity_level,
            "information_density": "Dense" if result.semantic_density > 0.7 else "Moderate" if result.semantic_density > 0.4 else "Light",
            "reasoning_indicators": len(result.reasoning_cues),
            "processing_difficulty": "Complex" if result.cognitive_load > 7 else "Moderate" if result.cognitive_load > 4 else "Simple",
            "argumentation_quality": "Strong" if result.argumentation_structure.get('reasoning_chain_length', 0) > 3 else "Moderate" if result.argumentation_structure.get('reasoning_chain_length', 0) > 1 else "Weak",
            "coherence_level": "High" if result.coherence_metrics.get('coherence_score', 0) > 0.7 else "Moderate" if result.coherence_metrics.get('coherence_score', 0) > 0.4 else "Low"
        }
    }
    
    # Include metadata if requested
    if include_metadata:
        response["processing_metadata"] = result.processing_metadata
    
    return response