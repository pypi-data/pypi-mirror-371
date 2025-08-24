"""
Problem Service - Handles problem-related business logic
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.problem import ProblemModel, Problem
from ..models.progress import ProgressModel


class ProblemService:
    """Service for problem-related operations"""
    
    def __init__(self, problem_model: ProblemModel, progress_model: ProgressModel, base_dir: Path):
        self.problem_model = problem_model
        self.progress_model = progress_model
        self.base_dir = base_dir
    
    def get_next_problem(self) -> Optional[Problem]:
        """Get the next problem to solve"""
        return self.problem_model.get_next_problem(
            self.progress_model.progress.completed_problems
        )
    
    def get_current_working_problem(self) -> Optional[Problem]:
        """Get the current working problem"""
        current_id = self.progress_model.progress.current_working_problem
        if current_id:
            return self.problem_model.get_problem_by_id(current_id)
        return None
    
    def set_current_working_problem(self, problem: Problem) -> None:
        """Set the current working problem"""
        self.progress_model.set_current_working_problem(problem.problem_id)
    
    def clear_current_working_problem(self) -> None:
        """Clear the current working problem"""
        self.progress_model.clear_current_working_problem()
    
    def mark_problem_completed(self, problem: Problem) -> None:
        """Mark a problem as completed"""
        if not self.progress_model.is_problem_completed(problem.problem_id):
            self.progress_model.add_completed_problem(problem.problem_id, problem.difficulty)
    
    def create_problem_file(self, problem: Problem) -> bool:
        """Create a problem file from template"""
        try:
            # Ensure category directory exists
            category_dir = self.base_dir / problem.category
            category_dir.mkdir(exist_ok=True)
            
            # Create file path
            file_path = self.base_dir / problem.filepath
            
            if file_path.exists():
                return True  # File already exists
            
            # Generate template content
            template_content = self._generate_problem_template(problem)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(template_content)
            
            return True
            
        except Exception as e:
            print(f"Error creating problem file: {e}")
            return False
    
    def test_solution(self, problem: Problem) -> Tuple[bool, str]:
        """Test a problem solution"""
        file_path = self.base_dir / problem.filepath
        
        if not file_path.exists():
            return False, f"Solution file not found: {problem.filepath}"
        
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip() if result.stdout.strip() else "Tests passed!"
            else:
                error_msg = "Tests failed!"
                if result.stdout.strip():
                    error_msg += f"\nSTDOUT: {result.stdout}"
                if result.stderr.strip():
                    error_msg += f"\nSTDERR: {result.stderr}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Test timed out (30s limit)"
        except Exception as e:
            return False, f"Error running tests: {e}"
    
    def benchmark_solution(self, problem: Problem, runs: int = 5) -> Dict:
        """Benchmark solution performance with multiple runs"""
        file_path = self.base_dir / problem.filepath
        
        if not file_path.exists():
            return {"error": f"Solution file not found: {problem.filepath}"}
        
        import statistics
        
        execution_times = []
        
        try:
            # Run multiple times for better accuracy
            for _ in range(runs):
                start_time = time.time()
                success, output = self.test_solution(problem)
                end_time = time.time()
                
                if not success:
                    return {"error": "Solution failed tests during benchmarking"}
                
                execution_times.append((end_time - start_time) * 1000)  # Convert to ms
            
            # Calculate statistics
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            
            # Performance rating
            if avg_time < 10:
                rating = "Excellent"
                rating_emoji = "🚀"
            elif avg_time < 50:
                rating = "Good"
                rating_emoji = "✅"
            elif avg_time < 200:
                rating = "Average"
                rating_emoji = "⚡"
            else:
                rating = "Slow"
                rating_emoji = "🐌"
            
            return {
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "std_dev_ms": std_dev,
                "runs": runs,
                "rating": rating,
                "rating_emoji": rating_emoji,
                "all_times": execution_times
            }
            
        except Exception as e:
            return {"error": f"Benchmarking failed: {e}"}
    def analyze_solution(self, problem: Problem) -> Dict:
        """Analyze solution quality and performance with benchmarking"""
        file_path = self.base_dir / problem.filepath
        
        if not file_path.exists():
            return {"error": f"Solution file not found: {problem.filepath}"}
        
        analysis = {
            "perfect_solution": True,
            "fast_completion": False,
            "total_issues": 0,
            "execution_time_ms": 0,
            "performance_rating": "Unknown",
            "solution_implemented": False,
            "code": "",
            "benchmark": {}
        }
        
        try:
            # Check if solution is actually implemented
            with open(file_path, 'r') as f:
                code = f.read()
            
            analysis["code"] = code  # Store code for graph generation
            
            # Check for signs that solution is not implemented
            if 'pass' in code and 'TODO' in code:
                analysis["solution_implemented"] = False
                analysis["perfect_solution"] = False
                return analysis
            
            # Check if the main solution method just has 'pass'
            lines = code.split('\n')
            in_solution_method = False
            method_has_implementation = False
            
            for line in lines:
                line = line.strip()
                if 'def ' in line and 'Solution' in code:
                    in_solution_method = True
                    continue
                
                if in_solution_method:
                    if line.startswith('def ') and 'test_' not in line:
                        in_solution_method = False
                        break
                    
                    if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                        if line != 'pass' and 'TODO' not in line:
                            method_has_implementation = True
            
            if not method_has_implementation:
                analysis["solution_implemented"] = False
                analysis["perfect_solution"] = False
                return analysis
            
            analysis["solution_implemented"] = True
            
            # Run benchmark (multiple test runs for accuracy)
            benchmark_result = self.benchmark_solution(problem, runs=3)
            
            if "error" in benchmark_result:
                analysis["solution_implemented"] = False
                analysis["perfect_solution"] = False
                analysis["error"] = benchmark_result["error"]
                return analysis
            
            analysis["benchmark"] = benchmark_result
            analysis["execution_time_ms"] = benchmark_result["avg_time_ms"]
            analysis["performance_rating"] = benchmark_result["rating"]
            analysis["fast_completion"] = benchmark_result["avg_time_ms"] < 50
            
            # Code quality analysis (simplified)
            issues = 0
            if len([line for line in code.split('\n') if len(line) > 120]):
                issues += 1  # Long lines
            
            if 'TODO' in code:
                issues += 1  # Unfinished code
            
            analysis["total_issues"] = issues
            analysis["perfect_solution"] = issues == 0
                
        except Exception as e:
            analysis["error"] = str(e)
            analysis["solution_implemented"] = False
        
        return analysis
    
    def get_category_progress(self, category_name: str) -> Dict:
        """Get progress for a specific category"""
        return self.problem_model.get_category_progress(
            category_name, 
            self.progress_model.progress.completed_problems
        )
    
    def get_all_categories_progress(self) -> List[Dict]:
        """Get progress for all categories"""
        progress_list = []
        
        for category in self.problem_model.categories:
            progress = self.get_category_progress(category.category)
            progress_list.append({
                "category": category.category,
                "display_name": category.display_name,
                **progress
            })
        
        return progress_list
    
    def _generate_problem_template(self, problem: Problem) -> str:
        """Generate template content for a problem"""
        function_name = self._generate_function_name(problem.name)
        
        template = f'''"""
