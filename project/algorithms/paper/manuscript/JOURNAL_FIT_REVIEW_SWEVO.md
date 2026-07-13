# Simulasi Peer Review & Editorial Assessment
## Target jurnal: *Swarm and Evolutionary Computation* (Elsevier, ISSN 2210-6502)

**Manuskrip yang direview:** "When Does Opposition-Based Learning Actually Help? An Origin-Bias-Controlled Audit under Tight Evaluation Budgets" (`manuscript.md` + `supplementary.md`, versi terkini pasca-restorasi Tabel 3/5 dan Figure 1/5)

**Catatan metodologis (harap dibaca dulu):** Laporan ini membedakan empat jenis pernyataan secara eksplisit, ditandai setiap kali muncul:
- **[FAKTA JURNAL]** — berasal dari *Author Information Pack* resmi Elsevier untuk SWEVO yang berhasil saya ambil dan baca penuh (lihat catatan versi di bawah), atau dari halaman Aims & Scope resmi.
- **[FAKTA MANUSKRIP]** — pernyataan terverifikasi langsung dari isi `manuscript.md`/`supplementary.md`.
- **[INTERPRETASI REVIEWER]** — penilaian kritis saya sebagai simulasi reviewer/editor.
- **[ESTIMASI SUBJEKTIF]** — angka probabilitas yang **tidak** berasal dari data acceptance-rate SWEVO yang terverifikasi (saya tidak punya akses ke angka itu), murni penilaian informed judgment.

**Batasan riset yang jujur harus diungkap di awal:** ScienceDirect memblokir akses otomatis (`403 Forbidden`) ke halaman *Guide for Authors* versi live. Saya berhasil memperoleh **Author Information Pack resmi Elsevier untuk SWEVO bertanggal 10 Januari 2016** (dokumen PDF resmi, bukan ringkasan pihak ketiga) beserta konfirmasi Aims & Scope terkini via pencarian web. Dokumen 2016 ini **mendahului** beberapa kebijakan Elsevier yang sekarang standar di seluruh jurnalnya (CRediT sejak ~2018–2020, Research Data Policy Option A/B/C sejak ~2019, disclosure Generative AI sejak 2023) — untuk item-item itu saya menandainya sebagai kebijakan **umum Elsevier-wide** yang **sangat mungkin** berlaku juga di SWEVO, bukan sebagai fakta yang saya baca langsung dari halaman SWEVO. Saya sarankan Anda mengonfirmasi ulang tiga hal (APC terbaru, opsi Research Data Policy yang dipakai, dan apakah highlights kini wajib) langsung di halaman ScienceDirect sebelum submit, karena saya tidak bisa memverifikasinya secara independen.

---

# 1. JOURNAL FIT DAN EDITORIAL SCREENING

**[FAKTA JURNAL]** Aims: *"Swarm and Evolutionary Computation is the first peer-reviewed publication of its kind that aims at reporting the most recent research and developments in nature-inspired intelligent computation based on swarm and evolutionary algorithms. It publishes advanced, innovative and interdisciplinary research involving theoretical, experimental and practical aspects of the two paradigms and their hybridizations... Survey papers reviewing the state-of-the-art of timely topics will also be welcomed as well as novel and interesting applications."* Scope mencakup daftar topik luas (GA, DE, PSO, ACO, hybridization, dsb.) dan secara eksplisit mendorong publikasi ke arah **aplikasi industri nyata** (Aerospace, Robotics, Power Systems, dst. — lihat *Author Information Pack* p.1–2).

**1. Apakah paper ini "masuk topik" atau benar-benar penting untuk jurnal ini?**
**[INTERPRETASI REVIEWER]** Secara topik, ya, jelas masuk: hybridization (FPA+OBL+bandit+JADE), swarm intelligence, evolutionary computation, benchmarking. Tapi "masuk topik" dan "penting bagi jurnal ini" adalah dua hal berbeda. SWEVO historically menerbitkan dua jenis artikel dominan: (a) algoritma baru/varian baru dengan validasi luas, dan (b) *meta-studi* tentang praktik benchmarking/bias (lihat §3 di bawah — SWEVO sudah menerbitkan Piotrowski et al. 2023 dan Rajwar & Deep 2025 persis di kategori kedua ini). Manuskrip Anda **sekarang** (setelah reframing sepanjang sesi ini) berada di kategori (b), bukan (a) — judul dan abstrak eksplisit tidak lagi menjual IFPOA-X sebagai algoritma unggulan. Ini keputusan editorial yang tepat: kategori (b) *lebih* jarang tapi *lebih* dihargai reviewer senior karena jarang ada yang berani melaporkan hasil negatif secara jujur.

**2. Apakah origin bias dan benchmark validity cukup sentral bagi komunitas swarm/EC?**
**[INTERPRETASI REVIEWER]** Ya, dan ini bisa dibuktikan bukan hanya lewat argumen tapi lewat preseden nyata: SWEVO sendiri menerbitkan Piotrowski, Napiórkowski & Piotrowska (2023), *"Choice of benchmark optimization problems does matter"* (SWEVO 83:101378) — yang menguji 73 algoritma pada 4 generasi CEC dan menyimpulkan superioritas algoritma sangat bergantung pada benchmark yang dipilih. SWEVO juga menerbitkan Rajwar & Deep (2025), *"Structural bias in metaheuristic algorithms: Insights, open problems, and future prospects"* (SWEVO, DOI 10.1016/j.swevo.2024.101812) yang **sudah Anda kutip sebagai referensi [36]**. Ini artinya topik "apakah keunggulan algoritma itu artefak benchmark" bukan sekadar relevan — ini topik yang *editor SWEVO sudah terbukti mau menerbitkannya*, dua kali, dalam tiga tahun terakhir.

**3. Apakah IFPOA-X sebagai experimental vehicle memperkuat atau melemahkan paper?**
**[INTERPRETASI REVIEWER]** Memperkuat, **dengan syarat** kerangka framing dipertahankan konsisten (yang sejauh ini memang konsisten di seluruh manuskrip: abstrak, §1, §5.6, §6 semua eksplisit menyebut IFPOA-X sebagai "experimental vehicle", bukan "recommended optimizer"). Risikonya: reviewer yang skeptis bisa bertanya "kalau IFPOA-X hanya kendaraan eksperimen, kenapa harus dibangun sebagai hybrid 4-komponen yang rumit (bandit+OBL+JADE+opsional surrogate), padahal 2 dari 4 komponennya (bandit, JADE) terbukti tidak berguna atau merugikan pada budget ini?" Jawaban paper sendiri sudah cukup baik (§5.4: kedua komponen itu justru bagian dari temuan — "adaptive machinery gagal pada budget rendah" adalah kontribusi kedua paper), tapi reviewer bisa saja menilai ini sebagai "algoritma yang didesain berlebihan untuk pertanyaan yang sebenarnya bisa dijawab dengan OBL-vs-baseline sederhana tanpa bandit/JADE sama sekali." Ini bukan flaw fatal, tapi **titik paling mungkin diserang** oleh Reviewer 2 yang skeptis terhadap desain algoritma.

**4. Apakah paper terlalu fokus pada kegagalan satu implementasi OBL?**
**[INTERPRETASI REVIEWER]** Ya, dan manuskrip sendiri sudah cukup jujur mengakuinya (§5.7.5 eksplisit: *"We are careful not to over-generalize from a single host algorithm and one elite-opposition variant"*). Ini kejujuran yang bagus, tapi juga berarti **generalisasi keilmuan aktualnya terbatas** pada satu varian OBL (elite-opposition/reflection dasar Tizhoosh) dan satu host algorithm. SWEVO baru saja menerbitkan Rai et al. (2026), *"Opposition based learning for metaheuristic algorithms: Theory, variants, applications, and performance evaluation"* (SWEVO 100:102271) — sebuah **survei OBL** yang kemungkinan mencakup >10 varian OBL. Reviewer yang familiar dengan survei ini bisa bertanya: apakah temuan "OBL bias ke origin" ini berlaku untuk varian OBL lain seperti PCOBL (centroid-based, sudah Anda kutip sebagai ref [29]) yang secara desain **tidak** merefleksikan ke pusat domain tetap? Manuskrip sudah menyebut PCOBL sebagai future work (§6) — ini tepat, tapi reviewer bisa memaksa Anda menjelaskan lebih eksplisit bahwa klaim causal Anda **scoped hanya untuk fixed-centre reflection OBL**, bukan untuk keluarga OBL secara umum.

