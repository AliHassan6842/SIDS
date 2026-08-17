import json
import os

import torch
from tqdm import tqdm

from .metrics import compute_metrics


class Trainer:
    def __init__(self, model, train_loader, val_loader, optimizer, criterion, device,
                 save_dir='checkpoints', early_stopping_patience=5):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.save_dir = save_dir
        self.early_stopping_patience = early_stopping_patience
        
        self.best_val_loss = float('inf')
        self.epochs_no_improve = 0
        
        os.makedirs(self.save_dir, exist_ok=True)
        
    def train_epoch(self, epoch):
        self.model.train()
        total_loss = 0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch} [Train]")
        for images, labels in pbar:
            images, labels = images.to(self.device), labels.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({'loss': loss.item()})
            
        avg_loss = total_loss / len(self.train_loader)
        metrics = compute_metrics(all_labels, all_preds)
        metrics['loss'] = avg_loss
        return metrics
        
    def validate(self, epoch):
        self.model.eval()
        total_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc=f"Epoch {epoch} [Val]")
            for images, labels in pbar:
                images, labels = images.to(self.device), labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                
        avg_loss = total_loss / len(self.val_loader)
        metrics = compute_metrics(all_labels, all_preds)
        metrics['loss'] = avg_loss
        return metrics
        
    def fit(self, num_epochs):
        history = {'train': [], 'val': []}
        
        for epoch in range(1, num_epochs + 1):
            train_metrics = self.train_epoch(epoch)
            val_metrics = self.validate(epoch)
            
            history['train'].append(train_metrics)
            history['val'].append(val_metrics)
            
            print(f"Epoch {epoch} - Train Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.4f}")
            print(f"Epoch {epoch} - Val Loss: {val_metrics['loss']:.4f}, Acc: {val_metrics['accuracy']:.4f}, F1: {val_metrics['macro_f1']:.4f}")
            
            # Checkpointing and Early Stopping
            if val_metrics['loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['loss']
                self.epochs_no_improve = 0
                self.save_checkpoint('best_model.pth', epoch, val_metrics)
                print(f"Saved new best model with Val Loss: {val_metrics['loss']:.4f}")
            else:
                self.epochs_no_improve += 1
                print(f"Early stopping counter: {self.epochs_no_improve}/{self.early_stopping_patience}")
                
            if self.epochs_no_improve >= self.early_stopping_patience:
                print("Early stopping triggered!")
                break
                
        # Save history
        with open(os.path.join(self.save_dir, 'history.json'), 'w') as f:
            json.dump(history, f, indent=4)
            
    def save_checkpoint(self, filename, epoch, metrics):
        path = os.path.join(self.save_dir, filename)
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics
        }, path)
