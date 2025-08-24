#!/usr/bin/env python3
"""
DSA Learning System - Main Entry Point
"""

import sys
import os
from pathlib import Path
import typer
from rich.console import Console

from .controllers.cli import DSACLIController


app = typer.Typer(
    name="dsa",
    help="🎓 DSA Learning System - Your RPG-style coding journey!",
    rich_markup_mode="rich"
)

console = Console()


@app.command("setup")
def setup_workspace(
    path: str = typer.Option(".", "--path", "-p", help="Directory to setup DSA workspace")
):
    """🚀 Setup DSA workspace in current or specified directory"""
    
    # Use current working directory if path is "."
    if path == ".":
        workspace_path = Path.cwd()
    else:
        workspace_path = Path(path).resolve()
        # Create the directory if it doesn't exist
        workspace_path.mkdir(parents=True, exist_ok=True)
    
    console.print(f"🚀 Setting up DSA workspace in: [cyan]{workspace_path}[/cyan]")
    
    try:
        # Create category directories
        categories = [
            "arrays_and_hashing", "two_pointers", "sliding_window", "stack",
            "binary_search", "linked_list", "trees", "tries", "heap_priority_queue",
            "backtracking", "graphs", "advanced_graphs", "1d_dynamic_programming",
            "2d_dynamic_programming", "greedy", "intervals", "math_and_geometry",
            "bit_manipulation"
        ]
        
        for category in categories:
            (workspace_path / category).mkdir(exist_ok=True)
        
        # Copy problem database
        import json
        from importlib import resources
        
        # Create problem list - Complete NeetCode 75
        problem_data = {
            "neetcode_75": [
                {
                    "category": "arrays_and_hashing",
                    "problems": [
                        {"name": "Two Sum", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/two-sum/", "order": 1},
                        {"name": "Valid Anagram", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/valid-anagram/", "order": 2},
                        {"name": "Contains Duplicate", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/contains-duplicate/", "order": 3},
                        {"name": "Group Anagrams", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/group-anagrams/", "order": 4},
                        {"name": "Top K Frequent Elements", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/top-k-frequent-elements/", "order": 5},
                        {"name": "Product of Array Except Self", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/product-of-array-except-self/", "order": 6},
                        {"name": "Valid Sudoku", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/valid-sudoku/", "order": 7},
                        {"name": "Encode and Decode Strings", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/encode-and-decode-strings/", "order": 8},
                        {"name": "Longest Consecutive Sequence", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/longest-consecutive-sequence/", "order": 9}
                    ]
                },
                {
                    "category": "two_pointers",
                    "problems": [
                        {"name": "Valid Palindrome", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/valid-palindrome/", "order": 10},
                        {"name": "Two Sum II", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/", "order": 11},
                        {"name": "3Sum", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/3sum/", "order": 12},
                        {"name": "Container With Most Water", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/container-with-most-water/", "order": 13},
                        {"name": "Trapping Rain Water", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/trapping-rain-water/", "order": 14}
                    ]
                },
                {
                    "category": "sliding_window",
                    "problems": [
                        {"name": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "order": 15},
                        {"name": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "order": 16},
                        {"name": "Longest Repeating Character Replacement", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/longest-repeating-character-replacement/", "order": 17},
                        {"name": "Permutation in String", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/permutation-in-string/", "order": 18},
                        {"name": "Minimum Window Substring", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/minimum-window-substring/", "order": 19},
                        {"name": "Sliding Window Maximum", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/sliding-window-maximum/", "order": 20}
                    ]
                },
                {
                    "category": "stack",
                    "problems": [
                        {"name": "Valid Parentheses", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/valid-parentheses/", "order": 21},
                        {"name": "Min Stack", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/min-stack/", "order": 22},
                        {"name": "Evaluate Reverse Polish Notation", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/evaluate-reverse-polish-notation/", "order": 23},
                        {"name": "Generate Parentheses", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/generate-parentheses/", "order": 24},
                        {"name": "Daily Temperatures", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/daily-temperatures/", "order": 25},
                        {"name": "Car Fleet", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/car-fleet/", "order": 26},
                        {"name": "Largest Rectangle in Histogram", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/largest-rectangle-in-histogram/", "order": 27}
                    ]
                },
                {
                    "category": "binary_search",
                    "problems": [
                        {"name": "Binary Search", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/binary-search/", "order": 28},
                        {"name": "Search a 2D Matrix", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/search-a-2d-matrix/", "order": 29},
                        {"name": "Koko Eating Bananas", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/koko-eating-bananas/", "order": 30},
                        {"name": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/", "order": 31},
                        {"name": "Search in Rotated Sorted Array", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/search-in-rotated-sorted-array/", "order": 32},
                        {"name": "Time Based Key-Value Store", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/time-based-key-value-store/", "order": 33},
                        {"name": "Median of Two Sorted Arrays", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/median-of-two-sorted-arrays/", "order": 34}
                    ]
                },
                {
                    "category": "linked_list",
                    "problems": [
                        {"name": "Reverse Linked List", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/reverse-linked-list/", "order": 35},
                        {"name": "Linked List Cycle", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/linked-list-cycle/", "order": 36},
                        {"name": "Merge Two Sorted Lists", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/merge-two-sorted-lists/", "order": 37},
                        {"name": "Remove Nth Node From End of List", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "order": 38},
                        {"name": "Copy List with Random Pointer", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/copy-list-with-random-pointer/", "order": 39},
                        {"name": "Add Two Numbers", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/add-two-numbers/", "order": 40},
                        {"name": "Find the Duplicate Number", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/find-the-duplicate-number/", "order": 41},
                        {"name": "LRU Cache", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/lru-cache/", "order": 42},
                        {"name": "Merge k Sorted Lists", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/merge-k-sorted-lists/", "order": 43},
                        {"name": "Reverse Nodes in k-Group", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/reverse-nodes-in-k-group/", "order": 44}
                    ]
                },
                {
                    "category": "trees",
                    "problems": [
                        {"name": "Invert Binary Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/invert-binary-tree/", "order": 45},
                        {"name": "Maximum Depth of Binary Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "order": 46},
                        {"name": "Diameter of Binary Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/diameter-of-binary-tree/", "order": 47},
                        {"name": "Balanced Binary Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/balanced-binary-tree/", "order": 48},
                        {"name": "Same Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/same-tree/", "order": 49},
                        {"name": "Subtree of Another Tree", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/subtree-of-another-tree/", "order": 50},
                        {"name": "Lowest Common Ancestor of a Binary Search Tree", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/", "order": 51},
                        {"name": "Binary Tree Level Order Traversal", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/binary-tree-level-order-traversal/", "order": 52},
                        {"name": "Binary Tree Right Side View", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/binary-tree-right-side-view/", "order": 53},
                        {"name": "Count Good Nodes in Binary Tree", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/count-good-nodes-in-binary-tree/", "order": 54},
                        {"name": "Validate Binary Search Tree", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/validate-binary-search-tree/", "order": 55},
                        {"name": "Kth Smallest Element in a BST", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/kth-smallest-element-in-a-bst/", "order": 56},
                        {"name": "Construct Binary Tree from Preorder and Inorder Traversal", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/", "order": 57},
                        {"name": "Binary Tree Maximum Path Sum", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/binary-tree-maximum-path-sum/", "order": 58},
                        {"name": "Serialize and Deserialize Binary Tree", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/serialize-and-deserialize-binary-tree/", "order": 59}
                    ]
                },
                {
                    "category": "tries",
                    "problems": [
                        {"name": "Implement Trie (Prefix Tree)", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/implement-trie-prefix-tree/", "order": 60},
                        {"name": "Design Add and Search Words Data Structure", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/design-add-and-search-words-data-structure/", "order": 61},
                        {"name": "Word Search II", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/word-search-ii/", "order": 62}
                    ]
                },
                {
                    "category": "heap_priority_queue",
                    "problems": [
                        {"name": "Kth Largest Element in a Stream", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/kth-largest-element-in-a-stream/", "order": 63},
                        {"name": "Last Stone Weight", "difficulty": "Easy", "leetcode_url": "https://leetcode.com/problems/last-stone-weight/", "order": 64},
                        {"name": "K Closest Points to Origin", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/k-closest-points-to-origin/", "order": 65},
                        {"name": "Kth Largest Element in an Array", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/kth-largest-element-in-an-array/", "order": 66},
                        {"name": "Task Scheduler", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/task-scheduler/", "order": 67},
                        {"name": "Design Twitter", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/design-twitter/", "order": 68},
                        {"name": "Find Median from Data Stream", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/find-median-from-data-stream/", "order": 69}
                    ]
                },
                {
                    "category": "backtracking",
                    "problems": [
                        {"name": "Subsets", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/subsets/", "order": 70},
                        {"name": "Combination Sum", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/combination-sum/", "order": 71},
                        {"name": "Permutations", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/permutations/", "order": 72},
                        {"name": "Subsets II", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/subsets-ii/", "order": 73},
                        {"name": "Combination Sum II", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/combination-sum-ii/", "order": 74},
                        {"name": "Word Search", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/word-search/", "order": 75},
                        {"name": "Palindrome Partitioning", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/palindrome-partitioning/", "order": 76},
                        {"name": "Letter Combinations of a Phone Number", "difficulty": "Medium", "leetcode_url": "https://leetcode.com/problems/letter-combinations-of-a-phone-number/", "order": 77},
                        {"name": "N-Queens", "difficulty": "Hard", "leetcode_url": "https://leetcode.com/problems/n-queens/", "order": 78}
                    ]
                }
            ]
        }
        
        # Write problem list
        with open(workspace_path / "problem_list.json", "w") as f:
            json.dump(problem_data, f, indent=2)
        
        # Create initial progress file
        initial_progress = {
            "completed_problems": [],
            "current_problem_index": 0,
            "last_updated": "",
            "stats": {
                "total_completed": 0,
                "easy_completed": 0,
                "medium_completed": 0,
                "hard_completed": 0
            },
            "current_working_problem": None,
            "game_data": {
                "xp": 0,
                "level": 1,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "daily_activities": {},
                "achievements": [],
                "total_xp_earned": 0,
                "problems_attempted_today": 0,
                "perfect_solutions": 0,
                "speed_completions": 0
            }
        }
        
        with open(workspace_path / "progress.json", "w") as f:
            json.dump(initial_progress, f, indent=2)
        
        # Create README
        readme_content = """# 🎓 My DSA Learning Journey

Welcome to your personal DSA workspace! 🚀

## 🎮 Quick Start

```bash
# Check your RPG profile
dsa profile

# Get your first problem
dsa next

# Complete problems and level up!
dsa done
```

## 📁 Workspace Structure

- `arrays_and_hashing/` - Array and hash table problems
- `two_pointers/` - Two pointer technique problems
- `sliding_window/` - Sliding window problems
- `stack/` - Stack-based problems
- ... (and more categories)

## 🎯 Commands

- `dsa profile` - View your RPG stats
- `dsa next` - Get next problem
- `dsa done` - Complete with full analysis
- `dsa dashboard` - Visual progress
- `dsa reset` - Start fresh

## 🏆 Your Journey

Track your progress from 🌱 Coding Seedling to 🎯 NeetCode Deity!

Happy coding! 🎉
"""
        
        with open(workspace_path / "README.md", "w") as f:
            f.write(readme_content)
        
        console.print("✅ [green]Workspace setup complete![/green]")
        console.print(f"📁 Created directories for all problem categories")
        console.print(f"📊 Initialized progress tracking")
        console.print(f"📋 Added problem database")
        
        console.print("\n🎯 [bold]Next steps:[/bold]")
        if str(workspace_path) != str(Path.cwd()):
            console.print(f"1. [cyan]cd {workspace_path}[/cyan]")
            console.print("2. [green]dsa profile[/green] - Check your starting stats")
            console.print("3. [yellow]dsa next[/yellow] - Get your first problem")
            console.print("4. [blue]dsa dashboard[/blue] - See your progress")
        else:
            console.print("1. [green]dsa profile[/green] - Check your starting stats")
            console.print("2. [yellow]dsa next[/yellow] - Get your first problem")
            console.print("3. [blue]dsa dashboard[/blue] - See your progress")
        
        console.print("\n🎮 [bold green]Welcome to your DSA RPG adventure![/bold green] 🌱")
        console.print("\n💫 [bold cyan]Good luck on your journey![/bold cyan]")
        console.print("   [dim]- Neon (Discord: neon8052)[/dim]")
        
    except Exception as e:
        console.print(f"❌ [red]Setup failed: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point for the DSA CLI"""
    
    # Add setup command to the main app
    app.command("setup")(setup_workspace)
    
    # Check if we're running the setup command
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Run setup directly
        app()
        return
    
    # Check if we're in a DSA workspace (has progress.json and problem_list.json)
    current_dir = Path.cwd()
    
    if not (current_dir / "progress.json").exists() or not (current_dir / "problem_list.json").exists():
        # Not in a workspace, show setup help
        console.print("🎓 [bold blue]DSA Learning System[/bold blue]")
        console.print("\n❌ [yellow]Not in a DSA workspace![/yellow]")
        console.print("\n🚀 [bold]To get started:[/bold]")
        console.print("1. [cyan]dsa setup[/cyan] - Setup workspace in current directory")
        console.print("2. [cyan]dsa setup --path /folder[/cyan] - Setup in specific directory")
        console.print("\n💡 [dim]The workspace contains your progress, problems, and solutions.[/dim]")
        console.print(f"\n🔧 Run [green]dsa setup[/green] to create your workspace!")
        return
    
    # We're in a workspace, run the full CLI
    controller = DSACLIController(current_dir)
    
    try:
        controller.app()
    except KeyboardInterrupt:
        console.print("\n👋 Happy coding!")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
