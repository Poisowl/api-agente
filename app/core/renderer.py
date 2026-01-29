from typing import List, Dict, Any
import re


class MessageRenderer:
    """Handles message rendering and formatting."""
    
    def render_messages(self, messages: List[str], context: Dict[str, Any]) -> List[str]:
        """Render messages with context variables."""
        rendered_messages = []
        
        for message in messages:
            rendered_message = self._render_template(message, context)
            rendered_messages.append(rendered_message)
        
        return rendered_messages
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render a single template with context variables."""
        # Simple template rendering - replace {variable} with context values
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, match.group(0)))
        
        return re.sub(r'\{([^}]+)\}', replace_var, template)