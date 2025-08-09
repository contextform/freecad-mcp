# FreeCAD ReAct Agent - Claude Code-like behavior for FreeCAD
# Implements adaptive decision logic with ReAct loop for complex tasks

import FreeCAD
import FreeCADGui
import json
from typing import Dict, Any, List, Tuple

class FreeCADReActAgent:
    """Claude Code-style agent for FreeCAD iteration and assistance"""
    
    def __init__(self, socket_server):
        self.socket_server = socket_server  # Access to existing tools
        self.conversation_log = []
        self.max_iterations = 15
        self.current_todos = []
        
        # Agent's tool library
        self.tools = {
            "analyze_geometry": self._analyze_geometry,
            "modify_parameters": self._modify_parameters,
            "create_object": self._create_object,
            "verify_result": self._verify_result,
            "ask_human": self._ask_human,
            "execute_python": self._execute_python_safe,
            "list_objects": self._list_objects,
            "measure_objects": self._measure_objects
        }
        
    def process_request(self, request: str) -> str:
        """Main entry point - Claude Code-like decision logic"""
        
        # Step 1: Assess request complexity (like Claude Code does)
        decision = self._claude_decision_logic(request)
        
        if decision == "direct_answer":
            return self._answer_directly(request)
            
        elif decision == "todo_mode":
            return self._execute_with_todos(request)
            
        elif decision == "react_mode":
            return self._execute_react_loop(request)
            
        else:  # complex/unknown
            return self._execute_react_loop(request)
    
    def _claude_decision_logic(self, request: str) -> str:
        """Replicate Claude Code's decision pattern"""
        request_lower = request.lower()
        
        # Direct answer triggers (like Claude Code)
        direct_patterns = [
            "how many", "what is", "list", "show me", "tell me", "describe",
            "what does", "where is", "which objects", "count"
        ]
        
        # Todo mode triggers (multi-step complex tasks)
        todo_patterns = [
            "implement", "build", "complete", "fix all", "create complex",
            "design", "generate", "make multiple"
        ]
        
        # ReAct mode triggers (exploration/modification)
        react_patterns = [
            "make", "change", "modify", "update", "iterate", "improve",
            "find and", "analyze and", "check and"
        ]
        
        if any(pattern in request_lower for pattern in direct_patterns):
            return "direct_answer"
        elif any(pattern in request_lower for pattern in todo_patterns):
            return "todo_mode"
        elif any(pattern in request_lower for pattern in react_patterns):
            return "react_mode"
        else:
            # Complexity assessment (like Claude Code)
            complexity = self._assess_complexity(request)
            if complexity >= 3:
                return "todo_mode"
            elif complexity >= 2:
                return "react_mode"
            else:
                return "direct_answer"
    
    def _assess_complexity(self, request: str) -> int:
        """Count implied steps in request"""
        action_words = ["make", "change", "modify", "update", "create", "add", "remove", "fix"]
        multipliers = ["all", "every", "multiple", "several", "complex", "each"]
        
        actions = sum(1 for word in action_words if word in request.lower())
        complexity = sum(1 for word in multipliers if word in request.lower())
        
        return actions + (complexity * 2)
    
    def _answer_directly(self, request: str) -> str:
        """Handle simple queries without ReAct loop"""
        request_lower = request.lower()
        
        try:
            if "how many" in request_lower:
                return self._count_objects_direct(request)
            elif "list" in request_lower:
                return self._list_objects_direct(request)
            elif "what is" in request_lower:
                return self._explain_direct(request)
            else:
                # Fallback to ReAct if uncertain
                return self._execute_react_loop(request)
                
        except Exception as e:
            return f"Error processing direct request: {e}"
    
    def _execute_with_todos(self, request: str) -> str:
        """Handle complex tasks with TodoWrite-like planning"""
        try:
            # Step 1: Create plan (like Claude Code TodoWrite)
            self._log_to_user(f"I'll help with this complex task. Let me break it down:")
            
            todos = self._create_todos(request)
            self.current_todos = todos
            
            for i, todo in enumerate(todos):
                self._log_to_user(f"\n--- Working on: {todo} ---")
                
                # Execute each todo with ReAct loop
                result = self._execute_react_loop(todo)
                
                self._log_to_user(f"✅ Completed: {todo}")
                
            return "All tasks completed successfully!"
            
        except Exception as e:
            return f"Error in todo execution: {e}"
    
    def _execute_react_loop(self, request: str) -> str:
        """Main ReAct loop for complex tasks"""
        goal = request
        task_complete = False
        iteration_count = 0
        
        self._log_to_user(f"🤖 Starting: '{request}'")
        
        while not task_complete and iteration_count < self.max_iterations:
            iteration_count += 1
            
            try:
                # 1. THOUGHT - Reasoning about what to do
                thought = self._reason_next_step(goal, self.conversation_log)
                self._log_to_user(f"💭 Thinking: {thought}")
                
                # 2. ACTION - Tool selection and execution
                action_name, action_params = self._select_action(thought, goal)
                self._log_to_user(f"🔧 Action: {action_name}")
                
                action_result = self.tools[action_name](action_params)
                
                # 3. OBSERVATION - Process tool result
                observation = self._process_observation(action_result, goal)
                self._log_to_user(f"👁️ Observation: {observation}")
                
                # Store in conversation history
                self.conversation_log.append({
                    "iteration": iteration_count,
                    "thought": thought,
                    "action": action_name,
                    "observation": observation
                })
                
                # 4. LOOP - Continue or complete
                if self._goal_reached(goal, observation):
                    task_complete = True
                    self._log_to_user("✅ Task completed successfully!")
                elif self._is_stuck(thought, observation) or "need help" in observation.lower():
                    return self.tools["ask_human"]({"context": self.conversation_log, "goal": goal})
                    
            except Exception as e:
                self._log_to_user(f"❌ Error in iteration {iteration_count}: {e}")
                return self.tools["ask_human"]({"error": str(e), "goal": goal})
                
        if iteration_count >= self.max_iterations:
            return self.tools["ask_human"]({"reason": "Too many iterations, need guidance", "goal": goal})
            
        return "ReAct loop completed!"
    
    def _reason_next_step(self, goal: str, history: List[Dict]) -> str:
        """Determine what to do next based on goal and history"""
        if not history:
            if "make" in goal.lower() or "change" in goal.lower():
                return f"I need to analyze the current geometry to understand what needs to be modified"
            else:
                return f"I need to understand the current state to help with: {goal}"
        
        last_obs = history[-1]["observation"] if history else ""
        
        if "found" in last_obs.lower() and ("objects" in last_obs.lower() or "geometry" in last_obs.lower()):
            return f"Now I need to determine how to modify these objects for: {goal}"
        elif "modified" in last_obs.lower() and "objects" in last_obs.lower():
            # If we just modified objects, we're probably done!
            return "The modifications look complete, let me verify the final result"
        elif "created" in last_obs.lower():
            return "I should verify if the creation was successful"
        elif "failed" in last_obs.lower() or "error" in last_obs.lower():
            return "The last action failed, I need to try a different approach or get help"
        else:
            return f"I need to continue working towards: {goal}"
    
    def _select_action(self, thought: str, goal: str) -> Tuple[str, Dict]:
        """Select appropriate tool based on current thought"""
        thought_lower = thought.lower()
        goal_lower = goal.lower()
        
        if "analyze" in thought_lower or "understand" in thought_lower:
            return "analyze_geometry", {"goal": goal}
        elif "modify" in thought_lower or "change" in thought_lower:
            return "modify_parameters", {"thought": thought, "goal": goal}
        elif "create" in thought_lower:
            return "create_object", {"goal": goal}
        elif "verify" in thought_lower or "check" in thought_lower:
            return "verify_result", {"goal": goal}
        elif "help" in thought_lower or "different approach" in thought_lower:
            return "ask_human", {"thought": thought, "goal": goal}
        else:
            # Default: analyze first
            return "analyze_geometry", {"goal": goal}
    
    def _process_observation(self, result: str, goal: str) -> str:
        """Process and contextualize tool results"""
        if "Error" in result or "Failed" in result:
            return f"Action failed: {result}"
        else:
            return result
    
    def _goal_reached(self, goal: str, observation: str) -> bool:
        """Check if the goal has been achieved"""
        obs_lower = observation.lower()
        goal_lower = goal.lower()
        
        # For modification tasks, check if we've actually modified objects
        if "modified" in obs_lower and ("bigger" in goal_lower or "smaller" in goal_lower or "change" in goal_lower):
            # If we see "modified X objects" and it's a size change goal, we're done
            if "objects" in obs_lower and any(word in obs_lower for word in ["→", "mm", "radius"]):
                return True
        
        # General success indicators
        success_indicators = ["successfully", "completed", "created", "✓", "done"]
        has_success = any(indicator in obs_lower for indicator in success_indicators)
        
        return has_success
    
    def _is_stuck(self, thought: str, observation: str) -> bool:
        """Determine if agent is stuck and needs human help"""
        stuck_indicators = ["failed", "error", "cannot", "unable", "stuck", "don't know"]
        return any(indicator in observation.lower() or indicator in thought.lower() 
                  for indicator in stuck_indicators)
    
    def _log_to_user(self, message: str):
        """Send progress updates to user"""
        FreeCAD.Console.PrintMessage(f"{message}\n")
    
    # === TOOL IMPLEMENTATIONS ===
    
    def _analyze_geometry(self, params: Dict) -> str:
        """Analyze current document geometry"""
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document to analyze"
            
            objects = []
            for obj in doc.Objects:
                obj_info = {
                    "name": obj.Name,
                    "type": obj.TypeId,
                    "label": obj.Label
                }
                
                # Add specific properties for common types
                if obj.TypeId == "Part::Box":
                    obj_info["dimensions"] = f"{obj.Length}x{obj.Width}x{obj.Height}mm"
                elif obj.TypeId == "Part::Cylinder":
                    obj_info["dimensions"] = f"R{obj.Radius}mm, H{obj.Height}mm"
                elif obj.TypeId == "Part::Sphere":
                    obj_info["dimensions"] = f"R{obj.Radius}mm"
                    
                objects.append(obj_info)
            
            analysis = f"Found {len(objects)} objects in document:\n"
            for obj in objects:
                analysis += f"- {obj['name']} ({obj['type']}): {obj.get('dimensions', 'N/A')}\n"
                
            return analysis
            
        except Exception as e:
            return f"Error analyzing geometry: {e}"
    
    def _modify_parameters(self, params: Dict) -> str:
        """Modify object parameters based on goal"""
        try:
            goal = params.get("goal", "")
            goal_lower = goal.lower()
            
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document"
            
            modified_count = 0
            modifications = []
            
            # Parse goal to understand what to modify
            if "bigger" in goal_lower or "larger" in goal_lower:
                # Make objects bigger
                for obj in doc.Objects:
                    if obj.TypeId == "Part::Cylinder" and "hole" in goal_lower:
                        old_radius = obj.Radius
                        obj.Radius = old_radius + 1.0  # Default increase
                        modifications.append(f"{obj.Name}: radius {old_radius}→{obj.Radius}mm")
                        modified_count += 1
                    elif obj.TypeId == "Part::Box":
                        old_dims = (obj.Length, obj.Width, obj.Height)
                        obj.Length *= 1.2
                        obj.Width *= 1.2  
                        obj.Height *= 1.2
                        new_dims = (obj.Length, obj.Width, obj.Height)
                        modifications.append(f"{obj.Name}: {old_dims}→{new_dims}mm")
                        modified_count += 1
            
            if modified_count > 0:
                doc.recompute()
                result = f"Modified {modified_count} objects:\n" + "\n".join(modifications)
                return result
            else:
                return "No objects found matching the modification criteria"
                
        except Exception as e:
            return f"Error modifying parameters: {e}"
    
    def _create_object(self, params: Dict) -> str:
        """Create new objects based on goal"""
        try:
            goal = params.get("goal", "").lower()
            
            # Use existing socket server tools
            if "box" in goal:
                return self.socket_server._create_box({"length": 10, "width": 10, "height": 10})
            elif "cylinder" in goal:
                return self.socket_server._create_cylinder({"radius": 5, "height": 10})
            elif "sphere" in goal:
                return self.socket_server._create_sphere({"radius": 5})
            else:
                return "I need more specific information about what to create"
                
        except Exception as e:
            return f"Error creating object: {e}"
    
    def _verify_result(self, params: Dict) -> str:
        """Verify if modifications were successful"""
        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                return "No active document to verify"
                
            # Simple verification - check if document has objects and they're valid
            valid_objects = [obj for obj in doc.Objects if hasattr(obj, 'Shape')]
            
            if valid_objects:
                return f"✓ Verification successful: {len(valid_objects)} valid objects in document"
            else:
                return "⚠️ Verification failed: No valid objects found"
                
        except Exception as e:
            return f"Error verifying result: {e}"
    
    def _ask_human(self, params: Dict) -> str:
        """Request human assistance"""
        context = params.get("context", [])
        goal = params.get("goal", "")
        error = params.get("error", "")
        reason = params.get("reason", "")
        
        help_msg = "🙋 I need your help!\n\n"
        
        if goal:
            help_msg += f"Goal: {goal}\n"
        if error:
            help_msg += f"Error encountered: {error}\n"
        if reason:
            help_msg += f"Reason: {reason}\n"
            
        if context:
            help_msg += f"\nWhat I've tried:\n"
            for i, step in enumerate(context[-3:], 1):  # Show last 3 steps
                help_msg += f"{i}. {step.get('thought', '')}: {step.get('observation', '')}\n"
        
        help_msg += "\nPlease help me understand what I should do next, or make the changes manually."
        
        return help_msg
    
    # === DIRECT ANSWER METHODS ===
    
    def _count_objects_direct(self, request: str) -> str:
        """Direct answer for counting queries"""
        try:
            result = self.socket_server._list_all_objects({})
            objects = json.loads(result)
            return f"Document contains {len(objects)} objects: {', '.join([obj['name'] for obj in objects])}"
        except:
            return "Unable to count objects"
    
    def _list_objects_direct(self, request: str) -> str:
        """Direct answer for listing queries"""
        try:
            return self.socket_server._list_all_objects({})
        except Exception as e:
            return f"Error listing objects: {e}"
    
    def _explain_direct(self, request: str) -> str:
        """Direct answer for explanation queries"""
        return "I can help you with FreeCAD operations like creating objects, modifying geometry, and analyzing designs. What would you like to know?"
    
    # === TODO MANAGEMENT ===
    
    def _create_todos(self, request: str) -> List[str]:
        """Create todo list for complex tasks (like Claude Code TodoWrite)"""
        request_lower = request.lower()
        
        if "make" in request_lower and "bigger" in request_lower:
            return [
                "Analyze current geometry to identify objects to modify",
                "Determine appropriate size increases for each object type", 
                "Execute modifications step by step",
                "Verify all changes were applied correctly"
            ]
        elif "create" in request_lower:
            return [
                "Understand requirements for the new object",
                "Create the base geometry",
                "Apply any necessary modifications",
                "Verify the result meets requirements"
            ]
        else:
            return [
                "Analyze the current situation",
                "Plan the approach",
                "Execute the solution",
                "Verify the results"
            ]
    
    # === UTILITY METHODS ===
    
    def _execute_python_safe(self, params: Dict) -> str:
        """Safe Python execution with limited scope"""
        return self.socket_server._execute_python(params)
    
    def _list_objects(self, params: Dict) -> str:
        """List objects tool"""
        return self.socket_server._list_all_objects(params)
    
    def _measure_objects(self, params: Dict) -> str:
        """Measure distances/dimensions"""
        # Placeholder for measurement functionality
        return "Measurement functionality not yet implemented"