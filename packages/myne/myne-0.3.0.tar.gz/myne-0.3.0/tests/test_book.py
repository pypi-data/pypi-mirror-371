import pytest
from myne import Book


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            "Sundome!! Milky Way v01 (2021) (Digital) (danke-Empire).cbz",
            Book(
                title="Sundome!! Milky Way",
                volume="1",
                year=2021,
                digital=True,
                group="danke-Empire",
                extension="cbz",
            ),
        ),
        (
            "Val x Love v01 (2018) (Digital) (danke-Empire).cbz",
            Book(
                title="Val x Love",
                volume="1",
                year=2018,
                digital=True,
                group="danke-Empire",
                extension="cbz",
            ),
        ),
        (
            "No Matter How I Look at It, It's You Guys' Fault I'm Not Popular! v01 (2013) (Digital) (danke-Empire).cbz",
            Book(
                title="No Matter How I Look at It, It's You Guys' Fault I'm Not Popular!",
                volume="1",
                year=2013,
                digital=True,
                group="danke-Empire",
                extension="cbz",
            ),
        ),
        (
            "D-Frag! v01 (2014) (F) (Digital) {danke-Empire}.cbz",
            Book(
                title="D-Frag!",
                volume="1",
                year=2014,
                digital=True,
                group="danke-Empire",
                extension="cbz",
                revision=2,
            ),
        ),
        (
            "By the Grace of the Gods v01 (2020) (Digital) (1r0n) (f).cbz",
            Book(
                title="By the Grace of the Gods",
                volume="1",
                year=2020,
                digital=True,
                group="1r0n",
                extension="cbz",
                revision=2,
            ),
        ),
        (
            "Killer Alchemist - Assassinations in Another World v04 (Digital-Compilation) (Square Enix) (Oak) (PRE).cbz",
            Book(
                title="Killer Alchemist - Assassinations in Another World",
                volume="4",
                digital=True,
                compilation=True,
                pre=True,
                publisher="Square Enix",
                group="Oak",
                extension="cbz",
            ),
        ),
        (
            "From Overshadowed to Overpowered - Second Reincarnation of a Talentless Sage v01 (Digital-Compilation) (UP!) (Oak) (f).cbz",
            Book(
                title="From Overshadowed to Overpowered - Second Reincarnation of a Talentless Sage",
                volume="1",
                digital=True,
                compilation=True,
                group="Oak",
                extension="cbz",
                revision=2,
            ),
        ),
        (
            "Buso Renkin v01 (2006) (Digital) (aKraa) (ED).cbz",
            Book(
                title="Buso Renkin",
                volume="1",
                year=2006,
                digital=True,
                group="aKraa",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "Smile Down the Runway v22 (2022) (Digital) (ED).cbz",
            Book(
                title="Smile Down the Runway",
                volume="22",
                year=2022,
                digital=True,
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "Uzumaki (2018) (Digital) (Deluxe Edition 3-in-1) (Mr. Kimiko-Teikō) (ED).cbz",
            Book(
                title="Uzumaki",
                year=2018,
                digital=True,
                edition="Deluxe Edition 3-in-1",
                group="Mr. Kimiko-Teikō",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "NE NE NE (2018) (Digital) (Shadowcat-Empire) (ED).cbz",
            Book(
                title="NE NE NE",
                year=2018,
                digital=True,
                group="Shadowcat-Empire",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "My Wife is Wagatsuma-san v09 (2015) (Digital) (morrol4n) (ED).cbz",
            Book(
                title="My Wife is Wagatsuma-san",
                volume="9",
                year=2015,
                digital=True,
                group="morrol4n",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "Baki v31 (2019) (Digital) (c1fi7) (ED).cbz",
            Book(
                title="Baki",
                volume="31",
                year=2019,
                digital=True,
                group="c1fi7",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "Bungo Stray Dogs - Another Story v01 (2019) (Digital) (faratnis) (ed).cbz",
            Book(
                title="Bungo Stray Dogs - Another Story",
                volume="1",
                year=2019,
                digital=True,
                group="faratnis",
                edited=True,
                extension="cbz",
            ),
        ),
        (
            "Kill the Villainess 001 (2021) (Digital) (1r0n).cbz",
            Book(
                title="Kill the Villainess",
                chapter="1",
                year=2021,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "The Strongest Wizard Becomes a Countryside Guard After Taking an Arrow to the Knee c020.5 (2023) (Digital) (UP!) (Oak).cbz",
            Book(
                title="The Strongest Wizard Becomes a Countryside Guard After Taking an Arrow to the Knee",
                chapter="20.5",
                year=2023,
                digital=True,
                group="Oak",
                extension="cbz",
            ),
        ),
        (
            "The Seven Deadly Sins - Four Knights of the Apocalypse 107.5 (2023) (Digital) (danke-Empire).cbz",
            Book(
                title="The Seven Deadly Sins - Four Knights of the Apocalypse",
                chapter="107.5",
                year=2023,
                digital=True,
                group="danke-Empire",
                extension="cbz",
            ),
        ),
        (
            "Grudge-laden Lackey c001 (2022) (Digital) (Dalte).cbz",
            Book(
                title="Grudge-laden Lackey",
                chapter="1",
                year=2022,
                digital=True,
                group="Dalte",
                extension="cbz",
            ),
        ),
        (
            "Yokohama Kaidashi Kikou - Deluxe Edition (2022-2024) (Digital) (1r0n).cbz",
            Book(
                title="Yokohama Kaidashi Kikou",
                edition="Deluxe Edition",
                year=2022,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "Adults' Picture Book - New Edition v01-02 (2024) (Digital) (LuCaZ).cbz",
            Book(
                title="Adults' Picture Book",
                edition="New Edition",
                volume="1-2",
                year=2024,
                digital=True,
                group="LuCaZ",
                extension="cbz",
            ),
        ),
        (
            "Gravitation - Collector's Edition v01 (2024) (Digital) (LuCaZ).cbz",
            Book(
                title="Gravitation",
                edition="Collector's Edition",
                volume="1",
                year=2024,
                digital=True,
                group="LuCaZ",
                extension="cbz",
            ),
        ),
        (
            "My Name Is Shingo - The Perfect Edition v01-02 (2024) (Digital) (1r0n).cbz",
            Book(
                title="My Name Is Shingo",
                edition="The Perfect Edition",
                volume="1-2",
                year=2024,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "Merin the Mermaid - 00 - Prologue (Digital) (Cobalt001).cbz",
            Book(
                title="Merin the Mermaid",
                chapter="0",
                digital=True,
                group="Cobalt001",
                extension="cbz",
            ),
        ),
        (
            "An Observation Log of My Fiancée Who Calls Herself a Villainess 033.5 - Extra 1 (2022) (Digital) (AntsyLich).cbz",
            Book(
                title="An Observation Log of My Fiancée Who Calls Herself a Villainess",
                chapter="33.5",
                year=2022,
                digital=True,
                group="AntsyLich",
                extension="cbz",
            ),
        ),
        (
            "They ridiculed me for my luckless job, but it's not actually that bad 002 - Of Course it's Weird! (2022) (Digital) (AntsyLich)",
            Book(
                title="They ridiculed me for my luckless job, but it's not actually that bad",
                chapter="2",
                year=2022,
                digital=True,
                group="AntsyLich",
            ),
        ),
        (
            "86--EIGHTY-SIX - Operation High School (2024) (Omnibus Edition) (Digital) (1r0n).cbz",
            Book(
                title="86--EIGHTY-SIX - Operation High School",
                year=2024,
                edition="Omnibus Edition",
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "The Eminence in Shadow v01 (2021) (Digital) (1r0n).cbz",
            Book(
                title="The Eminence in Shadow",
                volume="1",
                year=2021,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "Youjo Senki | The Saga of Tanya the Evil Vol.26",
            Book(
                title="Youjo Senki",
                volume="26",
            ),
        ),
        (
            "Witch and Mercenary v02 [Audiobook] [Seven Seas Siren] [Stick]",
            Book(
                title="Witch and Mercenary",
                volume="2",
                publisher="Seven Seas Siren",
                group="Stick",
            ),
        ),
        (
            "The Too-Perfect Saint - Tossed Aside by My Fiancé and Sold to Another Kingdom v01-02 [Seven Seas] [nao] ",  # Note trailing space
            Book(
                title="The Too-Perfect Saint - Tossed Aside by My Fiancé and Sold to Another Kingdom",
                volume="1-2",
                publisher="Seven Seas Entertainment",
                group="nao",
            ),
        ),
        (
            "Hikyouiku kara Nigetai Watashi | I Want to Escape from Princess Lessons v01 (2025) (Digital) (Seven Seas Edition) (1r0n)",
            Book(
                title="Hikyouiku kara Nigetai Watashi",
                volume="1",
                year=2025,
                digital=True,
                publisher="Seven Seas Entertainment",
                group="1r0n",
            ),
        ),
        (
            "Totto-Chan: The Little Girl at the Window [Kodansha USA] [Stick]",
            Book(
                title="Totto-Chan: The Little Girl at the Window",
                publisher="Kodansha",
                group="Stick",
            ),
        ),
        (
            "That Time I Got Reincarnated as a Slime V01-08 (danke-empire) (Kodansha Comics) ",
            Book(
                title="That Time I Got Reincarnated as a Slime",
                volume="1-8",
                group="danke-empire",
                publisher="Kodansha",
            ),
        ),
        (
            "Attack on Titan/Shingeki no Kyojin v26 (2018) (digital-SD) [Kodansha]",
            Book(
                title="Attack on Titan",
                digital=True,
                volume="26",
                year=2018,
                publisher="Kodansha",
            ),
        ),
        (
            "Spy x Family - Family Portrait [VIZ Media] [Bondman]",
            Book(
                title="Spy x Family - Family Portrait",
                publisher="Viz",
                group="Bondman",
            ),
        ),
        (
            "Slam Dunk - New Edition v13 (Colored Council) (Viz)",
            Book(
                title="Slam Dunk",
                edition="New Edition",
                volume="13",
                group="Colored Council",
                publisher="Viz",
            ),
        ),
        (
            "The Hero-Killing Bride - Volume 02 [J-Novel Club] [Premium].epub",
            Book(
                title="The Hero-Killing Bride",
                volume="2",
                publisher="J-Novel Club",
                edition="Premium",
                extension="epub",
            ),
        ),
        (
            "The Hero-Killing Bride - Volume 02 [J Novels Club] [Premium].epub",
            Book(
                title="The Hero-Killing Bride",
                volume="2",
                publisher="J-Novel Club",
                edition="Premium",
                extension="epub",
            ),
        ),
        (
            "The Summer Hikaru Died v01 [Yen Press] [Stick]",
            Book(
                title="The Summer Hikaru Died",
                volume="1",
                publisher="Yen Press",
                group="Stick",
            ),
        ),
        (
            "The Healer Consort 001-010 (2025) (Digital) (Oak)",
            Book(
                title="The Healer Consort",
                chapter="1-10",
                year=2025,
                digital=True,
                group="Oak",
            ),
        ),
        (
            "Lover Boy v01 (2025) (Digital) (1r0n).cbz",
            Book(
                title="Lover Boy",
                volume="1",
                year=2025,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "Dandadan 191 (2025)",
            Book(
                title="Dandadan",
                chapter="191",
                year=2025,
            ),
        ),
        (
            "Trying Out Alchemy After Being Fired as an Adventurer! 001-042 as v01-09 (Digital-Compilation) (Square Enix) (DigitalMangaFan)  ",  # Note trailing space
            Book(
                title="Trying Out Alchemy After Being Fired as an Adventurer!",
                volume="1-9",
                digital=True,
                compilation=True,
                publisher="Square Enix",
                group="DigitalMangaFan",
            ),
        ),
        (
            "The Healer Consort 001-010 as v01-02 (Digital-Compilation) (Oak)",
            Book(
                title="The Healer Consort",
                volume="1-2",
                digital=True,
                compilation=True,
                group="Oak",
            ),
        ),
        (
            "Natsume & Natsume v04 (2023) (Digital) (1r0n) (PRE)",
            Book(
                title="Natsume & Natsume",
                volume="4",
                year=2023,
                digital=True,
                group="1r0n",
                pre=True,
            ),
        ),
        (
            "The Eminence in Shadow v12.5 (2025) (Digital) (1r0n).cbz",
            Book(
                title="The Eminence in Shadow",
                volume="12.5",
                year=2025,
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "The Death Mage v01-02 (2023-2025) (Digital) (DigitalMangaFan)",
            Book(
                title="The Death Mage",
                volume="1-2",
                year=2023,
                digital=True,
                group="DigitalMangaFan",
            ),
        ),
        (
            "The Death Mage v01-02.25 (2023-2025) (Digital) (DigitalMangaFan)",
            Book(
                title="The Death Mage",
                volume="1-2.25",
                year=2023,
                digital=True,
                group="DigitalMangaFan",
            ),
        ),
        (
            "The Banished Saint's Pilgrimage: From Dying to Thriving 001-010 as v01-02 (Digital-Compilation) (Oak)",
            Book(
                title="The Banished Saint's Pilgrimage: From Dying to Thriving",
                volume="1-2",
                digital=True,
                compilation=True,
                group="Oak",
            ),
        ),
        (
            "Programmed for Heartbreak: Sartain in Love 001-029 as v01-04 (Digital-Compilation) (Oak)",
            Book(
                title="Programmed for Heartbreak: Sartain in Love",
                volume="1-4",
                digital=True,
                compilation=True,
                group="Oak",
            ),
        ),
        (
            "Programmed for Heartbreak: Sartain in Love 001-029 as v01.24-04.24 (Digital-Compilation) (Oak)",
            Book(
                title="Programmed for Heartbreak: Sartain in Love",
                volume="1.24-4.24",
                digital=True,
                compilation=True,
                group="Oak",
            ),
        ),
        (
            "The Otome Heroine's Fight for Survival Volume 05 PREPUB [10/14]",
            Book(
                title="The Otome Heroine's Fight for Survival",
                volume="5",
                pre=True,
            ),
        ),
        (
            "The Hero and the Sage, Reincarnated and Engaged - Volume 04 [J-Novel Club]",
            Book(
                title="The Hero and the Sage, Reincarnated and Engaged",
                volume="4",
                publisher="J-Novel Club",
            ),
        ),
        (
            "Three Cheats from Three Goddesses: The Broke Baron's Youngest Wants a Relaxing Life - Volume 01 [J-Novel Club]",
            Book(
                title="Three Cheats from Three Goddesses: The Broke Baron's Youngest Wants a Relaxing Life",
                volume="1",
                publisher="J-Novel Club",
            ),
        ),
        (
            "Veil - Vol 1 [We Need More Yankiis]",
            Book(
                title="Veil",
                volume="1",
                group="We Need More Yankiis",
            ),
        ),
        (
            "2.5 Dimensional Seduction 185.1 (2025) (Digital) (Rillant).cbz",
            Book(
                title="2.5 Dimensional Seduction",
                chapter="185.1",
                year=2025,
                digital=True,
                group="Rillant",
                extension="cbz",
            ),
        ),
        (
            "Sakamoto Days 210 (2025) (Digital) (Rillant).cbz",
            Book(
                title="Sakamoto Days",
                chapter="210",
                year=2025,
                digital=True,
                group="Rillant",
                extension="cbz",
            ),
        ),
        (
            "I'm a Curse Crafter, and I Don't Need an S-Rank Party! 042.2 (2025) (Digital) (Valdearg).cbz",
            Book(
                title="I'm a Curse Crafter, and I Don't Need an S-Rank Party!",
                chapter="42.2",
                year=2025,
                digital=True,
                group="Valdearg",
                extension="cbz",
            ),
        ),
        (
            "The Case Study of Vanitas 063 (2024) (Digital) (LuCaZ).cbz",
            Book(
                title="The Case Study of Vanitas",
                chapter="63",
                year=2024,
                digital=True,
                group="LuCaZ",
                extension="cbz",
            ),
        ),
        (
            "Hyeonjung's Residence c57 (Void).cbz",
            Book(
                title="Hyeonjung's Residence",
                chapter="57",
                group="Void",
                extension="cbz",
            ),
        ),
        (
            "The Crow's Prince c095 - Season 2 Finale (2022) (Digital) (Dalte).cbz",
            Book(
                title="The Crow's Prince",
                chapter="95",
                year=2022,
                digital=True,
                group="Dalte",
                extension="cbz",
            ),
        ),
        (
            "Edens Zero v01-31, 276-293 (2018-2025) (Digital) (danke-Empire, DeadMan, SlikkyOak)",
            Book(
                title="Edens Zero",
                volume="1-31",
                chapter="276-293",
                year=2018,
                digital=True,
                group="danke-Empire, DeadMan, SlikkyOak",
            ),
        ),
        (
            "Wistoria - Wand and Sword v01-08 + 033-051 (2022-2025) (Digital) (1r0n)",
            Book(
                title="Wistoria - Wand and Sword",
                volume="1-8",
                chapter="33-51",
                year=2022,
                digital=True,
                group="1r0n",
            ),
        ),
        (
            "[Unpaid Ferryman] Gamaran: Shura v01-31 (2022-2025) (Digital) (danke-Empire, Kaos, Rillant)",
            Book(
                title="Gamaran: Shura",
                volume="1-31",
                year=2022,
                digital=True,
                group="danke-Empire, Kaos, Rillant",
            ),
        ),
        (
            "The Eminence in Shadow v01-12 (2021-2025) (Digital) (1r0n)",
            Book(
                title="The Eminence in Shadow",
                volume="1-12",
                year=2021,
                digital=True,
                group="1r0n",
            ),
        ),
        (
            "One-Punch Man 193 (2024) (Digital) (Rillant) (f).cbz",
            Book(
                title="One-Punch Man",
                chapter="193",
                year=2024,
                digital=True,
                group="Rillant",
                revision=2,
                extension="cbz",
            ),
        ),
        (
            "One-Punch Man 193 (2024) (Digital) (Rillant) {f2}.cbz",
            Book(
                title="One-Punch Man",
                chapter="193",
                year=2024,
                digital=True,
                group="Rillant",
                revision=4,
                extension="cbz",
            ),
        ),
        (
            "86--EIGHTY-SIX - Operation High School (2024) (Collector's Edition) (Digital) (1r0n).cbz",
            Book(
                title="86--EIGHTY-SIX - Operation High School",
                year=2024,
                edition="Collector's Edition",
                digital=True,
                group="1r0n",
                extension="cbz",
            ),
        ),
        (
            "Zatch Bell! Revamped Edition v01 (2018 E-Book) (Zatch Bell Makai Scanlations)",
            Book(
                title="Zatch Bell!",
                edition="Revamped Edition",
                volume="1",
                group="Zatch Bell Makai Scanlations",
            ),
        ),
        (
            "Hellsing v01-03 (2023-2024) (Second Edition) (Digital) (LuCaZ)",
            Book(
                title="Hellsing",
                edition="Second Edition",
                volume="1-3",
                year=2023,
                digital=True,
                group="LuCaZ",
            ),
        ),
        (
            "Magic Knight Rayearth 2 {25th Anniversary Edition} (2020) (Digital) (XRA-Empire)",
            Book(
                title="Magic Knight Rayearth 2",
                edition="25th Anniversary Edition",
                year=2020,
                digital=True,
                group="XRA-Empire",
            ),
        ),
        (
            "Gunsmith Cats - Revised Edition (2007) (Digital) (XRA-Empire)",
            Book(
                title="Gunsmith Cats",
                edition="Revised Edition",
                year=2007,
                digital=True,
                group="XRA-Empire",
            ),
        ),
        (
            "Tekkonkinkreet - Black & White 30th Anniversary Edition (2023) (Digital) (1r0n)",
            Book(
                title="Tekkonkinkreet",
                edition="Black & White 30th Anniversary Edition",
                year=2023,
                digital=True,
                group="1r0n",
            ),
        ),
        (
            "Tekkonkinkreet - (Black & White 30th Anniversary Edition) (2023) (Digital) (1r0n)",
            Book(
                title="Tekkonkinkreet",
                edition="Black & White 30th Anniversary Edition",
                year=2023,
                digital=True,
                group="1r0n",
            ),
        ),
        (
            "Black_Summoner_Volume_20_Complete.epub",
            Book(
                title="Black Summoner",
                volume="20",
                extension="epub",
            ),
        ),
        (
            "Ishura v07 [Yen Audio] [Stick].m4b",
            Book(
                title="Ishura",
                volume="7",
                extension="m4b",
                group="Stick",
                publisher="Yen Audio",
            ),
        ),
        (
            "Alice in the Country of Diamonds - Bet on My Heart - Complete [Seven Seas][Scans_Compressed].pdf",
            Book(
                title="Alice in the Country of Diamonds - Bet on My Heart",
                publisher="Seven Seas Entertainment",
                extension="pdf",
            ),
        ),
        (
            "5 Centimeters per Second - One More Side - Complete [Vertical][Scans].pdf",
            Book(
                title="5 Centimeters per Second - One More Side",
                publisher="Vertical",
                extension="pdf",
            ),
        ),
    ],
)
def test_book(filename: str, expected: Book) -> None:
    book = Book.parse(filename)
    assert book == expected
    assert book.to_json() == expected.to_json()
    assert eval(repr(book)) == book == expected
