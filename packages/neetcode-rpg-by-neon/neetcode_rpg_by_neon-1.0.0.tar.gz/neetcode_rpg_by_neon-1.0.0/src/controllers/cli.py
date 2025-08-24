"""
CLI Controller - Main command line interface using Typer
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from ..models.problem import ProblemModel
from ..models.progress import ProgressModel
from ..services.problem_service import ProblemService
from ..services.rpg_service import RPGService
from ..views.console import ConsoleView


class DSACLIController:
    """Main CLI controller"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.console_view = ConsoleView()
        
        # Initialize models
        self.problem_model = ProblemModel(base_dir / "problem_list.json")
        self.progress_model = ProgressModel(base_dir / "progress.json")
        
        # Initialize services
        self.problem_service = ProblemService(
            self.problem_model, 
            self.progress_model, 
            base_dir
        )
        self.rpg_service = RPGService(self.progress_model)
        
        # Create Typer app
        self.app = typer.Typer(
            name="dsa",
            help="🎓 DSA Learning System - Your RPG-style coding journey!",
            rich_markup_mode="rich"
        )
        
        # Register commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all CLI commands"""
        
        @self.app.command("next")
        def next_problem():
            """🎯 Get next problem and create file"""
            self.cmd_next()
        
        @self.app.command("done")
        def complete_problem():
            """🚀 SMART COMPLETE: Full analysis + test + mark done"""
            self.cmd_done()
        
        @self.app.command("done-quick")
        def complete_quick():
            """⚡ QUICK: Test + mark complete (no analysis)"""
            self.cmd_done_quick()
        
        @self.app.command("done-basic")
        def complete_basic():
            """📝 BASIC: Just mark complete (no testing)"""
            self.cmd_done_basic()
        
        @self.app.command("current")
        def show_current():
            """👀 Show current working problem"""
            self.cmd_current()
        
        @self.app.command("test")
        def test_solution():
            """🧪 Test current solution"""
            self.cmd_test()
        
        @self.app.command("analyze")
        def analyze_solution():
            """🔍 Analyze code quality and performance"""
            self.cmd_analyze()
        
        @self.app.command("profile")
        def show_profile():
            """👤 View your RPG stats, level, XP, and title"""
            self.cmd_profile()
        
        @self.app.command("daily")
        def show_daily():
            """📅 Today's XP and activity log"""
            self.cmd_daily()
        
        @self.app.command("dashboard")
        def show_dashboard():
            """📊 Visual progress dashboard with charts"""
            self.cmd_dashboard()
        
        @self.app.command("achievements")
        def show_achievements():
            """🏅 View your badges and milestones"""
            self.cmd_achievements()
        
        @self.app.command("list")
        def list_problems():
            """📋 List all problems with status"""
            self.cmd_list()
        
        @self.app.command("status")
        def show_status():
            """📊 Show progress and current problem"""
            self.cmd_status()
        
        @self.app.command("reset")
        def reset_progress():
            """🔄 Reset all progress (start fresh)"""
            self.cmd_reset()
        
        @self.app.command("hint")
        def get_hint(problem_name: Optional[str] = None):
            """💡 Get hints for current or specific problem"""
            self.cmd_hint(problem_name)
    
    def cmd_next(self):
        """Get next problem and create file"""
        next_problem = self.problem_service.get_next_problem()
        
        if not next_problem:
            self.console_view.print_success("🎉 Congratulations! You've completed all problems!")
            return
        
        self.console_view.show_problem(next_problem)
        
        # Set as current working problem
        self.problem_service.set_current_working_problem(next_problem)
        
        # Create problem file
        if self.problem_service.create_problem_file(next_problem):
            self.console_view.print_success(f"✅ Created: {next_problem.filepath}")
            
            self.console_view.print("\n💡 [bold]Next steps:[/bold]")
            self.console_view.print(f"1. Visit: [link]{next_problem.leetcode_url}[/link]")
            self.console_view.print("2. Read the problem description carefully")
            self.console_view.print(f"3. Open and implement: [cyan]{next_problem.filepath}[/cyan]")
            self.console_view.print(f"4. Test: [yellow]dsa test[/yellow]")
            self.console_view.print(f"5. When done: [green]dsa done[/green]")
        else:
            self.console_view.print_error("Failed to create problem file")
    
    def cmd_done(self):
        """Complete problem with full analysis, benchmarking, and visual graphs"""
        current_problem = self._get_current_or_next_problem()
        if not current_problem:
            return
        
        self.console_view.print_header("🚀 SMART COMPLETE", current_problem.name)
        
        # First, check if solution is implemented (lightweight check)
        file_path = self.problem_service.base_dir / current_problem.filepath
        if not file_path.exists():
            self.console_view.print_error("❌ Solution file not found!")
            return
        
        # Quick implementation check
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            if 'pass' in code and 'TODO' in code:
                self.console_view.print_error("❌ Solution not implemented!")
                self.console_view.print("💡 You need to actually implement the solution to earn XP.")
                self.console_view.print("📝 Replace the 'pass' statement and 'TODO' comments with your code.")
                self.console_view.print(f"📁 Edit: [cyan]{current_problem.filepath}[/cyan]")
                return
        except Exception as e:
            self.console_view.print_error(f"❌ Error reading solution file: {e}")
            return
        
        # Test solution FIRST
        self.console_view.print("🧪 Testing solution...")
        success, output = self.problem_service.test_solution(current_problem)
        
        if not success:
            self.console_view.print_error("❌ Tests failed")
            self.console_view.print(output)
            self.console_view.print_info("Fix your solution before marking as done")
            return
        
        # Tests passed! Now do full analysis and benchmarking
        self.console_view.print_success("✅ All tests passed!")
        if output and "All test cases passed!" not in output:
            self.console_view.print(output)
        
        # Now run full analysis (including performance benchmarking)
        self.console_view.print("🔍 Running performance analysis...")
        self.console_view.print("⏱️  Benchmarking solution (3 runs)...")
        analysis = self.problem_service.analyze_solution(current_problem)
        self.console_view.show_analysis_results(analysis)
        
        # Generate visual complexity graph
        try:
            from ..services.graph_service import GraphService
            import warnings
            
            self.console_view.print("📊 Generating complexity visualization...")
            
            # Suppress matplotlib warnings during graph generation
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                graph_service = GraphService()
                graph_success = graph_service.create_and_show_complexity_graph(
                    code=analysis["code"],
                    problem_name=current_problem.name
                )
            
            if graph_success:
                self.console_view.print_success("📊 Complexity graph opened in your image viewer!")
                self.console_view.print_info("💡 Linear plots show how your solution scales with input size!")
            else:
                self.console_view.print_warning("⚠️  Could not open complexity graph")
                
        except ImportError:
            self.console_view.print_warning("📊 Visual analysis not available (missing matplotlib/pillow)")
        except Exception as e:
            self.console_view.print_error(f"📊 Graph generation failed: {e}")
        
        # Award XP
        xp_result = self.rpg_service.award_xp("problem_solved", current_problem.difficulty)
        
        # Bonus XP for perfect solution
        if analysis.get("perfect_solution", False):
            perfect_result = self.rpg_service.award_xp("perfect_solution")
            xp_result["xp_earned"] += perfect_result["xp_earned"]
        
        # Speed bonus
        if analysis.get("fast_completion", False):
            speed_result = self.rpg_service.award_xp("speed_completion")
            xp_result["xp_earned"] += speed_result["xp_earned"]
        
        self.console_view.show_xp_reward(xp_result)
        
        # Mark as completed
        self.problem_service.mark_problem_completed(current_problem)
        self.problem_service.clear_current_working_problem()
        
        # Show next problem
        next_problem = self.problem_service.get_next_problem()
        if next_problem:
            self.console_view.print(f"\n🎯 [bold]Next up:[/bold] {next_problem.name} ({next_problem.difficulty})")
            self.console_view.print("Run [green]dsa next[/green] when ready!")
        else:
            self.console_view.print_success("🏆 ALL PROBLEMS COMPLETED! AMAZING WORK!")
    
    def cmd_done_quick(self):
        """Quick completion without analysis"""
        current_problem = self._get_current_or_next_problem()
        if not current_problem:
            return
        
        self.console_view.print_header("⚡ QUICK COMPLETE", current_problem.name)
        
        # Check if solution is implemented
        analysis = self.problem_service.analyze_solution(current_problem)
        if not analysis.get("solution_implemented", False):
            self.console_view.print_error("❌ Solution not implemented!")
            self.console_view.print("💡 You need to actually implement the solution to earn XP.")
            self.console_view.print("📝 Replace the 'pass' statement and 'TODO' comments with your code.")
            self.console_view.print(f"📁 Edit: [cyan]{current_problem.filepath}[/cyan]")
            return
        
        success, output = self.problem_service.test_solution(current_problem)
        
        if success:
            self.console_view.print_success("🧪 Tests passed!")
            
            # Award XP (with speed bonus)
            xp_result = self.rpg_service.award_xp("problem_solved", current_problem.difficulty)
            speed_result = self.rpg_service.award_xp("speed_completion")
            xp_result["xp_earned"] += speed_result["xp_earned"]
            
            self.console_view.show_xp_reward(xp_result)
            
            # Mark as completed
            self.problem_service.mark_problem_completed(current_problem)
            self.problem_service.clear_current_working_problem()
            
            self.console_view.print_success("✅ Problem completed!")
        else:
            self.console_view.print_error("Tests failed. Fix your solution first.")
            self.console_view.print(output)
    
    def cmd_done_basic(self):
        """Basic completion without testing"""
        current_problem = self._get_current_or_next_problem()
        if not current_problem:
            return
        
        self.console_view.print_header("📝 BASIC COMPLETE", current_problem.name)
        
        # Award half XP for basic completion
        xp_result = self.rpg_service.award_xp("problem_solved", current_problem.difficulty)
        xp_result["xp_earned"] = xp_result["xp_earned"] // 2
        
        self.console_view.print_warning(f"Basic completion: Half XP awarded ({xp_result['xp_earned']} XP)")
        self.console_view.print_info("Use 'dsa done' or 'dsa done-quick' for full XP!")
        
        # Mark as completed
        self.problem_service.mark_problem_completed(current_problem)
        self.problem_service.clear_current_working_problem()
        
        self.console_view.print_success("✅ Problem marked as completed (no testing performed)")
    
    def cmd_current(self):
        """Show current working problem"""
        current_problem = self.problem_service.get_current_working_problem()
        
        if not current_problem:
            self.console_view.print_error("No current working problem set.")
            self.console_view.print_info("Run 'dsa next' to get a problem to work on.")
            return
        
        self.console_view.show_problem(current_problem)
        
        # Check if file exists
        file_path = self.base_dir / current_problem.filepath
        if file_path.exists():
            self.console_view.print_success(f"📁 File exists: {current_problem.filepath}")
        else:
            self.console_view.print_error(f"📁 File missing: {current_problem.filepath}")
            self.console_view.print_info("Run 'dsa next' to create the file.")
    
    def cmd_test(self):
        """Test current solution"""
        current_problem = self._get_current_or_next_problem()
        if not current_problem:
            return
        
        self.console_view.print_header("🧪 Testing Solution", current_problem.name)
        
        success, output = self.problem_service.test_solution(current_problem)
        
        if success:
            self.console_view.print_success("All tests passed!")
            if output and "All test cases passed!" not in output:
                self.console_view.print(output)
        else:
            self.console_view.print_error("Tests failed")
            self.console_view.print(output)
    
    def cmd_analyze(self):
        """Analyze current solution with visual complexity graphs"""
        current_problem = self._get_current_or_next_problem()
        if not current_problem:
            return
        
        self.console_view.print_header("🔍 Code Analysis", current_problem.name)
        
        analysis = self.problem_service.analyze_solution(current_problem)
        self.console_view.show_analysis_results(analysis)
        
        # Generate visual complexity graph if solution is implemented
        if analysis.get("solution_implemented", False) and analysis.get("code"):
            try:
                from ..services.graph_service import GraphService
                import warnings
                
                # Suppress matplotlib warnings during graph generation
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    
                    graph_service = GraphService()
                    success = graph_service.create_and_show_complexity_graph(
                        code=analysis["code"],
                        problem_name=current_problem.name
                    )
                
                if success:
                    self.console_view.print_success("📊 Complexity graph opened in your image viewer!")
                    self.console_view.print_info("💡 Compare your solution's complexity with the optimal approach!")
                else:
                    self.console_view.print_warning("⚠️  Could not open complexity graph")
                    
            except ImportError:
                self.console_view.print_warning("📊 Visual analysis not available (missing matplotlib/pillow)")
            except Exception as e:
                self.console_view.print_error(f"📊 Graph generation failed: {e}")
    
    def cmd_profile(self):
        """Show RPG profile"""
        stats = self.rpg_service.get_player_stats()
        self.console_view.show_player_profile(stats)
        
        # Show daily summary
        daily_data = self.rpg_service.get_daily_summary()
        self.console_view.show_daily_summary(daily_data)
    
    def cmd_daily(self):
        """Show daily activity"""
        daily_data = self.rpg_service.get_daily_summary()
        self.console_view.show_daily_summary(daily_data)
        
        # Show streak motivation
        stats = self.rpg_service.get_player_stats()
        
        if stats['current_streak'] == 0:
            self.console_view.print_info("Start your streak today! Complete any problem to begin.")
        elif stats['current_streak'] < 7:
            days_left = 7 - stats['current_streak']
            self.console_view.print(f"🎯 {days_left} more days to reach weekly streak bonus!")
        elif stats['current_streak'] % 7 == 0:
            self.console_view.print_success("🎉 Weekly streak achieved! Massive XP multiplier active!")
        else:
            days_to_next_week = 7 - (stats['current_streak'] % 7)
            self.console_view.print(f"⚡ {days_to_next_week} more days to next weekly milestone!")
    
    def cmd_dashboard(self):
        """Show progress dashboard"""
        categories_progress = self.problem_service.get_all_categories_progress()
        overall_stats = self.progress_model.progress.stats.__dict__
        
        self.console_view.show_progress_dashboard(categories_progress, overall_stats)
    
    def cmd_achievements(self):
        """Show achievements"""
        stats = self.rpg_service.get_player_stats()
        total_completed = self.progress_model.progress.stats.total_completed
        
        # Generate achievements
        achievements = []
        
        if total_completed >= 1:
            achievements.append("🥉 First Problem - Completed your first DSA problem!")
        if total_completed >= 5:
            achievements.append("🚀 Getting Started - 5 problems solved!")
        if total_completed >= 10:
            achievements.append("🥈 Problem Solver - 10 problems conquered!")
        if total_completed >= 25:
            achievements.append("🥇 Algorithm Master - 25 problems completed!")
        if total_completed >= 50:
            achievements.append("🏆 DSA Expert - 50 problems solved!")
        if total_completed >= 75:
            achievements.append("👑 NeetCode Champion - All 75 problems completed!")
        
        if stats['current_streak'] >= 3:
            achievements.append("🔥 On Fire - Solving problems consistently!")
        if stats['current_streak'] >= 7:
            achievements.append("⚡ Lightning Fast - 7+ day streak!")
        
        # Next milestone
        next_milestone = None
        if total_completed < 1:
            next_milestone = "Complete 1 problem to earn 'First Problem' badge"
        elif total_completed < 5:
            next_milestone = f"Complete {5 - total_completed} more problems to earn 'Getting Started' badge"
        elif total_completed < 10:
            next_milestone = f"Complete {10 - total_completed} more problems to earn 'Problem Solver' badge"
        
        self.console_view.show_achievements(achievements, next_milestone)
    
    def cmd_list(self):
        """List all problems"""
        problems = self.problem_model.problems
        completed_problems = self.progress_model.progress.completed_problems
        
        self.console_view.show_problem_list(problems, completed_problems)
    
    def cmd_status(self):
        """Show status"""
        stats = self.progress_model.progress.stats
        total_problems = len(self.problem_model.problems)
        
        if total_problems > 0:
            percentage = (stats.total_completed / total_problems) * 100
        else:
            percentage = 0
        
        status_text = f"""
[green]📊 Progress: {stats.total_completed}/{total_problems} ({percentage:.1f}%)[/green]
[blue]🟢 Easy: {stats.easy_completed}[/blue]
[yellow]🟡 Medium: {stats.medium_completed}[/yellow]
[red]🔴 Hard: {stats.hard_completed}[/red]
        """.strip()
        
        self.console_view.console.print(status_text)
        
        # Show current working problem
        current_problem = self.problem_service.get_current_working_problem()
        if current_problem:
            self.console_view.print(f"\n🔧 [bold]Currently Working On:[/bold] {current_problem.name} ({current_problem.difficulty})")
        
        # Show next problem
        next_problem = self.problem_service.get_next_problem()
        if next_problem:
            if not current_problem or current_problem.problem_id != next_problem.problem_id:
                self.console_view.print(f"🎯 [bold]Next Problem:[/bold] {next_problem.name} ({next_problem.difficulty})")
    
    def cmd_reset(self):
        """Reset progress"""
        self.console_view.print_header("🔄 Reset DSA Progress")
        
        self.console_view.print("This will reset your progress back to the beginning:")
        self.console_view.print("• XP, level, and streaks → 0")
        self.console_view.print("• All completed problems → unmarked")
        self.console_view.print("• Current working problem → cleared")
        
        # Ask about solution files
        delete_solutions = self.console_view.get_user_input(
            "Also delete your solution files? (y/n)", "n"
        ).lower() in ['y', 'yes']
        
        if delete_solutions:
            self.console_view.print_warning("⚠️  WARNING: This will delete ALL your solution files!")
            self.console_view.print("You will lose all your code implementations.")
        
        # Final confirmation
        if not self.console_view.confirm_action(
            "🚨 Final confirmation needed! This cannot be undone.", "RESET"
        ):
            self.console_view.print_error("Reset cancelled.")
            return
        
        try:
            # Reset progress
            self.progress_model.reset_all()
            
            deleted_files = 0
            if delete_solutions:
                deleted_files = self.problem_service.delete_solution_files()
            
            # Show success message
            self.console_view.print_success("✅ Reset Complete!")
            self.console_view.print("🌱 You are now a Level 1 Coding Seedling")
            self.console_view.print("🎯 All progress has been cleared")
            
            if deleted_files > 0:
                self.console_view.print(f"🗑️  Deleted {deleted_files} solution files")
            else:
                self.console_view.print("📁 Solution files kept (you can reuse your code)")
            
            self.console_view.print("\n🚀 Ready to start fresh!")
            self.console_view.print_info("Next steps:")
            self.console_view.print("  1. dsa profile")
            self.console_view.print("  2. dsa next")
            self.console_view.print("  3. Start your coding journey again!")
            
        except Exception as e:
            self.console_view.print_error(f"Reset failed: {e}")
    
    def cmd_hint(self, problem_name: Optional[str] = None):
        """Get hints for problem"""
        if problem_name:
            self.console_view.print_info(f"Hints for '{problem_name}' - Feature coming soon!")
        else:
            current_problem = self._get_current_or_next_problem()
            if current_problem:
                self.console_view.print_info(f"Hints for '{current_problem.name}' - Feature coming soon!")
    
    def _get_current_or_next_problem(self):
        """Get current working problem or next problem"""
        current_problem = self.problem_service.get_current_working_problem()
        
        if not current_problem:
            current_problem = self.problem_service.get_next_problem()
            if current_problem:
                self.console_view.print_warning("No current working problem set. Using next uncompleted problem.")
                self.problem_service.set_current_working_problem(current_problem)
        
        if not current_problem:
            self.console_view.print_success("🎉 No problems to work on!")
            return None
        
        return current_problem
