"""
RPG Service - Handles all RPG game mechanics
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from ..models.progress import ProgressModel, GameData


class RPGService:
    """Service for RPG game mechanics"""
    
    def __init__(self, progress_model: ProgressModel):
        self.progress_model = progress_model
        
        # XP and Level System
        self.xp_per_level = 100  # Base XP needed for level 2
        self.level_multiplier = 1.5  # Each level needs 50% more XP
        
        # XP Rewards
        self.xp_rewards = {
            "problem_easy": 50,
            "problem_medium": 100,
            "problem_hard": 200,
            "daily_streak": 25,
            "weekly_streak": 100,
            "category_50_percent": 150,
            "category_complete": 300,
            "perfect_analysis": 50,
            "speed_bonus": 25,
            "comeback": 75,
        }
        
        # Titles based on level ranges
        self.titles = {
            1: "🌱 Coding Seedling",
            5: "🚀 Algorithm Apprentice", 
            10: "⚔️ Data Structure Warrior",
            15: "🧙‍♂️ Code Wizard",
            20: "🏆 Algorithm Master",
            25: "👑 DSA Champion",
            30: "🌟 Legendary Coder",
            40: "🔥 Mythical Programmer",
            50: "💎 Diamond Developer",
            75: "🌌 Cosmic Coder",
            100: "🎯 NeetCode Deity"
        }
    
    def get_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a level"""
        if level <= 1:
            return 0
        
        total_xp = 0
        for lvl in range(2, level + 1):
            xp_needed = int(self.xp_per_level * (self.level_multiplier ** (lvl - 2)))
            total_xp += xp_needed
        
        return total_xp
    
    def get_level_from_xp(self, xp: int) -> int:
        """Calculate level from total XP"""
        level = 1
        while self.get_xp_for_level(level + 1) <= xp:
            level += 1
        return level
    
    def get_xp_for_next_level(self, current_level: int) -> int:
        """Get XP needed for next level"""
        return int(self.xp_per_level * (self.level_multiplier ** (current_level - 1)))
    
    def get_title(self, level: int) -> str:
        """Get title for current level"""
        title = "🌱 Coding Seedling"
        for level_req, title_name in sorted(self.titles.items(), reverse=True):
            if level >= level_req:
                title = title_name
                break
        return title
    
    def update_streak(self) -> Tuple[bool, int]:
        """Update daily streak and return (streak_continued, xp_earned)"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        game_data = self.progress_model.progress.game_data
        last_date = game_data.last_activity_date
        
        xp_earned = 0
        streak_continued = False
        
        if last_date == today:
            # Already active today
            return True, 0
        
        if last_date == yesterday:
            # Continuing streak
            game_data.current_streak += 1
            streak_continued = True
            xp_earned += self.xp_rewards["daily_streak"]
            
            # Weekly streak bonus
            if game_data.current_streak % 7 == 0:
                xp_earned += self.xp_rewards["weekly_streak"]
                
        elif last_date is None:
            # First day
            game_data.current_streak = 1
            streak_continued = True
        else:
            # Streak broken, but give comeback bonus if returning after break
            if last_date and (datetime.now() - datetime.strptime(last_date, "%Y-%m-%d")).days > 1:
                xp_earned += self.xp_rewards["comeback"]
            game_data.current_streak = 1
        
        # Update longest streak
        if game_data.current_streak > game_data.longest_streak:
            game_data.longest_streak = game_data.current_streak
        
        # Reset daily counters
        game_data.problems_attempted_today = 0
        game_data.last_activity_date = today
        
        # Track daily activity
        if today not in game_data.daily_activities:
            game_data.daily_activities[today] = []
        
        return streak_continued, xp_earned
    
    def award_xp(self, activity: str, difficulty: str = None, bonus_data: dict = None) -> Dict:
        """Award XP for an activity and return level up info"""
        game_data = self.progress_model.progress.game_data
        
        # Update streak first
        streak_continued, streak_xp = self.update_streak()
        
        # Calculate base XP
        base_xp = 0
        activity_description = ""
        
        if activity == "problem_solved":
            if difficulty == "Easy":
                base_xp = self.xp_rewards["problem_easy"]
                activity_description = "🟢 Easy Problem Solved"
            elif difficulty == "Medium":
                base_xp = self.xp_rewards["problem_medium"] 
                activity_description = "🟡 Medium Problem Solved"
            elif difficulty == "Hard":
                base_xp = self.xp_rewards["problem_hard"]
                activity_description = "🔴 Hard Problem Solved"
            
            game_data.problems_attempted_today += 1
            
        elif activity == "perfect_solution":
            base_xp = self.xp_rewards["perfect_analysis"]
            activity_description = "✨ Perfect Solution (No Code Issues)"
            game_data.perfect_solutions += 1
            
        elif activity == "speed_completion":
            base_xp = self.xp_rewards["speed_bonus"]
            activity_description = "⚡ Speed Completion Bonus"
            game_data.speed_completions += 1
        
        # Apply multipliers
        total_xp = base_xp
        multipliers = []
        
        # Streak multiplier
        if game_data.current_streak >= 7:
            multiplier = 1 + (game_data.current_streak // 7) * 0.1  # 10% per week
            total_xp = int(total_xp * multiplier)
            multipliers.append(f"🔥 {game_data.current_streak}-day streak (+{int((multiplier-1)*100)}%)")
        
        # First problem of the day bonus
        if game_data.problems_attempted_today == 1 and activity == "problem_solved":
            total_xp = int(total_xp * 1.5)
            multipliers.append("🌅 First Problem Today (+50%)")
        
        # Weekend warrior bonus
        if datetime.now().weekday() >= 5:  # Saturday or Sunday
            total_xp = int(total_xp * 1.2)
            multipliers.append("🎮 Weekend Warrior (+20%)")
        
        # Add streak XP
        total_xp += streak_xp
        
        # Update XP and level
        old_level = game_data.level
        old_xp = game_data.xp
        
        game_data.xp += total_xp
        game_data.total_xp_earned += total_xp
        new_level = self.get_level_from_xp(game_data.xp)
        
        level_up = new_level > old_level
        if level_up:
            game_data.level = new_level
        
        # Track activity
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in game_data.daily_activities:
            game_data.daily_activities[today] = []
        
        game_data.daily_activities[today].append({
            "activity": activity_description,
            "xp": total_xp,
            "time": datetime.now().strftime("%H:%M")
        })
        
        # Save progress
        self.progress_model.save()
        
        return {
            "xp_earned": total_xp,
            "base_xp": base_xp,
            "streak_xp": streak_xp,
            "multipliers": multipliers,
            "level_up": level_up,
            "old_level": old_level,
            "new_level": new_level,
            "current_xp": game_data.xp,
            "xp_to_next": self.get_xp_for_next_level(new_level),
            "current_streak": game_data.current_streak,
            "activity_description": activity_description
        }
    
    def get_player_stats(self) -> Dict:
        """Get comprehensive player statistics"""
        game_data = self.progress_model.progress.game_data
        current_level = game_data.level
        current_xp = game_data.xp
        
        # Calculate XP progress in current level
        xp_for_current_level = self.get_xp_for_level(current_level)
        xp_for_next_level = self.get_xp_for_level(current_level + 1)
        xp_in_current_level = current_xp - xp_for_current_level
        xp_needed_for_next = xp_for_next_level - current_xp
        
        return {
            "level": current_level,
            "xp": current_xp,
            "xp_in_current_level": xp_in_current_level,
            "xp_needed_for_next": xp_needed_for_next,
            "xp_for_next_level": self.get_xp_for_next_level(current_level),
            "title": self.get_title(current_level),
            "current_streak": game_data.current_streak,
            "longest_streak": game_data.longest_streak,
            "total_xp_earned": game_data.total_xp_earned,
            "problems_today": game_data.problems_attempted_today,
            "perfect_solutions": game_data.perfect_solutions,
            "speed_completions": game_data.speed_completions
        }
    
    def create_xp_bar(self, width: int = 30) -> str:
        """Create visual XP progress bar"""
        stats = self.get_player_stats()
        
        if stats["xp_for_next_level"] == 0:
            return "█" * width + " MAX LEVEL!"
        
        progress = stats["xp_in_current_level"] / stats["xp_for_next_level"]
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        
        return f"{bar} {stats['xp_in_current_level']}/{stats['xp_for_next_level']} XP"
    
    def get_daily_summary(self) -> Dict:
        """Get today's activity summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        game_data = self.progress_model.progress.game_data
        
        activities = game_data.daily_activities.get(today, [])
        total_xp_today = sum(activity["xp"] for activity in activities)
        
        return {
            "activities": activities,
            "total_xp_today": total_xp_today,
            "current_streak": game_data.current_streak,
            "has_activities": len(activities) > 0
        }
