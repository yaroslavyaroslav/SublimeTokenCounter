import sublime
import sublime_plugin
import tiktoken

VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED = "token_count_enabled"
PHANTOM_TEMPLATE = '<span style="color: lightgreen;">Chars</span>: <span style="color: lightgreen;">{characters_count:,}</span>,  <span style="color: lightcoral;">Tokens</span>: <span style="color: lightcoral;">{token_count:,}</span> <a href="close">[x]</a>'


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

        chars_count = len(total_text)

        self.show_phantom(selections[0], chars_count, total_token_count)
        view_settings.set(VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED, True)

    def count_tokens(self, text):
        settings = sublime.load_settings('TokenCounter.sublime-settings')
        tokenizer_encoding = settings.get('tokenizer_encoding', 'cl100k_base')
        model_name = settings.get('model_name', None)
        print(model_name)
        if model_name:
            tokenizer = tiktoken.encoding_for_model(model_name)
        else:
            tokenizer = tiktoken.get_encoding(tokenizer_encoding)

        tokens = tokenizer.encode(text)
        return len(tokens)

    def show_phantom(self, region, characters_count, token_count):
        # Create the phantom content
        phantom_content = PHANTOM_TEMPLATE.format(characters_count=characters_count, token_count=characters_count)

        # Use the add_phantom method to include the phantom
        self.view.add_phantom(
            "token_count",
            region,
            phantom_content,
            sublime.LAYOUT_INLINE,
            on_navigate=self.close_phantom,
        )

    def close_phantom(self, _):
        self.view.erase_phantoms("token_count")
        self.view.settings().set(VIEW_SETTINGS_KEY_TOKEN_COUNT_ENABLED, False)
