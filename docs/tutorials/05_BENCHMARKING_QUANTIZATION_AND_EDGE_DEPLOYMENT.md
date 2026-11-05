# Module 5: Benchmarking, Metrics, Calibration & Low-RAM Edge Optimization
**Author:** SIDS AI Research & Engineering Tutor Team (`tutor_optimization_edge`)  
**Language:** Roman Urdu + Technical English  
**Companion Executable Script:** [`ml/tutorials/05_benchmark_calibration_and_quantization.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/05_benchmark_calibration_and_quantization.py)

---

## 1. Introduction: "Model Kamyab Hua Ya Nakam? Benchmarking Aur Mobile Optimization"

Aap ne do bohot ahem aur practical sawalat kiye thay:
1. *"train or live dono pr bench mark kesa check krna ha"*
2. *"us ko ak chota devices yani kam ram pr chlna zarori ha... memory usage ko kesa smbhalen ga"*

Dunya ka behtareen model bhi agar 2GB RAM walay mobile par crash ho jaye ya live khet mein anjaan cheezon ko keera declare kar de, to woh bilkul bekaar hai.

Is module mein hum seekhein ge:
1. **Detection Metrics:** IoU, Precision, Recall, aur **mAP@0.5:0.95**.
2. **Open-Set / Out-of-Distribution (OOD) Calibration:** Anjaan cheezon ko `UNKNOWN` declare karne ka mathematical tareeqa.
3. **Quantization Math (FP32 se INT8):** Model ka size aur RAM $4\times$ kam karne ka tareeqa.
4. **Edge Profiling:** Mobile device ke liye RAM ($<45\text{ MB}$) aur Latency ($<50\text{ ms}$) measure karna.

---

## 2. Detection Metrics Deep Dive

### A. Intersection over Union (IoU)
Jab model ek bounding box predict karta hai, to hum dekhte hain ke woh asli box ke kitna ooper charha hai:
$$\text{IoU} = \frac{\text{Area}(B_{\text{pred}} \cap B_{\text{gt}})}{\text{Area}(B_{\text{pred}} \cup B_{\text{gt}})}$$

* Agar $\text{IoU} \ge 0.50$: Is prediction ko **True Positive ($TP$)** maana jata hai (Prediction sahi hai).
* Agar $\text{IoU} < 0.50$: Is prediction ko **False Positive ($FP$)** maana jata hai (Nishana ghalat hai).

### B. Precision vs Recall (Kisaan Ki Nazar Mein):
* **Precision (Sadaqat):**
  $$\text{Precision} = \frac{TP}{TP + FP}$$
  *Kisaan ke liye matlab:* Agar app ne bola ke "Yeh Whitefly hai", to kya sach mein Whitefly thi? Agar Precision kharab ho gi, to kisaan bekaar mein spray khareed le ga!
* **Recall (Shumooliyat):**
  $$\text{Recall} = \frac{TP}{TP + FN}$$
  *Kisaan ke liye matlab:* Khet ke patte par agar 10 keeray baithe thay, to model ne un mein se kitne dhoond nikale? Agar Recall kharab ho gi, to keera khet kha jayega aur app ko pata bhi nahi chale ga!

### C. Mean Average Precision (mAP@0.5 & mAP50-95):
Different confidence thresholds par Precision-Recall Curve banti hai.
1. **$AP$ (Average Precision):** PR-Curve ke neeche ka area (Area Under Curve - AUC).
2. **$\text{mAP@0.5}$:** Saari classes ka average AP jab $\text{IoU} = 0.50$ ho.
3. **$\text{mAP@0.5:0.95}$:** $\text{IoU}$ ko $0.50$ se $0.95$ tak $0.05$ ke steps mein change kar ke 10 dafa average nikala jata hai. Yeh industry ka sab se sakht aur authentic benchmark hai!

---

## 3. Open-Set / Out-of-Distribution (OOD) Calibration

Kisaan ke khet mein haath, joota, bail, mitti, aur 100 qisam ki ghaas phoos samne aayegi. Aam software kya karta hai? Woh bail ya jootay ko bhi 40% confidence ke sath "Rice Weevil" keh deta hai!

### The Solution: Confidence Calibration & Fail-Closed Gating:
$$S(x) = \max_{k \in \text{Classes}} P(y = k \mid x)$$

Decision Rule:
$$\text{Output} = \begin{cases} 
\text{IDENTIFIED}(k) & \text{agar } S(x) \ge \theta_{\text{accept}} \text{ (e.g. } 0.66\text{)} \\
\text{UNKNOWN} & \text{agar } \theta_{\text{low}} \le S(x) < \theta_{\text{accept}} \\
\text{NO\_DETECTION} & \text{agar } S(x) < \theta_{\text{low}} \text{ (e.g. } 0.25\text{)}
\end{cases}$$

Is se model jhoot nahi bolta. Agar koi anjaan cheez samne aayi, to model sach bol kar `UNKNOWN` keh deta hai!

---

## 4. INT8 Quantization: 4x Memory Reduction Math

Aam tor par neural network ke weights **32-bit Floating Point (FP32)** mein hote hain ($4\text{ Bytes}$ fi number).
Agar ek model mein 10 Million numbers hain:
$$\text{RAM Required} = 10,000,000 \times 4\text{ Bytes} \approx 40\text{ MB}$$

Agar hum isay **8-bit Integer (INT8)** mein convert kar dein ($1\text{ Byte}$ fi number):
$$\text{RAM Required} = 10,000,000 \times 1\text{ Byte} \approx 10\text{ MB} \quad (4\times \text{ Bachat!})$$

### The Affine Quantization Formula:
Continuous float value $r$ ko 8-bit integer $q \in [-128, 127]$ mein map kiya jata hai:
$$q = \text{round}\left(\frac{r}{S}\right) + Z$$
* $S$ (Scale Factor): Float range ko integer range par scale karta hai.
* $Z$ (Zero-Point Integer): Float zero ($0.0$) ko integer ke kis number par map karna hai.

Mobile phone ka processor (ARM Cortex CPU) integer arithmetic ko floating point se **3x se 5x tezi se execute karta hai**, aur battery bhi 70% kam kharch hoti hai!

---

## 5. Mobile Edge Latency & RAM Profiling

Script [`ml/tutorials/05_benchmark_calibration_and_quantization.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/05_benchmark_calibration_and_quantization.py) mein humne:
1. Exact IoU calculation engine implement kiya hai.
2. Precision, Recall, aur mAP benchmark compute kiya hai.
3. Anjaan OOD samples par Fail-Closed Rejection demonstrate kiya hai.
4. PyTorch model ko dynamic INT8 quantize kar ke memory aur execution speed profile ki hai!
