# Module 4: Knowledge Distillation & Model Weight Generation (Teacher-Student Pipeline)
**Author:** SIDS AI Research & Engineering Tutor Team (`tutor_distillation`)  
**Language:** Roman Urdu + Technical English  
**Companion Executable Script:** [`ml/tutorials/04_knowledge_distillation_pipeline.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/04_knowledge_distillation_pipeline.py)

---

## 1. Introduction: "Bade Model Se Chota Model Kaise Banayein?"

Aap ne sab se ahem aur dilchasp sawal poocha tha:
> *"ma kis tareka sa model ko distilled kar skta hu step by step or phir ma kis tareka sa weight bna sakta hu jo ka mujha chea ho ga project ka acording"*

Is process ko Machine Learning ki dunya mein **Knowledge Distillation (Ilm Ka Nichor)** kaha jata hai. Isay 2015 mein Turing Award Winner **Geoffrey Hinton** ne introduce karwaya tha.

### Asal Masla Kya Hai?
* **Bara Model (Teacher):** Maslan `Qwen2.5-VL-7B` ya `BioCLIP`. Is ke paas **7 Arab parameters** hain. Yeh dunya bhar ke keeron ko pehchanta hai, lekin isay chalane ke liye 16 GB ka bara GPU chahiye. Yeh kisaan ke phone par nahi chal sakta.
* **Chota Model (Student):** Maslan `YOLO11-Nano` ya `MobileNetV4`. Is ke paas sirf **3 se 5 Million parameters** hain (halka phulka). Yeh mobile par foran chal sakta hai, lekin agar isay thore se data par direct train karein to yeh ghalatiyan karta hai.

**Distillation Ka Jadoo:**
Hum bade Teacher model ko ustaad banate hain aur chote Student model ko shagird banate hain. Shagird ustaad ki aqal (soft probabilities aur feature representations) ko copy karta hai, aur **sirf 10 MB ka weight file (`.pt`)** ban kar tayyar ho jata hai!

---

## 2. Hard Labels vs Soft Labels ("Dark Knowledge")

Aam training mein hum model ko **Hard Labels** dete hain:
$$\text{Hard Label for Water Weevil: } [0, \quad 1, \quad 0, \quad 0]$$
Computer ko yeh bataya jata hai ke 100% Water Weevil hai, baqi sab 0% hain. Is mein koi extra information nahi hai.

Lekin jab ek bara **Teacher Model** photo dekhta hai, to woh **Soft Probabilities** generate karta hai:
$$\text{Teacher Soft Prediction: } [0.08, \quad 0.85, \quad 0.06, \quad 0.01]$$

Ghaur se dekhein! Is soft output mein **"Dark Knowledge"** chupi hui hai:
1. Model 85% confident hai ke yeh Water Weevil hai.
2. Lekin model yeh bhi keh raha hai ke 8% chance Leaf Roller ka hai aur 6% chance Beetle ka hai, jabke 1% chance Healthy Leaf ka hai.
3. Is ka matlab hai ke **Leaf Roller aur Beetle ki shakal Water Weevil se milti julti hai**, jabke Healthy Leaf bilkul alag hai!
Yeh chupi hui information chote student model ko bohat tezi se seekhne mein madad deti hai!

---

## 3. The Mathematics of Temperature Scaling ($\tau$)

Normal Softmax mein agar ek class bohot dominant ho, to doosri classes ki probabilities bohot choti (e.g. $0.00001$) ho jati hain, jinki dark knowledge nazar nahi aati.

Isay ubhaarne ke liye hum **Temperature Scaling ($\tau$)** use karte hain:
$$q_i = \frac{e^{z_i / \tau}}{\sum_j e^{z_j / \tau}}$$

* Jab $\tau = 1.0$: Standard Sharp Softmax.
* Jab $\tau = 4.0$ ya $5.0$: **Soft Distribution!** Sabhi classes ki chupi hui rishtaydari (relationships) wazeh ho jati hain!

```
Logits: [10.0, 2.0, 0.5]
---------------------------------------------------------------
Temperature τ = 1.0 (Sharp):   [0.9996, 0.0003, 0.0001] (Baqi sab dab gaye!)
Temperature τ = 4.0 (Soft):    [0.8521, 0.1154, 0.0325] (Dark Knowledge Zinda!)
```

---

## 4. The Distillation Loss Formula (Hinton Loss)

Training ke dauran student model ka total loss do hisson ka milap hota hai:

$$\mathcal{L}_{\text{total}} = \alpha \cdot \mathcal{L}_{\text{Student}}^{\text{Hard}} + (1 - \alpha) \cdot \tau^2 \cdot \mathcal{L}_{\text{KD}}^{\text{Soft}}$$

1. **$\mathcal{L}_{\text{Student}}^{\text{Hard}}$ (Ground Truth Loss):** Student ki prediction aur asli label ka Cross-Entropy loss ($\alpha = 0.3$).
2. **$\mathcal{L}_{\text{KD}}^{\text{Soft}}$ (Teacher Knowledge Transfer):** Student ke soft outputs aur Teacher ke soft outputs ke darmiyan **Kullback-Leibler (KL) Divergence Loss**:
   $$\mathcal{L}_{\text{KL}}(P \parallel Q) = \sum_{i} P(i) \log\left(\frac{P(i)}{Q(i)}\right)$$
3. **$\tau^2$ Factor:** Logits ko $\tau$ se divide karne par gradients $\frac{1}{\tau^2}$ kam ho jatay hain, is liye $\tau^2$ se multiply kar ke gradient ka balance barabar rakha jata hai!

---

## 5. Model Weights (`.pt` / `.pth`) Kaise Generate Aur Save Hotay Hain?

Aap ne poochha: *"ma kis tareka sa weight bna sakta hu jo ka mujha chea ho ga project ka acording"*

PyTorch mein ek model ke andar saari aqal uske **Weights aur Biases (Floating-Point Numbers)** mein hoti hai. In sab numbers ke collection ko **`state_dict`** kehte hain.

### Checkpoint Save Karne Ka Tareeqa:
```python
checkpoint = {
    "model_id": "sids-rice-pest-detector",
    "version": "1.0.0",
    "architecture": "YOLO11-Seg-Nano",
    "classes": ["rice-leaf-roller", "rice-water-weevil", "ladybird-beetle"],
    "state_dict": student_model.state_dict(),
    "distilled_from": "Qwen2.5-VL-7B",
    "temperature": 4.0,
    "sha256": calculate_weights_sha256(student_model)
}
torch.save(checkpoint, "models/artifacts/sids-student-distilled.pt")
```

Script [`ml/tutorials/04_knowledge_distillation_pipeline.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/04_knowledge_distillation_pipeline.py) mein humne ek complete Teacher-Student Distillation training loop implement kiya hai jo live weights generate aur save karta hai!
