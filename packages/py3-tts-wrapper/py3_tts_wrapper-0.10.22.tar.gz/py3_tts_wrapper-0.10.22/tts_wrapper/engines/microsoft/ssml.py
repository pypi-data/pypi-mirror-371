from typing import Optional

from tts_wrapper.ssml import BaseSSMLRoot, SSMLNode

# Microsoft/ssml.py


class MicrosoftSSML(BaseSSMLRoot):
    def __init__(self, lang: str, voice: str) -> None:
        self.lang = lang
        self.voice = voice
        self._inner = SSMLNode("voice", {"name": self.voice})
        self._root = SSMLNode(
            "speak",
            {
                "version": "1.0",
                "xml:lang": self.lang,
                "xmlns": "http://www.w3.org/2001/10/synthesis",
                "xmlns:mstts": "http://www.w3.org/2001/mstts",
            },
        ).add(self._inner)
        self._prosody = None

    def encode(self) -> str:
        return str(self)

    def add(self, text: str) -> str:
        self._inner.add(text)
        return str(self)

    def set_voice(self, new_voice: str, new_lang: str) -> None:
        """Updates the voice and language for the SSML without reconstructing the SSML nodes."""
        self.voice = new_voice
        self.lang = new_lang
        self._inner.update_attributes({"name": new_voice})
        self._root.update_attributes({"xml:lang": new_lang})

    def break_(self, time: str) -> "MicrosoftSSML":
        self._inner.add(SSMLNode("break", attrs={"time": time}))
        return self

    def say_as(
        self,
        text: str,
        interpret_as: str,
        format: Optional[str] = None,
    ) -> "MicrosoftSSML":
        attrs = {"interpret-as": interpret_as}
        if format:
            attrs["format"] = format
        self._inner.add(SSMLNode("say-as", attrs=attrs, children=[text]))
        return self

    def emphasis(self, text: str, level: str = "moderate") -> "MicrosoftSSML":
        self._inner.add(SSMLNode("emphasis", attrs={"level": level}, children=[text]))
        return self

    def prosody(
        self,
        text: str,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        volume: Optional[str] = None,
    ) -> "MicrosoftSSML":
        attrs = {}
        if rate:
            attrs["rate"] = rate
        if pitch:
            attrs["pitch"] = pitch
        if volume:
            attrs["volume"] = volume
        self._inner.add(SSMLNode("prosody", attrs=attrs, children=[text]))
        return self

    def clear_ssml(self) -> None:
        self._inner.clear_ssml()
