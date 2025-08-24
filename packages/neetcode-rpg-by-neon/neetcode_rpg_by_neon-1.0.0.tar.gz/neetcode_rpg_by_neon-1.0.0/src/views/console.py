"""
Console Views - Beautiful CLI output using Rich
"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import box

from ..models.problem import Problem


class ConsoleView:
    """Rich console view for beautiful CLI output"""
    
    def __init__(self):
        self.console = Console()
    
    def print(self, *args, **kwargs):
        """Print to console"""
        self.console.print(*args, **kwargs)
    
    def print_header(self, title: str, subtitle: str = None):
        """Print a beautiful header"""
        if subtitle:
            header_text = f"[bold blue]{title}[/bold blue]\n[dim]{subtitle}[/dim]"
        else:
            header_text = f"[bold blue]{title}[/bold blue]"
        
        self.console.print(Panel(header_text, box=box.DOUBLE))
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"✅ [green]{message}[/green]")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"❌ [red]{message}[/red]")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"⚠️  [yellow]{message}[/yellow]")
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"💡 [cyan]{message}[/cyan]")
    
    def show_problem(self, problem: Problem):
        """Display problem information"""
        difficulty_colors = {
            "Easy": "green",
            "Medium": "yellow", 
            "Hard": "red"
        }
        
        difficulty_color = difficulty_colors.get(problem.difficulty, "white")
        
        problem_info = f"""
[bold]{problem.name}[/bold]
[{difficulty_color}]Difficulty: {problem.difficulty}[/{difficulty_color}]
Category: {problem.category.replace('_', ' ').title()}
LeetCode: [link]{problem.leetcode_url}[/link]
File: [cyan]{problem.filepath}[/cyan]
        """.strip()
        
        self.console.print(Panel(problem_info, title="📚 Problem", box=box.ROUNDED))
    
    def show_xp_reward(self, xp_data: Dict):
        """Display XP reward with epic styling"""
        xp_text = f"""
[bold green]🎯 {xp_data['activity_description']}[/bold green]
[yellow]💰 Base XP: +{xp_data['base_xp']}[/yellow]
"""
        
        if xp_data['streak_xp'] > 0:
            xp_text += f"[orange1]🔥 Streak Bonus: +{xp_data['streak_xp']} (Day {xp_data['current_streak']})[/orange1]\n"
        
        for multiplier in xp_data['multipliers']:
            xp_text += f"[magenta]✨ {multiplier}[/magenta]\n"
        
        xp_text += f"\n[bold cyan]🏆 Total XP Earned: +{xp_data['xp_earned']}[/bold cyan]"
        xp_text += f"\n[blue]📊 Current XP: {xp_data['current_xp']:,}[/blue]"
        
        if xp_data['level_up']:
            xp_text += f"\n\n[bold yellow]🌟 LEVEL UP! {xp_data['old_level']} → {xp_data['new_level']} 🌟[/bold yellow]"
        else:
            xp_text += f"\n[dim]📈 XP to next level: {xp_data['xp_to_next']}[/dim]"
        
        self.console.print(Panel(xp_text, title="🎮 XP GAINED!", box=box.DOUBLE, border_style="bright_yellow"))
    
    def show_player_profile(self, stats: Dict):
        """Display player RPG profile"""
        # Create XP progress bar
        if stats["xp_for_next_level"] > 0:
            progress = stats["xp_in_current_level"] / stats["xp_for_next_level"]
            bar_width = 30
            filled = int(bar_width * progress)
            xp_bar = "█" * filled + "░" * (bar_width - filled)
            xp_display = f"{xp_bar} {stats['xp_in_current_level']}/{stats['xp_for_next_level']} XP"
        else:
            xp_display = "MAX LEVEL! 🎉"
        
        profile_text = f"""
[bold cyan]👤 {stats['title']}[/bold cyan]
[yellow]⭐ Level: {stats['level']}[/yellow]
[green]⚡ XP: {stats['xp']:,}[/green]
[blue]📊 Progress: {xp_display}[/blue]
[red]🔥 Current Streak: {stats['current_streak']} days[/red]
[purple]🏆 Longest Streak: {stats['longest_streak']} days[/purple]
[cyan]📈 Total XP Earned: {stats['total_xp_earned']:,}[/cyan]
[green]📅 Problems Today: {stats['problems_today']}[/green]
[yellow]✨ Perfect Solutions: {stats['perfect_solutions']}[/yellow]
[orange1]⚡ Speed Completions: {stats['speed_completions']}[/orange1]
        """.strip()
        
        self.console.print(Panel(profile_text, title="🎮 Player Profile", box=box.DOUBLE))
    
    def show_daily_summary(self, daily_data: Dict):
        """Display daily activity summary"""
        if not daily_data["has_activities"]:
            self.console.print(Panel(
                "[dim]📅 No activities today yet. Start coding to earn XP![/dim]",
                title="📅 Today's Adventure Log"
            ))
            return
        
        # Create activity table
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("Time", style="cyan")
        table.add_column("Activity", style="green")
        table.add_column("XP", style="yellow", justify="right")
        
        for activity in daily_data["activities"]:
            table.add_row(
                activity["time"],
                activity["activity"],
                f"+{activity['xp']}"
            )
        
        summary_text = f"""
