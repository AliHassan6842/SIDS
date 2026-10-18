from sids_ai.knowledge.thresholds import get_economic_threshold, list_economic_thresholds
from sids_ai.knowledge.pesticides import get_pesticide_registry

def test_load_real_json_thresholds():
    # punjab_thresholds.json has mango-hopper for mango
    threshold = get_economic_threshold("mango-hopper", "mango")
    assert threshold is not None
    assert threshold.pest_id == "mango-hopper"
    assert threshold.crop_id == "mango"
    assert threshold.threshold_value == 5.0
    
    thresholds = list_economic_thresholds("tomato")
    assert len(thresholds) >= 1
    assert any(t.pest_id == "tomato-fruit-borer" for t in thresholds)

def test_load_real_json_pesticides():
    # dpp_pesticides.json has tomato-fruit-borer for tomato (Coragen 20 SC)
    pesticides = get_pesticide_registry("tomato-fruit-borer", "tomato")
    assert len(pesticides) >= 1
    assert any("Coragen" in p.product_name for p in pesticides)
    
    pesticides = get_pesticide_registry("mango-hopper", "mango")
    assert len(pesticides) >= 1
    assert any("Confidor" in p.product_name for p in pesticides)