**5. Apakah editor bisa menganggapnya sebagai paper benchmark-only tanpa aplikasi nyata?**
**[INTERPRETASI REVIEWER]** Ini risiko nyata. SWEVO *Author Information Pack* secara eksplisit menyebut jurnal ini "fosters industrial uptake" dan mendaftar domain aplikasi konkret (Aerospace, Robotics, Power Systems, dst.). Manuskrip Anda **sepenuhnya sintetis**: F1–F13 klasik, CEC2017 subset, dan tiga varian shift buatan sendiri — nol validasi pada masalah dunia nyata atau bahkan pada suite CEC yang lebih baru dan lebih besar (CEC2020/2022 tidak diuji). Meskipun scope resmi SWEVO juga menerima "theoretical" dan bukan hanya "practical" (jadi ini bukan alasan desk-reject otomatis), editor yang sedang mencari keseimbangan portofolio isu bisa menilai kontribusi ini sebagai "penting secara metodologis, tapi murni benchmark-diagnostic" — yang bisa memengaruhi keputusan mereka mengirim ke reviewer yang tepat (metodolog statistik vs. reviewer aplikasi).

**6. Tiga alasan terkuat untuk desk rejection:**
**[INTERPRETASI REVIEWER]**
1. **Kepatuhan administratif gagal di titik masuk**: abstrak 378 kata (jauh melebihi batas umum ~250 kata Elsevier — lihat §7), 8 keyword phrases (melebihi maksimum 6 yang tertulis eksplisit di *Guide for Authors* resmi yang saya baca), tidak ada Highlights file, tidak ada CRediT statement, tidak ada competing-interest declaration, tidak ada funding statement. Editor junior yang melakukan screening cepat bisa mengembalikan manuskrip untuk kepatuhan administratif sebelum sempat dinilai substansinya — ini **bukan** penolakan ilmiah, tapi secara praktik sering terjadi dan terasa seperti desk rejection bagi penulis.
2. **Skala validasi tunggal-algoritma dianggap terlalu sempit** dibanding standar SWEVO yang terbiasa dengan studi 20+ algoritma dan >10 benchmark suite (lihat Piotrowski et al. 2023: 73 algoritma × 9 kompetisi). Editor bisa menilai "audit satu algoritma hybrid" sebagai kontribusi terlalu sempit untuk klaim yang cukup luas ("any OBL-based low-budget claim should be validated...").
3. **IFPOA-X sendiri tidak baru** secara algoritmik (kombinasi UCB1+OBL+JADE di atas FPA adalah kombinasi mekanisme yang sudah ada semua secara individual di literatur yang dikutip paper sendiri) — jika editor membaca sepintas dan salah mengira ini "paper algoritma baru", novelty algoritmik yang rendah bisa jadi alasan penolakan cepat sebelum membaca lebih dalam bahwa novelty sebenarnya ada di metodologi audit, bukan di algoritma.

**7. Tiga alasan terkuat editor mengirimkannya ke reviewer:**
**[INTERPRETASI REVIEWER]**
1. **Kedalaman statistik yang jarang ditemukan** bahkan di paper SWEVO yang diterima: Friedman+Iman–Davenport, Holm **dan** Finner sebagai sensitivity check, Vargha–Delaney A₁₂, bootstrap CI, CD diagram, dan yang terpenting — pembedaan eksplisit *per-function* vs *cross-function* yang justru sering dilanggar oleh paper metaheuristik lain yang diterbitkan di jurnal ini.
2. **Preseden topik yang sudah terbukti** (Piotrowski 2023, Rajwar & Deep 2025) berarti editor tahu ada audiens dan reviewer yang cocok untuk topik ini di database mereka sendiri.
3. **Kejujuran melaporkan hasil negatif** (JADE merugikan, bandit tidak terdeteksi, IFPOA-X kalah dari GWO/WOA secara cross-function bahkan di suite klasik) adalah sesuatu yang jarang dan biasanya dihargai reviewer senior sebagai tanda rigor, bukan kelemahan — asalkan editor membaca cukup jauh untuk melihatnya.

---

# 2. NOVELTY DAN SIGNIFIKANSI

**[INTERPRETASI REVIEWER]** Breakdown novelty per dimensi:

| Dimensi | Novelty | Penjelasan |
|---|---|---|
| Algoritmik (IFPOA-X sendiri) | **Rendah (3/10)** | UCB1, OBL dasar Tizhoosh, dan JADE semuanya mekanisme yang sudah ada; kombinasinya di atas FPA adalah rekombinasi, bukan mekanisme baru. Manuskrip sendiri tidak mengklaim ini sebagai kontribusi utama (benar) — tapi tetap perlu dinilai jujur sebagai low. |
| Metodologis (protokol equal-NFE + 4 kontrol independen + factorial) | **Tinggi (8/10)** | Kombinasi *empat* kontrol origin-bias yang saling melengkapi (custom shift, CEC2017 resmi, dua sweep magnitude/arah) **plus** factorial 2×2 OBL-on/off × geometri adalah desain audit yang jarang ditemukan lengkap dalam satu paper metaheuristik. Kebanyakan paper OBL-bias hanya menguji satu kondisi shift. |
| Desain eksperimen (equal-NFE, domain-safe F8 fix, seed pairing) | **Tinggi (7.5/10)** | Perhatian ke detail seperti domain-safety F8 pada shift bertanda dan paired-seed design untuk Wilcoxon berpasangan menunjukkan kedisiplinan eksperimen di atas rata-rata submission metaheuristik. |
| Statistik | **Sedang-tinggi (7/10)** | Pembedaan per-function vs cross-function secara eksplisit dan konsisten adalah kontribusi metodologis nyata (banyak paper published bahkan di jurnal top masih mencampur keduanya). Bukan teknik baru, tapi penerapannya jauh lebih disiplin dari rata-rata. |
| Temuan OBL (causal within-implementation) | **Sedang-tinggi (7/10)** | Factorial difference-in-differences (§5.7.5) adalah **cara paling kuat** yang bisa dilakukan tanpa mengubah algoritma untuk mengisolasi OBL sebagai mekanisme kausal — tapi scope-nya eksplisit terbatas pada satu implementasi OBL. |
| Praktik benchmarking metaheuristik (pesan untuk komunitas) | **Sedang (6/10)** | Pesan "validasi OBL harus disertai shifted control" bukan sepenuhnya baru (Walden & Buzdalov 2024 [15] sudah punya uji statistik formal untuk origin bias; Vermetten et al. 2022 [35] BIAS toolbox sudah menyediakan alat serupa untuk structural bias secara umum) — kontribusi paper ini adalah **menunjukkan kasus konkret dengan bukti kausal dalam satu implementasi**, bukan alat/metodologi baru untuk deteksi bias itu sendiri. |

**Skor novelty gabungan (weighted terhadap apa yang paper klaim sebagai kontribusi utamanya, yaitu audit metodologis + factorial, bukan algoritma):**

**[ESTIMASI SUBJEKTIF] Skor: 6.5/10 — "moderately novel", bukan "sufficiently novel for a highly selective venue" tapi realistis untuk SWEVO sebagai Q1 non-top-tier-eksklusif.**

Klaim "first" tidak dibuat secara eksplisit di manuskrip manapun yang saya baca (bagus — manuskrip menghindari klaim "first study" yang tidak defensible), dan itu tepat: Walden & Buzdalov [15] dan Vermetten et al. BIAS toolbox [35] sudah lebih dulu membangun **alat deteksi** bias serupa. Kontribusi paper ini yang defensible dan jujur adalah "the most complete within-single-implementation causal demonstration of OBL's origin-dependence to date that I am aware of," bukan "the first to show origin bias exists" — dan manuskrip sudah, secara umum, tidak melampaui batas ini.

---

# 3. PERBANDINGAN DENGAN PAPER YANG DITERBITKAN DI SWEVO (2023–2026)

**[FAKTA — terverifikasi via Crossref API langsung, bukan tebakan]** Berikut lima artikel SWEVO 2023–2026 yang paling relevan, dengan metadata terverifikasi (judul, penulis, volume, DOI dikonfirmasi lewat `api.crossref.org`):

