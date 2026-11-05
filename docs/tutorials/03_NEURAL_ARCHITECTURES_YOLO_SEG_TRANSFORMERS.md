# Module 3: Neural Architectures (Classification, Regression, YOLO vs Vision Transformers)
**Author:** SIDS AI Research & Engineering Tutor Team (`tutor_architectures`)  
**Language:** Roman Urdu + Technical English  
**Companion Executable Script:** [`ml/tutorials/03_classification_regression_and_yolo.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/03_classification_regression_and_yolo.py)

---

## 1. Introduction: "Classification, Regression Aur Detection Ka Asli Farq"

Aap ne poochha tha:
> *"phir clasifications regresions or agr transformer ki zarorat ha to kesa krna ha kia krna ha or kis trah sa ho ga"*

Machine Learning mein visual tasks ko 3 bunyadi mathematical categories mein baanta jata hai:

```text
+--------------------------------------------------------------------------+
| 1. Image Classification                                                  |
|    Input: Pura Patta                                                     |
|    Output: Ek Class Label (e.g., "Rice Leaf Roller", Probability: 95%)   |
|    Math: Softmax + Categorical Cross-Entropy Loss                        |
+--------------------------------------------------------------------------+
| 2. Bounding Box Regression                                               |
|    Input: Keere ki location                                              |
|    Output: 4 Continuous Floating Numbers [x_center, y_center, w, h]      |
|    Math: Smooth L1 / Complete IoU (CIoU) Loss                            |
+--------------------------------------------------------------------------+
| 3. Object Detection (YOLO / DETR)                                        |
|    Detection = Classification Head + Regression Head (Dono ka Milap!)    |
+--------------------------------------------------------------------------+
| 4. Instance Segmentation (YOLO-Seg)                                      |
|    Output: Keere ki Body ka Pixel Mask + Category + Bounding Box         |
+--------------------------------------------------------------------------+
```

---

## 2. Classification Head Math: Softmax & Cross-Entropy

Classification head ka maqsad hota hai un-normalized numbers (jinhein **Logits** $z$ kehte hain) ko valid **Probabilities** ($0.0$ se $1.0$, jinka sum $1.0$ ho) mein convert karna:

### The Softmax Equation:
Agar model ke paas $K$ classes hain (maslan: 1=Leaf Roller, 2=Water Weevil, 3=Healthy Leaf):
$$P(y = k \mid x) = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}}$$

### The Categorical Cross-Entropy Loss:
Model jab ghalat prediction karta hai, to loss usay mathematically punish karta hai:
$$\mathcal{L}_{\text{cls}} = -\sum_{k=1}^{K} y_k \log(p_k)$$
* Agar Asli Label $y = 1$ hai aur model ne $p_1 = 0.99$ predict kiya: $\mathcal{L} = -\log(0.99) \approx 0.01$ (Bohot chota loss - Shabash!).
* Agar Asli Label $y = 1$ hai aur model ne $p_1 = 0.05$ predict kiya: $\mathcal{L} = -\log(0.05) \approx 3.00$ (Bara loss - Model ko foran weights update karne parenge!).

---

## 3. Regression Head Math: IoU & CIoU Loss

Bounding box coordinates continuous numbers hotay hain. Purane models Mean Squared Error ($MSE$) use karte thay, lekin $MSE$ box ke aspect ratio aur overlap ko nahi samajhta.

Modern models **Complete IoU (CIoU) Loss** use karte hain:
$$\mathcal{L}_{\text{CIoU}} = 1 - \text{IoU} + \frac{\rho^2(b, b^{\text{gt}})}{c^2} + \alpha v$$

1. $\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}}$: Dono boxes kitna aapas mein juday hain.
2. $\frac{\rho^2(b, b^{\text{gt}})}{c^2}$: Predicted box ke center aur Asli box ke center ka faasla (Euclidean distance $\rho$), divided by the enclosing diagonal $c$.
3. $\alpha v$: Aspect ratio (lamba vs chora) ka farq:
   $$v = \frac{4}{\pi^2} \left(\arctan\frac{w^{\text{gt}}}{h^{\text{gt}}} - \arctan\frac{w}{h}\right)^2$$

---

## 4. YOLO Architecture Internals (YOLOv8 / YOLO11)

YOLO ka kamal yeh hai ke yeh **"Single-Stage"** detector hai — yeh photo ko ek hi jhatke mein forward pass kar ke saare keeray dhoond leta hai:

```
+-------------------------------------------------------------------------+
|                              INPUT IMAGE                                |
|                           [ 384 x 384 x 3 ]                             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| BACKBONE (C3k2 / Darknet Feature Extractor)                             |
| * Layer 1-4: Low-level edges, colors, leaf textures                     |
| * Layer 5-8: Mid-level insect legs, antennae, wings                     |
| * Layer 9-12: High-level semantic context ("Insect sitting on Cotton")  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| NECK (PANet: Path Aggregation Feature Pyramid Network)                  |
| * P3 (Scale 1: Small bugs - 48x48 grid)                                 |
| * P4 (Scale 2: Medium bugs - 24x24 grid)                                |
| * P5 (Scale 3: Large bugs / entire leaves - 12x12 grid)                 |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| DECOUPLED DETECTION HEADS                                               |
| * Head A (Classification): Insect Class (Rice Weevil, Jassid, etc.)    |
| * Head B (Regression): Box coordinates [x, y, w, h]                     |
| * Head C (Proto-Seg): 32 Prototype Masks for body segmentation          |
+-------------------------------------------------------------------------+
```

---

## 5. Vision Transformers (ViT) & RT-DETR: Kisaan ke Phone ke liye Kaunsa Behtar Hai?

Aap ne poochha: *"transformer ki zarorat ha to kesa krna ha?"*

### A. Vision Transformer (ViT) Kaise Kaam Karta Hai?
Transformer pehle Natural Language (text) ke liye bana tha. Computer vision mein ViT image ko text ke "Words" ki tarah todta hai:
1. Ek $384 \times 384$ image ko $16 \times 16$ ke chote tukron (Patches) mein kaata jata hai:
   $$\text{Total Patches} = \left(\frac{384}{16}\right) \times \left(\frac{384}{16}\right) = 24 \times 24 = 576 \text{ Patches!}$$
2. Har patch ko ek 1D vector ($D=768$) mein project kiya jata hai.
3. **Self-Attention Mechanism:** Har patch doosre har patch ke sath dosti (relationship) calculate karta hai:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$

### B. The Crucial Verdict for SIDS & Farmers:
| Property | CNN / YOLO (MobileNet / YOLO11-Nano) | Vision Transformer (ViT-Base / Swin) |
| :--- | :--- | :--- |
| **Model Size** | **6 MB – 12 MB** (Halka!) | **350 MB – 1.2 GB** (Bohot bhari!) |
| **Mobile RAM Usage**| **< 45 MB** (2GB RAM phone par chalta hai) | **600 MB – 1.5 GB** (Budget phone crash karega) |
| **Inference Latency**| **30 ms – 50 ms** (Palk jhapaktay hi) | **400 ms – 1500 ms** (Kisaan intezar karega) |
| **Dataset Requirement**| **Kam data par train ho jata hai** (Inductive Bias) | **Lakhon images chahiye** (Overfitting ka khatra) |

**Nateeja:** Mobile phone par kisaan ke offline use ke liye **YOLO11-Nano ya MobileNetV4** sab se behtareen hai! Transformer (jaise Qwen-VL) ko hum sirf **Cloud par Teacher / Distillation** ke liye use karte hain!

Script [`ml/tutorials/03_classification_regression_and_yolo.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/03_classification_regression_and_yolo.py) mein humne Classification Head, CIoU Regression Head, aur Self-Attention Block ka practical PyTorch code implement kiya hai!
