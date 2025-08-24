"""
Graph Service - Visual complexity analysis with matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import tempfile
import subprocess
import platform
import os
import warnings
from typing import Dict

# Suppress matplotlib font warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class GraphService:
    """Service for creating visual complexity graphs"""
    
    def __init__(self):
        # Set up matplotlib style
        plt.style.use('default')
        
        # Complexity mappings for visualization
        self.complexity_map = {
            "O(1)": 1,
            "O(log n)": 2,
            "O(n)": 3,
            "O(n log n)": 4,
            "O(n²)": 5,
            "O(n³)": 6,
            "O(2ⁿ)": 7,
            "O(n!)": 8,
            "Unknown": 3  # Default to O(n)
        }
        
        self.complexity_labels = {
            1: "O(1)",
            2: "O(log n)",
            3: "O(n)",
            4: "O(n log n)",
            5: "O(n²)",
            6: "O(n³)",
            7: "O(2ⁿ)",
            8: "O(n!)"
        }
        
        self.complexity_colors = {
            1: "#2ecc71",  # Green - Excellent
            2: "#27ae60",  # Dark Green - Very Good
            3: "#f39c12",  # Orange - Good
            4: "#e67e22",  # Dark Orange - Fair
            5: "#e74c3c",  # Red - Poor
            6: "#c0392b",  # Dark Red - Very Poor
            7: "#8e44ad",  # Purple - Terrible
            8: "#2c3e50"   # Dark - Worst
        }
    
    def analyze_code_complexity(self, code: str) -> Dict:
        """Analyze code to estimate complexity using pattern recognition"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        
        # Pattern-based analysis for better accuracy
        time_complexity = self._analyze_time_complexity(lines, code)
        space_complexity = self._analyze_space_complexity(lines, code)
        
        return {
            "time_complexity": time_complexity,
            "space_complexity": space_complexity,
            "time_numeric": self.complexity_map.get(time_complexity, 3),
            "space_numeric": self.complexity_map.get(space_complexity, 1)
        }
    
    def _analyze_time_complexity(self, lines: list, full_code: str) -> str:
        """Analyze time complexity using pattern recognition"""
        
        # Check for common O(1) patterns
        if not any('for ' in line or 'while ' in line for line in lines):
            return "O(1)"
        
        # Count actual nested loops (more accurate)
        nested_loops = 0
        current_nesting = 0
        max_nesting = 0
        
        for line in lines:
            # Count opening of loops
            if 'for ' in line or 'while ' in line:
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            
            # Rough estimation of closing (when indentation decreases)
            # This is simplified but works for most cases
            if line and not line.startswith('    ') and current_nesting > 0:
                current_nesting = max(0, current_nesting - 1)
        
        # Check for specific patterns
        code_lower = full_code.lower()
        
        # Hash table operations (Two Sum pattern)
        if ('dict' in code_lower or '{}' in full_code) and max_nesting <= 1:
            if 'sort' not in code_lower:
                return "O(n)"  # Hash table with single loop = O(n)
        
        # Sorting patterns
        if 'sort' in code_lower:
            return "O(n log n)"
        
        # Binary search patterns
        if 'binary' in code_lower or ('left' in code_lower and 'right' in code_lower and 'mid' in code_lower):
            return "O(log n)"
        
        # Nested loop patterns
        if max_nesting == 1:
            return "O(n)"
        elif max_nesting == 2:
            return "O(n²)"
        elif max_nesting == 3:
            return "O(n³)"
        else:
            return "O(2ⁿ)"
    
    def _analyze_space_complexity(self, lines: list, full_code: str) -> str:
        """Analyze space complexity"""
        
        # Count data structures
        space_structures = 0
        
        # Check for space-consuming patterns
        patterns = ['dict()', '{}', '[]', 'list()', 'set()', 'collections.']
        
        for pattern in patterns:
            if pattern in full_code:
                space_structures += 1
        
        # Check for recursive calls (stack space)
        if 'return ' in full_code and any('(' in line and ')' in line for line in lines):
            # Might be recursive
            if space_structures > 0:
                return "O(n)"
        
        # Determine space complexity
        if space_structures == 0:
            return "O(1)"
        elif space_structures <= 2:
            return "O(n)"
        else:
            return "O(n²)"
    
    def get_optimal_complexity(self, problem_name: str) -> Dict:
        """Get optimal complexity for common problems"""
        # Hardcoded optimal complexities for common problems
        optimal_data = {
            "Two Sum": {"time": "O(n)", "space": "O(n)"},
            "Valid Anagram": {"time": "O(n)", "space": "O(1)"},
            "Contains Duplicate": {"time": "O(n)", "space": "O(n)"},
            "Group Anagrams": {"time": "O(n log n)", "space": "O(n)"},
            "Top K Frequent Elements": {"time": "O(n log n)", "space": "O(n)"},
            "Valid Palindrome": {"time": "O(n)", "space": "O(1)"},
            "3Sum": {"time": "O(n²)", "space": "O(1)"},
            "Container With Most Water": {"time": "O(n)", "space": "O(1)"},
        }
        
        optimal = optimal_data.get(problem_name, {"time": "O(n)", "space": "O(1)"})
        
        return {
            "time_complexity": optimal["time"],
            "space_complexity": optimal["space"],
            "time_numeric": self.complexity_map.get(optimal["time"], 3),
            "space_numeric": self.complexity_map.get(optimal["space"], 1)
        }
    
    def create_complexity_graph(self, user_solution: Dict, optimal_solution: Dict, problem_name: str) -> str:
        """Create complexity comparison graph with linear plots"""
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.patch.set_facecolor('white')
        
        # Input sizes for plotting
        n_values = [10, 50, 100, 500, 1000, 5000, 10000]
        
        # Calculate time complexity values
        user_time_values = [self._calculate_complexity_value(n, user_solution['time_numeric']) for n in n_values]
        optimal_time_values = [self._calculate_complexity_value(n, optimal_solution['time_numeric']) for n in n_values]
        
        # Time Complexity Plot
        ax1.plot(n_values, user_time_values, 'o-', linewidth=3, markersize=8, 
                label=f"Your Solution: {user_solution['time_complexity']}", color='#FF6B6B')
        ax1.plot(n_values, optimal_time_values, 's-', linewidth=3, markersize=8,
                label=f"Optimal Solution: {optimal_solution['time_complexity']}", color='#4ECDC4')
        
        ax1.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Time Units', fontsize=12, fontweight='bold')
        ax1.set_title('⏱️ Time Complexity Growth', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        # Add background gradient
        ax1.set_facecolor('#F8F9FA')
        
        # Calculate space complexity values
        user_space_values = [self._calculate_complexity_value(n, user_solution['space_numeric']) for n in n_values]
        optimal_space_values = [self._calculate_complexity_value(n, optimal_solution['space_numeric']) for n in n_values]
        
        # Space Complexity Plot
        ax2.plot(n_values, user_space_values, 'o-', linewidth=3, markersize=8,
                label=f"Your Solution: {user_solution['space_complexity']}", color='#FF6B6B')
        ax2.plot(n_values, optimal_space_values, 's-', linewidth=3, markersize=8,
                label=f"Optimal Solution: {optimal_solution['space_complexity']}", color='#4ECDC4')
        
        ax2.set_xlabel('Input Size (n)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Space Units', fontsize=12, fontweight='bold')
        ax2.set_title('💾 Space Complexity Growth', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        
        # Add background gradient
        ax2.set_facecolor('#F8F9FA')
        
        # Add overall title
        fig.suptitle(f'📊 Complexity Analysis: {problem_name}', fontsize=16, fontweight='bold')
        
        # Add explanation text
        explanation = """
        📈 Linear plots show how execution time and memory usage grow with input size
        🔴 Red line: Your solution  🔵 Blue line: Optimal solution
        📊 Lower lines are better (less time/space needed)
        """
        
        fig.text(0.5, 0.02, explanation, ha='center', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
        
        # Save to temp file
        temp_file = tempfile.mktemp(suffix='.png')
        plt.savefig(temp_file, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return temp_file
    
    def _calculate_complexity_value(self, n: int, complexity_level: int) -> float:
        """Calculate the actual value for a given complexity and input size"""
        if complexity_level == 1:  # O(1)
            return 1
        elif complexity_level == 2:  # O(log n)
            return max(1, n.bit_length())
        elif complexity_level == 3:  # O(n)
            return n
        elif complexity_level == 4:  # O(n log n)
            return n * max(1, n.bit_length())
        elif complexity_level == 5:  # O(n²)
            return n * n
        elif complexity_level == 6:  # O(n³)
            return n * n * n
        elif complexity_level == 7:  # O(2ⁿ) - cap it for visualization
            return min(2 ** min(n, 20), 10**8)  # Cap exponential for plotting
        elif complexity_level == 8:  # O(n!) - cap it heavily
            import math
            return min(math.factorial(min(n, 10)), 10**8)
        else:
            return n  # Default to O(n)
    
    def open_image(self, image_path: str) -> bool:
        """Open image with system default viewer"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", image_path], check=True)
            elif system == "Windows":
                os.startfile(image_path)
            else:  # Linux
                subprocess.run(["xdg-open", image_path], check=True)
            
            return True
        except Exception as e:
            print(f"Could not open image: {e}")
            return False
    
    def create_and_show_complexity_graph(self, code: str, problem_name: str) -> bool:
        """Analyze code and create/show complexity graph"""
        try:
            # Analyze user's code
            user_analysis = self.analyze_code_complexity(code)
            
            # Get optimal complexity
            optimal_analysis = self.get_optimal_complexity(problem_name)
            
            # Create graph
            graph_path = self.create_complexity_graph(
                user_analysis, 
                optimal_analysis, 
                problem_name
            )
            
            # Open graph
            success = self.open_image(graph_path)
            
            return success
            
        except Exception as e:
            print(f"Error creating complexity graph: {e}")
            return False