1. Piotrowski, A. P., Napiórkowski, J. J., & Piotrowska, A. E. (2023). *Choice of benchmark optimization problems does matter.* **Swarm and Evolutionary Computation**, 83, 101378. DOI: 10.1016/j.swevo.2023.101378.
2. Chen, C., Liu, Q., Jing, Y., Zhang, M., Cheng, S., & Li, Y. (2024). *On the representativeness metric of benchmark problems in numerical optimization.* **Swarm and Evolutionary Computation**, 91, 101716. DOI: 10.1016/j.swevo.2024.101716.
3. Rajwar, K., & Deep, K. (2025). *Structural bias in metaheuristic algorithms: Insights, open problems, and future prospects.* **Swarm and Evolutionary Computation**, DOI: 10.1016/j.swevo.2024.101812. *(Sudah dikutip di manuskrip Anda sebagai ref [36].)*
4. Li, J., Gao, L., & Li, X. (2024). *Multi-operator opposition-based learning with the neighborhood structure for numerical optimization problems and its applications.* **Swarm and Evolutionary Computation**, 84(C), 101457. DOI: 10.1016/j.swevo.2023.101457.
5. Yi, X., Ding, X., & Chen, Q. (2025). *A differential evolution algorithm considering multi-population based on birth & death process and opposition-based learning with condition.* **Swarm and Evolutionary Computation**, 96, 101966. DOI: 10.1016/j.swevo.2025.101966.
6. Rai, R., Sasmal, B., Das, A., Bharasa, T., Dhal, K. G., & Naskar, P. K. (2026). *Opposition based learning for metaheuristic algorithms: Theory, variants, applications, and performance evaluation.* **Swarm and Evolutionary Computation**, 100, 102271. DOI: 10.1016/j.swevo.2025.102271.

**Catatan kejujuran metodologis:** saya memverifikasi metadata (judul, penulis, volume, DOI) keenam artikel di atas langsung lewat Crossref API. Saya **tidak** membaca full-text keenamnya (di luar Piotrowski et al., yang abstraknya saya temukan lewat pencarian web terpisah) — jadi perbandingan mendalam di bawah untuk artikel #2, #3 (selain judul dan yang sudah Anda kutip), #4, #5, #6 didasarkan pada judul, topik, dan pola umum publikasi SWEVO, bukan pembacaan detail isi. Ini saya tandai per baris.

| Aspek | Manuskrip Anda | Piotrowski et al. 2023 *(dibaca abstrak)* | Chen et al. 2024 *(judul only)* | Li et al. 2024 *(judul only)* | Rai et al. 2026 *(judul only)* |
|---|---|---|---|---|---|
| Jumlah algoritma diuji | 8 (1 proposed + 7 baseline) | **73 algoritma** | tidak diketahui | varian OBL tunggal + baseline | survei, bukan studi empiris baru |
| Jumlah benchmark suite | 4 (klasik + CEC2017 subset + 2 shift buatan) | **9 kompetisi (CEC 2011/2014/2017/2020)** | fokus pada 1 metrik representativeness baru | tidak diketahui | N/A (survei) |
| Independent runs | 20 (15 untuk far/mixed) | tidak diketahui dari abstrak | tidak diketahui | tidak diketahui | N/A |
| Fairness protocol | equal-NFE ketat (500), dijelaskan sangat rinci | tidak diketahui, kemungkinan best-known-result per kompetisi resmi CEC | tidak diketahui | tidak diketahui | N/A |
| Statistical rigor | Friedman+Iman-Davenport+Holm+Finner+A₁₂+bootstrap, per-function **vs** cross-function dipisah eksplisit | tidak diketahui detail | tidak diketahui | tidak diketahui | N/A |
| Causal/ablation test | **2×2 factorial dengan difference-in-differences** — elemen paling unik | tidak ada indikasi (studi observasional lintas-algoritma) | N/A (metrik teoritis) | kemungkinan ablation varian OBL vs baseline sederhana | N/A |
| Reproducibility | Repo publik lengkap + README + smoke-test | tidak diketahui | tidak diketahui | tidak diketahui | N/A |
| Real-world validation | **Tidak ada** | tidak diketahui | tidak diketahui | *"and its applications"* di judul → kemungkinan ada aplikasi nyata | N/A |
| Fokus diskusi | Sangat dalam pada satu pertanyaan sempit (origin bias 1 mekanisme) | Luas, lintas dekade algoritma | Sempit, metrik tunggal | Sedang | Sangat luas (survei komprehensif) |

**[INTERPRETASI REVIEWER] Kesimpulan perbandingan:** Manuskrip Anda **kalah dalam skala** (jumlah algoritma dan suite yang diuji jauh lebih kecil dari Piotrowski et al.) tapi **unggul dalam kedalaman kausal** untuk pertanyaan yang jauh lebih sempit dan tajam. Ini bukan kelemahan otomatis — banyak paper SWEVO yang diterima justru bertipe "sempit tapi dalam" (mis. Chen et al. 2024 tentang satu metrik representativeness). Risiko terbesarnya adalah **jika reviewer yang menilai Anda kebetulan pernah mereview atau membaca Piotrowski et al. 2023**, mereka mungkin bertanya secara eksplisit: "mengapa hanya 8 algoritma dan 4 kondisi, ketika studi sejenis di jurnal yang sama menguji 73 algoritma pada 9 kompetisi resmi?" Jawaban defensible Anda (yang sudah implisit ada di paper): tujuan Anda bukan mensurvei luas, tapi membuktikan kausalitas *dalam satu implementasi* — sesuatu yang studi observasional skala-Piotrowski secara desain **tidak bisa** lakukan. Saran saya di §11: eksplisitkan kontras ini di Related Work (§2.5/§2.6), karena saat ini paper mengutip Vermetten/Velasco/Mohamed untuk kritik fair-comparison umum, tapi belum mengontraskan diri secara eksplisit dengan preseden SWEVO yang paling dekat topiknya (Piotrowski 2023, Chen 2024).

---

# 4. AUDIT METODOLOGI DAN ALGORITMA

## A. IFPOA-X

**[FAKTA MANUSKRIP + INTERPRETASI]**
- **Masih layak disebut FPA?** Batas. Operator global (§3.1.1) memang Lévy-flight pollination sesuai FPA asli [3], tapi operator lokal sepenuhnya diganti JADE (§3.3) — bukan self-pollination FPA asli sama sekali. Pemilihan operator lewat bandit UCB1 juga menggantikan mekanisme switch-probability tetap FPA asli sepenuhnya. **Ini pada dasarnya adalah hybrid DE(JADE)-bandit-OBL yang meminjam satu operator dari FPA**, bukan "FPA yang ditingkatkan." Manuskrip sendiri cukup jujur soal ini secara implisit (deskripsi §3 sudah akurat secara teknis), tapi judul framework "IFPOA-X" (dengan "FPA" di namanya) bisa membuat reviewer FPA-purist keberatan bahwa ini lebih tepat disebut hybrid generik. **Rekomendasi**: satu kalimat eksplisit di §3 pembuka yang mengakui operator lokal FPA asli sepenuhnya digantikan JADE akan mencegah keberatan ini di review.
- **Operator global/lokal dirumuskan dengan benar?** Ya — formulasi Lévy-flight Mantegna (§3.1.1) dan current-to-pbest/1 JADE (§3.3) keduanya konsisten dengan literatur aslinya yang dikutip [3, 18].
- **UCB1 valid?** Ya secara formal (indeks UCB1 standar, §3.1), tapi manuskrip sendiri (§5.4, "Why the adaptive components fail") memberikan analisis *post-hoc* yang meyakinkan bahwa pada ~21 generasi, bandit tidak pernah keluar dari fase eksplorasi — ini kejujuran metodologis yang bagus, bukan cacat desain UCB1 itu sendiri.
- **Reward scalar jelas?** Ya, didefinisikan eksplisit sebagai clipped normalized improvement (§3.1, persamaan reward). Cukup jelas untuk direproduksi.
- **JADE-style sesuai formulasi asli?** Ya, mengikuti current-to-pbest/1 + parameter sukses-historis (Cauchy F, Normal CR) sesuai Zhang & Sanderson [18], dengan modifikasi kecil (archive eksternal digabung populasi) yang dijelaskan jujur sebagai peningkatan diversitas.
- **OBL dijelaskan tepat?** Ya, dan justru ini bagian terkuat manuskrip: catatan geometris di §3.2 ("reflection through the domain centre does *not* move a candidate closer to that centre... elite-replication effect") adalah salah satu penjelasan konseptual OBL paling presisi yang saya lihat di draft manapun sesi ini — ini poin kekuatan nyata, bukan basa-basi.
- **Konsisten diposisikan sebagai experimental vehicle?** Ya, konsisten di Abstrak, §1, §3 pembuka, §5.6, §6 — ini sudah solid setelah revisi-revisi sebelumnya di sesi ini.

