import random
import re
from crewai.tools import BaseTool

class DiceRollerTool(BaseTool):
    name: str = "roll_dice"
    description: str = "Roll dice in standard notation (e.g., '1d20', '2d6', '1d20+2'). Useful for determining outcomes of actions."

    def _run(self, dice_notation: str) -> str:
        # Match something like "1d20" or "2d6+3" or "1d8-1"
        match = re.match(r"^(\d+)d(\d+)(?:([+-])(\d+))?$", dice_notation.strip().lower())
        if not match:
            return f"Error: Invalid dice notation '{dice_notation}'. Use standard notation like '1d20' or '2d6+3'."
        
        num_dice = int(match.group(1))
        sides = int(match.group(2))
        
        if num_dice <= 0 or sides <= 0:
            return "Error: Number of dice and sides must be positive integers."
            
        modifier_sign = match.group(3)
        modifier_val = int(match.group(4)) if match.group(4) else 0
        
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        if modifier_sign == '+':
            total += modifier_val
        elif modifier_sign == '-':
            total -= modifier_val
            
        modifier_str = f" {modifier_sign} {modifier_val}" if modifier_sign else ""
        return f"Rolled {dice_notation}: {rolls}{modifier_str} = {total}"
