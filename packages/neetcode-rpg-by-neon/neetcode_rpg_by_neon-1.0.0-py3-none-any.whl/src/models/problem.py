"""
Problem Model - Handles problem data operations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Problem:
    """Individual problem data structure"""
    name: str
    difficulty: str
    leetcode_url: str
    order: int
    category: str
    
    @property
    def problem_id(self) -> str:
        """Generate problem ID"""
        return f"{self.category}_{self.name.lower().replace(' ', '_').replace('-', '_')}"
    
    @property
    def filename(self) -> str:
        """Generate filename for this problem"""
        problem_name = self.name.lower().replace(' ', '_').replace('-', '_')
        return f"{self.order:03d}_{problem_name}.py"
    
    @property
    def filepath(self) -> str:
        """Generate relative filepath"""
        return f"{self.category}/{self.filename}"


@dataclass
class Category:
    """Problem category data structure"""
    category: str
    problems: List[Problem]
    
    @property
    def display_name(self) -> str:
        """Get display name for category"""
        return self.category.replace('_', ' ').title()


class ProblemModel:
    """Model for managing problem data"""
    
    def __init__(self, problem_list_file: Path):
        self.problem_list_file = problem_list_file
        self._categories: Optional[List[Category]] = None
        self._problems: Optional[List[Problem]] = None
    
    @property
    def categories(self) -> List[Category]:
        """Get all categories"""
        if self._categories is None:
            self.load()
        return self._categories
    
    @property
    def problems(self) -> List[Problem]:
        """Get all problems in order"""
        if self._problems is None:
            self._problems = []
            for category in self.categories:
                self._problems.extend(category.problems)
            # Sort by order
            self._problems.sort(key=lambda x: x.order)
        return self._problems
    
    def load(self) -> None:
        """Load problems from file"""
        try:
            with open(self.problem_list_file, 'r') as f:
                data = json.load(f)
            
            self._categories = []
            
            for category_data in data.get("neetcode_75", []):
                category_name = category_data["category"]
                problems = []
                
                for problem_data in category_data["problems"]:
                    problem = Problem(
                        name=problem_data["name"],
                        difficulty=problem_data["difficulty"],
                        leetcode_url=problem_data["leetcode_url"],
                        order=problem_data.get("order", 999),
                        category=category_name
                    )
                    problems.append(problem)
                
                category = Category(category=category_name, problems=problems)
                self._categories.append(category)
                
        except FileNotFoundError:
            self._categories = []
    
    def get_problem_by_id(self, problem_id: str) -> Optional[Problem]:
        """Get problem by ID"""
        for problem in self.problems:
            if problem.problem_id == problem_id:
                return problem
        return None
    
    def get_problems_by_category(self, category_name: str) -> List[Problem]:
        """Get all problems in a category"""
        for category in self.categories:
            if category.category == category_name:
                return category.problems
        return []
    
    def get_next_problem(self, completed_problems: List[str]) -> Optional[Problem]:
        """Get the next uncompleted problem"""
        completed_set = set(completed_problems)
        
        for problem in self.problems:
            if problem.problem_id not in completed_set:
                return problem
        
        return None
    
    def get_category_progress(self, category_name: str, completed_problems: List[str]) -> Dict:
        """Get progress for a specific category"""
        category_problems = self.get_problems_by_category(category_name)
        if not category_problems:
            return {"total": 0, "completed": 0, "percentage": 0}
        
        completed_set = set(completed_problems)
        completed_count = sum(1 for p in category_problems if p.problem_id in completed_set)
        
        return {
            "total": len(category_problems),
            "completed": completed_count,
            "percentage": (completed_count / len(category_problems)) * 100 if category_problems else 0
        }
