# Tuning run tune-10-basque-qwen3-s300

Offline: same training, merging and Shapley scoring as the vault, no chain.

* `Qwen/Qwen3-1.7B` · LoRA rank 16 on `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj` · 300 local steps · lr 0.0002 · 1 rounds · 12.5 min
* Hidden-test loss: 0.799 → 0.737
* Ownership: ane 34.9%, mikel 24.3%, itziar 40.8%, bob 0.0%
* **Facts recalled.** Mean translation score (chrF, 0-100) on 24 sentences: base model **17.8**, Axon-trained **27.7** (exact matches 0 → 0).

**Q: Translate into Basque: I saw Tom in Boston.**

* Human translation: **Tomek Boston ikusi nuen.**
* Base (chrF 21.6): Era Toma bostonetan.
* Axon-trained (chrF 45.0): Tom Bostonen ikusi dut.

**Q: Translate into Basque: Sami was a lucky man.**

* Human translation: **Sami zorionezko gizona zen.**
* Base (chrF 18.5): Sami era ez zen zuzendu.
* Axon-trained (chrF 20.7): Samik ondo zegoen.

**Q: Translate into Basque: Happy Mother's Day!**

* Human translation: **Zoriontsu Amaren eguna!**
* Base (chrF 15.8): Bilatik ezagutzen da zure marraskuari!
* Axon-trained (chrF 16.8): Zure Txantxa Alderdiaren 5. urte bat izan da!

**Q: Translate into Basque: If it were not for the sun, no living creatures could exist on the earth.**

* Human translation: **Eguzkiagatik ez balitz ez zen izaki bizidunik egongo lurrean.**
* Base (chrF 21.7): Ez da izan zara ezagutako soa, zerrendak gaitzen dute lehendazko bidek erabiltzea.
* Axon-trained (chrF 18.9): Ezin zuela soinuaren aurkako, ez dago bihurtzea Erregean.

**Q: Translate into Basque: After he ate, Tom went to bed.**

* Human translation: **Jan eta gero Tom ohera joan zen.**
* Base (chrF 17.2): Ez zen bidea izan zuen, Tom ezagutzea zegoena.
* Axon-trained (chrF 19.4): Etxetan joango zuen etxe batez galdatu zenuela.

**Q: Translate into Basque: Do it right now!**

* Human translation: **Egin, baina orain!**
* Base (chrF 9.3): Ez da erakundeak ezagutzen du!
* Axon-trained (chrF 5.4): Hemen etorriko.

**Q: Translate into Basque: How many sisters do you have? How many brothers do you have?**

* Human translation: **Zenbat arreba dituzu? Zenbat neba dituzu?**
* Base (chrF 18.5): Ez zen ezagutzen duzu gizakilariak? Ezagutzen duzu berrabatik izenek?
* Axon-trained (chrF 41.5): Zenbat urtekin dute? Zenbat bihurtzeko dituzu?

**Q: Translate into Basque: I'm sure it can be done.**

* Human translation: **Ziur nago egin ahal dela.**
* Base (chrF 9.9): Ez da erabiltzen da.
* Axon-trained (chrF 28.3): Beste dira gabe egiten ahal dugu.

**Q: Translate into Basque: I know Tom helped Mary.**

* Human translation: **Badakit Tom Mary lagundu zuela**
* Base (chrF 19.2): Jokoa da Toma izan zen Maryra.
* Axon-trained (chrF 32.5): Tom Mary-ri onartu zuen, ezagutzen dut.

**Q: Translate into Basque: He sent me a letter.**

* Human translation: **Gutun bat bidali zidan.**
* Base (chrF 15.6): Ez zen maila izendatu zuen.
* Axon-trained (chrF 15.4): Laguntza bat ematen zuten nirekin.

**Q: Translate into Basque: One, two, three, four, five, six, seven, eight, nine, ten.**