## B. Experimental fairness

**[FAKTA MANUSKRIP]** Equal-NFE (§4.3) diaudit sendiri oleh manuskrip dengan cukup transparan: caching (tidak masalah karena domain kontinu), noise F7 (RNG bersama), TPE (bukan population-based, dijelaskan eksplisit), overshoot (dipotong ke 500 tepat).

**[INTERPRETASI REVIEWER] Confound yang belum sepenuhnya ditutup, dan manuskrip sendiri sudah cukup jujur mengakui sebagian:**
1. **Inisialisasi tidak seragam** (§4.3, diakui eksplisit sebagai limitation): IFPOA-X/FPA/PSO pakai Latin-Hypercube, baseline `mealpy` pakai uniform-random `mealpy` default. Ini **genuine confound** yang bisa menguntungkan grup IFPOA-X secara sistematis pada budget rendah (LHS punya coverage lebih baik di generasi awal). Manuskrip benar mengakui ini sebagai limitation, tapi **tidak mengukur besarnya efek** — reviewer statistik yang ketat kemungkinan besar akan meminta minimal sensitivity check kecil (mis. re-run 2-3 baseline dengan LHS init pada subset fungsi) untuk membuktikan confound ini tidak mengubah kesimpulan utama.
2. **Baseline untuned vs IFPOA-X yang justru "tuned" oleh proses skripsi/HPO sebelumnya** — parameter IFPOA-X (Tabel S1) tampak sangat spesifik (`bandit_c=1.4`, `obl_frequency=3`, dst.) yang mengindikasikan sudah melalui proses tuning ekstensif (kemungkinan dari fase HPO proyek asal), sementara baseline eksplisit tidak di-tuning. Manuskrip sudah mengakui asimetri ini sebagai "baseline honesty" trade-off (§4.4) — ini jujur, tapi reviewer bisa membalik argumen: **IFPOA-X sendiri juga tidak "out-of-the-box", ia sudah melalui rekayasa berat sebelumnya**, sehingga framing "IFPOA-X out-of-the-box vs baseline out-of-the-box" (§5.6) sedikit tidak simetris dan idealnya diperhalus.

## C. Origin-bias audit

**[INTERPRETASI REVIEWER]** Ini bagian **terkuat** manuskrip. Kombinasi empat kontrol (custom shift, CEC2017 official 10-fungsi, dua sweep magnitude/arah) plus domain-safe F8 fix, plus factorial 2×2 dengan difference-in-differences (§5.7.5, p=4.9×10⁻⁴) secara kolektif memberikan **bukti kausal within-implementation yang solid** — bukan sekadar asosiasi. Perbedaan association vs. within-algorithm causal evidence vs. universal claim tentang seluruh keluarga OBL **sudah dibedakan dengan baik** di manuskrip terkini (lihat §5.7.5 paragraf penutup dan §6 paragraf kedua-dari-akhir yang eksplisit membatasi generalisasi). Ini adalah hasil dari revisi-revisi sebelumnya di sesi ini dan sudah cukup matang.

Satu titik lemah tersisa: **rotasi hanya diuji pada 10 dari 13 fungsi (subset CEC2017, §5.7.2)**, dan tiga dari empat kontrol (custom shift, far, mixed) adalah **shift-only**, tidak menguji non-separability/rotasi sama sekali. Manuskrip sudah mengakui ini eksplisit sebagai limitation (i) di §5.6 — jujur dan tepat, tidak perlu ditutup-tutupi, tapi reviewer metodolog kemungkinan akan tetap mencatatnya sebagai celah, bukan sebagai alasan penolakan.

## D. Statistics

**[INTERPRETASI REVIEWER]** Penggunaan Friedman+Iman–Davenport, Kendall's W, Holm (primer) dan Finner (sensitivity), Wilcoxon per-fungsi, A₁₂, bootstrap CI, dan CD diagram semuanya konsisten dan sesuai standar Derrac et al. [23] yang dikutip sebagai acuan metodologis. **Yang paling saya hargai**: manuskrip secara eksplisit dan berulang (§4.5, §5.1, §5.2) membedakan unit analisis per-function vs cross-function, dan secara jujur melaporkan bahwa Holm-corrected p=0.061 vs GWO/WOA **tidak signifikan** bahkan sebelum kontrol origin-bias diterapkan — ini adalah **pola yang sangat jarang** dilakukan jujur di literatur metaheuristik (biasanya "menang 12/13 fungsi" langsung diklaim sebagai superioritas global tanpa koreksi multiple-comparison lintas-fungsi).

**Tidak ditemukan** dalam audit saya: p-value overclaim, uncorrected multiple comparison yang dibiarkan tanpa disclaimer, pseudoreplication yang tidak diungkap, atau inkonsistensi framing antara Abstrak-Results-Conclusion (ketiganya konsisten menyebut "5.23–5.77" dan "p=0.061" dengan angka yang sama). Ini titik yang sangat solid dan salah satu alasan kuat kenapa manuskrip layak dikirim ke reviewer eksternal.

Satu catatan kecil: N=13 fungsi sebagai unit sampel untuk uji cross-function (Friedman dkk.) **secara statistik valid** tapi **secara daya (power) terbatas** — inilah kenapa Holm p=0.061 (marginal, bukan signifikan) untuk GWO/WOA. Manuskrip sudah transparan soal ini ("given only N = 13 functions", §5.1) — bagus, tapi reviewer metodolog bisa meminta power analysis eksplisit atau setidaknya effect-size interpretation yang lebih hati-hati di sekitar angka p=0.061 ini (saat ini sudah cukup hati-hati, tapi bisa diperkuat).

---

# 5. SO WHAT? DAN NILAI ILMIAH

**[INTERPRETASI REVIEWER]**

1. **Pelajaran umum bagi komunitas EC**: Sebuah keunggulan performa metaheuristik pada budget rendah yang tampak besar dan signifikan secara statistik (rank 1.31, menang 12/13 fungsi) bisa sepenuhnya merupakan artefak keselarasan geometris antara mekanisme algoritma (di sini: reflection OBL) dan struktur benchmark (optima berpusat), dan ini bisa dibuktikan secara kausal dengan factorial sederhana tanpa perlu mengubah algoritma.
2. **Hanya berlaku untuk IFPOA-X?** Secara ketat (dan manuskrip sudah jujur soal ini), temuan kausal langsung hanya berlaku untuk implementasi OBL fixed-centre-reflection dalam IFPOA-X pada budget 500-NFE. Tapi manuskrip dengan tepat membingkainya sebagai *"existence result"* — bukti bahwa pola kegagalan ini **mungkin terjadi** dan **layak dicurigai** di algoritma lain yang memakai mekanisme serupa (§5.7.5, §6), bukan generalisasi universal.
3. **Cukup penting untuk mengubah praktik evaluasi OBL-based methods?** Berpotensi ya, jika toolkit yang dirilis (`functions_shifted.py`, dst., §6 "Code availability") benar-benar dipakai peneliti lain. Tapi dampak nyata bergantung pada visibilitas paper — ini argumen kuat untuk memilih venue dengan jangkauan pembaca luas di komunitas metaheuristik, yang mendukung SWEVO sebagai pilihan (lihat §12).
4. **Existence result, general principle, atau case study?** Existence result yang solid secara statistik dalam satu case study — ini penilaian paling akurat dan manuskrip sendiri sudah membingkainya seperti ini secara eksplisit di §5.7.5 ("a cautionary existence result"). Tidak melebih-lebihkan diri sebagai general principle.
5. **Menjelaskan mengapa penting di luar tabel ranking?** Ya — §5.7.5 dan §6 secara eksplisit menghubungkan temuan ke implikasi praktis untuk reviewer/venue ("we urge that any low-budget... claim for a reflection-based operator be treated as unverified until checked against a shifted control, and that reviewers and venues request one"). Ini kalimat "so what" yang kuat dan konkret, bukan generik.
6. **Dampak bagi desain benchmark dan klaim superiority**: Cukup jelas diartikulasikan — rekomendasi konkret untuk mewajibkan shifted control sebagai validity check standar bagi metode berbasis reflection/centre-bias, sejalan dengan preseden Rajwar & Deep [36] dan Vermetten et al. BIAS toolbox [35] yang sudah dikutip.

---

# 6. EVALUASI SETIAP BAGIAN MANUSKRIP

