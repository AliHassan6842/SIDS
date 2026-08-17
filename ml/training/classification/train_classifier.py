import argparse
import json
import os

import torch
from torch import nn, optim

from .dataset import get_dataloaders
from .model import create_model
from .trainer import Trainer


def parse_args():
    parser = argparse.ArgumentParser(description="Train Disease Classification Model")
    parser.add_argument('--train-dir', type=str, required=True, help="Path to training data directory")
    parser.add_argument('--val-dir', type=str, required=True, help="Path to validation data directory")
    parser.add_argument('--model-name', type=str, default='tf_efficientnetv2_s', help="Model name for timm")
    parser.add_argument('--epochs', type=int, default=30, help="Number of epochs to train")
    parser.add_argument('--batch-size', type=int, default=32, help="Batch size")
    parser.add_argument('--lr', type=float, default=1e-3, help="Learning rate")
    parser.add_argument('--image-size', type=int, default=224, help="Input image size")
    parser.add_argument('--save-dir', type=str, default='checkpoints', help="Directory to save models")
    parser.add_argument('--patience', type=int, default=5, help="Early stopping patience")
    parser.add_argument('--num-workers', type=int, default=4, help="Number of dataloader workers")
    return parser.parse_args()

def main():
    args = parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Dataloaders
    train_loader, val_loader, classes = get_dataloaders(
        train_dir=args.train_dir,
        val_dir=args.val_dir,
        batch_size=args.batch_size,
        image_size=args.image_size,
        num_workers=args.num_workers
    )
    
    print(f"Found {len(classes)} classes: {classes}")
    
    # Save classes mapping
    os.makedirs(args.save_dir, exist_ok=True)
    with open(os.path.join(args.save_dir, 'classes.json'), 'w') as f:
        json.dump(classes, f, indent=4)
        
    # Model
    model = create_model(model_name=args.model_name, num_classes=len(classes))
    
    # Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    # Trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        save_dir=args.save_dir,
        early_stopping_patience=args.patience
    )
    
    # Fit
    trainer.fit(num_epochs=args.epochs)

if __name__ == '__main__':
    main()
