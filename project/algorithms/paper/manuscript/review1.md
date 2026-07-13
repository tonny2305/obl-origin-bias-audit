# Laporan Peer Review Manuskrip

Saya telah menelaah dokumen lengkap yang terdiri atas **29 halaman, 11 tabel, dan 9 gambar**, termasuk formulasi IFPOA-X, protokol equal-NFE, expanded ablation, CEC2017, tiga shifted controls, pembahasan, kesimpulan, dan daftar pustaka. 

## 1. Executive Summary & Initial Impression

### Ringkasan penelitian

Paper ini menguji apakah keunggulan algoritma berbasis **Opposition-Based Learning** pada anggaran sangat terbatas benar-benar berasal dari kualitas pencarian algoritma atau hanya karena OBL selaras dengan geometri benchmark klasik yang banyak memiliki optimum di sekitar pusat domain. IFPOA-X menggabungkan FPA, OBL, UCB1, dan local search bergaya JADE. Pada F1–F13 klasik, IFPOA-X memperoleh mean rank terbaik, tetapi ablation menunjukkan hampir seluruh keunggulan berasal dari OBL, sementara UCB1 tidak memberikan manfaat terukur dan JADE justru merugikan. Ketika optimum digeser melalui beberapa kontrol dan subset CEC2017, ranking IFPOA-X turun menjadi sekitar posisi kelima–keenam. 

### Kontribusi utama yang paling kuat

Novelty terbaik paper ini **bukan IFPOA-X sebagai algoritma baru**, melainkan:

> **audit kritis terhadap validitas klaim performa OBL pada benchmark yang origin-centred.**

Ini merupakan kontribusi metodologis yang menarik karena paper tidak menyembunyikan hasil negatif. Temuan bahwa algoritma yang terlihat dominan pada benchmark klasik kemudian jatuh secara konsisten setelah shift merupakan cerita ilmiah yang lebih bernilai daripada paper metaheuristik biasa yang hanya mengklaim “algoritma baru lebih baik”.

### Keputusan editorial awal

## **MAJOR REVISION**

Paper memiliki inti ilmiah yang berpotensi diterbitkan, khususnya di *Evolutionary Intelligence* atau *Journal of Heuristics*. Namun, **file ini belum layak disubmit dalam kondisi sekarang**. Apabila dikirim tanpa perbaikan, keputusan yang paling mungkin adalah **desk rejection atau reject**, terutama karena:

1. klaim statistik lama belum konsisten dengan analisis lanjutan;
2. causal attribution kepada OBL belum diuji secara langsung;
3. formulasi shift pada manuskrip masih bermasalah;
4. fairness protokol eksperimen belum cukup terjamin;
5. proposed full IFPOA-X dikalahkan oleh varian tanpa JADE;
6. masih terdapat `Target venue`, provenance note, dan `[TODO: link]`;
7. beberapa rumus tampil sebagai LaTeX mentah atau rusak di Word.

### Penilaian keseluruhan

| Aspek                        |       Skor |
| ---------------------------- | ---------: |
| Kebaruan ide utama           |     8.5/10 |
| Signifikansi metodologis     |       8/10 |
| Kualitas desain eksperimen   |       6/10 |
| Validitas statistik saat ini |     5.5/10 |
| Kejelasan algoritma          |     5.5/10 |
| Reproducibility              |       4/10 |
| Bahasa dan presentasi        |     6.5/10 |
| Kesiapan submit              | **4.5/10** |
| Potensi setelah revisi       |   **8/10** |

---

# 2. Evaluasi Struktur dan Konten

## A. Judul dan Abstrak

### Kekuatan

Judul bersifat menarik, problem-driven, dan jauh lebih baik daripada judul generik seperti “An Improved Flower Pollination Algorithm”. Pertanyaan “When Does OBL Actually Help?” langsung mengisyaratkan audit kritis.

Abstract juga telah mencakup:

* masalah;
* metode;
* baseline;
* budget;
* hasil ablation;
* shifted controls;
* kesimpulan utama.

### Kelemahan kritis

