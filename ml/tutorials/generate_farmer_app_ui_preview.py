"""
Generate a High-Fidelity Mobile App UI Preview for SIDS
Demonstrates what the Farmer ACTUALLY sees on the phone screen
(Not messy raw backend bounding boxes, but a professional mobile UX).
"""

import cv2
import numpy as np
from pathlib import Path


def generate_mobile_app_mockup():
    # Mobile screen dimensions (Width: 600, Height: 1100)
    w, h = 600, 1100
    screen = np.full((h, w, 3), 24, dtype=np.uint8)  # Modern dark mode chassis

    # 1. Camera Viewport (Top 65% of screen)
    cam_h = 720
    # Simulate a realistic green crop leaf with texture and veins
    leaf_canvas = np.zeros((cam_h, w, 3), dtype=np.uint8)
    
    # Leaf background gradient (Deep agricultural green)
    for y in range(cam_h):
        grad = int(35 + 25 * (y / cam_h))
        leaf_canvas[y, :] = (25, grad, 20)

    # Big natural leaf shape
    cv2.ellipse(leaf_canvas, (300, 360), (280, 320), 15, 0, 360, (35, 115, 30), -1)
    
    # Leaf secondary gradient highlights
    cv2.ellipse(leaf_canvas, (300, 360), (240, 280), 15, 0, 360, (40, 130, 35), -1)

    # Primary and secondary leaf veins
    cv2.line(leaf_canvas, (60, 150), (520, 600), (55, 155, 48), 5)
    cv2.line(leaf_canvas, (240, 320), (120, 480), (50, 145, 42), 2)
    cv2.line(leaf_canvas, (350, 430), (480, 320), (50, 145, 42), 2)
    cv2.line(leaf_canvas, (180, 260), (300, 160), (50, 145, 42), 2)

    # Add realistic cluster of aphids (small translucent golden-green bodies)
    np.random.seed(101)
    cluster_pts = []
    for _ in range(45):
        cx = int(np.random.normal(320, 35))
        cy = int(np.random.normal(390, 45))
        if 100 < cx < 500 and 150 < cy < 650:
            cluster_pts.append((cx, cy))
            # Insect body
            cv2.ellipse(leaf_canvas, (cx, cy), (6, 4), np.random.randint(0, 180), 0, 360, (40, 220, 240), -1)
            # Insect tiny legs/antennae
            cv2.circle(leaf_canvas, (cx, cy), 1, (10, 80, 80), -1)

    # Modern UX: Translucent Glow over the detected colony area (Not raw ugly boxes!)
    overlay = leaf_canvas.copy()
    colony_hull = cv2.convexHull(np.array(cluster_pts))
    cv2.drawContours(overlay, [colony_hull], -1, (0, 220, 255), -1)
    # Alpha blend glow
    cv2.addWeighted(overlay, 0.18, leaf_canvas, 0.82, 0, leaf_canvas)
    # Smooth neon border around the colony
    cv2.drawContours(leaf_canvas, [colony_hull], -1, (0, 230, 255), 2, cv2.LINE_AA)

    # Modern Focus Pin targeting the colony center
    pin_x, pin_y = 320, 340
    cv2.circle(leaf_canvas, (pin_x, pin_y), 24, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.circle(leaf_canvas, (pin_x, pin_y), 6, (0, 220, 255), -1, cv2.LINE_AA)
    cv2.line(leaf_canvas, (pin_x - 30, pin_y), (pin_x - 12, pin_y), (255, 255, 255), 1)
    cv2.line(leaf_canvas, (pin_x + 12, pin_y), (pin_x + 30, pin_y), (255, 255, 255), 1)
    cv2.line(leaf_canvas, (pin_x, pin_y - 30), (pin_x, pin_y - 12), (255, 255, 255), 1)
    cv2.line(leaf_canvas, (pin_x, pin_y + 12), (pin_x, pin_y + 30), (255, 255, 255), 1)

    # Copy camera viewport to screen
    screen[0:cam_h, 0:w] = leaf_canvas

    # Top App Bar (Modern Header)
    cv2.rectangle(screen, (0, 0), (w, 70), (18, 18, 18), -1)
    cv2.putText(screen, "SIDS AI Scout - Live Field Analysis", (24, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    # Status Pill (Offline-Ready)
    cv2.rectangle(screen, (w - 140, 24), (w - 20, 52), (35, 70, 35), -1)
    cv2.putText(screen, "OFFLINE AI", (w - 128, 43), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 255, 120), 1, cv2.LINE_AA)

    # 2. Bottom Sheet: Farmer-Friendly Diagnostic Card (Modern UI Glassmorphism)
    card_y = 660
    cv2.rectangle(screen, (16, card_y), (w - 16, h - 30), (32, 35, 38), -1)
    cv2.rectangle(screen, (16, card_y), (w - 16, h - 30), (60, 65, 75), 2)  # Card border

    # Grab handle on bottom sheet
    cv2.line(screen, (w // 2 - 30, card_y + 14), (w // 2 + 30, card_y + 14), (120, 120, 120), 3)

    # Identification Header
    cv2.putText(screen, "Cotton Aphid (Sabz Teela / Sust)", (36, card_y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(screen, "Scientific: Aphis gossypii | Family: Aphididae", (36, card_y + 82), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 165, 175), 1, cv2.LINE_AA)

    # Status Badges: [97% Confidence] [High Severity Gucha] [Action Required]
    # Badge 1: Confidence
    cv2.rectangle(screen, (36, card_y + 105), (170, card_y + 135), (45, 60, 35), -1)
    cv2.putText(screen, "MATCH: 97.4%", (48, card_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 255, 130), 1, cv2.LINE_AA)

    # Badge 2: Infestation Severity
    cv2.rectangle(screen, (180, card_y + 105), (355, card_y + 135), (60, 30, 25), -1)
    cv2.putText(screen, "SWARM: 18.2% COVERED", (190, card_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 140, 255), 1, cv2.LINE_AA)

    # Badge 3: ETL Trigger
    cv2.rectangle(screen, (365, card_y + 105), (550, card_y + 135), (70, 20, 20), -1)
    cv2.putText(screen, "ETL THRESHOLD BREACH", (375, card_y + 125), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 100, 255), 1, cv2.LINE_AA)

    # Diagnostic Explanation (Human-readable for farmer)
    diag_text1 = "Diagnosis: Sucking pest colony detected on cotton leaf."
    diag_text2 = "Danger: Secretes honeydew leading to sooty mold fungus."
    diag_text3 = "Economic Threshold Level (ETL) breached (>15% leaf area)."
    
    cv2.putText(screen, diag_text1, (36, card_y + 170), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (230, 230, 230), 1, cv2.LINE_AA)
    cv2.putText(screen, diag_text2, (36, card_y + 195), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(screen, diag_text3, (36, card_y + 220), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 180, 255), 1, cv2.LINE_AA)

    # Immediate Action Box
    cv2.rectangle(screen, (36, card_y + 245), (w - 36, card_y + 315), (22, 25, 28), -1)
    cv2.rectangle(screen, (36, card_y + 245), (w - 36, card_y + 315), (75, 45, 30), 1)
    cv2.putText(screen, "Recommended Action (Punjab Agri Advisory):", (48, card_y + 270), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120, 200, 255), 1, cv2.LINE_AA)
    cv2.putText(screen, "Apply Imidacloprid 200SL (60ml/acre) or Acetamiprid 20SP.", (48, card_y + 295), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (240, 240, 240), 1, cv2.LINE_AA)

    # Action Buttons: [View Treatment Details] [Add to Expense Log]
    btn_y = card_y + 335
    # Button 1 (Primary Action)
    cv2.rectangle(screen, (36, btn_y), (310, btn_y + 50), (30, 140, 60), -1)
    cv2.putText(screen, "View Spray Guidelines", (65, btn_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)

    # Button 2 (Secondary Action - Khata / Expense Record)
    cv2.rectangle(screen, (325, btn_y), (w - 36, btn_y + 50), (45, 50, 58), -1)
    cv2.putText(screen, "Add to Khata", (375, btn_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 225, 230), 1, cv2.LINE_AA)

    # Save output preview image
    output_path = Path("ml/tutorials/farmer_mobile_app_view_mockup.png")
    cv2.imwrite(str(output_path), screen)
    print(f"Realistic Farmer Mobile UI Mockup generated at: {output_path}")


if __name__ == "__main__":
    generate_mobile_app_mockup()
