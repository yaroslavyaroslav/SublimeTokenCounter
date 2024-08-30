import sublime
import sublime_plugin
import tiktoken

VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED = "token_count_enabled"

class TokensCountCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view_settings = self.view.settings()
        is_enabled = view_settings.get(VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED, False)

        if is_enabled:
            self.close_phantom(None)  # Close existing phantom
            view_settings.set(VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED, False)
            return

        # Get selected text
        selections = self.view.sel()

        if not selections:
            sublime.message_dialog("No text selected!")
            return


        total_text = "\n".join([self.view.substr(sel) for sel in selections])

        total_token_count = self.count_tokens(total_text)

        self.show_phantom(selections[0], total_token_count)
        view_settings.set(VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED, True)

    def count_tokens(self, text):
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(text)
        return len(tokens)

    def show_phantom(self, region, token_count):
        # Create the phantom content
        phantom_content = f'<span style="color: lightgreen;">Total Tokens:</span> <span style="color: lightcoral;">{token_count}</span> <a href="close">[x]</a>'

        # Use the add_phantom method to include the phantom
        self.view.add_phantom("token_count", region, phantom_content, sublime.LAYOUT_INLINE, on_navigate=self.close_phantom)

    def close_phantom(self, _):
        # Close the phantom display by erasing existing phantoms
        self.view.erase_phantoms("token_count")
