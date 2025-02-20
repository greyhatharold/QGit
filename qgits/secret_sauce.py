#!/usr/bin/env python3

import hashlib
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class SecretSauce:
    """Handles secret repository statistics and insights generation."""
    
    SAUCE_FILE = '.qgit_sauce'
    ENCRYPTION_KEY = b'qgit_secret_sauce_v1'  # Basic encryption key
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path)
        self.sauce_path = self.repo_path / self.SAUCE_FILE
    
    def generate_sauce(self, repo_url: str, commit_data: List[Dict], 
                      authors_data: Dict) -> Dict:
        """Generate secret sauce data for the repository."""
        sauce_data = {
            'generated_at': datetime.now().isoformat(),
            'repo_fingerprint': self._generate_fingerprint(repo_url),
            'insights': self._generate_insights(commit_data, authors_data),
            'fun_facts': self._generate_fun_facts(commit_data, authors_data),
            'easter_eggs': self._generate_easter_eggs(commit_data)
        }
        
        # Encrypt and save the sauce
        self._save_sauce(sauce_data)
        return sauce_data
    
    def read_sauce(self) -> Optional[Dict]:
        """Read and decrypt existing sauce data."""
        if not self.sauce_path.exists():
            return None
            
        try:
            encrypted_data = self.sauce_path.read_bytes()
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return None
    
    def _generate_fingerprint(self, repo_url: str) -> str:
        """Generate unique repository fingerprint."""
        timestamp = datetime.now().strftime('%Y%m%d')
        data = f"{repo_url}|{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _generate_insights(self, commit_data: List[Dict], 
                          authors_data: Dict) -> Dict:
        """Generate interesting repository insights."""
        # Analyze commit patterns
        commit_times = [c['date'] for c in commit_data]
        commit_messages = [c['message'] for c in commit_data]
        insights = {
            'peak_productivity': self._analyze_peak_times(commit_times),
            'commit_style': self._analyze_commit_messages(commit_messages),
            'author_personalities': self._analyze_author_personalities(authors_data),
            'code_rhythm': self._analyze_code_rhythm(commit_times),
            'collaboration_patterns': self._analyze_collaboration(authors_data)
        }
        
        return insights
    
    def _generate_fun_facts(self, commit_data: List[Dict], 
                           authors_data: Dict) -> List[Dict]:
        """Generate fun facts about the repository."""
        facts = []
        
        # Longest coding streak
        streak = self._find_longest_streak(commit_data)
        if streak:
            facts.append({
                'emoji': '🔥',
                'title': 'Longest Coding Streak',
                'value': f"{streak} days"
            })
        
        # Night owl index
        night_owl_score = self._calculate_night_owl_index(commit_data)
        facts.append({
            'emoji': '🦉',
            'title': 'Night Owl Index',
            'value': f"{night_owl_score}/10"
        })
        
        # Coffee time commits
        coffee_commits = self._count_coffee_time_commits(commit_data)
        facts.append({
            'emoji': '☕',
            'title': 'Coffee Time Commits',
            'value': f"{coffee_commits} commits during coffee hours"
        })
        
        # Team spirit score
        spirit_score = self._calculate_team_spirit(authors_data)
        facts.append({
            'emoji': '🤝',
            'title': 'Team Spirit Score',
            'value': f"{spirit_score}/100"
        })
        
        return facts
    
    def _generate_easter_eggs(self, commit_data: List[Dict]) -> List[Dict]:
        """Generate hidden easter eggs based on repository patterns."""
        easter_eggs = []
        
        # Special commit numbers
        special_commits = self._find_special_commits(commit_data)
        if special_commits:
            easter_eggs.extend(special_commits)
        
        # Code poetry
        poetry = self._generate_code_poetry(commit_data)
        if poetry:
            easter_eggs.append({
                'type': 'poetry',
                'content': poetry
            })
        
        return easter_eggs
    
    def _analyze_peak_times(self, commit_times: List[str]) -> Dict:
        """Analyze peak productivity times."""
        hours = [datetime.fromisoformat(t).hour for t in commit_times]
        peak_hour = max(set(hours), key=hours.count)
        return {
            'peak_hour': peak_hour,
            'peak_period': 'morning' if 5 <= peak_hour < 12 else
                          'afternoon' if 12 <= peak_hour < 17 else
                          'evening' if 17 <= peak_hour < 22 else 'night'
        }
    
    def _analyze_commit_messages(self, messages: List[str]) -> Dict:
        """Analyze commit message patterns."""
        emoji_count = sum(1 for m in messages if '�' in m)
        avg_length = sum(len(m) for m in messages) / len(messages)
        return {
            'emoji_percentage': (emoji_count / len(messages)) * 100,
            'avg_length': avg_length,
            'style': 'expressive' if emoji_count > len(messages) * 0.3 else
                    'concise' if avg_length < 50 else 'detailed'
        }
    
    def _analyze_author_personalities(self, authors_data: Dict) -> Dict:
        """Analyze coding personalities based on commit patterns."""
        personalities = {}
        for author, commits in authors_data.items():
            # Analyze commit timing, message style, and frequency
            personality = self._determine_personality(commits)
            personalities[author] = personality
        return personalities
    
    def _determine_personality(self, commits: List[Dict]) -> str:
        """Determine author's coding personality."""
        personalities = [
            "The Perfectionist 🎯",
            "The Innovation Wizard 🧙‍♂️",
            "The Problem Solver 🔧",
            "The Code Poet 📝",
            "The Efficiency Expert ⚡",
            "The Team Player 🤝",
            "The Night Owl 🦉",
            "The Early Bird 🐦",
            "The Documentation Hero 📚",
            "The Refactoring Artist 🎨"
        ]
        # Use commit patterns to select personality
        return random.choice(personalities)
    
    def _save_sauce(self, data: Dict) -> None:
        """Encrypt and save sauce data."""
        json_data = json.dumps(data, indent=2)
        encrypted_data = self._encrypt_data(json_data)
        self.sauce_path.write_bytes(encrypted_data)
    
    def _encrypt_data(self, data: str) -> bytes:
        """Simple XOR encryption (for fun, not security)."""
        data_bytes = data.encode()
        key_bytes = self.ENCRYPTION_KEY * (len(data_bytes) // len(self.ENCRYPTION_KEY) + 1)
        key_bytes = key_bytes[:len(data_bytes)]
        return bytes(a ^ b for a, b in zip(data_bytes, key_bytes))
    
    def _decrypt_data(self, data: bytes) -> str:
        """Decrypt XOR encrypted data."""
        # XOR encryption is symmetric
        return self._encrypt_data(data.decode()).decode()
    
    def _find_longest_streak(self, commit_data: List[Dict]) -> int:
        """Find longest consecutive days with commits."""
        if not commit_data:
            return 0
            
        dates = sorted(set(c['date'].split('T')[0] for c in commit_data))
        max_streak = current_streak = 1
        
        for i in range(1, len(dates)):
            date1 = datetime.fromisoformat(dates[i-1])
            date2 = datetime.fromisoformat(dates[i])
            if (date2 - date1).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
                
        return max_streak
    
    def _calculate_night_owl_index(self, commit_data: List[Dict]) -> int:
        """Calculate night owl score (0-10)."""
        night_commits = sum(1 for c in commit_data 
                          if 22 <= datetime.fromisoformat(c['date']).hour or 
                          datetime.fromisoformat(c['date']).hour <= 5)
        return min(10, int((night_commits / len(commit_data)) * 20))
    
    def _count_coffee_time_commits(self, commit_data: List[Dict]) -> int:
        """Count commits during typical coffee hours (9-11 AM)."""
        return sum(1 for c in commit_data 
                  if 9 <= datetime.fromisoformat(c['date']).hour <= 11)
    
    def _calculate_team_spirit(self, authors_data: Dict) -> int:
        """Calculate team collaboration score (0-100)."""
        if len(authors_data) <= 1:
            return 50
            
        commit_counts = list(len(commits) for commits in authors_data.values())
        variance = sum((c - sum(commit_counts)/len(commit_counts))**2 
                      for c in commit_counts) / len(commit_counts)
        
        # Lower variance means more balanced contributions
        return min(100, max(0, int(100 * (1 - variance/1000))))
    
    def _find_special_commits(self, commit_data: List[Dict]) -> List[Dict]:
        """Find commits with special numbers or patterns."""
        special_commits = []
        for i, commit in enumerate(commit_data, 1):
            if self._is_special_number(i):
                special_commits.append({
                    'type': 'special_commit',
                    'number': i,
                    'message': commit['message'],
                    'reason': self._get_special_number_reason(i)
                })
        return special_commits
    
    def _is_special_number(self, n: int) -> bool:
        """Check if a number is special (palindrome, power, etc)."""
        return (str(n) == str(n)[::-1] or  # Palindrome
                int(n ** 0.5) ** 2 == n or  # Perfect square
                n in [42, 69, 100, 500, 1000])  # Special numbers
    
    def _get_special_number_reason(self, n: int) -> str:
        """Get reason why a number is special."""
        if str(n) == str(n)[::-1]:
            return "Palindrome commit! 🔄"
        if int(n ** 0.5) ** 2 == n:
            return f"Perfect square commit! ({int(n ** 0.5)}²) ⭐"
        return "Milestone commit! 🎉"
    
    def _generate_code_poetry(self, commit_data: List[Dict]) -> Optional[str]:
        """Generate poetry from commit messages."""
        if len(commit_data) < 5:
            return None
            
        # Select interesting words from commit messages
        words = []
        for commit in commit_data:
            words.extend(w for w in commit['message'].split() 
                        if len(w) > 3 and w.isalnum())
        
        if len(words) < 10:
            return None
            
        # Generate a small poem
        random.shuffle(words)
        lines = [
            f"{words[0]} {words[1]} {words[2]}",
            f"{words[3]} {words[4]}",
            f"{words[5]} {words[6]} {words[7]}",
            f"{words[8]} {words[9]}"
        ]
        
        return "\n".join(lines)
