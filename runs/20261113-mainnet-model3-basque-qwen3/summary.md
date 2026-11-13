# Run 20261113-mainnet-model3-basque-qwen3

* Hardware: **NVIDIA GeForce RTX 4090** · base model `Qwen/Qwen3-1.7B` · wall time 17.3 min
* Contract: [`axon.ebukaa.near`](https://nearblocks.io/address/axon.ebukaa.near) (mainnet), model id 3
* Hidden-test loss: **0.797 → 0.723**
* Paid queries: 1 · paid to owners 0.0095 NEAR (after the 5% platform fee)

## Ownership

| Contributor | Share |
|---|---|
| ane | 35.1% |
| mikel | 0.0% |
| itziar | 64.9% |
| bob | 0.0% |

## Rounds

| Round | Test loss | Shares minted | Adapter hash |
|---|---|---|---|
| 1 | 0.723 | ane 26239, bob 0, itziar 48497, mikel 0 | `d938a6bae3c506e5…` |

## Same question, base model vs Axon-trained model

Reworded questions about facts in the contributors' private data. *Reference* is the answer in that data.

* **Facts recalled.** Mean translation score (chrF, 0-100) on 24 sentences: base model **17.8**, Axon-trained **30.7** (exact matches 0 → 0).

**Q: Translate into Basque: I saw Tom in Boston.**

* Human translation: **Tomek Boston ikusi nuen.**
* Base (chrF 21.6): Era Toma bostonetan.
* Axon-trained (chrF 65.2): Tomari Bostontean ikusi nuen.

**Q: Translate into Basque: Sami was a lucky man.**

* Human translation: **Sami zorionezko gizona zen.**
* Base (chrF 18.5): Sami era ez zen zuzendu.
* Axon-trained (chrF 22.2): Samik guraso zuela izan zen.

**Q: Translate into Basque: Happy Mother's Day!**

* Human translation: **Zoriontsu Amaren eguna!**
* Base (chrF 15.8): Bilatik ezagutzen da zure marraskuari!
* Axon-trained (chrF 15.7): Zure Zaraitzaren Haurituak!

**Q: Translate into Basque: If it were not for the sun, no living creatures could exist on the earth.**

* Human translation: **Eguzkiagatik ez balitz ez zen izaki bizidunik egongo lurrean.**
* Base (chrF 21.7): Ez da izan zara ezagutako soa, zerrendak gaitzen dute lehendazko bidek erabiltzea.
* Axon-trained (chrF 20.5): Ez da utzi guren bidean jantza behar izango zuela, ezin duzu bihurtzen joaten.

**Q: Translate into Basque: After he ate, Tom went to bed.**

* Human translation: **Jan eta gero Tom ohera joan zen.**
* Base (chrF 17.2): Ez zen bidea izan zuen, Tom ezagutzea zegoena.
* Axon-trained (chrF 26.6): Bere txanburra joango zuen.

**Q: Translate into Basque: Do it right now!**

* Human translation: **Egin, baina orain!**
* Base (chrF 9.3): Ez da erakundeak ezagutzen du!
* Axon-trained (chrF 11.4): Hau egiteko gogoratu!

**Q: Translate into Basque: How many sisters do you have? How many brothers do you have?**

* Human translation: **Zenbat arreba dituzu? Zenbat neba dituzu?**
* Base (chrF 18.5): Ez zen ezagutzen duzu gizakilariak? Ezagutzen duzu berrabatik izenek?
* Axon-trained (chrF 37.2): Zenbat urtekin dute? Zenbat herrialde batzuk duzu?

**Q: Translate into Basque: I'm sure it can be done.**

* Human translation: **Ziur nago egin ahal dela.**
* Base (chrF 9.9): Ez da erabiltzen da.
* Axon-trained (chrF 12.7): Beste dira gogor dezakezu.

**Q: Translate into Basque: I know Tom helped Mary.**

* Human translation: **Badakit Tom Mary lagundu zuela**
* Base (chrF 19.2): Jokoa da Toma izan zen Maryra.
* Axon-trained (chrF 42.3): Badakit Tomek Marinari jasotu zuen.

**Q: Translate into Basque: He sent me a letter.**

* Human translation: **Gutun bat bidali zidan.**
* Base (chrF 15.6): Ez zen maila izendatu zuen.
* Axon-trained (chrF 13.8): Letra emangoa sendatu zuen.

**Q: Translate into Basque: One, two, three, four, five, six, seven, eight, nine, ten.**

* Human translation: **Bat, bi, hiru, lau. bost, sei, zazpi, zortzi, bederatzi, hamar.**
* Base (chrF 15.9): Era, dua, tri, quattro, cinc, sei, set, oito, nein, diez.
* Axon-trained (chrF 19.0): Unu, duen, umea, hiru, urteko, seku, aste, gauza, nire, zenbatan.

**Q: Translate into Basque: Layla asked Sami to leave her alone.**

* Human translation: **Laylak Samiri bakarrik usteko eskatu zion.**
* Base (chrF 20.8): Layla asko Sami ezarazi zeregia.
* Axon-trained (chrF 32.3): Laylak Samiren lagundu beharko zuela esan zuen.

**Q: Translate into Basque: Will Tom do that?**

* Human translation: **Tomek hori egingo zuen?**
* Base (chrF 11.9): Ez da, Tom ezaraz?
* Axon-trained (chrF 54.9): Hark, Tomek hori egiten dena?

**Q: Translate into Basque: I was born in Osaka in 1977.**

* Human translation: **Osakan jaio nintzen 1977an.**
* Base (chrF 27.1): Era naitutako osakaetan 1977ean.
* Axon-trained (chrF 89.4): Osakan jaio nintzen 1977ean.

**Q: Translate into Basque: Sami and Layla are here to stay.**

* Human translation: **Sami eta Layla hemen daude geratzeko.**
* Base (chrF 43.8): Sami eta Layla ezagutzen dira.
* Axon-trained (chrF 22.6): Samik eta Laila horretan jarri dira.

**Q: Translate into Basque: Does Tom like his parents?**

* Human translation: **Gustuko ahal ditu Tomek bere gurasoak ?**
* Base (chrF 12.2): Ezta Tomen ezagutzen du?
* Axon-trained (chrF 45.7): Badakit Tomek inoiz ez du zure gurasoak gustuko?

**Q: Translate into Basque: Layla took all the money Sami had.**

* Human translation: **Layla Samiren diru guztia hartu zuen.**
* Base (chrF 22.4): Layla izan zen Sami ezagutako bideak.
* Axon-trained (chrF 35.4): Laylak Samiren geldia emango zuen.

**Q: Translate into Basque: I hate my job.**

* Human translation: **Gorroto dut nire lana.**
* Base (chrF 12.6): Ez zen maitzen ezagutako zeregia da.
* Axon-trained (chrF 11.8): Ez dut zure emakumea gustuko.

**Q: Translate into Basque: Where have you been? Everyone phoned you.**

* Human translation: **Non egon zara? Denok deitu dizute**
* Base (chrF 15.6): Ez da ez izan zen? Ezagutzen duzu gaitza.
* Axon-trained (chrF 11.5): Nik ezazu? Gurek zabaldu zuen.

**Q: Translate into Basque: What's mine is mine, and what's yours is mine.**

* Human translation: **Nirea nirea da, eta zurea ere nirea da.**
* Base (chrF 28.3): Ez da zuzena da, eta ez da zuzena da.
* Axon-trained (chrF 71.2): Nirea nirea da eta zurea nirea da.

**Q: Translate into Basque: It cannot continue like this.**

* Human translation: **Ezin dut horrela jarraitu.**
* Base (chrF 17.8): Ez ez da gaitu.
* Axon-trained (chrF 31.7): Ez da horrelako hiltzen kontuan hartu.

**Q: Translate into Basque: There can be more than one correct answer.**

* Human translation: **Erantzun zuzen bat baino gehiago egon ahal dira.**
* Base (chrF 17.1): Ez da izeneko ezagutzak dira.
* Axon-trained (chrF 12.6): Ezin da ezta egia zehazten.

**Q: Translate into Basque: Don't you think it's funny?**

* Human translation: **Ez duzu uste barregarria denik?**
* Base (chrF 10.5): Ez da ez izan da?
* Axon-trained (chrF 26.5): Ez duzu zabaldu funtzionarri bat dela?

**Q: Translate into Basque: Excellent!**

* Human translation: **Ederki!**
* Base (chrF 4.6): Bilatua!
* Axon-trained (chrF 4.4): Oso gogoko!

Full output: `log.txt`. Hardware and config: `env.json`. Transactions are in the log and on the explorer.
