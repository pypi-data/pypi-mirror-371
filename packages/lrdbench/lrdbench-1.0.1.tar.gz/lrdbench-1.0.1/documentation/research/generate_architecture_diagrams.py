#!/usr/bin/env python3
"""
Generate Architecture Diagrams for Fractional PINO Research Paper
Creates visual representations of the neural operator architecture and components.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
import matplotlib.patches as mpatches

# Set style for publication-quality figures
plt.style.use('default')
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['lines.linewidth'] = 2

def create_fractional_pino_architecture():
    """Create the main Fractional PINO architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'Fractional PINO Architecture', fontsize=16, fontweight='bold', 
            ha='center', va='center')
    
    # Input Layer
    input_box = FancyBboxPatch((0.5, 6.5), 2, 0.8, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.5, 6.9, 'Input Time Series', ha='center', va='center', fontweight='bold')
    
    # Spectral Convolution Layer
    spectral_box = FancyBboxPatch((3.5, 6.5), 3, 0.8, boxstyle="round,pad=0.1", 
                                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
    ax.add_patch(spectral_box)
    ax.text(5, 6.9, 'Spectral Convolution (FNO)', ha='center', va='center', fontweight='bold')
    
    # Multi-Scale Processing
    multiscale_box = FancyBboxPatch((0.5, 5), 2, 0.8, boxstyle="round,pad=0.1", 
                                    facecolor='lightcoral', edgecolor='darkred', linewidth=2)
    ax.add_patch(multiscale_box)
    ax.text(1.5, 5.4, 'Multi-Scale\nProcessing', ha='center', va='center', fontweight='bold')
    
    # Attention Mechanism
    attention_box = FancyBboxPatch((3.5, 5), 3, 0.8, boxstyle="round,pad=0.1", 
                                   facecolor='gold', edgecolor='orange', linewidth=2)
    ax.add_patch(attention_box)
    ax.text(5, 5.4, 'Multi-Head\nAttention', ha='center', va='center', fontweight='bold')
    
    # Physics Constraints
    physics_box = FancyBboxPatch((7, 5), 2.5, 0.8, boxstyle="round,pad=0.1", 
                                 facecolor='lightyellow', edgecolor='goldenrod', linewidth=2)
    ax.add_patch(physics_box)
    ax.text(8.25, 5.4, 'Physics\nConstraints', ha='center', va='center', fontweight='bold')
    
    # Feature Fusion
    fusion_box = FancyBboxPatch((3.5, 3.5), 3, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='plum', edgecolor='purple', linewidth=2)
    ax.add_patch(fusion_box)
    ax.text(5, 3.9, 'Feature Fusion', ha='center', va='center', fontweight='bold')
    
    # Output Projection
    output_box = FancyBboxPatch((3.5, 2), 3, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='lightsteelblue', edgecolor='steelblue', linewidth=2)
    ax.add_patch(output_box)
    ax.text(5, 2.4, 'Output Projection', ha='center', va='center', fontweight='bold')
    
    # Hurst Estimation
    hurst_box = FancyBboxPatch((3.5, 0.5), 3, 0.8, boxstyle="round,pad=0.1", 
                               facecolor='lightpink', edgecolor='crimson', linewidth=2)
    ax.add_patch(hurst_box)
    ax.text(5, 0.9, 'Hurst Exponent', ha='center', va='center', fontweight='bold')
    
    # Arrows
    arrows = [
        ((2.5, 6.9), (3.5, 6.9)),  # Input to Spectral
        ((5, 6.5), (5, 5.8)),      # Spectral to Multi-scale
        ((5, 6.5), (5, 5.8)),      # Spectral to Attention
        ((2.5, 5.4), (3.5, 3.9)),  # Multi-scale to Fusion
        ((6.5, 5.4), (6.5, 3.9)),  # Attention to Fusion
        ((8.25, 5), (6.5, 3.9)),   # Physics to Fusion
        ((5, 3.5), (5, 2.8)),      # Fusion to Output
        ((5, 2), (5, 1.3))         # Output to Hurst
    ]
    
    for start, end in arrows:
        arrow = FancyArrowPatch(start, end, arrowstyle='->', lw=2, color='black')
        ax.add_patch(arrow)
    
    # Add labels for key components
    ax.text(1.5, 4.5, 'Kernel Sizes:\n[3, 5, 7, 11]', ha='center', va='center', 
            fontsize=8, style='italic')
    ax.text(8.25, 4.5, 'Fractional\nDerivatives\nMellin Transform', ha='center', va='center', 
            fontsize=8, style='italic')
    
    plt.tight_layout()
    plt.savefig('fractional_pino_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_multi_scale_processing():
    """Create diagram showing multi-scale feature extraction."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(5, 5.5, 'Multi-Scale Feature Extraction with Attention', fontsize=14, fontweight='bold', 
            ha='center', va='center')
    
    # Input features
    input_box = FancyBboxPatch((0.5, 4.5), 2, 0.6, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.5, 4.8, 'Input Features', ha='center', va='center', fontweight='bold')
    
    # Multi-scale layers
    scales = [3, 5, 7, 11]
    colors = ['lightcoral', 'lightgreen', 'gold', 'plum']
    y_pos = 3.5
    
    for i, (scale, color) in enumerate(zip(scales, colors)):
        x_pos = 0.5 + i * 2.2
        box = FancyBboxPatch((x_pos, y_pos), 1.8, 0.6, boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x_pos + 0.9, y_pos + 0.3, f'Kernel {scale}', ha='center', va='center', fontweight='bold')
        
        # Arrow from input
        arrow = FancyArrowPatch((1.5, 4.5), (x_pos + 0.9, y_pos + 0.6), arrowstyle='->', lw=1.5)
        ax.add_patch(arrow)
    
    # Attention mechanism
    attention_box = FancyBboxPatch((3.5, 2), 3, 0.8, boxstyle="round,pad=0.1", 
                                   facecolor='gold', edgecolor='orange', linewidth=2)
    ax.add_patch(attention_box)
    ax.text(5, 2.4, 'Multi-Head\nAttention', ha='center', va='center', fontweight='bold')
    
    # Arrows to attention
    for i in range(4):
        x_pos = 0.5 + i * 2.2 + 0.9
        arrow = FancyArrowPatch((x_pos, y_pos), (3.5, 2.4), arrowstyle='->', lw=1.5)
        ax.add_patch(arrow)
    
    # Output fusion
    output_box = FancyBboxPatch((7.5, 2), 2, 0.8, boxstyle="round,pad=0.1", 
                                facecolor='lightsteelblue', edgecolor='steelblue', linewidth=2)
    ax.add_patch(output_box)
    ax.text(8.5, 2.4, 'Feature\nFusion', ha='center', va='center', fontweight='bold')
    
    # Arrow to output
    arrow = FancyArrowPatch((6.5, 2.4), (7.5, 2.4), arrowstyle='->', lw=2)
    ax.add_patch(arrow)
    
    # Add attention details
    ax.text(5, 1.2, '4 Attention Heads\nScale Combination', ha='center', va='center', 
            fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.savefig('multi_scale_processing.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_physics_constraint_framework():
    """Create diagram showing the physics-informed constraint framework."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(5, 5.5, 'Physics-Informed Constraint Framework', fontsize=14, fontweight='bold', 
            ha='center', va='center')
    
    # Input data
    input_box = FancyBboxPatch((0.5, 4.5), 2, 0.6, boxstyle="round,pad=0.1", 
                               facecolor='lightblue', edgecolor='navy', linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.5, 4.8, 'Input Data\n(t, y, hurst)', ha='center', va='center', fontweight='bold')
    
    # Constraint types
    constraints = [
        ('Fractional\nDerivatives', 'lightcoral', 3.5, 4.5),
        ('Mellin\nTransform', 'lightgreen', 5.5, 4.5),
        ('Scale\nInvariance', 'gold', 7.5, 4.5)
    ]
    
    for name, color, x, y in constraints:
        box = FancyBboxPatch((x, y), 1.8, 0.6, boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + 0.9, y + 0.3, name, ha='center', va='center', fontweight='bold')
        
        # Arrow from input
        arrow = FancyArrowPatch((2.5, 4.8), (x + 0.9, y + 0.6), arrowstyle='->', lw=1.5)
        ax.add_patch(arrow)
    
    # Constraint computation
    constraint_box = FancyBboxPatch((3.5, 2.5), 3, 0.8, boxstyle="round,pad=0.1", 
                                    facecolor='plum', edgecolor='purple', linewidth=2)
    ax.add_patch(constraint_box)
    ax.text(5, 2.9, 'Constraint\nComputation', ha='center', va='center', fontweight='bold')
    
    # Arrows to constraint computation
    for x, y in [(4.4, 4.5), (6.4, 4.5), (8.4, 4.5)]:
        arrow = FancyArrowPatch((x, y), (4.4, 3.3), arrowstyle='->', lw=1.5)
        ax.add_patch(arrow)
    
    # Loss function
    loss_box = FancyBboxPatch((3.5, 1), 3, 0.8, boxstyle="round,pad=0.1", 
                              facecolor='lightsteelblue', edgecolor='steelblue', linewidth=2)
    ax.add_patch(loss_box)
    ax.text(5, 1.4, 'Multi-Objective\nLoss Function', ha='center', va='center', fontweight='bold')
    
    # Arrow to loss
    arrow = FancyArrowPatch((5, 2.5), (5, 1.8), arrowstyle='->', lw=2)
    ax.add_patch(arrow)
    
    # Loss components
    ax.text(5, 0.3, 'Data + Physics + Operator + Hurst Loss', ha='center', va='center', 
            fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.savefig('physics_constraint_framework.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_training_pipeline():
    """Create diagram showing the training pipeline."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(6, 5.5, 'Fractional PINO Training Pipeline', fontsize=14, fontweight='bold', 
            ha='center', va='center')
    
    # Training steps
    steps = [
        ('Forward Pass\n(Physics Constraints)', 'lightblue', 1, 4),
        ('Loss\nComputation', 'lightcoral', 3.5, 4),
        ('Backward\nPass', 'lightgreen', 6, 4),
        ('Parameter\nUpdate', 'gold', 8.5, 4),
        ('Validation\nMetrics', 'plum', 11, 4)
    ]
    
    for name, color, x, y in steps:
        box = FancyBboxPatch((x, y), 2.2, 0.8, boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + 1.1, y + 0.4, name, ha='center', va='center', fontweight='bold', fontsize=9)
    
    # Arrows between steps
    for i in range(4):
        start_x = 1 + i * 2.5 + 1.1
        end_x = 1 + (i + 1) * 2.5
        arrow = FancyArrowPatch((start_x, 4.4), (end_x, 4.4), arrowstyle='->', lw=2)
        ax.add_patch(arrow)
    
    # Loss components
    loss_components = [
        ('Data Loss\n(MSE)', 'lightsteelblue', 2.25, 2.5),
        ('Physics Loss\n(Constraints)', 'lightyellow', 5.75, 2.5),
        ('Operator Loss\n(Learning)', 'lightpink', 9.25, 2.5)
    ]
    
    for name, color, x, y in loss_components:
        box = FancyBboxPatch((x, y), 1.8, 0.6, boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + 0.9, y + 0.3, name, ha='center', va='center', fontweight='bold', fontsize=8)
        
        # Arrow to loss computation
        arrow = FancyArrowPatch((x + 0.9, y + 0.6), (4.6, 4), arrowstyle='->', lw=1.5)
        ax.add_patch(arrow)
    
    # Training loop indicator
    loop_arrow = FancyArrowPatch((11, 3.6), (1, 3.6), arrowstyle='->', lw=2, color='red')
    ax.add_patch(loop_arrow)
    ax.text(6, 3.2, 'Training Loop', ha='center', va='center', fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('training_pipeline.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Generating Fractional PINO architecture diagrams...")
    
    # Generate all diagrams
    create_fractional_pino_architecture()
    create_multi_scale_processing()
    create_physics_constraint_framework()
    create_training_pipeline()
    
    print("All diagrams generated successfully!")
    print("Files created:")
    print("- fractional_pino_architecture.png")
    print("- multi_scale_processing.png")
    print("- physics_constraint_framework.png")
    print("- training_pipeline.png")
