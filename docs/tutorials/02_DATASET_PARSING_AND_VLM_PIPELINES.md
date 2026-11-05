# Module 2: Dataset Engineering, JSON Schemas, PyTorch DataLoaders & VLM Auto-Labeling
**Author:** SIDS AI Research & Engineering Tutor Team (`tutor_dataset_pipeline`)  
**Language:** Roman Urdu + Technical English  
**Companion Executable Script:** [`ml/tutorials/02_dataset_json_and_dataloader.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/02_dataset_json_and_dataloader.py)

---

## 1. Introduction: "Khaam (Raw) Data Se Trained Model Tak Ka Safar"

Aap ne poochha tha:
> *"data ko parse kesa krna ha image form ma data kesa lana ha... json kesa bnana ha model ka lia"*

ML engineering mein 80% waqt model architecture par nahi, balkay **Data Pipeline Engineering** par lagta hai. Agar aap ka data loader inefficient ho, to aap ka 12-core CPU ya powerful GPU 90% waqt farigh (idle) betha rahega aur data aane ka intezar karega (I/O Bottleneck).

Is module mein hum seekhein ge:
1. Classification vs Detection Dataset Structures.
2. COCO JSON Schema aur YOLO text files ka difference.
3. PyTorch `Dataset` aur `DataLoader` ka internal mechanics.
4. Detection mein variable number of insects ke liye **Custom Collate Function** kyun zaroori hota hai.
5. Large Vision-Language Models (VLM) se **Zero-Shot Auto-Labeling** kar ke JSON dataset generate karne ka tareeqa.

---

## 2. Dataset Formats: ImageNet vs COCO vs YOLO

```
+-------------------------------------------------------------------------+
| Format 1: ImageNet (Sirf Classification ke liye)                       |
|   dataset/                                                              |
|   ├── train/                                                            |
|   │   ├── rice_water_weevil/ -> [img1.jpg, img2.jpg, ...]               |
|   │   └── healthy_leaf/      -> [img10.jpg, img11.jpg, ...]             |
|   (Masla: Ek photo mein sirf ek class ho sakti hai, box nahi hota)      |
+-------------------------------------------------------------------------+
| Format 2: YOLO Detection Format (Individual .txt per image)             |
|   dataset/                                                              |
|   ├── images/train/ -> [field_001.jpg, field_002.jpg]                   |
|   └── labels/train/ -> [field_001.txt, field_002.txt]                   |
|   * field_001.txt contents:                                             |
|     0 0.512 0.480 0.150 0.220  <-- (class_id, x_center, y_center, w, h)|
|     1 0.810 0.230 0.080 0.090  <-- (second insect in same photo)        |
+-------------------------------------------------------------------------+
| Format 3: Microsoft COCO JSON (Universal Industry Standard)             |
|   dataset/                                                              |
|   ├── images/                                                           |
|   └── annotations/instances_train.json                                  |
|   * Ek single master JSON file mein saare images, categories aur        |
|     bounding boxes/polygons link hotay hain!                            |
+-------------------------------------------------------------------------+
```

---

## 3. Microsoft COCO JSON Structure Deep Dive

Jab hum modern dataset banatay hain, to hum Microsoft COCO standard JSON generate karte hain:

```json
{
  "info": {
    "description": "SIDS Agricultural Pest Dataset",
    "version": "1.0",
    "year": 2026
  },
  "categories": [
    { "id": 1, "name": "rice-leaf-roller", "supercategory": "pest" },
    { "id": 2, "name": "ladybird-beetle", "supercategory": "beneficial" }
  ],
  "images": [
    {
      "id": 101,
      "file_name": "crop_capture_001.jpg",
      "width": 1920,
      "height": 1080
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 101,
      "category_id": 1,
      "bbox": [540.0, 320.0, 180.0, 240.0],
      "area": 43200.0,
      "iscrowd": 0
    }
  ]
}
```

* `image_id`: Yeh link karta hai ke yeh bounding box kis photo ke andar hai.
* `category_id`: Yeh link karta hai ke yeh keera kaunsa hai (Pest ya Dost).
* `bbox`: `[xmin, ymin, width, height]` in absolute pixels.

---

## 4. PyTorch Dataset & The Variable-Length Collate Problem

Aam tor par PyTorch mein jab aap batch banatay hain (e.g. `batch_size = 4`), to PyTorch saare tensors ko stack kar deta hai:
$$\text{Images Batch Tensor Shape: } [B, C, H, W] = [4, 3, 384, 384]$$

Lekin Object Detection mein har tasweer ke andar keeron ki taadad mukhtalif hoti hai:
* Photo 1 mein **3 keeray** hain $\implies$ Boxes shape: $[3, 4]$
* Photo 2 mein **0 keera** hai (healthy leaf) $\implies$ Boxes shape: $[0, 4]$
* Photo 3 mein **7 keeray** hain $\implies$ Boxes shape: $[7, 4]$

Agar aap default PyTorch `DataLoader` chalayein ge, to woh **CRASH** ho jayega! Kyunke woh $[3, 4]$ aur $[7, 4]$ ko ek single square tensor mein stack nahi kar sakta!

### The Solution: Custom `collate_fn`
Hum ek custom collate function likhte hain jo images ko to stack karta hai, lekin boxes aur labels ko batch index ke sath list ya flat padded tensor mein combine karta hai:

```python
def detection_collate_fn(batch):
    images, targets = zip(*batch)
    stacked_images = torch.stack(images, dim=0) # [B, 3, H, W]
    return stacked_images, targets              # targets rehta hai list of dicts!
```

---

## 5. VLM Zero-Shot Auto-Labeling (Knowledge Extraction Without Humans)

Chunke aap ke paas 50 log nahi hain jo baith kar haath se 10,000 photos par boxes lagayein, hum **Alibaba ke Qwen2.5-VL** ya **DeepSeek-VL** ko ek **Structured Auto-Labeler** ke tor par use karte hain.

### Prompting Strategy for the Teacher VLM:
```text
System: You are an expert agricultural entomologist and computer vision annotator.
User: Analyze this leaf image.
Output strictly valid JSON with this schema:
{
  "substrate": "CROP_LEAF" | "SOIL" | "INDOOR_DOMESTIC",
  "crop_type": "rice" | "cotton" | "wheat" | "unknown",
  "detections": [
    {
      "label": "rice-water-weevil",
      "biological_role": "HARMFUL_PEST" | "BENEFICIAL_PREDATOR",
      "bbox_normalized": [center_x, center_y, width, height],
      "confidence": 0.94
    }
  ]
}
```

Script [`ml/tutorials/02_dataset_json_and_dataloader.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/02_dataset_json_and_dataloader.py) mein humne is VLM auto-labeler ka simulation aur pura JSON parser pipeline implement kiya hai jo live run hota hai!