| Bagian | Kekuatan | Kelemahan | Risiko reviewer | Perubahan konkret |
|---|---|---|---|---|
| **Title** | Ringkas (13 kata), tidak algoritmik, langsung menyatakan pertanyaan riset | — | Rendah | Tidak perlu diubah |
| **Abstract** | Sangat informatif, angka lengkap (rank, p-value, effect) | **378 kata**, jauh di atas standar ~250 kata Elsevier | **Tinggi** — bisa memicu permintaan revisi administratif di screening pertama | Pangkas ~35% ke ~250 kata; pindahkan detail angka sekunder (p=0.061 spesifik per-baseline) ke body |
| **Keywords** | Relevan dan spesifik | **8 frasa**, melebihi maksimum 6 yang tertulis eksplisit di Guide for Authors resmi yang saya baca | Sedang | Pangkas ke 6: pertahankan "opposition-based learning," "origin bias," "benchmark validity," "flower pollination algorithm," "ablation study," "equal-NFE evaluation protocol"; buang "metaheuristic optimization" (terlalu generik, dilarang guide) dan "low-budget optimization" (redundan dgn equal-NFE) |
| **Introduction** | Motivasi bertingkat jelas (§1 paragraf 1-5), kontribusi diurutkan dengan baik | Agak panjang untuk introduction jurnal (bisa dipadatkan 10-15%) | Rendah | Opsional, tidak wajib |
| **Related Work** | Table 1 positioning sangat efektif secara visual; sitasi 2022-2025 terkini (Velasco, Vermetten x2, Mohamed, Rajwar&Deep) menunjukkan riset literatur yang hidup | Belum eksplisit mengontraskan diri dengan Piotrowski 2023/Chen 2024 (preseden SWEVO terdekat) | Sedang | Tambahkan 2-3 kalimat kontras eksplisit di §2.5/2.6 (lihat §3 di atas) |
| **Research Gap** | Kalimat gap dirumuskan eksplisit dalam blockquote (§2.6) — praktik bagus, jarang dilakukan penulis lain | — | Rendah | — |
| **Methodology (§3)** | OBL geometric note (§3.2) sangat presisi; formulasi lengkap dan bisa direproduksi | Nama "IFPOA-X" bisa menyesatkan re: identitas FPA (lihat §4A) | Sedang | Tambah 1 kalimat pengakuan operator lokal FPA sepenuhnya diganti JADE |
| **Experimental Setup (§4)** | Equal-NFE protocol diaudit sendiri secara transparan, parameter lengkap di Supp S1 | Inisialisasi tidak seragam antara dua "keluarga" algoritma (confound, sudah diakui tapi tidak diukur) | Sedang-tinggi | Idealnya: sensitivity check kecil (lihat §11) |
| **Statistical Analysis (§4.5)** | Pembedaan per-function/cross-function eksplisit dan konsisten di seluruh paper — kekuatan utama | N=13 power terbatas (diakui, sudah cukup transparan) | Rendah | — |
| **Results (§5.1-5.5)** | Tabel 3 (D30 full summary) dan konvergensi (Figure 1) baru saja dikembalikan ke main text — memperkuat "sellability" visual | — | Rendah | — |
| **Discussion/Limitations (§5.6)** | Sangat jujur, 6 limitation eksplisit dengan prioritas future work | — | Rendah — justru kekuatan | — |
| **Conclusion (§6)** | Scoping causal claim eksplisit ("within the tested IFPOA-X implementation and 500-NFE setting"), rekomendasi konkret ke reviewer/venue | — | Rendah | — |
| **Supplementary Material** | Terstruktur rapi (S1-S4 tabel, S1-S2 figure), semua disitasi di main text | — | Rendah | — |
| **Code and Data Availability** | Repo publik GitHub dengan README lengkap, stub kompatibilitas didokumentasikan jujur | Tidak ada persistent identifier (DOI arsip, mis. Zenodo) — GitHub saja tidak permanen | **Tinggi jika jurnal memakai Research Data Policy Option C** (lihat §7) | Arsipkan repo ke Zenodo/Software Heritage untuk DOI permanen sebelum submit |
| **References** | 41 referensi, semua diverifikasi manual via Crossref sepanjang sesi ini (bukan estimasi — ini fakta dari histori kerja kita), penomoran kontinu 1-41 tanpa gap | Untuk artikel riset (bukan survei), 41 referensi ada di sisi lebih rendah dibanding norma SWEVO untuk topik meta-benchmarking (Piotrowski et al. kemungkinan >60 mengingat cakupan 73 algoritma) | Sedang | Opsional: tambah 3-5 sitasi lagi terutama dari perbandingan langsung dengan Piotrowski/Chen/Rai (lihat §3) |

**Item spesifik yang diminta:**
- Abstrak ≤250 kata? **Tidak — 378 kata, gagal.**
- 1-7 keywords? Guide resmi yang saya baca bilang **maksimum 6** — Anda punya **8, gagal.**
- Judul terlalu panjang/algoritmik? Tidak, sudah baik.
- Main manuscript terlalu panjang? ~13.600 kata raw. SWEVO tidak punya batas kata keras yang saya temukan di guide resmi, tapi ini di sisi panjang untuk artikel riset reguler (bukan survei) — realistis masih diterima asalkan padat dan tidak ada pengulangan, yang sejauh ini memang tidak ada.
- Supplementary dipakai efektif? Ya, sudah cukup seimbang setelah restorasi Tabel 3/5 dan Figure 1/5 ke main text.
- Figures/tables terlalu padat? Tidak — tabel-tabel numerik (Tabel 3, 5, S2) padat tapi standar untuk jenis studi ini, dan caption jelas.
- Semua equation editable & bernomor? **[FAKTA MANUSKRIP]** Equation di §3.1-3.3 menggunakan LaTeX `$$...$$` (bukan gambar) — akan otomatis lolos syarat "math as editable text, not images" saat dikonversi ke Word/LaTeX submission, **tapi belum bernomor** (tidak ada `(1)`, `(2)`, dst.) — ini pelanggaran ringan yang harus diperbaiki karena guide eksplisit meminta "number consecutively any equations... if referred to explicitly in the text", dan beberapa equation memang dirujuk implisit dari teks.
- Citation numbering sesuai urutan kemunculan? **Ya — sudah diverifikasi ketat sepanjang sesi ini (lihat CITATION_MAPPING.md), 1-41 kontinu tanpa gap/duplikat.**
- Reference metadata lengkap? Ya, semua entry punya penulis, tahun, judul, jurnal/prosiding, volume/halaman atau DOI — bahkan mencatat koreksi transparan untuk 2 sitasi yang sebelumnya salah (lihat anotasi "Verified via Crossref; corrects..." di ref [33], [34], [40]).
- Bahasa British/American konsisten? **[FAKTA MANUSKRIP]** Saya tidak menemukan campuran eksplisit (mis. "colour" vs "color", "-ise" vs "-ize") dalam pembacaan saya, tapi ini perlu dicek ulang dengan grep otomatis sebelum submit karena saya tidak melakukan pemeriksaan huruf-demi-huruf lengkap di laporan ini.
- Em dash/frasa formulaik/AI-generated feel? **[FAKTA — dari histori kerja sesi ini]** Sudah melalui style-pass eksplisit sebelumnya (142→15 em dash, "crucially"/"notably"/"taken together" dihilangkan, "not X but Y" dikurangi 5→2) — ini sudah ditangani dengan baik dan terdokumentasi di `STYLE_CHANGELOG.md`.

---

# 7. KEPATUHAN TERHADAP GUIDE FOR AUTHORS

**[FAKTA JURNAL, dari Author Information Pack Elsevier 10 Jan 2016 yang saya baca penuh, dilengkapi kebijakan Elsevier-wide untuk item yang mendahului dokumen 2016]**