[bold green]🎯 Total XP Today: {daily_data['total_xp_today']}[/bold green]
[red]🔥 Current Streak: {daily_data['current_streak']} days[/red]
        """.strip()
        
        self.console.print(Panel(table, title="📅 Today's Adventure Log"))
        self.console.print(Panel(summary_text, box=box.SIMPLE))
    
    def show_progress_dashboard(self, categories_progress: List[Dict], overall_stats: Dict):
        """Display visual progress dashboard"""
        # Overall progress
        total_completed = overall_stats.get("total_completed", 0)
        total_problems = sum(cat["total"] for cat in categories_progress)
        
        if total_problems > 0:
            overall_progress = total_completed / total_problems
            bar_width = 40
            filled = int(bar_width * overall_progress)
            overall_bar = "█" * filled + "░" * (bar_width - filled)
            overall_display = f"{overall_bar} {overall_progress*100:.1f}%"
        else:
            overall_display = "No problems available"
        
        self.console.print(Panel(
            f"[bold green]📈 Overall Progress: {overall_display}[/bold green]",
            title="🎓 DSA Learning Dashboard"
        ))
        
        # Category progress table
        table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        table.add_column("Category", style="cyan", width=25)
        table.add_column("Progress", style="green", width=25)
        table.add_column("Completed", style="yellow", justify="right")
        
        for cat in categories_progress:
            if cat["total"] > 0:
                progress = cat["completed"] / cat["total"]
                bar_width = 20
                filled = int(bar_width * progress)
                progress_bar = "█" * filled + "░" * (bar_width - filled)
                progress_display = f"{progress_bar} {cat['percentage']:.1f}%"
            else:
                progress_display = "No problems"
            
            table.add_row(
                cat["display_name"],
                progress_display,
                f"{cat['completed']}/{cat['total']}"
            )
        
        self.console.print(table)
    
    def show_achievements(self, achievements: List[str], next_milestone: str = None):
        """Display achievements and badges"""
        if not achievements:
            self.console.print(Panel(
                "[dim]🌟 Complete your first problem to start earning badges![/dim]",
                title="🏅 Your Achievements"
            ))
            return
        
        # Create achievements display
        achievement_text = "\n".join(f"  {achievement}" for achievement in achievements)
        
        if next_milestone:
            achievement_text += f"\n\n[bold yellow]🎯 Next Milestone:[/bold yellow]\n  {next_milestone}"
        
        self.console.print(Panel(achievement_text, title="🏅 Your Achievements", box=box.ROUNDED))
    
    def show_problem_list(self, problems: List[Problem], completed_problems: List[str]):
        """Display list of problems with completion status"""
        completed_set = set(completed_problems)
        
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("#", style="dim", width=4)
        table.add_column("Status", width=6)
        table.add_column("Problem", style="cyan")
        table.add_column("Difficulty", width=10)
        table.add_column("Category", style="dim")
        
        for problem in problems:
            status = "✅" if problem.problem_id in completed_set else "❌"
            
            difficulty_colors = {"Easy": "green", "Medium": "yellow", "Hard": "red"}
            difficulty_color = difficulty_colors.get(problem.difficulty, "white")
            
            table.add_row(
                str(problem.order),
                status,
                problem.name,
                f"[{difficulty_color}]{problem.difficulty}[/{difficulty_color}]",
                problem.category.replace('_', ' ').title()
            )
        
        self.console.print(table)
    
    def confirm_action(self, message: str, confirmation_word: str = "yes") -> bool:
        """Get user confirmation for an action"""
        self.console.print(f"\n[yellow]{message}[/yellow]")
        response = self.console.input(f"Type '{confirmation_word}' to confirm: ").strip()
        return response.lower() == confirmation_word.lower()
    
    def get_user_input(self, prompt: str, default: str = None) -> str:
        """Get user input with optional default"""
        if default:
            full_prompt = f"{prompt} (default={default}): "
        else:
            full_prompt = f"{prompt}: "
        
        response = self.console.input(full_prompt).strip()
        return response if response else (default or "")
    
    def show_analysis_results(self, analysis: Dict):
        """Display code analysis results including benchmarks"""
        if "error" in analysis:
            self.print_error(f"Analysis failed: {analysis['error']}")
            return
        
        if not analysis.get("solution_implemented", True):
            self.console.print(Panel(
                "[red]❌ Solution not implemented![/red]\n[yellow]Replace 'pass' and 'TODO' with your actual solution.[/yellow]",
                title="🔍 Analysis Results",
                box=box.ROUNDED,
                border_style="red"
            ))
            return
        
        # Performance info with benchmark details
        benchmark = analysis.get("benchmark", {})
        
        if benchmark:
            # Detailed benchmark results
            perf_text = f"""
[green]{benchmark.get('rating_emoji', '⚡')} Execution Time: {benchmark['avg_time_ms']:.2f}ms (avg of {benchmark['runs']} runs)[/green]
[blue]📊 Performance: {benchmark['rating']}[/blue]
[cyan]📈 Range: {benchmark['min_time_ms']:.2f}ms - {benchmark['max_time_ms']:.2f}ms[/cyan]
[yellow]📏 Std Dev: ±{benchmark['std_dev_ms']:.2f}ms[/yellow]
            """.strip()
        else:
            # Fallback to simple timing
            perf_text = f"""
[green]⚡ Execution Time: {analysis['execution_time_ms']:.2f}ms[/green]
[blue]📊 Performance: {analysis['performance_rating']}[/blue]
            """.strip()
        
        if analysis["perfect_solution"]:
            perf_text += "\n[bold green]✨ Perfect Solution! No issues found.[/bold green]"
        else:
            perf_text += f"\n[yellow]⚠️  Found {analysis['total_issues']} code issues[/yellow]"
        
        self.console.print(Panel(perf_text, title="🔍 Analysis Results", box=box.ROUNDED))