**Pertama, abstrak masih mengandung klaim statistik lama.** Abstract menyebut “12/13 Wilcoxon wins per baseline, (p<0.05)”, sedangkan analisis lanjutan Anda menunjukkan bahwa setelah koreksi Holm, keunggulan terhadap beberapa baseline kuat tidak lagi signifikan. Klaim unadjusted tidak boleh tetap dipakai sebagai headline.

**Kedua, “four independent controls” terlalu kuat.** Tiga kontrol dibangun dari suite klasik yang sama dengan variasi shift, sehingga lebih tepat disebut **four distinct controls**, bukan statistically independent controls.

**Ketiga, CEC2017 yang digunakan hanya subset 10 fungsi**, tetapi abstrak membuatnya terdengar seolah seluruh suite CEC2017 digunakan.

**Keempat, abstrak menyimpulkan terlalu luas bahwa semua klaim OBL perlu dicurigai.** Penelitian hanya menguji satu bentuk elite-opposition dalam satu host algorithm dan satu budget utama.

### Solusi

* Ganti klaim kemenangan unadjusted dengan hasil Holm-adjusted.
* Tulis “a 10-function CEC2017 subset”.
* Ganti “four independent controls” menjadi “four complementary controls”.
* Batasi conclusion:

> “for the elite-opposition implementation examined under the tested low-budget conditions.”

* Kurangi abstract dari sekitar 264 kata menjadi 200–230 kata jika panduan jurnal menetapkan maksimal 250 kata.

### Judul alternatif yang lebih kuat

Untuk *Evolutionary Intelligence*:

> **When Does Opposition-Based Learning Actually Help? An Origin-Bias-Controlled Audit under Tight Evaluation Budgets**

Untuk *Journal of Heuristics*:

> **Benchmark Origin Bias in Opposition-Based Heuristics: A Controlled Low-Budget Evaluation**

IFPOA-X tidak harus muncul dalam judul karena kontribusi terkuatnya bukan algoritma tersebut.

---

## B. Introduction

### Kekuatan

Introduction berhasil membangun hubungan antara:

* anggaran evaluasi rendah;
* metaheuristic benchmarking;
* OBL;
* benchmark geometry;
* ancaman terhadap validitas kesimpulan algoritmik.

Research question utama juga jelas dan relevan.

### Kelemahan

Introduction membawa terlalu banyak cerita sekaligus:

1. expensive optimization;
2. surrogate-assisted optimization;
3. ASHA;
4. Bayesian optimization;
5. hybrid algorithm design;
6. OBL;
7. benchmark origin bias.

Padahal surrogate dan ASHA tidak digunakan dalam eksperimen. Akibatnya, introduction menjanjikan paper sample-efficient expensive optimization, tetapi eksperimen sebenarnya adalah **low-NFE synthetic benchmarking**.

Terdapat pula ketidaksesuaian antara research gap dan hasil penelitian. Research gap masih menyatakan bahwa novelty adalah integrasi UCB1, OBL, JADE, surrogate, dan ASHA. Namun:

* surrogate/ASHA tidak diuji;
* UCB1 tidak bermanfaat;
* JADE merugikan;
* kontribusi utama akhirnya adalah origin-bias audit.

### Solusi

Restrukturisasi introduction menjadi empat blok:

1. **Masalah:** klaim superioritas metaheuristik sering bergantung pada benchmark.
2. **Mekanisme yang dicurigai:** OBL menggunakan refleksi terhadap pusat domain.
3. **Gap:** sedikit penelitian yang menguji OBL setelah optimum dipindahkan atau benchmark ditransformasi.
4. **Tujuan dan RQ:** menguji apakah manfaat OBL bertahan di bawah kontrol geometri.

Gunakan research questions eksplisit:

* **RQ1:** Apakah IFPOA-X unggul pada benchmark klasik dalam 500 NFE?
* **RQ2:** Komponen mana yang menyebabkan keunggulan tersebut?
* **RQ3:** Apakah marginal benefit OBL bertahan setelah optimum digeser dan fungsi dirotasi?
* **RQ4:** Seberapa konsisten hasil tersebut pada beberapa konfigurasi shift?

Kurangi pembahasan surrogate/ASHA menjadi maksimal satu paragraf atau hilangkan seluruhnya.

---

## C. Literature Review / Related Work

