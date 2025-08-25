from songfinder import classSettings as settings
from songfinder import gestchant


class Diapo:
    def __init__(self, element, numero, stype, max_car, nombre=0, text=""):
        self.element = element
        self.numero = numero
        self.nombre = nombre
        self.etype = element.etype
        self.stype = stype
        self.max_car = max_car
        self._title = None

        self._text = text
        self._nbLignes = None

        self.police = None
        self._theme_name = "theone"
        self._aspectRatio = None

    @property
    def text(self):
        if not self._nbLignes:
            newline = settings.GENSETTINGS.get("Syntax", "newline")
            text = self._text
            text = "\n" + newline + "\n" + text
            text = text.replace("\n ", "\n")
            text = gestchant.numerote(text, self.numero, self.nombre, self.etype)
            text = gestchant.print_title(
                text,
                self.element.title,
                self.numero,
                self.etype,
            )
            text = gestchant.check_bis(text, self.etype)
            text = gestchant.saut_ligne(text, self.max_car, self.etype)
            text = gestchant.verifie_ponctuation(text, self.etype)
            text = gestchant.nettoyage(text)
            text = gestchant.clean_maj(text, self.etype)
            text = gestchant.verifie_ponctuation_maj(text, self.etype)
            text = gestchant.majuscule(text, self.etype)
            text = gestchant.nettoyage(text)
            text = gestchant.clean_line(text)

            self._nbLignes = len([ligne for ligne in text.splitlines() if ligne != ""])
            self._text = text
        return self._text

    @property
    def title(self):
        if not self._title:
            if self.element.title:
                self._title = self.etype + " -- " + self.element.title
                if self.nombre > 1:
                    self._title = f"{self._title} -- {self.numero}/{self.nombre}"
            else:
                self._title = self.etype
        return self._title

    @property
    def beamer(self):
        text = self.text
        if settings.PRESSETTINGS.get(self.etype, "Numerote_diapo"):
            num = f"({self.numero!s}/{self.nombre!s})"
            text = text.replace(num, f"{{\\footnotesize {num}}}\n\\vspace{{1em}}\n")
        elif settings.PRESSETTINGS.get(self.etype, "Print_title"):
            text = text.replace(
                f"{self.element.title.upper()}\n",
                f"{self.element.title.upper()}\n\\vspace{{1em}}\n",
            )
        # Add background header
        return text

    @property
    def latex(self):
        # Remove title if is in text because it will be added latter
        text = self.text
        lengh_title = len(self.element.title)
        if text[:lengh_title] == self.element.title.upper():
            text = text[lengh_title:]

        # Add subtitle: Refrain; Pont
        if self.stype == "\\sc":
            tab = "\\tab "
            title = "Refrain"
        elif self.stype == "\\spc":
            tab = "\\tab "
            title = "Pre-refrain"
        elif self.stype == "\\sb":
            tab = ""
            title = "Pont"
        else:
            tab = ""
            title = ""
        add = f"\n\\textbf{{{title}}}\n{tab}"

        if title != "" and text.find(add) == -1:
            out = add + text.replace("\n", f"\n{tab}") + "\n\n"
        else:
            out = text
        return out

    @property
    def num(self):
        if self.numero:
            text = "(" + str(self.numero) + "/" + str(self.nombre) + ")"
        else:
            text = ""
        return text

    @property
    def theme_name(self):
        return self._theme_name

    @property
    def background_name(self):
        back_name = settings.PRESSETTINGS.get(self.etype, "Background")
        if self.etype == "image":
            back_name = self.element.chemin
            self._aspectRatio = "keep"
        return back_name

    @property
    def markdown(self):
        # Add subtitle: Refrain; Pont
        if self.stype == "\\sc":
            tab = "> "
            title = "Refrain"
        elif self.stype == "\\spc":
            tab = "> "
            title = "Pre-refrain"
        elif self.stype == "\\sb":
            tab = ""
            title = "Pont"
        else:
            tab = ""
            title = ""
        add = f"\n**{title}**\n{tab}"

        if title != "" and self.text.find(add) == -1:
            out = add + self.text.replace("\n", f"\n{tab}") + "\n\n"
        else:
            out = self.text
        return out

    def print_diapo(self, theme):
        theme.text = self.text
        theme.update_back(self.background_name, self._aspectRatio)
        theme.update_font_color()
        theme.resize_font()

    def prefetch(self, themes, text=False):
        for theme in reversed(themes):
            if text:
                theme.text = self.text
                theme.resize_font()
            theme.prefetch_back(self.background_name, self._aspectRatio)