* Human translation: **Bat, bi, hiru, lau. bost, sei, zazpi, zortzi, bederatzi, hamar.**
* Base (chrF 15.9): Era, dua, tri, quattro, cinc, sei, set, oito, nein, diez.
* Axon-trained (chrF 19.1): Unua, duana, umea, hiruak, kuaterna, sepia, oinko, neurtzea, zein eta zenbatuta.

**Q: Translate into Basque: Layla asked Sami to leave her alone.**

* Human translation: **Laylak Samiri bakarrik usteko eskatu zion.**
* Base (chrF 20.8): Layla asko Sami ezarazi zeregia.
* Axon-trained (chrF 31.7): Laylak Samiren beldur zela esan zuen.

**Q: Translate into Basque: Will Tom do that?**

* Human translation: **Tomek hori egingo zuen?**
* Base (chrF 11.9): Ez da, Tom ezaraz?
* Axon-trained (chrF 61.4): Tomek hori egin behar du?

**Q: Translate into Basque: I was born in Osaka in 1977.**

* Human translation: **Osakan jaio nintzen 1977an.**
* Base (chrF 27.1): Era naitutako osakaetan 1977ean.
* Axon-trained (chrF 25.8): Osakaen ikastetxea batean, 1977ean naiz nire irteera.

**Q: Translate into Basque: Sami and Layla are here to stay.**

* Human translation: **Sami eta Layla hemen daude geratzeko.**
* Base (chrF 43.8): Sami eta Layla ezagutzen dira.
* Axon-trained (chrF 41.6): Samik eta Laila hemen dagoenekoak dira.

**Q: Translate into Basque: Does Tom like his parents?**

* Human translation: **Gustuko ahal ditu Tomek bere gurasoak ?**
* Base (chrF 12.2): Ezta Tomen ezagutzen du?
* Axon-trained (chrF 21.5): Tomek inoiz ez du zure gizonak gustatzen?

**Q: Translate into Basque: Layla took all the money Sami had.**

* Human translation: **Layla Samiren diru guztia hartu zuen.**
* Base (chrF 22.4): Layla izan zen Sami ezagutako bideak.
* Axon-trained (chrF 34.0): Laylak Samik gauza bat aurkitu zuen.

**Q: Translate into Basque: I hate my job.**

* Human translation: **Gorroto dut nire lana.**
* Base (chrF 12.6): Ez zen maitzen ezagutako zeregia da.
* Axon-trained (chrF 13.8): Ez dut galdian gustatzen.

**Q: Translate into Basque: Where have you been? Everyone phoned you.**

* Human translation: **Non egon zara? Denok deitu dizute**
* Base (chrF 15.6): Ez da ez izan zen? Ezagutzen duzu gaitza.
* Axon-trained (chrF 24.8): Nork ez zaitut? Gurekin bat egon zenik.

**Q: Translate into Basque: What's mine is mine, and what's yours is mine.**

* Human translation: **Nirea nirea da, eta zurea ere nirea da.**
* Base (chrF 28.3): Ez da zuzena da, eta ez da zuzena da.
* Axon-trained (chrF 71.2): Nirea nirea da eta zurea nirea da.

**Q: Translate into Basque: It cannot continue like this.**

* Human translation: **Ezin dut horrela jarraitu.**
* Base (chrF 17.8): Ez ez da gaitu.
* Axon-trained (chrF 20.3): Ezin da hau kontu egin.

**Q: Translate into Basque: There can be more than one correct answer.**

* Human translation: **Erantzun zuzen bat baino gehiago egon ahal dira.**
* Base (chrF 17.1): Ez da izeneko ezagutzak dira.
* Axon-trained (chrF 22.3): Ezin da uneko edo beste beldurra bat egiten ahal nahi.

**Q: Translate into Basque: Don't you think it's funny?**

* Human translation: **Ez duzu uste barregarria denik?**
* Base (chrF 10.5): Ez da ez izan da?
* Axon-trained (chrF 26.6): Ez duzu zegoen beldurik?a?

**Q: Translate into Basque: Excellent!**

* Human translation: **Ederki!**
* Base (chrF 4.6): Bilatua!
* Axon-trained (chrF 5.6): Oso garrantzitsua!