### Kekuatan

Strukturnya logis dan mencakup FPA, OBL, adaptive operator selection, baseline modern, expensive optimization, serta praktik statistik.

### Kelemahan

Bagian OBL justru terlalu tipis untuk paper yang kontribusi utamanya mengkritik OBL. Hanya sedikit pembahasan mengenai:

* jenis-jenis opposition;
* quasi-opposition;
* generalized opposition;
* dynamic opposition;
* elite opposition;
* kelemahan empiris OBL;
* invariance terhadap translasi;
* benchmark central symmetry;
* transformed benchmark instances.

Referensi terbaru juga terbatas. Untuk submission 2026, literatur 2022–2026 mengenai OBL, benchmark transformation, dan critical metaheuristic evaluation perlu ditambahkan.

**Provenance note mengenai Scite harus dihapus.** Editor tidak perlu diberi tahu bahwa referensi diverifikasi melalui Scite. Bahkan keputusan untuk tidak mengutip paper seminal hanya karena tidak memiliki DOI tidak tepat. Paper asli TPE dan Demšar tetap harus dikutip meskipun tidak memiliki DOI.

Research gap juga masih salah fokus pada “belum ada algoritma yang menggabungkan empat komponen”, padahal dua komponen tidak membantu dan dua lainnya tidak diuji.

### Solusi

Buat tabel related work seperti berikut:

| Study | Host algorithm | OBL type | Centred benchmark | Shifted/rotated test | Tight NFE | Ablation |
| ----- | -------------- | -------- | ----------------- | -------------------- | --------- | -------- |

Kemudian tunjukkan bahwa gap sebenarnya adalah:

> Existing OBL studies commonly report gains on unshifted suites but rarely isolate the interaction between opposition operators and benchmark-centre geometry.

Ini jauh lebih defensible daripada klaim “belum ada yang menggabungkan UCB1 + JADE + ASHA + OBL”.

---

## D. Methodology

Ini merupakan bagian yang memerlukan revisi terbesar.

### 1. Identitas algoritma belum sepenuhnya jelas

Operator global IFPOA-X ditulis sebagai:

[
u_{\text{child}}=u_{\text{parent}}+c_tL,
]

sementara global pollination pada FPA asli biasanya melibatkan arah terhadap solusi terbaik. Dengan formulasi sekarang, reviewer dapat mempertanyakan apakah algoritma ini masih layak disebut FPA atau hanya random Lévy search dengan komponen tambahan.

**Solusi:** tampilkan terlebih dahulu persamaan FPA asli, kemudian tuliskan secara eksplisit bagian mana yang dipertahankan, dihapus, dan dimodifikasi.

---

### 2. Formulasi single-objective tercampur dengan multi-objective

Paper menggunakan istilah:

* Pareto front;
* crowding distance;
* hypervolume;
* fidelity rung;
* cohort;
* multi-objective archive;

padahal seluruh eksperimen paper bersifat single-objective.

Hal ini menambah kompleksitas tanpa memperkuat hasil. Pernyataan bahwa hypervolume “reduces to an ordinary improvement signal” belum cukup; tuliskan persamaan scalar reward yang benar-benar digunakan.

**Solusi:** buat implementasi metode yang khusus untuk paper ini:

* scalar best-so-far;
* scalar archive;
* scalar reward;
* tanpa Pareto front;
* tanpa crowding distance;
* tanpa fidelity rung;
* tanpa ASHA.

Versi multi-objective dapat disebut satu kalimat sebagai implementasi terpisah di repository.

---

### 3. Mekanisme OBL dijelaskan secara matematis kurang tepat

Paper menyatakan OBL efektif karena refleksi “mengarah ke pusat domain tempat optimum berada”. Secara matematis, refleksi:

[
x^{o}=a+b-x
]

**tidak memindahkan kandidat lebih dekat ke pusat**. Jarak kandidat dan opposite terhadap pusat adalah sama.

Pada fungsi simetris seperti Sphere dengan batas simetris:

[
f(x)=f(-x).
]

Artinya, opposite dari elite memiliki fitness yang sama dengan elite. Karena algoritma kemudian menggunakan opposite tersebut untuk mengganti anggota terburuk, manfaat yang diamati mungkin bukan karena “menemukan titik lebih dekat ke optimum”, melainkan karena **fitness-preserving elite replication**.

