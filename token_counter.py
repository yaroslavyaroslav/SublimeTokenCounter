import sublime
from sublime import Phantom, PhantomSet, PhantomLayout
import sublime_plugin
import tiktoken
import threading

VIEW_SETTINGS_KEY_TOKEN_COUNT = "VIEW_SETTINGS_KEY_TOKEN_COUNT"
TOKEN_PHANTOM_KEY = "token_count"
PHANTOM_TEMPLATE = (
    '<span style="color: lightgreen;">Chars</span>: <span style="color: lightgreen;">{characters_count:,}</span>,'
    + '  <span style="color: lightcoral;">Tokens</span>:'
    + ' <span style="color: lightcoral;">{token_count:,}</span> <a href="close">[x]</a>'
)


def get_tokenizer_async(callback, model_name=None, tokenizer_encoding="cl100k_base"):
    def load_tokenizer():
        if model_name:
            tokenizer = tiktoken.encoding_for_model(model_name)
        else:
            tokenizer = tiktoken.get_encoding(tokenizer_encoding)

        sublime.set_timeout(lambda: callback(tokenizer), 0)

    threading.Thread(target=load_tokenizer).start()


class TokensCountCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view_settings = self.view.settings()
        is_enabled = view_settings.get(VIEW_SETTINGS_KEY_TOKEN_COUNT, False)

        if is_enabled:
            self.close_phantom(None)
            view_settings.set(VIEW_SETTINGS_KEY_TOKEN_COUNT, False)
            return

        selections = self.view.sel()

        if not selections:
            sublime.message_dialog("No text selected!")
            return

        total_text = "\n".join([self.view.substr(sel) for sel in selections])

        chars_count = len(total_text)

        self.load_and_count_tokens(total_text, chars_count, selections[0])
        view_settings.set(VIEW_SETTINGS_KEY_TOKEN_COUNT, True)

    def on_tokenizer_ready(self, tokenizer, text, chars_count, region):
        token_count = self.count_tokens_sync(tokenizer, text)
        self.show_phantom(region, chars_count, token_count)

    def load_and_count_tokens(self, text, chars_count, region):
        settings = sublime.load_settings("TokenCounter.sublime-settings")
        model_name: str | None = settings.get("model_name", None)  # type: ignore
        tokenizer_encoding: str = settings.get("tokenizer_encoding", "cl100k_base")  # type: ignore

        get_tokenizer_async(
            callback=lambda tokenizer: self.on_tokenizer_ready(
                tokenizer, text, chars_count, region
            ),
            model_name=model_name,
            tokenizer_encoding=tokenizer_encoding,
        )

    def count_tokens_sync(self, tokenizer, text):
        tokens = tokenizer.encode(text)
        return len(tokens)

    def show_phantom(self, region, characters_count, token_count):
        phantom_content = PHANTOM_TEMPLATE.format(
            characters_count=characters_count, token_count=token_count
        )

        line_beginning = self.view.line(self.view.sel()[0])

        phantom = Phantom(
            line_beginning, phantom_content, PhantomLayout.INLINE, self.close_phantom
        )

        self.phantom_set = PhantomSet(self.view, TOKEN_PHANTOM_KEY)

        self.phantom_set.update([phantom])

    def close_phantom(self, _):
        self.phantom_set.update([])
        self.view.settings().set(VIEW_SETTINGS_KEY_TOKEN_COUNT, False)
