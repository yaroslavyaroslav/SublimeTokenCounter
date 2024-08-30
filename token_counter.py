import sublime
import sublime_plugin
import subprocess

class TokenCountCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_phantoms("token_count")

        # Get selected text
        selections = self.view.sel()

        if not selections:
            sublime.message_dialog("No text selected!")
            return

        # Use a specific model's tokenizer; replace with the model you desire
        total_text = "\n".join([self.view.substr(sel) for sel in selections])

        token_count = self.count_tokens(total_text)

        self.show_phantom(selections[0], token_count)

    def count_tokens(self, text):
        # Call the Rust binary
        process = subprocess.Popen(
            ["/Users/yar/Development/Rust/token-counter/target/release/tiktoken_counter", "-"],  # Using '-' for stdin
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send the text to stdin and read the output
        stdout, stderr = process.communicate(input=text)

        if process.returncode != 0:
            sublime.message_dialog(f"Error running Rust token counter: {stderr}")
            return 0

        # Parse the token count
        try:
            return int(stdout.strip())
        except ValueError:
            return 0

    def show_phantom(self, region, token_count):
        # Create the phantom content
        phantom_content = f'<span style="color: lightgreen;">Total Tokens:</span> <span style="color: lightcoral;">{token_count}</span> <a href="close">[x]</a>'

        # Use the add_phantom method to include the phantom
        self.view.add_phantom("token_count", region, phantom_content, sublime.LAYOUT_INLINE, on_navigate=self.close_phantom)

    def close_phantom(self, _):
        # Close the phantom display by erasing existing phantoms
        self.view.erase_phantoms("token_count")