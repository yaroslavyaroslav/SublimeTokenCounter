import sublime
import sublime_plugin
# import tiktoken

class TokenCountCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_phantoms("token_count")

        # Get selected text
        selections = self.view.sel()

        if not selections:
            sublime.message_dialog("No text selected!")
            return

        # Use a specific model's tokenizer; replace with the model you desire
        # tokenizer = tiktoken.get_encoding("gpt-3.5-turbo")  # Update model as needed

        total_token_count = 0

        for sel in selections:
            # selected_text = self.view.substr(sel)
            # total_token_count += self.count_tokens(tokenizer, selected_text)
            total_token_count = 3000

        self.show_phantom(selections[0], total_token_count)

    # def count_tokens(self, tokenizer, text):
    #     # Tokenize the text and return the token count
    #     tokens = tokenizer.encode(text)
    #     return len(tokens)

    def show_phantom(self, region, token_count):
        # Create the phantom content
        phantom_content = f'Total Tokens: {token_count} <a href="close">[x]</a>'

        # Create a phantom at the specified region
        phantom = sublime.Phantom(
            region,  # Position the phantom at the selection
            phantom_content,
            sublime.LAYOUT_INLINE  # Use inline layout for the phantom display
        )

        # Use the add_phantom method to include the phantom
        self.view.add_phantom("token_count", region, phantom_content, sublime.LAYOUT_INLINE, on_navigate=self.close_phantom)

    def close_phantom(self, _):
        # Close the phantom display by erasing existing phantoms
        self.view.erase_phantoms("token_count")