Ini merupakan isu konseptual paling penting dalam paper.

### Solusi

Ubah penjelasan menjadi:

> On centrally symmetric landscapes, opposition can preserve the quality of an elite solution at its reflected location, enabling rapid replacement of inferior population members.

Tambahkan dua kontrol:

1. **Elite-clone replacement:** mengganti worst individual dengan duplikat elite menggunakan jadwal yang sama.
2. **Random-reflection control:** transformasi dengan biaya evaluasi dan replacement pressure yang sama tetapi tanpa exact opposition.

Dengan demikian, Anda dapat membedakan:

* manfaat genuine opposition;
* manfaat elite replication;
* manfaat replacement pressure.

---

### 4. Atribusi kausal kepada OBL belum langsung

Ablation menunjukkan OBL penting pada suite klasik. Separately, full IFPOA-X jatuh pada shifted suite. Namun belum ada eksperimen yang secara langsung menguji interaksi:

[
\text{OBL on/off} \times \text{centred/shifted geometry}.
]

Karena itu, kesimpulan bahwa OBL menyebabkan collapse masih kuat secara indikatif, tetapi belum kausal.

### Solusi paling penting

Jalankan minimal:

| Geometry | Full | No OBL |
| -------- | ---: | -----: |
| Centred  |    ✓ |      ✓ |
| Shifted  |    ✓ |      ✓ |

Lebih baik lagi jalankan full, no-OBL, no-JADE, dan base pada seluruh kontrol. Laporkan **difference-in-differences** atau perubahan marginal benefit OBL:

[
\Delta_{\text{OBL, centred}}-\Delta_{\text{OBL, shifted}}.
]

Eksperimen ini akan menjadi bukti terkuat paper.

---

### 5. Full IFPOA-X dikalahkan oleh ablation-nya sendiri

Removing JADE meningkatkan hasil pada 11 dari 13 fungsi. Artinya, algoritma yang diusulkan bukan konfigurasi terbaiknya sendiri.

Jika paper tetap dipasarkan sebagai “proposed IFPOA-X algorithm”, reviewer dapat menyimpulkan bahwa desain algoritmanya gagal.

### Solusi

Pilih salah satu framing:

* **Framing metodologis:** IFPOA-X hanyalah experimental vehicle, bukan algoritma yang direkomendasikan.
* **Framing algoritmik:** buat simplified variant tanpa JADE, tetapi semua eksperimen utama harus diulang.

Untuk mempercepat submission, framing metodologis jauh lebih aman.

---

### 6. Fairness equal-NFE belum sepenuhnya aman

Beberapa potensi confound serius:

* IFPOA-X menggunakan Latin Hypercube Sampling, sedangkan baseline kemungkinan menggunakan random initialization.
* Cache hit IFPOA-X tidak dihitung sebagai NFE; belum jelas apakah cache yang sama diberikan kepada baseline.
* Boundary handling dapat berbeda antarimplementasi.
* Baseline memakai default `mealpy`, sedangkan IFPOA-X memiliki banyak parameter khusus.
* F7 mengandung noise; belum dijelaskan apakah noise RNG dipisahkan dari algorithm RNG.
* TPE bukan population-based, sehingga pernyataan “population size 24 for every algorithm” tidak tepat.

Pada budget 500 NFE, perbedaan initialization dan boundary repair dapat sangat memengaruhi ranking.

### Solusi

* Gunakan initial population yang identik untuk seluruh population-based baseline.
* Terapkan cache yang identik kepada semua algoritma atau hitung semua objective calls tanpa pengecualian.
* Standarkan boundary repair.
* Laporkan versi Python, Mealpy, Optuna, dan Opfunu.
* Pisahkan RNG fungsi noisy dari RNG algoritma.
* Jelaskan bahwa `n_ei_candidates=24` pada TPE bukan population size.
* Tambahkan sensitivity check untuk DE/L-SHADE atau hapus klaim bahwa default configuration otomatis adil.

---

### 7. Rumus shift pada naskah berpotensi salah

Manuskrip menulis:

[
g(x)=f(x-o), \qquad g(x^*)=f(0)=0.
]

Formulasi tersebut hanya benar apabila native optimum fungsi memang berada di nol. Rosenbrock, misalnya, memiliki native optimum pada vektor satu.

Formulasi umum seharusnya:

[
g(x)=f(x-o+x_0),
]

dengan (x_0) sebagai native optimum dan (o) sebagai target optimum baru.

Walaupun kode Anda mungkin telah memverifikasi pergeseran, **persamaan yang ditampilkan dalam manuskrip masih harus diperbaiki**. Saat dirender, persamaan ini juga muncul sebagai LaTeX mentah dengan backslash.

Tambahkan tabel:

| Function | Native optimum (x_0) | Target optimum (o) | Transformation | Verified error |
| -------- | -------------------: | -----------------: | -------------- | -------------: |

---

### 8. F8 tidak sebaiknya dikeluarkan secara post hoc

F8 dikeluarkan dari mixed-shift control setelah ditemukan nilai fitness negatif akibat konstruksi shift. Transparansi ini baik, tetapi solusi ilmiah terbaik bukan mempertahankan eksklusi—melainkan memperbaiki shift agar valid dan menjalankan ulang F8.

Eksklusi setelah melihat hasil dapat menimbulkan pertanyaan mengenai post-hoc exclusion.

---

## E. Experimental Setup dan Statistik

### Masalah utama: statistik baru belum terintegrasi

Section 4.5 masih hanya menjelaskan:

* Wilcoxon;
* Friedman;
* Nemenyi;
* Cohen’s (d).

Namun bagian CEC kemudian menggunakan:

* Iman–Davenport;
* Kendall’s (W);
* Holm correction.

Analisis lanjutan yang Anda sebutkan—Finner, Vargha–Delaney (A_{12}), bootstrap CI—belum terlihat konsisten di manuskrip.

Section 5.2 masih menyatakan semua baseline dikalahkan dengan (p<0.05), padahal hasil Holm yang Anda laporkan sebelumnya menunjukkan beberapa perbandingan tidak signifikan.

Ini adalah **inkonsistensi fatal** bila tidak diperbaiki.

### Solusi

Tuliskan satu statistical analysis plan yang berlaku untuk semua suite:

1. Friedman test;
2. Iman–Davenport correction;
3. Kendall’s (W);
4. post-hoc Holm dengan IFPOA-X sebagai control;
5. Finner sebagai sensitivity result jika diperlukan;
6. Vargha–Delaney (A_{12}) atau Cliff’s delta;
7. bootstrap confidence intervals;
8. adjusted (p)-values.

Hindari Cohen’s (d) sebagai effect size utama karena hasil metaheuristik biasanya skewed dan heavy-tailed.

### Unit analisis harus diperjelas

Bedakan:

* pengujian 20 stochastic runs dalam satu fungsi;
* pengujian lintas fungsi;
* ranking lintas benchmark suite.

Jangan mencampurkan “12/13 function wins” dengan bukti bahwa algoritma secara global signifikan.

---

## F. Results & Discussion

### Kekuatan

Section 5.7 adalah bagian terbaik manuskrip. Sintesis empat kondisi dan penurunan ranking yang konsisten memberikan narasi yang jelas dan menarik. 

Pembahasan keterbatasan juga relatif jujur, termasuk:

* untuned baselines;
* budget hanya 500 NFE;
* audit D=50 belum dilakukan;
* surrogate/ASHA tidak diuji;
* masalah F8. 

### Kelemahan

Beberapa narasi masih bertentangan dengan hasil:

* “adaptive operator selection helps escape local optima” bertentangan dengan bandit yang tidak bermanfaat;
* “advantage is preserved as dimensionality grows” hanya terbukti pada suite klasik, bukan shifted controls;
* “TPE needs more evaluations” bersifat spekulatif;
* explanation bahwa JADE gagal karena warm-up belum diuji;
* claim bahwa WOA/GWO menang karena tidak bergantung pada origin belum cukup—bisa juga dipengaruhi boundary handling atau initialization.

CEC2017 hanya menampilkan win/loss/tie dan CD diagram. Reviewer memerlukan:

* daftar fungsi yang digunakan;
* error (f(x)-f^*);
* median dan IQR;
* mean ranks;
* adjusted p-values;
* alasan pemilihan subset.

### Penyajian visual

Beberapa grafik terlalu kecil untuk dibaca:

* convergence grid 13 fungsi;
* CD diagram;
* label pada figure 9;
* tabel numerik padat.

Pindahkan seluruh convergence grids dan full numeric tables ke supplementary material. Main manuscript cukup menampilkan:

* rank summary;
* interaction plot;
* satu atau dua representative convergence curves;
* adjusted statistical table.

Jangan menuliskan path lokal seperti:

`results/analysis_D30/summary.md`

di artikel jurnal.

---

## G. Conclusion & Future Work

### Kekuatan

Conclusion menjawab pertanyaan penelitian dan menyampaikan implikasi untuk reviewer serta peneliti metaheuristik. Komitmen untuk tidak menyembunyikan hasil negatif sangat baik.

### Kelemahan

Ada sentence fragment:

> “Because OBL improves search by reflecting candidates through the domain centre, where the classical optima cluster, and this is precisely the kind of advantage that could be a benchmark artifact.”

Kalimat ini tidak memiliki main clause.

Beberapa klaim juga terlalu universal:

> “geometry can manufacture a performance advantage for any such method, independent of genuine search quality.”

Data Anda belum membuktikan “any method”. Paper hanya menguji satu host algorithm dan satu elite-opposition implementation.

Pernyataan bahwa IFPOA-X “remains genuinely effective only on origin-centred landscapes” juga tidak dibuktikan. Penelitian hanya menunjukkan bahwa bukti keunggulannya tidak bertahan pada kontrol yang diuji.

### Solusi

Gunakan formulasi lebih presisi:

> “The evidence shows that the apparent superiority of the examined elite-opposition implementation is strongly conditional on benchmark-centre geometry under the tested 500-NFE regime.”

Repository `[TODO: link]` wajib diselesaikan sebelum submit. 

---

# 3. Evaluasi Metode Adaptif dan Algoritma

| Komponen           | Penilaian                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| UCB1               | Formulasi dasar masuk akal, tetapi reward bersifat nonstationary dan manfaat empiris tidak terdeteksi                          |
| JADE local search  | Formulasi recognizable, tetapi full algorithm dirugikan oleh komponen ini                                                      |
| OBL                | Merupakan komponen dominan, tetapi mekanisme manfaatnya kemungkinan bercampur dengan elite replication                         |
| Step adaptation    | Perlu definisi acceptance dan penjelasan apakah benar merupakan one-fifth rule atau hanya heuristik terinspirasi rule tersebut |
| Hypervolume reward | Tidak logis dipertahankan dalam paper single-objective tanpa definisi scalar reduction yang eksplisit                          |
| Cache              | Berpotensi merusak fairness bila hanya diberikan kepada IFPOA-X                                                                |
| Algorithm 1        | Belum menunjukkan pengecekan sisa NFE sebelum OBL dan child evaluation; berpotensi overshoot                                   |
| Complexity         | Klaim overhead “negligible” belum didukung runtime measurement pada eksperimen ini                                             |

Tambahkan kondisi sebelum setiap evaluasi:

```text
if remaining_NFE == 0:
    break
```

Jelaskan pula bagaimana (N_a=0) pada UCB1 ditangani sebelum indeks pertama dihitung.

---

# 4. Bahasa, Format, dan Konsistensi

## Masalah yang harus diperbaiki

* Hapus baris **Target venue**.
* Hapus seluruh **Provenance note**.
* Isi repository URL.
* Hapus local file paths.
* Ganti `20 run` menjadi `20 runs`.
* Ganti `α=0,05` menjadi `α=0.05`.
* Konsisten antara British English dan American English:

  * centre/center;
  * behaviour/behavior;
  * favour/favor;
  * minimised/minimized.