| Item | Syarat resmi | Status manuskrip Anda |
|---|---|---|
| Editable Word/LaTeX source | Wajib; LaTeX `elsarticle.cls` direkomendasikan | **Ready** — Markdown mudah dikonversi ke salah satu format ini |
| Single-column layout (submission) | Wajib eksplisit di guide | **Ready** (Markdown default single-column) |
| Title page (judul, penulis, afiliasi) | Judul ringkas; nama depan/belakang jelas; afiliasi per-penulis dengan superscript huruf kecil; alamat pos lengkap per afiliasi | **Needs revision** — hanya ada satu baris "Affiliation: STMKG" bersama untuk 4 penulis, tanpa superscript individual, tanpa alamat pos lengkap |
| Corresponding author + email | Wajib, harus jelas siapa dan email aktif | **Missing** — tidak ada penanda corresponding author maupun email di manuskrip |
| Abstract ≤ ~250 kata | Faktual, ringkas, berdiri sendiri | **Needs revision** — 378 kata |
| Keywords ≤ 6 | Maks 6, hindari istilah umum/plural/multi-konsep | **Needs revision** — 8 keyword |
| Highlights 3-5 bullet, ≤85 karakter | Opsional per dokumen 2016, tapi file terpisah "Highlights" jika disertakan | **Missing** (opsional secara resmi, tapi sangat disarankan untuk daya jual di screening editor) |
| Graphical abstract | Opsional, didorong | **Missing** — tidak ada file graphical abstract di folder figures/ |
| Editable equations, bernomor | Wajib sebagai teks bukan gambar; nomor jika dirujuk | **Needs revision** — sudah editable (LaTeX), belum bernomor |
| Editable tables tanpa vertical rules | Wajib | **Ready** — tabel Markdown tidak memakai vertical rule secara visual saat dirender |
| Figures sebagai file resolusi tinggi terpisah | Wajib, format EPS/PDF/TIFF | **Ready** — PDF vector + PNG tersedia untuk semua figure |
| Supplementary material disitasi di main text | Wajib | **Ready** — semua Supp Table/Figure disitasi eksplisit |
| Data repository & linking | Didorong kuat, terutama untuk Research Data Policy | **Ready sebagian** — repo GitHub publik ada, tapi tanpa persistent identifier (lihat di bawah) |
| Data availability statement | Standar Elsevier-wide sejak Research Data Policy diberlakukan (bukan di dokumen 2016, tapi berlaku umum sekarang) | **Ready** — §6 sudah punya "Data availability" dan "Code availability" statement eksplisit |
| Software citation | Standar praktik terkini | **Ready** — mealpy [38], optuna [39], opfunu [40] semua disitasi sebagai software reference dengan anotasi eksplisit |
| Funding statement | Wajib | **Missing** |
| Competing-interest declaration | Wajib | **Missing** |
| CRediT author contribution | Standar Elsevier-wide sejak ~2020 (mendahului dokumen 2016 yang saya baca, tapi hampir pasti berlaku sekarang) | **Missing** |
| Acknowledgements | Opsional, section terpisah sebelum referensi jika ada | **Missing** (boleh kosong jika memang tidak ada pihak yang perlu diakui, tapi section placeholder tetap baik ada) |
| Generative AI disclosure | Kebijakan Elsevier-wide sejak 2023 (mendahului dokumen 2016) | **Missing** — lihat §8 di bawah untuk draft yang saya siapkan |
| Submission checklist umum | — | Lihat semua item di atas |

**[INTERPRETASI REVIEWER] Soal Research Data Policy Option C:** Anda menyebutkan jurnal ini menerapkan Option C — saya **tidak bisa memverifikasi ini secara independen** karena halaman resminya tidak bisa saya akses (403). Saya akan memperlakukan pernyataan Anda sebagai fakta yang Anda peroleh langsung dari halaman jurnal (bukan saya validasi ulang). **Jika benar Option C** ("data available on request" atau setara — biasanya opsi paling longgar dari A/B/C, di mana C umumnya berarti pernyataan ketersediaan data cukup tanpa keharusan deposit di repository ber-DOI), maka repo GitHub Anda **kemungkinan besar sudah cukup** secara formal. Namun **praktik terbaik** (dan yang akan meningkatkan kepercayaan reviewer soal reproducibility, terlepas dari opsi kebijakan resmi) tetap: **arsipkan repo ke Zenodo atau Software Heritage untuk mendapat DOI permanen**, karena GitHub URL bisa berubah/dihapus dan tidak dianggap "persistent identifier" oleh sebagian reviewer metodologi ketat, bahkan di bawah Option C sekalipun.

---

# 8. GENERATIVE AI DISCLOSURE

**[INTERPRETASI REVIEWER]** Berdasarkan kebijakan Elsevier tentang penggunaan AI generatif dalam penulisan (kebijakan umum yang berlaku across jurnal Elsevier, meski tidak tercantum di dokumen 2016 yang saya baca), berikut draft disclosure yang jujur, proporsional, dan tidak berlebihan, ditulis untuk ditambahkan sebagai bagian terpisah sebelum References atau di bagian Acknowledgements:

> **Declaration of generative AI and AI-assisted technologies in the writing process.**
> During the preparation of this work, the authors used AI-assisted tools for language editing, structural consistency checks, citation formatting, and manuscript organization (including table/figure renumbering and cross-reference verification). All AI-suggested citations were independently verified against primary sources (Crossref) before inclusion, and all experimental design, code implementation, data analysis, statistical interpretation, and scientific conclusions were conceived, executed, and validated solely by the human authors. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.

**Penilaian saya**: draft ini jujur dan proporsional — tidak mengklaim AI sebagai penulis, tidak menyembunyikan penggunaan AI untuk *editing* dan *organisasi*, tapi juga tegas menyatakan tanggung jawab penuh penulis atas isi ilmiah. Ini sesuai dengan prinsip umum kebijakan Elsevier ("AI cannot be listed as an author... authors are ultimately responsible and accountable for the contents of the work").

**Wording berisiko yang perlu dinormalisasi?** Setelah style-pass ekstensif yang sudah dilakukan sepanjang sesi ini (142→15 em dash, penghapusan frasa formulaik "crucially"/"notably"/"taken together", pengurangan "not X but Y"), saya **tidak** menemukan frasa yang secara jelas terlihat sebagai output AI mentah dalam pembacaan saya kali ini. Draft saat ini sudah cukup natural. Satu pola yang masih berulang cukup sering: struktur kalimat "X, and Y" atau "X; Z" yang panjang di beberapa paragraf hasil analisis (mis. §5.4 paragraf "Why the adaptive components fail") — ini bukan tanda AI per se, tapi kalimatnya cukup panjang (>60 kata) di beberapa tempat dan bisa dipecah untuk keterbacaan, bukan untuk menghilangkan "AI-feel."

---

# 9. ESTIMASI PELUANG EDITORIAL

**[ESTIMASI SUBJEKTIF — bukan dari data acceptance-rate SWEVO yang terverifikasi. Saya tidak punya akses ke angka riil desk-rejection/acceptance rate historis SWEVO, jadi ini murni penilaian informed judgment berdasarkan kualitas manuskrip yang saya baca, dibandingkan pola umum jurnal Q1 Elsevier di bidang serupa.]**

## Skenario A: Manuskrip disubmit dalam kondisi sekarang (item administratif §7 belum diperbaiki)

| Outcome | Estimasi |
|---|---|
| Desk rejection (administratif atau scope) | 20–30% |
| Dikirim ke external review | 70–80% |
| Reject after review | 25–35% (dari yang direview) |
| Major revision | 40–50% (dari yang direview) |
| Minor revision | 10–15% (dari yang direview) |
| Eventual acceptance (setelah siklus revisi penuh) | 35–45% secara keseluruhan |

**Dasar penilaian**: kualitas ilmiah inti (statistik, desain audit, kejujuran pelaporan) sudah cukup kuat untuk lolos screening substantif, tapi risiko desk-rejection di Skenario A didorong murni oleh kegagalan administratif konkret (abstrak 378 kata, 8 keyword, tidak ada CRediT/funding/competing-interest) yang **mudah sekali diperbaiki** namun jika tidak diperbaiki bisa membuat editor mengembalikan manuskrip sebelum reviewer sempat membacanya.

## Skenario B: Semua revisi wajib (§11, kategori "Mandatory before submission") telah diselesaikan

| Outcome | Estimasi |
|---|---|
| Desk rejection | <5–10% |
| Dikirim ke external review | 90–95% |
| Reject after review | 10–20% (dari yang direview) |
| Major revision | 35–45% (dari yang direview) |
| Minor revision | 25–35% (dari yang direview) |
| Eventual acceptance (setelah siklus revisi) | 55–65% secara keseluruhan |

**Dasar penilaian**: dengan gap administratif tertutup, keputusan editorial akan murni bergantung pada substansi — dan substansi saat ini (equal-NFE rigor, empat kontrol independen, factorial kausal, kejujuran hasil negatif) berada di atas rata-rata submission metaheuristik yang saya nilai secara umum. Risiko residual di Skenario B: skala validasi tunggal-algoritma (§4B) dan generalisasi terbatas-satu-varian-OBL (§2) tetap bisa memicu setidaknya satu putaran major revision meminta eksperimen tambahan kecil (lihat §11) — makanya estimasi acceptance tidak mendekati 80-90% bahkan di skenario terbaik.

