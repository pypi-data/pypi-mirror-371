from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .execution_step import ExecutionStep


@dataclass
class ExecutionHistory:
    """Command execution history model."""
    steps: List[ExecutionStep] = field(default_factory=list)

    def add_step(self, step: ExecutionStep) -> None:
        """Append a step to the history."""
        self.steps.append(step)
    
    def get_step(self, index: int) -> Optional[ExecutionStep]:
        """Return the step at a given index or None if out of range."""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None

    def get_last_step(self) -> Optional[ExecutionStep]:
        """Return the last step in the history or None if empty."""
        if not self.steps:
            return None
        return self.steps[-1]
    
    def get_steps_count(self) -> int:
        """Return the number of steps."""
        return len(self.steps)

    def all_successful(self) -> bool:
        """Return True if all steps succeeded (or True if empty)."""
        if not self.steps:
            return True
        return all(step.success for step in self.steps)

    def __iter__(self) -> Iterator[ExecutionStep]:
        """Iterate over steps in order."""
        return iter(self.steps)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize history to a dictionary."""
        return {
            'steps': [step.to_dict() for step in self.steps],
            'total_steps': len(self.steps),
            'all_successful': self.all_successful()
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ExecutionHistory':
        """Create history from a dictionary."""
        history = ExecutionHistory()
        for step_data in data.get('steps', []):
            history.add_step(ExecutionStep.from_dict(step_data))
        return history