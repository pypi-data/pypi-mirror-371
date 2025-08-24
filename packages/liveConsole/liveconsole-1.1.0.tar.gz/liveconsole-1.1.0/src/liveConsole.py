import customtkinter as ctk
import tkinter as tk
import traceback
import inspect
import threading
import sys
import io
import pygments
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
import keyword
import builtins


class StdoutRedirect(io.StringIO):
    def __init__(self, write_callback):
        super().__init__()
        self.write_callback = write_callback

    def write(self, s):
        if s.strip():
            self.write_callback(s, "output")

    def flush(self):
        pass


class InteractiveConsoleText(tk.Text):
    """A tk.Text widget with Python syntax highlighting for interactive console."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.lexer = PythonLexer()
        self.style = get_style_by_name("monokai")

        # Configure tags for different output types
        self.tag_configure("prompt", foreground="#00ff00", font=("Consolas", 12, "bold"))
        self.tag_configure("output", foreground="#ffffff", font=("Consolas", 12))
        self.tag_configure("error", foreground="#ff6666", font=("Consolas", 12))
        self.tag_configure("result", foreground="#66ccff", font=("Consolas", 12))
        self.tag_configure("suggestion", background="#444444", foreground="#cccccc", font=("Consolas", 12))

        # Apply tag configs for syntax highlighting
        for token, style in self.style:
            if style["color"]:
                fg = f"#{style['color']}"
                font = ("Consolas", 12, "bold" if style["bold"] else "normal")
                self.tag_configure(str(token), foreground=fg, font=font)

        # Bind events
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Return>", self.on_enter)
        self.bind("<Shift-Return>", self.on_shift_enter)
        self.bind("<Button-1>", self.on_click)
        self.bind("<KeyPress>", self.on_key_press)
        self.bind("<Motion>", self.on_mouse_motion)
        self.bind("<Tab>", self.on_tab)

        # Track current command
        self.current_prompt_start = None
        self.current_prompt_end = None
        self.command_history = []
        self.history_index = -1
        self.hover_command = None
        self.suggestion_window = None
        self.suggestions = []
        self.selected_suggestion = 0

        # Build suggestion lists
        self.keywords = keyword.kwlist
        self.builtins = [name for name in dir(builtins) if not name.startswith('_')]
        
        # Initialize with prompt
        self.insert("end", ">>> ")
        self.tag_add("prompt", "end-4c", "end")
        self.current_prompt_start = self.index("end-4c")
        self.mark_set("insert", "end")

    def get_suggestions(self, partial_word):
        """Get code suggestions for partial word."""
        suggestions = []
        
        # Add matching keywords
        for kw in self.keywords:
            if kw.startswith(partial_word.lower()):
                suggestions.append(kw)
        
        # Add matching builtins
        for builtin in self.builtins:
            if builtin.startswith(partial_word):
                suggestions.append(builtin)
        
        # Add matching variables from namespace
        if hasattr(self.master, 'userLocals'):
            for var in self.master.userLocals:
                if var.startswith(partial_word) and not var.startswith('_'):
                    suggestions.append(var)
        
        if hasattr(self.master, 'userGlobals'):
            for var in self.master.userGlobals:
                if var.startswith(partial_word) and not var.startswith('_'):
                    suggestions.append(var)
        
        # Remove duplicates and sort
        suggestions = sorted(list(set(suggestions)))
        return suggestions[:10]  # Limit to 10 suggestions

    def show_suggestions(self):
        """Show code suggestions popup."""
        # Get current word being typed
        cursor_pos = self.index(tk.INSERT)
        line_start = self.index(f"{cursor_pos} linestart")
        current_line = self.get(line_start, cursor_pos)
        
        # Find the current word
        words = current_line.split()
        if not words:
            return
        
        current_word = words[-1]
        # Handle cases like "print(" where we want to suggest after the parenthesis
        for char in "([{,.":
            if char in current_word:
                current_word = current_word.split(char)[-1]
        
        if len(current_word) < 2:  # Only show suggestions for 2+ characters
            self.hide_suggestions()
            return
        
        suggestions = self.get_suggestions(current_word)
        if not suggestions:
            self.hide_suggestions()
            return
        
        self.suggestions = suggestions
        self.selected_suggestion = 0
        
        # Create or update suggestion window
        if not self.suggestion_window:
            self.suggestion_window = tk.Toplevel(self)
            self.suggestion_window.wm_overrideredirect(True)
            self.suggestion_window.configure(bg="#2d2d2d")
            
            self.suggestion_listbox = tk.Listbox(
                self.suggestion_window,
                bg="#2d2d2d",
                fg="white",
                selectbackground="#0066cc",
                font=("Consolas", 10),
                height=min(len(suggestions), 8)
            )
            self.suggestion_listbox.pack()
        
        # Clear and populate listbox
        self.suggestion_listbox.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestion_listbox.insert(tk.END, suggestion)
        
        self.suggestion_listbox.selection_set(0)
        
        # Position window near cursor
        x, y, _, _ = self.bbox(cursor_pos)
        x += self.winfo_rootx()
        y += self.winfo_rooty() + 20
        
        self.suggestion_window.geometry(f"+{x}+{y}")
        self.suggestion_window.deiconify()

    def hide_suggestions(self):
        """Hide suggestions popup."""
        if self.suggestion_window:
            self.suggestion_window.withdraw()

    def apply_suggestion(self, suggestion=None):
        """Apply selected suggestion at the cursor position (only missing letters)."""
        if not suggestion and self.suggestions:
            suggestion = self.suggestions[self.selected_suggestion]
        if not suggestion:
            return

        # Current cursor position
        cursor_pos = self.index(tk.INSERT)

        # Get the word fragment before the cursor
        line_start = self.index(f"{cursor_pos} linestart")
        current_line = self.get(line_start, cursor_pos)

        fragment = ""
        for i in range(len(current_line)):
            if current_line[-(i+1)] in " \t([{,.)":
                break
            fragment = current_line[-(i+1):]

        # Only insert the missing part
        if suggestion.startswith(fragment):
            missing_part = suggestion[len(fragment):]
            self.insert(cursor_pos, missing_part)
            self.mark_set("insert", f"{cursor_pos} + {len(missing_part)}c")

        self.hide_suggestions()


    def on_tab(self, event):
        """Handle Tab key for autocompletion."""
        if self.suggestion_window and self.suggestion_window.winfo_viewable():
            self.apply_suggestion()
            return "break"
        else:
            self.show_suggestions()
            return "break"

    def is_incomplete_statement(self, code):
        """Check if the code is an incomplete statement that needs more lines."""
        code = code.split("\n")
        if code[-1].strip() == "":
            return(False)
        if code[0].strip().endswith(":"):
            return(True)
        return(False)

    def get_indent_level(self, line):
        """Get the indentation level of a line."""
        return len(line) - len(line.lstrip(' '))

    def should_auto_indent(self, line):
        """Check if we should add indentation after this line."""
        stripped = line.strip()
        return (stripped and stripped[-1] == ':')

    def on_click(self, event):
        self.hide_suggestions()
        click_pos = self.index(f"@{event.x},{event.y}")

        if self.current_prompt_start:
            click_pos = self.index(tk.CURRENT)
            if self.compare(click_pos, "<", self.current_prompt_start):
                self.mark_set("insert", "end")
                return "break"

    def on_mouse_motion(self, event):
        """Handle mouse motion for hover copying previous commands."""

        mouse_pos = self.index(f"@{event.x},{event.y}")
        line_start = self.index(f"{mouse_pos} linestart")
        line_end = self.index(f"{mouse_pos} lineend")
        line_text = self.get(line_start, line_end)
        
        # Check if this line starts with ">>> " (a previous command)
        if line_text.startswith(">>> ") and line_start != self.current_prompt_start:
            command = line_text[4:]  # Remove ">>> "
            if command.strip():
                # Change cursor to indicate clickable
                self.config(cursor="hand2")
                self.hover_command = command.strip()
            else:
                self.config(cursor="xterm")
                self.hover_command = None
        else:
            self.config(cursor="xterm")
            self.hover_command = None

    def on_key_press(self, event):
        if self.suggestion_window and self.suggestion_window.winfo_viewable():
            if event.keysym == "Down":
                self.selected_suggestion = min(self.selected_suggestion + 1, len(self.suggestions) - 1)
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(self.selected_suggestion)
                return "break"
            elif event.keysym == "Up":
                self.selected_suggestion = max(self.selected_suggestion - 1, 0)
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(self.selected_suggestion)
                return "break"
            elif event.keysym == "Escape":
                self.hide_suggestions()
                return "break"
            elif event.keysym in ["Return", "Tab"]:
                self.apply_suggestion()
                return "break"

        # Ensure cursor is always at least 4 chars after current_prompt_start
        prompt_end_index = f"{self.current_prompt_start} + 3c"

        if event.keysym not in ["Up", "Down", "Left", "Right", "Shift_L", "Shift_R", "Control_L", "Control_R"]:
            if self.compare("insert", "<", prompt_end_index):
                self.mark_set("insert", prompt_end_index)

        # Block Backspace if at or before prompt
        if event.keysym == "BackSpace" and self.compare("insert", "<=", prompt_end_index):
            return "break"

    def on_key_release(self, event):
        # Hide suggestions on certain keys
        if event.keysym in ["Return", "Escape", "Left", "Right", "Home", "End"]:
            self.hide_suggestions()
        # Show suggestions on typing
        elif event.keysym not in ["Up", "Down", "Shift_L", "Shift_R", "Control_L", "Control_R"]:
            self.after_idle(self.show_suggestions)
        
        # Only highlight the current command line
        if self.current_prompt_start:
            self.highlight_current_line()

    def on_shift_enter(self, event):
        """Handle Shift+Enter for new line with auto-indent."""
        self.hide_suggestions()
        
        if self.current_prompt_start:
            # Get current line to determine indent
            current_line_start = self.index("insert linestart")
            current_line_end = self.index("insert lineend")
            current_line = self.get(current_line_start, current_line_end)
            
            # Calculate indent level
            base_indent = self.get_indent_level(current_line)
            
            # If the current line should increase indent, add 4 spaces
            if self.should_auto_indent(current_line):
                base_indent += 4
            
            # Insert newline with proper indentation
            self.insert("insert", "\n" + " " * base_indent)
            self.mark_set("insert", "end")
        return "break"

    def on_enter(self, event):
        """Handle Enter key - execute if complete, newline if incomplete."""
        self.hide_suggestions()
        
        if self.current_prompt_start:
            # Get text from after the prompt to end
            prompt_end = f"{self.current_prompt_start} + 3c"  # Skip ">>> "
            command = self.get(prompt_end, "end-1c")
            
            if not command.strip():
                return "break"
            
            # Check if it's an incomplete statement
            if self.is_incomplete_statement(command):
                # Add newline with auto-indent
                current_line_start = self.index("insert linestart")
                current_line_end = self.index("insert lineend")
                current_line = self.get(current_line_start, current_line_end)
                base_indent = self.get_indent_level(current_line)
                
                if self.should_auto_indent(current_line):
                    base_indent += 4
                
                self.insert("insert", "\n" + " " * base_indent)
                self.see("end")
                return "break"
            
            # Execute the complete command
            if command.strip():
                self.command_history.append(command)
                self.history_index = len(self.command_history)
                
                # Move to end and add newline for the executed command
                self.mark_set("insert", "end")
                self.insert("end", "\n")
                self.see("end")

                # Execute the command in a thread to prevent freezing
                threading.Thread(target=self.execute_command_and_add_prompt, args=(command,), daemon=True).start()
            # self.see("end")

        return "break"

    def highlight_current_line(self):
        if not self.current_prompt_start:
            return
            
        # Clear existing syntax highlighting tags from current line
        line_start = self.current_prompt_start
        line_end = "end-1c"
        
        # Remove all token tags from current line
        for token, style in self.style:
            self.tag_remove(str(token), line_start, line_end)
        
        # Get the command text (without the prompt)
        command = self.get(line_start, line_end)
        
        if not command.strip():
            return
            
        # Highlight the command
        self.mark_set("range_start", line_start)
        
        for token, content in pygments.lex(command, self.lexer):
            if content.strip():  # Only highlight non-whitespace
                self.mark_set("range_end", f"range_start + {len(content)}c")
                self.tag_add(str(token), "range_start", "range_end")
            self.mark_set("range_start", f"range_start + {len(content)}c")

    def write_output(self, text, tag="output"):
        """Write output to the console - thread safe."""
        def _write():
            # Insert output at the end
            self.insert("end", text + "\n", tag)
            self.see("end")
        
        # Use after() to ensure GUI updates happen on main thread
        self.after(0, _write)

    def add_new_prompt(self):
        """Add a new prompt - thread safe."""
        def _add_prompt():
            self.insert("end", ">>> ")
            self.tag_add("prompt", "end-4c", "end")
            self.current_prompt_start = self.index("end-4c")
            self.mark_set("insert", "end")
            self.see("end")
        
        self.after(0, _add_prompt)

    def execute_command_and_add_prompt(self, command):
        """Execute a command and then add a new prompt."""
        try:
            # Try eval first for expressions
            result = eval(command, self.master.userGlobals, self.master.userLocals)
            if result is not None:
                self.write_output(str(result), "result")
                self.master.userLocals["_"] = result
        except SyntaxError:
            try:
                # If eval fails, try exec for statements
                exec(command, self.master.userGlobals, self.master.userLocals)
            except Exception:
                self.write_output(traceback.format_exc(), "error")
        except Exception:
            self.write_output(traceback.format_exc(), "error")
        
        # Add new prompt after execution is complete
        self.add_new_prompt()


class InteractiveConsole(ctk.CTk):
    def __init__(self, userGlobals=None, userLocals=None):
        super().__init__()
        self.title("Live Interactive Console")
        self.geometry("900x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # If no globals/locals provided, get them from caller frame
        if userGlobals is None or userLocals is None:
            caller_frame = inspect.currentframe().f_back
            if userGlobals is None:
                userGlobals = caller_frame.f_globals
            if userLocals is None:
                userLocals = caller_frame.f_locals

        # Create frame for the text widget
        frame = ctk.CTkFrame(self)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Single console text widget
        self.console = InteractiveConsoleText(
            frame, 
            wrap="word", 
            bg="#1e1e1e", 
            fg="white", 
            insertbackground="white",
            font=("Consolas", 12)
        )
        self.console.pack(fill="both", expand=True, padx=5, pady=5)

        # Namespace
        self.userGlobals = userGlobals
        self.userLocals = userLocals

        # Redirect stdout/stderr to write to console
        sys.stdout = StdoutRedirect(self.console.write_output)
        sys.stderr = StdoutRedirect(lambda text, tag: self.console.write_output(text, "error"))

        # Give console access to namespaces
        self.console.master = self
    
    def probe(self, *args, **kwargs):
        self.mainloop(*args, **kwargs)

# Example usage
if __name__ == "__main__":
    foo = 42

    def greet(name):
        print(f"Hello {name}!")
        return f"Greeted {name}"

    InteractiveConsole().probe()