---

# 10. SIMULASI KEPUTUSAN EDITOR

**Keputusan: MAJOR REVISION**

*(Catatan silang-cek penting: ini konsisten dengan dua review independen sebelumnya — `review1.md` dan `review2.md` — yang keduanya, menurut ringkasan riwayat kerja kita, juga merekomendasikan Major Revision. Konvergensi tiga penilaian independen — dua review manusia-gaya sebelumnya dan simulasi editorial ini — pada kesimpulan yang sama adalah sinyal yang cukup kuat, bukan kebetulan.)*

### 1. Confidential comments to the editor
Manuskrip ini melaporkan audit metodologis yang jujur dan secara statistik disiplin terhadap bias geometri pada satu mekanisme opposition-based learning, dengan bukti kausal within-implementation yang kuat (factorial 2×2, difference-in-differences p=4.9×10⁻⁴). Saya menilai kontribusi ini defensible untuk SWEVO, sejalan dengan preseden Piotrowski et al. (2023) dan Rajwar & Deep (2025) yang sudah diterbitkan jurnal ini pada topik serupa. Kelemahan utama bukan pada rigor ilmiah inti melainkan pada (a) skala validasi yang jauh lebih sempit dari norma studi meta-benchmarking di jurnal ini, (b) generalisasi yang secara ketat terbatas pada satu varian OBL, dan (c) sejumlah kegagalan kepatuhan administratif Elsevier yang trivial untuk diperbaiki. Saya merekomendasikan pengiriman ke reviewer eksternal yang familiar dengan statistical methodology untuk metaheuristic benchmarking (bukan hanya reviewer aplikasi algoritma).

### 2. Comments to the authors
Studi Anda mengangkat pertanyaan penting yang jarang diuji secara langsung di literatur: apakah keunggulan low-budget sebuah metaheuristik berbasis opposition adalah properti algoritmik genuine atau artefak keselarasan geometris dengan benchmark. Desain audit empat-kontrol plus factorial kausal Anda adalah kontribusi metodologis nyata, dan kejujuran Anda melaporkan hasil negatif (JADE merugikan, bandit tidak terdeteksi, IFPOA-X tidak signifikan lebih baik dari GWO/WOA secara cross-function bahkan pada suite klasik) patut dihargai. Namun manuskrip memerlukan revisi substansial sebelum dapat dipertimbangkan untuk publikasi.

### 3. Major comments
1. Perkuat generalisasi eksternal: saat ini kesimpulan sepenuhnya bergantung pada satu implementasi OBL (elite-reflection, Tizhoosh). Diskusikan secara eksplisit dan lebih tegas bahwa varian OBL non-fixed-centre (mis. PCOBL yang sudah dikutip) mungkin tidak menunjukkan pola serupa, dan pertimbangkan apakah eksperimen tambahan kecil (bahkan hanya pada 2-3 fungsi) dengan satu varian OBL alternatif dapat memperkuat klaim generalisasi.
2. Ukur besarnya confound inisialisasi (Latin-Hypercube vs default `mealpy`) yang saat ini hanya diakui sebagai limitation tanpa kuantifikasi. Sebuah sensitivity check kecil akan menutup celah metodologis ini.
3. Perbaiki seluruh item kepatuhan administratif Guide for Authors (lihat §7 laporan ini): abstrak melebihi batas kata, keyword melebihi maksimum, tidak ada CRediT/funding/competing-interest/generative-AI disclosure, equation belum bernomor, title page belum lengkap.
4. Kontraskan temuan Anda secara eksplisit dengan studi benchmark-validity yang sudah diterbitkan di jurnal ini sendiri (Piotrowski et al. 2023; Chen et al. 2024) untuk memperjelas positioning novelty relatif terhadap preseden terdekat.

### 4. Minor comments
1. Tambahkan persistent identifier (DOI arsip via Zenodo/Software Heritage) untuk repository kode, melengkapi tautan GitHub yang sudah ada.
2. Pertimbangkan menambah 1 kalimat di §3 yang mengakui operator lokal FPA asli sepenuhnya digantikan JADE dalam IFPOA-X, untuk mengantisipasi keberatan soal identitas algoritma.
3. Beberapa kalimat analisis (mis. §5.4 paragraf "Why the adaptive components fail") melebihi 60 kata; pertimbangkan memecahnya untuk keterbacaan.

### 5. Alasan akhir keputusan
Kekuatan metodologis dan kejujuran pelaporan hasil manuskrip ini berada di atas ambang minimum untuk dipertimbangkan serius oleh jurnal ini, dan topiknya memiliki preseden penerimaan yang jelas di SWEVO. Namun keterbatasan skala/generalisasi (Major comment 1-2) dan kegagalan kepatuhan administratif substansial (Major comment 3) mencegah rekomendasi Minor Revision atau Accept pada tahap ini.

---

# 11. ACTIONABLE REVISION PLAN

| Priority | Problem | Why it matters | Exact revision | Section affected | Requires new experiment? | Estimated impact on acceptance probability |
|---|---|---|---|---|---|---|
| **Mandatory** | Abstrak 378 kata (>250) | Risiko tinggi terkena screening administratif sebelum dinilai reviewer | Pangkas ke ≤250 kata, pindahkan detail sekunder ke body | Abstract | Tidak | Tinggi (mencegah desk-reject administratif) |
| **Mandatory** | 8 keyword (>6 maksimum resmi) | Pelanggaran eksplisit guide resmi | Pangkas ke 6 keyword paling representatif | Keywords | Tidak | Sedang |
| **Mandatory** | Tidak ada CRediT, funding statement, competing-interest declaration | Wajib Elsevier-wide, hampir pasti diminta sistem submission otomatis sebelum manuskrip bisa diproses | Tambahkan ketiga section standar sebelum References | Back matter | Tidak | Tinggi (blocker submission teknis, bukan hanya ilmiah) |
| **Mandatory** | Title page: afiliasi tidak per-penulis, tidak ada corresponding author/email | Wajib guide resmi | Tambahkan superscript afiliasi per penulis, tandai 1 corresponding author + email + alamat pos | Title page | Tidak | Tinggi |
| **Mandatory** | Equation belum bernomor | Pelanggaran eksplisit guide resmi untuk equation yang dirujuk di teks | Nomori semua persamaan yang dirujuk (§3.1-3.3) | Methodology | Tidak | Rendah-sedang |
| **Mandatory** | Tidak ada generative-AI disclosure | Kebijakan Elsevier-wide standar sekarang | Tambahkan section disclosure (draf tersedia di §8 laporan ini) | Back matter | Tidak | Sedang |
| **Strongly recommended** | Confound inisialisasi (LHS vs default) tidak diukur, hanya diakui | Reviewer statistik ketat kemungkinan besar akan memintanya | Sensitivity check kecil: re-run 2-3 baseline dengan LHS init pada subset fungsi (mis. F1, F5, F9), bandingkan hasil | §4.3/§5.6 | **Ya, tapi kecil** (2-3 baseline × subset fungsi, bukan full re-run) | Sedang-tinggi (menutup celah metodologis paling sering ditanyakan reviewer) |
| **Strongly recommended** | Positioning novelty vs preseden SWEVO terdekat belum eksplisit | Reviewer yang familiar SWEVO recent issues bisa menanyakan ini langsung | Tambah 2-3 kalimat kontras eksplisit dengan Piotrowski et al. 2023 dan Chen et al. 2024 di §2.5/2.6 | Related Work | Tidak | Sedang |
| **Strongly recommended** | Repo kode hanya di GitHub, tanpa persistent identifier | Praktik terbaik reproducibility, relevan untuk Research Data Policy | Arsipkan ke Zenodo/Software Heritage, dapatkan DOI, tambahkan ke §6 Code/Data availability | Code/Data availability | Tidak | Sedang |
| **Strongly recommended** | Identitas algoritma "FPA" dalam IFPOA-X bisa dipertanyakan reviewer purist | Mencegah keberatan yang mudah dihindari | Satu kalimat pengakuan eksplisit di §3 pembuka | Methodology | Tidak | Rendah-sedang |
| **Optional** | Highlights file dan graphical abstract belum ada | Opsional secara resmi, tapi membantu daya tarik di screening editor dan visibilitas online | Buat highlights 3-5 bullet (≤85 karakter) dan 1 graphical abstract | Submission package | Tidak | Rendah-sedang (bantu "sellability" tapi bukan syarat wajib) |
| **Optional** | Referensi 41 entri, agak sedikit untuk topik meta-benchmarking di jurnal ini | Tidak wajib, tapi memperkuat kedalaman literature review | Tambah 3-5 sitasi dari perbandingan §3 (Piotrowski, Chen, Li, Yi, Rai) jika relevan untuk diskusi | Related Work/Discussion | Tidak | Rendah |
| **Future work** | Generalisasi ke varian OBL lain (PCOBL, dst.) | Sudah diakui manuskrip sebagai future work eksplisit — tidak perlu dipaksakan sekarang | Tidak ada tindakan wajib sekarang; pertahankan framing scoped yang sudah ada | §6 Conclusion | Ya (studi terpisah) | — (bukan untuk revisi ini) |
| **Future work** | Audit origin-bias pada D=50 dan CEC2017 penuh | Sudah diakui eksplisit sebagai limitation/future work | Tidak ada tindakan wajib sekarang | §5.6 | Ya (studi terpisah) | — (bukan untuk revisi ini) |

