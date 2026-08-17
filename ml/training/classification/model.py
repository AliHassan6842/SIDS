import timm


def create_model(model_name='tf_efficientnetv2_s', num_classes=10, pretrained=True):
    """
    Create a model using timm.
    Candidates: 
    - mobilenetv4_conv_small (if available)
    - mobilenetv3_large_100
    - tf_efficientnetv2_s
    """
    try:
        model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)
    except Exception as e:
        print(f"Failed to create model {model_name} due to: {e}. Falling back to mobilenetv3_large_100")
        model = timm.create_model('mobilenetv3_large_100', pretrained=pretrained, num_classes=num_classes)
        
    return model
