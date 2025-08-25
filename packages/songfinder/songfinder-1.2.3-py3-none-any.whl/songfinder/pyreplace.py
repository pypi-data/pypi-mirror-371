# cython: language_level=3 # noqa: ERA001

try:
    from songfinder import libLoader

    module = libLoader.load(__file__, py2c=True)
    globals().update(
        {n: getattr(module, n) for n in module.__all__}
        if hasattr(module, "__all__")
        else {k: v for (k, v) in module.__dict__.items() if not k.startswith("_")},
    )
except (ImportError, NameError):
    # Fall back
    def simplify_char(text):
        text = text.decode("utf-8")
        text = (
            text.replace("(e)", "")
            .replace("(h)", "")
            .replace("(f)", "")
            .replace("~", " ")
            .replace(".", " ")
            .replace(",", " ")
            .replace(";", " ")
            .replace(":", " ")
            .replace("!", " ")
            .replace("'", " ")
            .replace("?", " ")
            .replace('"', " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace("[v", " ")
            .replace("]", " ")
            .replace("/", " ")
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .replace("_", " ")
            .replace("-", " ")
            .replace(" bis ", " ")
            .replace(" ter ", " ")
            .replace(" x2 ", " ")
            .replace(" x3 ", " ")
            .replace(" x4 ", " ")
        )

        for i in range(10):
            text = text.replace(str(i), "")

        return text

    def cleanup_space(text):
        text = text.replace("    ", " ").replace("   ", " ").replace("  ", " ")
        return text.encode("utf-8")

    def cleanup_char(text):
        text = text.decode("utf-8")
        return (
            text.replace(" \n", "\n")
            .replace("\n ", "\n")
            .replace("\r\n", "\n")
            .replace("\t", "")
            .replace("\n\n\n\n", "\n")
            .replace("\n\n\n", "\n")
            .replace("\n\n", "\n")
        )
