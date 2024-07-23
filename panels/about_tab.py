import subprocess
import logging
import platform
import getmac
import socket
import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['about_tab']

        self.image = self._gtk.Image("info-bubble", self._gtk.content_width * .2, self._gtk.content_height * .2)
        self.core_path = os.path.join('/home', 'pi', 'SyncraftCore')
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.en_btn = self._gtk.Button("timezone", "English - EN", None, .80, Gtk.PositionType.LEFT)
        self.pt_btn = self._gtk.Button("timezone", "Português - PT", None, .80, Gtk.PositionType.LEFT)
        self.de_btn = self._gtk.Button("timezone", "Deutsch - DE", None, .80, Gtk.PositionType.LEFT)
        self.pl_btn = self._gtk.Button("timezone", "Polski - PL", None, .80, Gtk.PositionType.LEFT)

        self.en_btn.connect("clicked",self.set_text, "EN")
        self.pt_btn.connect("clicked",self.set_text, "PT")
        self.de_btn.connect("clicked",self.set_text, "DE")
        self.pl_btn.connect("clicked",self.set_text, "PL")

        self.btn_grid = self._gtk.HomogeneousGrid()
        self.btn_grid.attach(self.en_btn, 0, 0, 1, 1)
        self.btn_grid.attach(self.de_btn, 0, 1, 1, 1)
        self.btn_grid.attach(self.pt_btn, 1, 0, 1, 1)
        self.btn_grid.attach(self.pl_btn, 1, 1, 1, 1)

        self.content.add(self.info)

        self.main_label = Gtk.Label("")
        self.set_text(button=None, lang="EN")

        self.main_label.set_halign(Gtk.Align.CENTER)
        self.main_label.set_valign(Gtk.Align.CENTER)

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.btn_grid.attach(self.main_label, 0, 2, 2, 10)

        scroll.add(self.btn_grid)

        self.content.add(scroll)

        grid = self._gtk.HomogeneousGrid()

        self.labels['about_tab'] = self._gtk.HomogeneousGrid()
        self.labels['about_tab'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['about_tab'])

    def set_text(self, button, lang: str) -> str:
        txt: str = """"""
        if lang == "PT":
            txt = """
            SwierVision é um fork do KlipperScreen, uma
            interface de código aberto dedicada a impressoras
            3D que utilizam o firmware Klipper. Graças ao time
            original do KlipperScreen, nossas impressoras
            receberam rapidamente uma interface maravilhosa para
            uso contínuo, que foi aprimorada pelo time de
            desenvolvimento dedicado da Syncraft.
            
            O nome do software "SwierVision" deveria ter sido algo
            genérico como "KlipperScreenIDEX" ou similar; entretanto,
            o CEO do projeto insistiu que o primeiro programador do
            projeto deveria ter seu nome estampado em algum software
            da máquina. O sobrenome deste programador era complicado,
            principalmente considerando que o idioma primário do time
            de desenvolvimento é o português brasileiro, não o polonês.
            Portanto, chamar um software de "SWIERCZYNSKI" seria uma
            tarefa árdua, e assim foi criado o nome "SwierVision", que
            coloca as iniciais do sobrenome (SWIER) e finaliza com
            "Visão" (VISION). Contudo, essa estratégia não foi efetiva
            no objetivo de facilitar a pronúncia do software, e o time
            continuou pronunciando o nome do software de forma incorreta.
            Para o bem da comunicação do time de desenvolvimento, outros
            forks, como Mainsail, mantiveram seus nomes originais.

            O nome da Syncraft IDEX também foi modificado, anteriormente
            referenciado como "Syncraft X2", combinando com o nome
            "Syncraft X1" (máquina de um único extrusor da Syncraft).
            Não conseguimos encontrar uma única pessoa na empresa que
            discordasse de que o nome "Syncraft IDEX" era melhor que
            "Syncraft X2", então o alteramos.

            Houve uma discussão dentro da empresa sobre desenvolver
            um jogo para jogar enquanto imprime, algo fácil e rápido,
            como um jogo inspirado em Brickgame™ ou similar, mas, por 
            questões de gerenciamento de tempo no desenvolvimento, a
            ideia foi descartada. Entretanto, é difícil negar que
            aguardar o término das impressões seria menos entediante
            se houvesse um jogo para passar o tempo.
            A ideia do jogo pode ter sido descartada, mas serviu para
            criar uma piada interna dentro do time de desenvolvimento
            sobre como deveríamos criar um modelo da Syncraft com
            placas de vídeo RTX™ 4080 embutidas, para que o
            consumidor pudesse jogar jogos de alto calibre como
            Cyberpunk 2077™ enquanto aguardava suas impressões,
            já utilizando o calor gerado pela placa de vídeo
            para aquecer a mesa.

            Infelizmente, o CEO não aprovou a ideia.
            """
        elif lang == "EN":
            txt = """
            SwierVision is a KlipperScreen fork,
            an open source interface dedicated to
            3D printers using Klipper firmware.
            Thanks to the original KlipperScreen team,
            our printers quickly got a wonderful
            interface, which has been improved by
            Syncraft's dedicated development team.
            The software name "SwierVision" should
            have been something generic like
            "KlipperScreenIDEX" or similar;
            however, the project's CEO insisted
            that the project's first programmer
            should have his name on some of the
            machine's software. This programmer's
            last name was complicated, especially
            considering that the dev team's primary
            language is Brazilian Portuguese, not Polish.
            Therefore, calling a software "SWIERCZYNSKI"
            would be an hard task, and thus the name
            "SwierVision" was created, which includes
            the initials of the surname (SWIER) and ends
            with "Vision". However, this strategy was not
            effective in facilitating the pronunciation
            of the software, and the team continued to
            pronounce the name of the software incorrectly.
            For the sake of communication, other forks,
            such as Mainsail, kept their original names.

            Syncraft IDEX's name has also been changed,
            previously referred to as "Syncraft X2",
            combining with the name "Syncraft X1"
            (Syncraft's single extruder machine).
            We couldn't find a single person at the
            company who disagreed that the name
            "Syncraft IDEX" was better than "Syncraft X2",
            so we changed it.

            There was also a discussion among part of the
            company whether it was a valid idea to put out
            a game that was easy and quick to develop
            (like a game inspired by Brickgame™), but for
            reasons of time management in development,
            the idea was discarded. However, it's hard to
            deny that waiting for prints to finish would be
            less boring if there was a fun game to play.
            The idea for the game may have been discarded,
            but it served to create an internal joke within
            the dev team, about how we should create a Syncraft
            model with built-in RTX™ 4080 so that consumers
            could play heavy games like Cyberpunk 2077™
            while waiting, while using the heat generated by
            the graphics card to heat up the printer bed.
            
            Unfortunately, the CEO did not approve the idea.
            """
        elif lang == "DE":
            txt = """
            SwierVision ist ein Zweig von KlipperScreen,
            einer Open-Source-Schnittstelle für 3D-Drucker
            mit Klipper-Firmware. Dank des ursprünglichen
            KlipperScreen-Teams erhielten unsere Drucker
            schnell eine wunderbare Benutzeroberfläche
            für den weiteren Gebrauch, die vom engagierten
            Entwicklungsteam von Syncraft verbessert wurde.
            Der Softwarename „SwierVision“ sollte etwas
            Generisches wie „KlipperScreenIDEX“ oder ähnliches
            sein; Der CEO des Projekts bestand jedoch darauf,
            dass der Name des ersten Programmierers des Projekts
            auf einige Softwareprogramme der Maschine gedruckt
            werden sollte. Der Nachname dieses Programmierers
            war kompliziert, insbesondere wenn man bedenkt,
            dass die Hauptsprache des Entwicklungsteams
            brasilianisches Portugiesisch und nicht
            Polnisch ist. Daher wäre es eine mühsame Aufgabe,
            eine Software „SWIERCZYNSKI“ zu nennen, und so
            wurde der Name „SwierVision“ geschaffen, der
            die Initialen des Nachnamens (SWIER) enthält
            und mit „Vision“ (VISION) endet. Allerdings
            war diese Strategie bei der Erleichterung der
            Aussprache der Software nicht wirksam und das
            Team sprach den Namen der Software weiterhin
            völlig falsch aus. Aus Gründen der Kommunikation
            des Entwicklungsteams behielten andere Forks,
            wie z. B. Mainsail, ihre ursprünglichen Namen.

            Der Name des Syncraft IDEX wurde ebenfalls geändert
            und wurde zuvor als „Syncraft X2“ bezeichnet,
            kombiniert mit dem Namen „Syncraft X1“
            (Syncrafts Einzelextrudermaschine). Wir konnten
            keine einzige Person im Unternehmen finden, die
            der Meinung war, dass der Name „Syncraft IDEX“
            besser sei als „Syncraft X2“, also haben wir ihn geändert.

            In einem Teil des Unternehmens gab es eine Diskussion
            darüber, ob es eine sinnvolle Idee sei, ein Spiel
            herauszubringen, das einfach und schnell zu entwickeln
            sei (wie ein von Brickgame™ oder ähnlichem inspiriertes
            Spiel), aber aus Gründen des Zeitmanagements in der
            Entwicklung wurde die Idee abgelehnt wurde verworfen.
            Es lässt sich jedoch kaum leugnen, dass das Warten auf
            den Abschluss der Ausdrucke weniger langweilig wäre,
            wenn es ein Spiel zum Zeitvertreib gäbe. Die Idee für
            das Spiel wurde vielleicht verworfen, aber sie diente
            dazu, innerhalb des Entwicklungsteams einen internen
            Witz darüber zu erzeugen, wie wir ein Syncraft-Modell
            mit integrierten RTX™ 4080-Grafikkarten entwickeln
            sollten, damit Verbraucher hochkarätige Spiele spielen
            können. B. Cyberpunk 2077™, während Sie auf Ihre
            Ausdrucke warten und bereits die von der Grafikkarte
            erzeugte Wärme zum Heizen des Tisches nutzen.
            
            Leider stimmte der CEO der Idee nicht zu.
            """
        elif lang == "PL":
            txt = """
            SwierVision jest rozwidleniem KlipperScreen,
            interfejsu open source dedykowanego drukarkom
            3D korzystającym z oprogramowania sprzętowego
            Klipper. Dzięki oryginalnemu zespołowi KlipperScreen
            nasze drukarki szybko otrzymały wspaniały
            interfejs do dalszego użytku, który został ulepszony
            przez dedykowany zespół programistów Syncraft.
            Nazwa oprogramowania „SwierVision” powinna mieć
            nazwę ogólną, np. „KlipperScreenIDEX” lub podobną;
            jednakże dyrektor generalny projektu nalegał, aby
            nazwisko pierwszego programisty projektu było
            wydrukowane na części oprogramowania maszyny.
            Nazwisko tego programisty było skomplikowane,
            zwłaszcza biorąc pod uwagę, że głównym językiem
            zespołu programistów jest brazylijski portugalski,
            a nie polski. Dlatego nazwanie programu „SWIERCZYNSKI”
            byłoby zadaniem trudnym i dlatego powstała nazwa
            „SwierVision”, która zawiera inicjały nazwiska (SWIER)
            i kończy się na „Vision” (VISION). Jednak ta strategia
            nie okazała się skuteczna w ułatwianiu wymowy
            oprogramowania, w związku z czym zespół w dalszym ciągu
            całkowicie niepoprawnie wymawiał nazwę oprogramowania.
            W trosce o komunikację zespołu programistów inne
            widelce, takie jak Mainsail, zachowały swoje
            oryginalne nazwy.

            Zmieniono także nazwę Syncraft IDEX, wcześniej
            określaną jako „Syncraft X2”, łączącą się z nazwą
            „Syncraft X1” (pojedyncza wytłaczarka Syncraft).
            Nie znaleźliśmy ani jednej osoby w firmie, która nie
            zgodziłaby się, że nazwa „Syncraft IDEX” jest lepsza
            niż „Syncraft X2”, więc ją zmieniliśmy.

            Wśród części firmy wywiązała się dyskusja, czy słusznym
            pomysłem było wypuszczenie gry, która byłaby łatwa i
            szybka w przygotowaniu (jak gra inspirowana Brickgame™
            lub podobną), ale ze względu na zarządzanie czasem w
            tworzeniu, pomysł został odrzucony. Trudno jednak
            zaprzeczyć, że oczekiwanie na zakończenie wydruków
            byłoby mniej nudne, gdyby istniała gra dla zabicia czasu.
            Pomysł na grę mógł zostać odrzucony, ale wywołał wewnętrzny
            żart w zespole programistów na temat tego, jak powinniśmy
            stworzyć model Syncraft z wbudowanymi kartami graficznymi
            RTX™ 4080, aby konsumenci mogli grać w gry wysokiego kalibru.
            jak Cyberpunk 2077™, czekając na wydruki, wykorzystując już
            ciepło generowane przez kartę graficzną do ogrzewania stołu.
            
            Niestety dyrektor nie zgodził się z tym pomysłem.
            """
        else:
            txt = lang
    


        self.main_label.set_text(str(txt))