Problem: {problem.name}
Difficulty: {problem.difficulty}
Category: {problem.category.replace('_', ' ').title()}
Link: {problem.leetcode_url}

Description:
Visit the LeetCode link above to read the full problem description.

Constraints:
- Check the LeetCode problem for detailed constraints
- Consider edge cases like empty inputs, single elements, etc.
"""

from typing import List, Optional, Dict, Set, Tuple


class Solution:
    def {function_name}(self, param: List[int]) -> int:
        """
        Approach: [Describe your approach here]
        
        Algorithm:
        1. [Step 1 description]
        2. [Step 2 description]
        3. [Step 3 description]
        
        Time Complexity: O(?) - [explanation]
        Space Complexity: O(?) - [explanation]
        """
        # TODO: Implement your solution here
        pass


def test_solution():
    """Test cases for the solution"""
    sol = Solution()
    
    # TODO: Add test cases based on the examples
    # Example test structure:
    # assert sol.{function_name}(input) == expected_output
    
    print("✅ All test cases passed!")


if __name__ == "__main__":
    test_solution()
'''
        
        return template
    
    def _generate_function_name(self, problem_name: str) -> str:
        """Generate appropriate function name"""
        import re
        
        # Convert to camelCase
        words = re.findall(r'\\w+', problem_name.lower())
        if not words:
            return "solution"
        
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def delete_solution_files(self, categories: List[str] = None) -> int:
        """Delete solution files for specified categories"""
        if categories is None:
            categories = [cat.category for cat in self.problem_model.categories]
        
        deleted_count = 0
        
        for category in categories:
            category_dir = self.base_dir / category
            if category_dir.exists():
                for solution_file in category_dir.glob("*.py"):
                    if solution_file.name not in ["__init__.py"]:
                        solution_file.unlink()
                        deleted_count += 1
        
        return deleted_count
