# Run 20261114-mainnet-model9-clinical-tee

* Contributors trained on: **NVIDIA GeForce RTX 4090** · **scored and recorded by the vault inside an attested Intel TDX TEE** (Phala `axon-vault-tee2`, evidence in [`runs/tee-mainnet2/`](../tee-mainnet2/)) · base model `Qwen/Qwen2.5-1.5B-Instruct` · wall time 40.4 min
* Contract: [`axon.ebukaa.near`](https://nearblocks.io/address/axon.ebukaa.near) (mainnet), model id 9
* Hidden-test loss: **1.456 → 1.228**
* Paid queries: 1 · paid to owners 0.0095 NEAR (after the 5% platform fee)

## Ownership

| Contributor | Share |
|---|---|
| neuro-clinic | 0.0% |
| metabolic-clinic | 61.8% |
| alice | 38.2% |
| bob | 0.0% |

## Rounds

| Round | Test loss | Shares minted | Adapter hash |
|---|---|---|---|
| 1 | 1.228 | alice 87010, bob 0, metabolic-clinic 140931, neuro-clinic 0 | `51f652d43712009a…` |
| 2 | 1.228 | alice 0, bob 0, metabolic-clinic 0, neuro-clinic 0 | `51f652d43712009a…` |

## Same question, base model vs Axon-trained model

Reworded questions about facts in the contributors' private data. *Reference* is the answer in that data.

* **Facts recalled.** Right gene: base model **3/12**, Axon-trained **5/12**. Right inheritance pattern: base model **3/12**, Axon-trained **10/12**.

**Q: Which gene is linked to Laing distal myopathy?** *(from neuro-clinic's data)*

* Answer in the data: gene **MYH7**
* Base ✅: Laing distal myopathy (LDM) is an inherited muscle disorder that primarily affects the muscles of the hands and feet. It's caused by mutations in the *MYH7* gene. The *MYH7* gene provides instructions for making a protein called desmin, which plays a crucial role in maintaining the structure of muscle cells. Mutations in this gene can lead to abnormal formation or breakdown of muscle fibers, resulting in LDM symptoms such as weakness in the extremities and difficulty with fine motor skills. Therefore, **the MYH7 gene** is directly associated with Laing
* Axon-trained ❌: The LAMC2 gene provides instructions for making a protein that plays an important role in the development of muscles and other soft tissues during early development. This protein, called laminin alpha 2, is found primarily on the outside (extracellular) surface of muscle cells. It helps form structures called desmosomes, which attach individual muscle cells (myocytes) together and provide structural support for the developing muscle tissue. Desmosomes also help regulate the transfer of substances between adjacent muscle cells; this regulation is necessary for normal cell growth and function. Mutations in the LAMC2 gene
* Reference: Mutations in the MYH7 gene cause Laing distal myopathy. The MYH7 gene provides instructions for making a protein that is found in heart (cardiac) muscle and in type I skeletal muscle fibers. Type I fibers, which are also known as slow-twitch fibers, are one of two types of fibers that make up skeletal muscles. Type I fibers are the primary component of skeletal muscles that are resistant to fatigue. For example, musc

**Q: How is Laing distal myopathy passed down in families?** *(from neuro-clinic's data)*

* Answer in the data: **autosomal dominant**
* Base ❌: Laing distal myopathy (LDM) is an inherited muscle disorder that affects the muscles at the ends of limbs and can be transmitted through generations within families. It's important to note that LDM is not directly related to the "Laing" family name; it refers to a specific genetic condition. The inheritance pattern for LDM typically follows an autosomal recessive mode of transmission. This means: 1. **Genetic Basis**: The disease-causing gene responsible for LDM is located on one of the non-sex chromosomes (autosomes). 2. **Recessive Gene**: Individuals
* Axon-trained ❌: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal dominant pattern, which means one copy of the altered gene in each cell is sufficient to cause the disorder. In most cases, an affected person inherits the mutation from one affected parent. A small percentage of cases result from new mutations in the gene. These cases occur

**Q: Which gene is linked to McLeod neuroacanthocytosis syndrome?** *(from neuro-clinic's data)*

* Answer in the data: gene **XK**
* Base ❌: McLeod neuroacanthocytosis syndrome (MNS) is caused by mutations in the *SLC25A4* gene on chromosome 16q23-qter. The SLC25A4 gene encodes for an enzyme called pyruvate dehydrogenase complex subunit A4 (PDHA4), which plays a crucial role in energy metabolism and red blood cell production. Mutations in this gene can lead to impaired function of PDHA4, resulting in various hematological disorders including MNS. This condition typically presents with symptoms such as microcy
* Axon-trained ❌: McLeod neuroacanthocytosis syndrome is caused by mutations in the KAT6B gene. This gene provides instructions for making an enzyme called katanin that plays an important role in breaking down (degrading) long strands of DNA known as chromosomal arms. Chromosomal arms contain most of the genetic material in each cell and provide the information needed for cells to grow, divide, and differentiate into different types of cells. During early development, multiple chromosomes attach (attach) at specific locations on the arm of chromosome 4; this attachment is called a centromere. As cells prepare
* Reference: Mutations in the XK gene cause McLeod neuroacanthocytosis syndrome. The XK gene provides instructions for producing the XK protein, which carries the blood antigen Kx. Blood antigens are found on the surface of red blood cells and determine blood type. The XK protein is found in various tissues, particularly the brain, muscle, and heart. The function of the XK protein is unclear; researchers believe that it might pla

**Q: How is McLeod neuroacanthocytosis syndrome passed down in families?** *(from neuro-clinic's data)*

* Answer in the data: **x-linked recessive**
* Base ❌: McLeod Neuroacanthocytosis Syndrome (MNS) is an extremely rare genetic disorder that affects the nervous system and blood cells. It's caused by mutations in the gene encoding for the protein called MLCN1. The inheritance pattern of this condition can be complex: 1. **Autosomal Recessive Inheritance**: This means both parents must carry one copy each of the mutated gene to pass it on to their child. If they do not have symptoms themselves but are carriers, there is a 25% chance with each pregnancy that the child will inherit two copies of the mutation
* Axon-trained ❌: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: McLeod neuroacanthocytosis syndrome is inherited in an X-linked recessive pattern. The gene associated with this condition is located on the X chromosome, which is one of the two sex chromosomes. In males (who have only one X chromosome), one altered copy of the gene in each cell is sufficient to cause the condition. I

**Q: Which gene is linked to infantile neuronal ceroid lipofuscinosis?** *(from neuro-clinic's data)*

* Answer in the data: gene **PPT1**
* Base ❌: Infantile neuronal ceroid lipofuscinoses (INCLs) are a group of rare genetic disorders that affect the brain and nervous system in infants or young children. These conditions result from mutations in specific genes involved in lysosomal function. The most well-known INL associated with these diseases is **BCH1** (also known as CLN3). This gene encodes for beta-ketothiolase-2, which plays a crucial role in breaking down fatty acids within cells. Mutations in this gene lead to impaired lipid metabolism, particularly affecting the accumulation of certain types of
* Axon-trained ❌: INCPRT on chromosome 19 is associated with infantile neuronal ceroid lipofuscinosis.
* Reference: Mutations in the PPT1 gene cause most cases of infantile NCL. The PPT1 gene provides instructions for making an enzyme called palmitoyl-protein thioesterase 1. This enzyme is active in cell compartments called lysosomes, which digest and recycle different types of molecules. Palmitoyl-protein thioesterase 1 removes certain fats called long-chain fatty acids from proteins, which probably helps break down the proteins.

**Q: How is infantile neuronal ceroid lipofuscinosis passed down in families?** *(from neuro-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ✅: Infantile Neuronal Ceroid Lipofuscinoses (INCLs) are a group of rare genetic disorders that affect the brain and nervous system. These conditions are inherited in an autosomal recessive manner. ### Autosomal Recessive Inheritance In genetics, inheritance patterns can be categorized into several types: 1. **Autosomal Dominant**: A person with one copy of the mutated gene has a 50% chance of passing it on to their offspring. 2. **Autosomal Recessive**: Both copies of the gene must come from the same parent for the
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to spastic paraplegia type 7?** *(from neuro-clinic's data)*

* Answer in the data: gene **SPG7**
* Base ✅: Spastic Paraplegia Type 7 (SPG7) is caused by mutations in the *SLC26A4* gene. The SLC26A4 gene encodes for a protein called "solute carrier family 26 member A4" or more commonly known as "Na+/K+-ATPase". This enzyme plays an important role in maintaining sodium and potassium balance across cell membranes, particularly within neurons. Mutations in this gene can lead to various neurological disorders including SPG7, which affects motor control of the legs due to abnormal nerve function leading to
* Axon-trained ✅: SPG7 is caused by mutations in the CASK gene. This gene provides instructions for making a protein that plays an important role in development and function of neurons, which are nerve cells in the brain and spinal cord. The CASK protein helps form connections (synapses) between neurons; it also regulates the movement of molecules into and out of synapses. Mutations in the CASK gene lead to the production of abnormally short versions of the CASK protein or no functional protein at all. These changes disrupt the formation and function of synapses, particularly those involved in transmitting signals from the nervous
* Reference: Mutations in the SPG7 gene cause spastic paraplegia type 7. The SPG7 gene provides instructions for producing a protein called paraplegin. Located within the inner membrane of the energy-producing centers of cells (mitochondria), paraplegin is one of the proteins that form a complex called the m-AAA protease. The m-AAA protease is responsible for assembling ribosomes (cellular structures that process the cell's genet

**Q: How is spastic paraplegia type 7 passed down in families?** *(from neuro-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Spastic Paraplegia Type 7 (SPG7) is an inherited neurological disorder that affects the nervous system and causes muscle stiffness or spasms on both sides of the body below the waist. This condition can be transmitted through genetic inheritance patterns. ### Types of Inheritance Patterns 1. **Autosomal Dominant**: - If one parent has SPG7, there's a 50% chance their child will inherit the gene mutation. - The affected individual may show symptoms before birth if it’s from a carrier mother who carries only one copy of the mutated gene but
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to arginine:glycine amidinotransferase deficiency?** *(from metabolic-clinic's data)*

* Answer in the data: gene **GATM**
* Base ❌: Arginine:Glycine Amidinotransferase (AGAT) deficiency can be caused by mutations in the AGAT1 gene or the AGT gene. The AGAT1 gene encodes for an enzyme called Arginine-Glycine Amidinotransferase (AGAT), which plays a crucial role in the urea cycle of amino acid metabolism. This enzyme catalyzes the transfer of amide groups from glutamine and glycine to formarginate, which then enters the urea cycle as part of ornithine transcarbamylase activity. Mut
* Axon-trained ❌: The ARG1 gene provides instructions for making an enzyme called arginine glycine amidinotransferase (AGAT). This enzyme participates in the production of molecules that cells use as energy (proteins and fats) from the food we eat. AGAT also plays a role in the development of blood vessels before birth. Mutations in the ARG1 gene cause arginine:glycine amidinotransferase deficiency, which is part of a larger group of related disorders known as aminoacyl-tRNA synthetases deficiencies. People with this condition have a shortage (
* Reference: Mutations in the GATM gene cause arginine:glycine amidinotransferase deficiency. The GATM gene provides instructions for making the enzyme arginine:glycine amidinotransferase. This enzyme participates in the two-step production (synthesis) of the compound creatine from the protein building blocks (amino acids) glycine, arginine, and methionine. Specifically, arginine:glycine amidinotransferase controls the first step

**Q: How is arginine:glycine amidinotransferase deficiency passed down in families?** *(from metabolic-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Arginine-glycine amidinotransferase (AGAT) deficiency is an inherited metabolic disorder that affects the body's ability to produce certain amino acids and other compounds. This condition can be transmitted through genetic inheritance patterns. ### Genetic Basis: The AGAT enzyme plays a crucial role in the metabolism of arginine and glycine. It catalyzes the transfer of ammonia from arginine to glycine, forming citrulline and glutamate. When this process fails due to AGAT deficiency, it leads to accumulation of toxic intermediates such as argininosuccinate and its
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to aromatic l-amino acid decarboxylase deficiency?** *(from metabolic-clinic's data)*

* Answer in the data: gene **DDC**
* Base ❌: Aromatic L-aminoadipate transaminase (ALAT) or Aromatic L-amino acid decarboxylase (AAADC), also known as ALAD, is the enzyme that catalyzes the conversion of L-phenylalanine and L-glutamate into pyridoxal 5'-phosphate and α-ketoglutarate. The disease caused by AAADC deficiency is called phenylketonuria (PKU). PKU is an inherited metabolic disorder in which there is insufficient activity of the enzyme aldehyde dehydrogenase (ALDH2
* Axon-trained ❌: The AADC gene (encoding aromatic l-amino acid decarboxylase) provides instructions for making an enzyme called aromatic l-amino acid decarboxylase. This enzyme plays a critical role in the production of several neurotransmitters, which transmit signals across chemical connections between nerve cells (neurons). Neurotransmitters include dopamine and serotonin, all of which are made from amino acids, which are building blocks of protein. Dopamine and serotonin are involved in numerous bodily functions including sleep, arousal, digestion, body temperature regulation, and mood. Aromatic l-amino acid decarboxyl
* Reference: Mutations in the DDC gene cause AADC deficiency. The DDC gene provides instructions for making the AADC enzyme, which is important in the nervous system. This enzyme helps produce dopamine and serotonin from other molecules. Dopamine and serotonin are neurotransmitters, which are chemical messengers that transmit signals between nerve cells, both in the brain and spinal cord (central nervous system) and in other part

**Q: How is aromatic l-amino acid decarboxylase deficiency passed down in families?** *(from metabolic-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Aromatic L-Amino Acid Decarboxylase (ALAD) deficiency is an inherited metabolic disorder that affects the body's ability to break down certain amino acids into their corresponding neurotransmitters and other compounds. This condition can be transmitted through genetic inheritance patterns. ### Types of Genetic Inheritance Patterns 1. **Autosomal Dominant**: - If one parent has ALAD deficiency, there is a 50% chance for each child to inherit the gene mutation. - The affected individual will show symptoms because they have both copies of the mutated gene (one from each parent). 2
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to carnitine palmitoyltransferase I deficiency?** *(from metabolic-clinic's data)*

* Answer in the data: gene **CPT1A**
* Base ✅: Carnitine palmitoyltransferase I (CPT1) deficiency is caused by mutations in the CPT1A or CPT1B genes. The two main types of this condition are: - **Type 1**: Caused by mutations in the CPT1A gene. - **Type 2**: Caused by mutations in the CPT1B gene. These genetic defects lead to an inability to properly process fatty acids through the mitochondria, which can result in severe metabolic disorders if left untreated. Treatment typically involves dietary modifications and sometimes supplementation with carnitine to
* Axon-trained ✅: The CPT1A gene provides instructions for making an enzyme called carnitine palmitoyltransferase 1 (CPT1). This enzyme plays a critical role in fat metabolism, which is the breakdown of fats to release energy. The two forms of CPT1 found in most organisms, including humans and mice, each consist of two protein subunits that join together to form a larger molecule. Each CPT1 subunit contains a binding site for carnitine, which is a natural substance that helps transport certain molecules into cells where they can be used for energy production. In muscle
* Reference: Mutations in the CPT1A gene cause CPT I deficiency. This gene provides instructions for making an enzyme called carnitine palmitoyltransferase 1A, which is found in the liver. Carnitine palmitoyltransferase 1A is essential for fatty acid oxidation, which is the multistep process that breaks down (metabolizes) fats and converts them into energy. Fatty acid oxidation takes place within mitochondria, which are the energ

**Q: How is carnitine palmitoyltransferase I deficiency passed down in families?** *(from metabolic-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Carnitine Palmitoyltransferase (CPT) I deficiency can be inherited in several ways depending on the specific gene involved and whether it's an autosomal dominant or recessive trait. 1. Autosomal Dominant: In this case, if one parent has CPTI deficiency, there’s a 50% chance that their child will inherit the condition. This type of inheritance pattern means that even though both parents may not show symptoms themselves, they could pass along the defective allele to their offspring with each pregnancy. 2. Recessive Inheritance: If the mutation causing
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to 3-beta-hydroxysteroid dehydrogenase deficiency?** *(from metabolic-clinic's data)*

* Answer in the data: gene **HSD3B2**
* Base ❌: The gene that is linked to 3-beta-hydroxysteroid dehydrogenase (3β-HSD) deficiency is the *HSD17B4* gene. This enzyme plays an important role in steroid hormone metabolism and synthesis. Deficiency of this enzyme can lead to various endocrine disorders such as congenital adrenal hyperplasia (CAH), which affects both males and females but more commonly occurs in females due to their higher levels of estrogen precursors. Some key points about the HSD17B4 gene: - It encodes for the 3β-hydro
* Axon-trained ✅: The gene linked to 3-beta-hydroxysteroid dehydrogenase deficiency is HSD3B2.
* Reference: Mutations in the HSD3B2 gene cause 3-HSD deficiency. The HSD3B2 gene provides instructions for making the 3-HSD enzyme. This enzyme is found in the gonads and adrenal glands. The 3-HSD enzyme is involved in the production of many hormones, including cortisol, aldosterone, androgens, and estrogen. Cortisol has numerous functions such as maintaining energy and blood sugar levels, protecting the body from stress, and su

**Q: How is 3-beta-hydroxysteroid dehydrogenase deficiency passed down in families?** *(from metabolic-clinic's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: 3-Beta-Hydroxysteroid Dehydrogenase (HSD) deficiency can be inherited in several ways depending on the specific gene involved and its location within the genome. 1. Autosomal Dominant Inheritance: This type of inheritance means that if one parent has HSD deficiency, there's a 50% chance their child will inherit it as well. The condition usually manifests itself early in life due to the lack of proper hormone production or metabolism. 2. X-linked Inheritance: If the gene responsible for HSD deficiency is located on the X chromosome, males have an increased
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to Rothmund-Thomson syndrome?** *(from alice's data)*

* Answer in the data: gene **RECQL4**
* Base ❌: Rothmund-Thompson Syndrome (RTS) is caused by mutations in the RTEL1 gene on chromosome 9q34.2-35. It's also known as Werner syndrome with atypical features or Warts and hair loss disease. The symptoms of RTS include: • Short stature • Hair loss • Skin changes such as hyperpigmentation, hypopigmentation, and telangiectasia • Dental problems including tooth decay, enamel defects, and dental crowding • Skeletal abnormalities like shortening of long bones, scoliosis, and joint contractures
* Axon-trained ❌: Rothmund-Thomson syndrome is caused by mutations in the TSG101 gene. This gene provides instructions for making a protein that plays an important role in early development of many tissues and organs before birth. Specifically, this protein helps form stable connections (junctions) between cells; it is essential for the process known as cell adhesion. Cell adhesion is necessary for proper formation of the placenta, which supplies oxygen and nutrients to developing baby. The TSG101 protein also appears to be involved in other critical developmental processes including the division and movement of cells. Mutations
* Reference: Mutations in the RECQL4 gene cause about two-thirds of all cases of Rothmund-Thomson syndrome. This gene provides instructions for making one member of a protein family called RecQ helicases. Helicases are enzymes that bind to DNA and temporarily unwind the two spiral strands (double helix) of the DNA molecule. This unwinding is necessary for copying (replicating) DNA in preparation for cell division, and for repairi

**Q: How is Rothmund-Thomson syndrome passed down in families?** *(from alice's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Rothmund-Thompson (RTT) Syndrome is an X-linked recessive disorder that affects males and females equally but more frequently in males due to the presence of only one copy of the gene on the Y chromosome. Here's how it passes down: 1. **Genetic Basis**: RTT is caused by mutations in the *MECP2* gene located on the long arm of the X chromosome (Xq28). This gene plays a crucial role in regulating genes involved in brain development and function. 2. **Males vs Females**: - Males have one X
* Axon-trained ✅: Rothmund-Thomson syndrome (RTS) is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

**Q: Which gene is linked to Holt-Oram syndrome?** *(from alice's data)*

* Answer in the data: gene **TBX5**
* Base ❌: Holt-Oram综合征是一种遗传性心脏疾病，其主要特征是右心室发育不良和上肢的异常。这种病症通常是由位于人类染色体17q21区域的一个基因突变引起的。 具体来说，该病与以下基因有关： 1. **MYBPC3**：这是最常被提及的基因之一，它编码的是肌钙蛋白T（Troponin T），这是一种在心脏细胞中起关键作用的蛋白质。当这个基因发生突变时，会导致心脏肌肉中的收缩功能受损，从而引发心脏病。
* Axon-trained ✅: Mutations in the TBX5 gene cause Holt-Oram syndrome. This gene provides instructions for making a protein that plays an important role in development before birth and during childhood. Specifically, this protein helps determine the formation of various structures within cells (cellular components) called organelles known as mitochondria. Mitochondria are essential for many cellular functions, including generating energy for the body's cells. Mutations in the TBX5 gene lead to the production of an abnormally short version of the mitochondrial DNA transcription factor 5 protein. The shortened protein cannot perform its function properly, which
* Reference: Mutations in the TBX5 gene cause Holt-Oram syndrome. This gene provides instructions for making a protein that plays a role in the development of the heart and upper limbs before birth. In particular, this gene appears to be important for the process that divides the developing heart into four chambers (cardiac septation). The TBX5 gene also appears to play a critical role in regulating the development of bones in th

**Q: How is Holt-Oram syndrome passed down in families?** *(from alice's data)*

* Answer in the data: **autosomal dominant**
* Base ✅: Holt-Oram Syndrome (HO) is an autosomal dominant genetic disorder that affects the heart and upper limb muscles. It's characterized by: 1. **Heart defects**: The most common feature of HO is congenital heart disease, often involving atrial septal defect or ventricular septal defect. 2. **Upper limb abnormalities**: - **Carpal tunnel syndrome**: This can lead to numbness, tingling, and weakness in the hands. - **Muscular dystrophy-like conditions**: Some individuals may develop muscle wasting and weakness in their arms and legs over time
* Axon-trained ✅: This condition is inherited in an autosomal dominant pattern, which means one copy of the altered gene in each cell is sufficient to cause the disorder. In many cases, an affected person has a parent with the condition. However, parents of an individual with an autosomal dominant condition each carry one copy of the mutated gene that causes the condition but do not show signs and symptoms of the condition themselves.
* Reference: This condition is inherited in an autosomal dominant pattern, which means one copy of the altered gene in each cell is sufficient to cause the disorder.

**Q: Which gene is linked to hyperparathyroidism-jaw tumor syndrome?** *(from alice's data)*

* Answer in the data: gene **CDC73**
* Base ❌: Hyperparathyroidism-Jaw Tumor Syndrome (HPT) is caused by mutations in the PTH1R receptor gene on chromosome 2q37. This condition involves overactive parathyroid glands and can lead to various symptoms including bone pain, fractures, kidney stones, and jaw tumors. The specific mutation that causes HPT typically results in an alteration of the protein encoded by this gene, which affects its function or structure. The exact nature of these alterations varies among individuals with the disorder but generally impacts how well the hormone produced by the affected parathyroid cells functions within the body
* Axon-trained ❌: The SH2D1A gene provides instructions for making a protein that plays an important role in cell growth and division (proliferation). This protein, called the phosphatidylinositol 3-kinase regulatory subunit 2 (PI3K-RS2), is found primarily inside cells in the center of small structures called lysosomes. Lysosomes contain acids used to break down foreign substances or damaged cellular material within the cell. PI3K-RS2 helps control whether these breakdown processes occur. Mutations in the SH2D1A gene lead to the production
* Reference: Mutations in the CDC73 gene (also known as the HRPT2 gene) cause hyperparathyroidism-jaw tumor syndrome. The CDC73 gene provides instructions for making a protein called parafibromin. This protein is found throughout the body and is likely involved in gene transcription, which is the first step in protein production. Parafibromin is also thought to play a role in cell growth and division (proliferation), either promo

**Q: How is hyperparathyroidism-jaw tumor syndrome passed down in families?** *(from alice's data)*

* Answer in the data: **autosomal dominant**
* Base ✅: Hyperparathyroidism-Jaw Tumor Syndrome (HPT) is an autosomal dominant genetic disorder that can be inherited from one parent to their offspring. This means if you inherit the gene mutation for HPT from just one of your parents, it will cause you to have this condition. The specific genes involved in HPT include PTH1R and CYP24A1 on chromosome 3q26-qter and chromosome Xp28 respectively. These genes play roles in regulating calcium metabolism and bone health. Inheritance patterns: - Autosomal Dominant: The disease occurs
* Axon-trained ✅: This condition is inherited in an autosomal dominant pattern, which means one copy of the altered gene in each cell is sufficient to cause the disorder.
* Reference: This condition is inherited in an autosomal dominant pattern, which means one copy of the altered gene in each cell is sufficient to cause the disorder.

**Q: Which gene is linked to thiamine-responsive megaloblastic anemia syndrome?** *(from alice's data)*

* Answer in the data: gene **SLC19A2**
* Base ❌: Thiamine-responsive megaloblastic anemia (TRMA) is caused by mutations in the *VPM1* gene on chromosome 20q13.4-15. It leads to impaired function of the enzyme pyruvate carboxylase, which affects the metabolism of carbohydrates and proteins. The specific mutation that causes TRMA involves changes in the coding sequence or regulatory regions of the VPM1 gene. These genetic alterations disrupt normal protein production or activity, leading to reduced levels of functional pyruvate carboxylase and subsequent effects on red blood cell
* Axon-trained ✅: Mutations in the SLC19A2 gene cause thiamine-responsive megaloblastic anemia syndrome. This gene provides instructions for making a protein called thiamine transporter 1 (ThiT), which transports thiamine into cells. ThiT specifically brings this water-soluble vitamin into cells that lack its ability to absorb fat-soluble vitamins such as vitamin D and vitamin E. Mutations in the SLC19A2 gene prevent thiT from reaching these types of cells, reducing or eliminating the amount of thiamine that reaches these cells. When there
* Reference: Mutations in the SLC19A2 gene cause thiamine-responsive megaloblastic anemia syndrome. This gene provides instructions for making a protein called thiamine transporter 1, which transports thiamine into cells. Thiamine is found in many different foods and is important for numerous body functions. Most mutations in the SLC19A2 gene lead to the production of an abnormally short, nonfunctional thiamine transporter 1. Oth

**Q: How is thiamine-responsive megaloblastic anemia syndrome passed down in families?** *(from alice's data)*

* Answer in the data: **autosomal recessive**
* Base ❌: Thiamine-responsive megaloblastic anemia (TRMA) is caused by mutations or deficiencies of the vitamin B12-dependent enzyme methylmalonyl-CoA mutase (MCM). This condition can be inherited in several ways: 1. Autosomal Dominant Inheritance: TRMA can sometimes have dominant inheritance patterns where one copy of the mutated gene from either parent causes the disease. 2. X-linked Inheritance: There's also evidence for some cases with X-linked recessive inheritance, though this type is less common and typically associated with other conditions like pernicious anemia.
* Axon-trained ✅: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.
* Reference: This condition is inherited in an autosomal recessive pattern, which means both copies of the gene in each cell have mutations. The parents of an individual with an autosomal recessive condition each carry one copy of the mutated gene, but they typically do not show signs and symptoms of the condition.

Full output: `log.txt`. Hardware and config: `env.json`. Transactions are in the log and on the explorer.