* Ubah seluruh rumus LaTeX mentah menjadi Word Equation atau LaTeX template jurnal.
* Rapikan Algorithm 1; saat ini Input/Output dan pseudocode terlalu padat.
* Jangan menyebut Opfunu sebagai “official CEC implementation”; tulis bahwa Opfunu menyediakan implementation of CEC2017 definitions.
* Hindari penggunaan bold berlebihan dalam body text.
* Kurangi penggunaan dash panjang dan kalimat 50–80 kata.
* Pastikan semua caption dapat berdiri sendiri dan menjelaskan NFE, dimension, runs, dan statistic.
* Tambahkan data availability dan code availability statement formal.

---

# 5. Actionable Checklist

| Prioritas    | Masalah                               | Tindakan konkret                                                                                                       |
| ------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **High 1**   | Klaim statistik tidak konsisten       | Integrasikan Iman–Davenport, Holm, Kendall’s (W), (A_{12}), dan CI ke Sections 4.5, 5.1, 5.2, Abstract, dan Conclusion |
| **High 2**   | Atribusi OBL belum kausal             | Jalankan experiment `OBL on/off × centred/shifted`; tampilkan interaction effect                                       |
| **High 3**   | Mekanisme OBL salah dijelaskan        | Ganti narasi “reflection moves toward centre” dengan central-symmetry/elite-replication explanation                    |
| **High 4**   | Potential elite-replication confound  | Tambahkan elite-clone dan random-reflection controls                                                                   |
| **High 5**   | Shift equation salah di manuskrip     | Gunakan (g(x)=f(x-o+x_0)); tambahkan native-optimum verification table                                                 |
| **High 6**   | Fairness initialization/cache         | Gunakan initial populations, cache policy, boundary repair, dan objective budget accounting yang sama                  |
| **High 7**   | Proposed algorithm kalah dari no-JADE | Ubah framing menjadi methodological audit; jangan menjual full IFPOA-X sebagai optimizer terbaik                       |
| **High 8**   | F8 dikeluarkan                        | Perbaiki domain-safe shift dan rerun F8                                                                                |
| **High 9**   | Research gap salah fokus              | Ganti gap integrasi komponen menjadi gap origin-bias-controlled evaluation                                             |
| **High 10**  | Repository belum ada                  | Publikasikan kode, raw results, seed, environment lock, dan commands sebelum submit                                    |
| **Medium 1** | CEC subset tidak transparan           | Sebutkan 10 fungsi, selection rule, optimum bias removal, dan raw results                                              |
| **Medium 2** | Untuned baseline                      | Tambahkan sensitivity configuration minimal untuk DE/L-SHADE atau batasi klaim                                         |
| **Medium 3** | Noisy F7                              | Gunakan independent objective RNG dan common noise sequence                                                            |
| **Medium 4** | Literatur kurang mutakhir             | Tambahkan studi OBL dan benchmark-validity 2022–2026                                                                   |
| **Medium 5** | Main paper terlalu padat              | Pindahkan full tables dan convergence grids ke supplement                                                              |
| **Medium 6** | Sample efficiency overclaim           | Gunakan istilah “low-NFE performance”, kecuali ada expensive real-world application                                    |
| **Low 1**    | Format angka                          | Gunakan titik desimal dan scientific notation konsisten                                                                |
| **Low 2**    | Bahasa                                | Pecah kalimat panjang dan hilangkan repetisi                                                                           |
| **Low 3**    | Caption/figure readability            | Perbesar font, garis, dan legend                                                                                       |
| **Low 4**    | Reference formatting                  | Gunakan style jurnal dan final publication year, bukan “2016/2018”                                                     |

## Rekomendasi akhir

Paper ini mempunyai **ide publikasi yang kuat**, tetapi manuskrip harus diposisikan sebagai:

> **a methodological audit of opposition-based heuristic evaluation**

bukan sebagai:

> **a new superior hybrid Flower Pollination Algorithm**.

Untuk **Evolutionary Intelligence**, peluangnya cukup baik setelah statistik, fairness, dan framing diperbaiki. Untuk **Journal of Heuristics**, eksperimen interaksi OBL × geometry serta kontrol elite-replication hampir wajib agar kontribusinya benar-benar dianggap general methodological insight. Dalam bentuk sekarang keputusan saya adalah **Major Revision**, tetapi setelah seluruh high-priority issues diselesaikan, manuskrip dapat berkembang menjadi paper yang kompetitif dan substantif.