**[INTERPRETASI REVIEWER]** Saya sengaja **tidak** merekomendasikan eksperimen tambahan besar (mis. mengulang audit di D=50, menambah algoritma ke-9/10, atau menguji varian OBL lain) sebagai *mandatory* karena kelemahan fatal manuskrip ini bukan pada kekurangan data — desainnya sudah cukup untuk membuktikan klaim yang **discoped dengan benar**. Satu-satunya eksperimen tambahan yang saya rekomendasikan (confound inisialisasi) itu pun **kecil** dan ditujukan untuk menutup celah metodologis spesifik yang sudah diakui manuskrip sendiri, bukan untuk memperluas cakupan klaim.

---

# 12. REKOMENDASI AKHIR

**1. Apakah paper layak langsung disubmit ke SWEVO?**
**[INTERPRETASI REVIEWER]** Belum, dalam kondisi administratif sekarang. Substansi ilmiah sudah layak, tapi item Mandatory di §11 (terutama abstrak/keyword/CRediT/funding/title-page) harus diselesaikan lebih dulu — ini pekerjaan administratif, bukan riset ulang, dan bisa selesai dalam hitungan jam-hari, bukan minggu.

**2. Apakah kemungkinan desk rejection terlalu tinggi?**
**[ESTIMASI SUBJEKTIF]** Dalam kondisi sekarang: sedang (20-30%, didorong murni oleh gap administratif, lihat §9 Skenario A). Setelah item Mandatory diperbaiki: rendah (<10%, §9 Skenario B). Ini bukan risiko "paper Anda tidak layak", tapi risiko "paper Anda belum siap secara format submission."

**3. Apakah lebih baik mencoba jurnal ini dulu karena fit-nya kuat?**
**[INTERPRETASI REVIEWER]** Ya — fit topik dengan SWEVO genuinely kuat dan didukung preseden konkret (Piotrowski 2023, Rajwar & Deep 2025 yang sudah Anda kutip). Ini bukan kasus "menembak terlalu tinggi tanpa alasan" — tapi saya sarankan menyelesaikan seluruh item Mandatory §11 **sebelum** submit pertama, karena siklus review SWEVO (seperti kebanyakan jurnal Elsevier Q1) bisa memakan waktu 3-6 bulan per putaran; kegagalan administratif yang bisa dicegah di awal akan sia-siakan waktu tersebut.

**4. Apakah paper sebaiknya tetap ditargetkan ke Evolutionary Intelligence?**
**[INTERPRETASI REVIEWER]** *Evolutionary Intelligence* (Springer) tetap pilihan realistis dan valid sebagai **jalur cadangan**, bukan pilihan yang lebih superior — bar penerimaannya secara umum sedikit lebih rendah dari SWEVO (SWEVO memiliki CiteScore/SJR yang lebih tinggi dan reputasi lebih established di komunitas EC/swarm), tapi risikonya jauh lebih rendah dan siklus review historically sedikit lebih cepat untuk jurnal ini. Karena manuskrip Anda sudah melalui reformulasi substansial menuju kualitas SWEVO-tier sepanjang sesi kerja ini, saya sarankan **mencoba SWEVO lebih dulu** (setelah item Mandatory selesai), dengan *Evolutionary Intelligence* sebagai fallback konkret jika SWEVO menolak.

**5. Urutan jurnal terbaik:**

| Rank | Jurnal | Scientific fit | Prestige (Q1/Q2 approx.) | Probability of acceptance *(estimasi subjektif)* | Speed | Zero-APC subscription route? |
|---|---|---|---|---|---|---|
| 1 | **Swarm and Evolutionary Computation** (Elsevier) | Sangat kuat (preseden langsung) | Q1, established | Sedang (butuh Skenario B di atas) | Sedang-lambat (~3-6 bulan/putaran, estimasi umum Elsevier Q1) | **Ya** — [FAKTA JURNAL] guide resmi eksplisit menyatakan rute Subscription "No open access publication fee payable by authors"; OA fee (2016: USD 2400, kemungkinan lebih tinggi sekarang) hanya berlaku jika memilih rute Open Access |
| 2 | **Evolutionary Intelligence** (Springer) | Kuat (target awal proyek ini) | Q2-Q1 borderline, ESCI/Scopus | Lebih tinggi dari SWEVO | Umumnya lebih cepat | Ya (rute subscription/hybrid non-OA umumnya tersedia) |
| 3 | **Applied Soft Computing** (Elsevier) | Kuat tapi scope lebih luas dari swarm/EC murni | Q1, sering IF lebih tinggi dari SWEVO (berarti bisa lebih kompetitif, bukan lebih mudah) | Sedang, mirip SWEVO | Sedang | Ya (opsi subscription) |
| 4 | **Algorithms** (MDPI) | Cukup baik untuk studi metodologis/benchmark | Q2, Scopus-indexed | Tinggi | Cepat (MDPI dikenal cepat) | **Tidak** — MDPI adalah gold-OA murni, APC wajib |
| 5 | **Expert Systems with Applications** (Elsevier) | Sedang — risiko ditolak karena kurang aplikasi nyata (lihat §1 poin 5) | Q1 tinggi, sangat kompetitif | Rendah-sedang untuk paper benchmark-only | Sedang | Ya (opsi subscription) |

**Jika SWEVO dinilai terlalu ambisius**, tiga alternatif Scopus yang realistis dan lebih longgar tanpa mengorbankan kredibilitas:
1. **Evolutionary Intelligence** (Springer) — fit topik sangat dekat, bar lebih realistis, sudah jadi target awal proyek ini.
2. **Soft Computing** (Springer) — scope luas mencakup metaheuristik dan analisis benchmark, bar sedang.
3. **Algorithms** (MDPI, open access) — cepat, Scopus-indexed, cocok untuk studi metodologis yang tajam meski sempit skalanya; catatan: APC wajib (bukan zero-APC), pertimbangkan jika ada dukungan dana publikasi institusi.

---

## Ringkasan satu-paragraf

**[INTERPRETASI REVIEWER, sebagai penutup]** Manuskrip ini adalah audit metodologis yang jujur, disiplin secara statistik, dan memiliki fit topik yang kuat dengan preseden konkret di *Swarm and Evolutionary Computation* — tapi belum siap submit hari ini murni karena kegagalan kepatuhan administratif (abstrak, keyword, CRediT, funding, title page) yang seluruhnya dapat diperbaiki dalam hitungan hari, bukan minggu. Substansi ilmiahnya — protokol equal-NFE yang ketat, empat kontrol origin-bias independen, factorial kausal 2×2 dengan difference-in-differences yang signifikan, dan kejujuran melaporkan hasil negatif (JADE merugikan, bandit tidak terdeteksi, IFPOA-X tidak signifikan lebih baik dari GWO/WOA secara cross-function) — berada di atas rata-rata submission metaheuristik yang lazim saya nilai, dan sejalan dengan preseden Piotrowski et al. (2023) dan Rajwar & Deep (2025) yang sudah diterbitkan jurnal yang sama. Saya **tidak** menjamin acceptance — tidak ada review yang bisa menjamin itu — tapi saya menilai Major Revision sebagai outcome paling realistis dan dapat dicapai jika item Mandatory di §11 diselesaikan sebelum submit.
