"""
Duplicate file finder with fuzzy matching across two directories.
"""
import re
import math
from pathlib import Path
from typing import List, Tuple, Dict, Set
from difflib import SequenceMatcher
from collections import Counter

# Constants for similarity thresholds and weights
DEFAULT_NAME_THRESHOLD = 0.7

NAME_SIMILARITY_WEIGHT = 0.6
SIZE_SIMILARITY_WEIGHT = 0.4
EXACT_MATCH_THRESHOLD = 0.95
VERY_SIMILAR_THRESHOLD = 0.8
SIZE_EXACT_MATCH_THRESHOLD = 0.99
SIZE_VERY_CLOSE_THRESHOLD = 0.95


class DuplicateFinder:
    """Finds potential duplicate files across two directories."""
    
    @staticmethod
    def get_file_info(directory: str, include_subdirs: bool = True) -> List[Dict]:
        """
        Get information about all files in a directory.
        
        Args:
            directory: Path to directory
            include_subdirs: If True, recursively scan subdirectories
            
        Returns:
            List of dicts with file information
        """
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        files_info = []
        
        # Choose iterator based on whether to include subdirectories
        file_iterator = dir_path.rglob('*') if include_subdirs else dir_path.iterdir()
        
        for file_path in file_iterator:
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    # Get relative path from base directory for display
                    rel_path = file_path.relative_to(dir_path)
                    files_info.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'relative_path': str(rel_path),
                        'size': file_size,
                        'extension': file_path.suffix.lower()
                    })
                except OSError:
                    continue
        
        return files_info
    
    @staticmethod
    def tokenize_filename(filename: str) -> List[str]:
        """
        Tokenize filename into words, splitting on common separators and numbers.
        
        Args:
            filename: Filename to tokenize
            
        Returns:
            List of lowercase tokens
        """
        # Remove extension
        base = Path(filename).stem.lower()
        
        # Split on non-alphanumeric characters and preserve words
        tokens = re.findall(r'[a-z]+|\d+', base)
        
        return tokens
    
    @staticmethod
    def calculate_idf(all_files: List[Dict]) -> Dict[str, float]:
        """
        Calculate Inverse Document Frequency for all tokens across files.
        
        Args:
            all_files: List of file info dicts
            
        Returns:
            Dict mapping token to IDF score
        """
        # Count how many files contain each token
        doc_frequency = Counter()
        total_docs = len(all_files)
        
        for file_info in all_files:
            tokens = set(DuplicateFinder.tokenize_filename(file_info['name']))
            for token in tokens:
                doc_frequency[token] += 1
        
        # Calculate IDF: log(total_docs / doc_frequency)
        idf = {}
        for token, freq in doc_frequency.items():
            idf[token] = math.log(total_docs / freq)
        
        return idf
    
    @staticmethod
    def calculate_tfidf_similarity(name1: str, name2: str, idf: Dict[str, float]) -> float:
        """
        Calculate TF-IDF based similarity between two filenames.
        
        Args:
            name1: First filename
            name2: Second filename
            idf: IDF scores for all tokens
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        tokens1 = DuplicateFinder.tokenize_filename(name1)
        tokens2 = DuplicateFinder.tokenize_filename(name2)
        
        # Calculate TF (term frequency) for each filename
        tf1 = Counter(tokens1)
        tf2 = Counter(tokens2)
        
        # Get all unique tokens
        all_tokens = set(tokens1) | set(tokens2)
        
        # Calculate TF-IDF vectors
        vec1 = []
        vec2 = []
        for token in all_tokens:
            idf_score = idf.get(token, 1.0)  # Default IDF of 1.0 for unknown tokens
            vec1.append(tf1.get(token, 0) * idf_score)
            vec2.append(tf2.get(token, 0) * idf_score)
        
        # Calculate cosine similarity
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    @staticmethod
    def calculate_name_similarity(name1: str, name2: str) -> float:
        """
        Calculate similarity ratio between two filenames.
        
        Args:
            name1: First filename
            name2: Second filename
            
        Returns:
            Similarity ratio between 0 and 1
        """
        # Remove extensions for comparison
        base1 = Path(name1).stem.lower()
        base2 = Path(name2).stem.lower()
        
        return SequenceMatcher(None, base1, base2).ratio()
    
    @staticmethod
    def calculate_size_similarity(size1: int, size2: int) -> float:
        """
        Calculate similarity based on file sizes.
        
        Args:
            size1: First file size in bytes
            size2: Second file size in bytes
            
        Returns:
            Similarity ratio between 0 and 1
        """
        if size1 == 0 or size2 == 0:
            return 0.0 if size1 != size2 else 1.0
        
        smaller = min(size1, size2)
        larger = max(size1, size2)
        
        return smaller / larger
    
    @staticmethod
    def find_duplicates(
        dir1: str,
        dir2: str,
        name_threshold: float = DEFAULT_NAME_THRESHOLD,
        include_subdirs1: bool = True,
        include_subdirs2: bool = True,
        use_tfidf: bool = True
    ) -> List[Dict]:
        """
        Find potential duplicate files between two directories.
        
        Args:
            dir1: First directory path
            dir2: Second directory path
            name_threshold: Minimum name similarity (0-1)
            include_subdirs1: If True, recursively scan subdirectories in dir1
            include_subdirs2: If True, recursively scan subdirectories in dir2
            use_tfidf: If True, use TF-IDF similarity (better for common terms)
            
        Returns:
            List of potential matches with confidence scores
        """
        files1 = DuplicateFinder.get_file_info(dir1, include_subdirs1)
        files2 = DuplicateFinder.get_file_info(dir2, include_subdirs2)
        
        # Calculate IDF scores across all files if using TF-IDF
        idf = None
        if use_tfidf:
            all_files = files1 + files2
            idf = DuplicateFinder.calculate_idf(all_files)
        
        matches = []
        
        for file1 in files1:
            for file2 in files2:
                # Skip if different file extensions
                if file1['extension'] != file2['extension']:
                    continue
                
                # Use TF-IDF or basic similarity
                if use_tfidf and idf:
                    name_sim = DuplicateFinder.calculate_tfidf_similarity(
                        file1['name'],
                        file2['name'],
                        idf
                    )
                else:
                    name_sim = DuplicateFinder.calculate_name_similarity(
                        file1['name'],
                        file2['name']
                    )
                
                size_sim = DuplicateFinder.calculate_size_similarity(
                    file1['size'],
                    file2['size']
                )
                
                # Check if name meets minimum threshold (size is informational only)
                if name_sim >= name_threshold:
                    # Calculate overall confidence (weighted average)
                    confidence = (name_sim * NAME_SIMILARITY_WEIGHT + size_sim * SIZE_SIMILARITY_WEIGHT)
                    
                    # Determine match reasons
                    reasons = []
                    if name_sim >= EXACT_MATCH_THRESHOLD:
                        reasons.append("Name exact match")
                    elif name_sim >= VERY_SIMILAR_THRESHOLD:
                        reasons.append("Name very similar")
                    else:
                        reasons.append("Name similar")
                    
                    if size_sim >= SIZE_EXACT_MATCH_THRESHOLD:
                        reasons.append("Size exact match")
                    elif size_sim >= SIZE_VERY_CLOSE_THRESHOLD:
                        reasons.append("Size very close")
                    else:
                        reasons.append("Size similar")
                    
                    matches.append({
                        'file1_name': file1['name'],
                        'file1_path': file1['path'],
                        'file1_relative_path': file1.get('relative_path', file1['name']),
                        'file1_size': file1['size'],
                        'file2_name': file2['name'],
                        'file2_path': file2['path'],
                        'file2_relative_path': file2.get('relative_path', file2['name']),
                        'file2_size': file2['size'],
                        'name_similarity': name_sim,
                        'size_similarity': size_sim,
                        'confidence': confidence,
                        'reasons': ', '.join(reasons)
                    })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
