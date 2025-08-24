"""
Progress Model - Handles all progress data operations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GameData:
    """RPG game data structure"""
    xp: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[str] = None
    daily_activities: Dict = None
    achievements: List[str] = None
    total_xp_earned: int = 0
    problems_attempted_today: int = 0
    perfect_solutions: int = 0
    speed_completions: int = 0
    
    def __post_init__(self):
        if self.daily_activities is None:
            self.daily_activities = {}
        if self.achievements is None:
            self.achievements = []


@dataclass
class Stats:
    """Progress statistics"""
    total_completed: int = 0
    easy_completed: int = 0
    medium_completed: int = 0
    hard_completed: int = 0


@dataclass
class Progress:
    """Main progress data structure"""
    completed_problems: List[str] = None
    current_problem_index: int = 0
    last_updated: str = ""
    stats: Stats = None
    current_working_problem: Optional[str] = None
    game_data: GameData = None
    
    def __post_init__(self):
        if self.completed_problems is None:
            self.completed_problems = []
        if self.stats is None:
            self.stats = Stats()
        if self.game_data is None:
            self.game_data = GameData()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class ProgressModel:
    """Model for managing progress data"""
    
    def __init__(self, progress_file: Path):
        self.progress_file = progress_file
        self._progress: Optional[Progress] = None
    
    @property
    def progress(self) -> Progress:
        """Get current progress, loading if necessary"""
        if self._progress is None:
            self.load()
        return self._progress
    
    def load(self) -> Progress:
        """Load progress from file"""
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
            
            # Convert dict to dataclass
            stats_data = data.get('stats', {})
            stats = Stats(**stats_data)
            
            game_data_dict = data.get('game_data', {})
            game_data = GameData(**game_data_dict)
            
            progress_data = {
                'completed_problems': data.get('completed_problems', []),
                'current_problem_index': data.get('current_problem_index', 0),
                'last_updated': data.get('last_updated', datetime.now().isoformat()),
                'current_working_problem': data.get('current_working_problem'),
                'stats': stats,
                'game_data': game_data
            }
            
            self._progress = Progress(**progress_data)
            
        except FileNotFoundError:
            self._progress = Progress()
            self.save()
        
        return self._progress
    
    def save(self) -> None:
        """Save progress to file"""
        if self._progress is None:
            return
        
        # Update timestamp
        self._progress.last_updated = datetime.now().isoformat()
        
        # Convert to dict for JSON serialization
        data = {
            'completed_problems': self._progress.completed_problems,
            'current_problem_index': self._progress.current_problem_index,
            'last_updated': self._progress.last_updated,
            'current_working_problem': self._progress.current_working_problem,
            'stats': asdict(self._progress.stats),
            'game_data': asdict(self._progress.game_data)
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_completed_problem(self, problem_id: str, difficulty: str) -> None:
        """Add a completed problem"""
        if problem_id not in self.progress.completed_problems:
            self.progress.completed_problems.append(problem_id)
            self.progress.stats.total_completed += 1
            
            # Update difficulty stats
            difficulty_lower = difficulty.lower()
            if difficulty_lower == 'easy':
                self.progress.stats.easy_completed += 1
            elif difficulty_lower == 'medium':
                self.progress.stats.medium_completed += 1
            elif difficulty_lower == 'hard':
                self.progress.stats.hard_completed += 1
            
            self.save()
    
    def set_current_working_problem(self, problem_id: str) -> None:
        """Set the current working problem"""
        self.progress.current_working_problem = problem_id
        self.save()
    
    def clear_current_working_problem(self) -> None:
        """Clear the current working problem"""
        self.progress.current_working_problem = None
        self.save()
    
    def is_problem_completed(self, problem_id: str) -> bool:
        """Check if a problem is completed"""
        return problem_id in self.progress.completed_problems
    
    def reset_all(self, keep_solutions: bool = True) -> None:
        """Reset all progress"""
        self._progress = Progress()
        self.save()
    
    def reset_rpg_only(self) -> None:
        """Reset only RPG data"""
        self.progress.game_data = GameData()
        self.save()
