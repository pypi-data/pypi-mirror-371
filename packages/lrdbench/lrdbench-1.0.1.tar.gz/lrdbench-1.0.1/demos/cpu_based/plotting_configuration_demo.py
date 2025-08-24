"""
Global Plotting Configuration Demo

This script demonstrates the global plotting configuration system that ensures
consistent visualization across all models and estimators in the project.

Features:
1. Centralized plotting configuration
2. Consistent styling across all plots
3. Customizable themes and color schemes
4. Export-ready plot formatting
5. Interactive plotting options
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import sys
import os
from dataclasses import dataclass
from enum import Enum

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PlotTheme(Enum):
    """Available plotting themes."""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    SCIENTIFIC = "scientific"
    PRESENTATION = "presentation"

@dataclass
class PlotConfig:
    """Global plotting configuration."""
    
    # Theme settings
    theme: PlotTheme = PlotTheme.DEFAULT
    
    # Figure settings
    default_figsize: Tuple[int, int] = (12, 8)
    dpi: int = 300
    
    # Style settings
    style: str = "seaborn-v0_8"
    palette: str = "husl"
    
    # Font settings
    font_family: str = "serif"
    font_size: int = 12
    title_font_size: int = 14
    label_font_size: int = 11
    
    # Color settings
    primary_color: str = "#2E86AB"
    secondary_color: str = "#A23B72"
    accent_color: str = "#F18F01"
    background_color: str = "#FFFFFF"
    
    # Line settings
    line_width: float = 1.5
    line_alpha: float = 0.8
    grid_alpha: float = 0.3
    
    # Export settings
    save_format: str = "png"
    save_dpi: int = 300
    save_bbox_inches: str = "tight"
    
    # Interactive settings
    interactive: bool = False

class GlobalPlottingConfig:
    """Global plotting configuration manager."""
    
    def __init__(self, config: Optional[PlotConfig] = None):
        """
        Initialize the global plotting configuration.
        
        Parameters
        ----------
        config : PlotConfig, optional
            Custom configuration. If None, uses default configuration.
        """
        self.config = config or PlotConfig()
        self._setup_plotting_style()
    
    def _setup_plotting_style(self) -> None:
        """Set up the global plotting style based on configuration."""
        # Set matplotlib style
        plt.style.use(self.config.style)
        
        # Set seaborn palette
        sns.set_palette(self.config.palette)
        
        # Configure matplotlib rcParams
        plt.rcParams.update({
            'font.family': self.config.font_family,
            'font.size': self.config.font_size,
            'axes.titlesize': self.config.title_font_size,
            'axes.labelsize': self.config.label_font_size,
            'figure.dpi': self.config.dpi,
            'savefig.dpi': self.config.save_dpi,
            'savefig.format': self.config.save_format,
        })
        
        # Set interactive mode if requested
        if self.config.interactive:
            plt.ion()
    
    def apply_theme(self, theme: PlotTheme) -> None:
        """
        Apply a specific theme to the plotting configuration.
        
        Parameters
        ----------
        theme : PlotTheme
            Theme to apply
        """
        self.config.theme = theme
        
        if theme == PlotTheme.DARK:
            plt.style.use('dark_background')
            self.config.background_color = "#1E1E1E"
            self.config.primary_color = "#4FC3F7"
            self.config.secondary_color = "#FF8A80"
            self.config.accent_color = "#FFD54F"
            
        elif theme == PlotTheme.LIGHT:
            plt.style.use('default')
            self.config.background_color = "#FFFFFF"
            self.config.primary_color = "#2196F3"
            self.config.secondary_color = "#F44336"
            self.config.accent_color = "#FF9800"
            
        elif theme == PlotTheme.SCIENTIFIC:
            plt.style.use('seaborn-v0_8-paper')
            self.config.font_family = "serif"
            self.config.font_size = 10
            self.config.title_font_size = 12
            self.config.label_font_size = 10
            
        elif theme == PlotTheme.PRESENTATION:
            plt.style.use('seaborn-v0_8-talk')
            self.config.font_size = 14
            self.config.title_font_size = 16
            self.config.label_font_size = 12
            self.config.line_width = 2.0
        
        self._setup_plotting_style()
    
    def create_figure(self, figsize: Optional[Tuple[int, int]] = None, 
                     **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a figure with consistent styling.
        
        Parameters
        ----------
        figsize : tuple, optional
            Figure size. If None, uses default from config.
        **kwargs : dict
            Additional arguments for plt.subplots()
            
        Returns
        -------
        tuple
            (figure, axes) tuple
        """
        if figsize is None:
            figsize = self.config.default_figsize
            
        fig, ax = plt.subplots(figsize=figsize, **kwargs)
        
        # Apply consistent styling
        ax.set_facecolor(self.config.background_color)
        ax.grid(True, alpha=self.config.grid_alpha)
        
        return fig, ax
    
    def style_axes(self, ax: plt.Axes, title: str = "", 
                  xlabel: str = "", ylabel: str = "") -> None:
        """
        Apply consistent styling to axes.
        
        Parameters
        ----------
        ax : plt.Axes
            Axes to style
        title : str
            Plot title
        xlabel : str
            X-axis label
        ylabel : str
            Y-axis label
        """
        if title:
            ax.set_title(title, fontsize=self.config.title_font_size, 
                        fontweight='bold', color=self.config.primary_color)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.config.label_font_size)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=self.config.label_font_size)
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_color(self.config.primary_color)
            spine.set_linewidth(0.8)
    
    def save_plot(self, filename: str, fig: Optional[plt.Figure] = None) -> None:
        """
        Save a plot with consistent settings.
        
        Parameters
        ----------
        filename : str
            Output filename
        fig : plt.Figure, optional
            Figure to save. If None, saves current figure.
        """
        if fig is None:
            fig = plt.gcf()
        
        # Ensure results/plots directory exists
        os.makedirs('results/plots', exist_ok=True)
        
        filepath = os.path.join('results/plots', filename)
        fig.savefig(filepath, dpi=self.config.save_dpi, 
                   bbox_inches='tight')
        print(f"Plot saved to: {filepath}")

class PlottingConfigurationDemo:
    """Demonstration of the global plotting configuration system."""
    
    def __init__(self):
        """Initialize the plotting configuration demo."""
        self.plot_config = GlobalPlottingConfig()
        self.demo_data = self._generate_demo_data()
    
    def _generate_demo_data(self) -> Dict[str, np.ndarray]:
        """Generate demo data for plotting."""
        np.random.seed(42)
        
        # Generate sample time series
        t = np.linspace(0, 10, 1000)
        
        # Different types of data
        data = {
            'sine_wave': np.sin(2 * np.pi * t) + 0.1 * np.random.randn(1000),
            'random_walk': np.cumsum(np.random.randn(1000) * 0.1),
            'exponential': np.exp(-t/3) + 0.05 * np.random.randn(1000),
            'polynomial': 0.1 * t**2 - t + 5 + 0.2 * np.random.randn(1000)
        }
        
        return data
    
    def demo_basic_plotting(self) -> None:
        """Demonstrate basic plotting with global configuration."""
        print("="*60)
        print("BASIC PLOTTING DEMO")
        print("="*60)
        
        # Create figure with global config
        fig, ax = self.plot_config.create_figure()
        
        # Plot all data types
        colors = [self.plot_config.config.primary_color,
                 self.plot_config.config.secondary_color,
                 self.plot_config.config.accent_color,
                 '#4CAF50']  # Green
        
        for i, (name, data) in enumerate(self.demo_data.items()):
            ax.plot(data, label=name, color=colors[i], 
                   linewidth=self.plot_config.config.line_width,
                   alpha=self.plot_config.config.line_alpha)
        
        # Style the plot
        self.plot_config.style_axes(ax, 
                                   title="Basic Plotting Demo",
                                   xlabel="Time",
                                   ylabel="Value")
        
        ax.legend(fontsize=self.plot_config.config.label_font_size)
        plt.tight_layout()
        plt.show()
        
        # Save the plot
        self.plot_config.save_plot("basic_plotting_demo.png", fig)
    
    def demo_theme_comparison(self) -> None:
        """Demonstrate different themes."""
        print("\n" + "="*60)
        print("THEME COMPARISON DEMO")
        print("="*60)
        
        themes = [PlotTheme.DEFAULT, PlotTheme.DARK, PlotTheme.SCIENTIFIC, PlotTheme.PRESENTATION]
        theme_names = ["Default", "Dark", "Scientific", "Presentation"]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, (theme, theme_name) in enumerate(zip(themes, theme_names)):
            # Apply theme
            self.plot_config.apply_theme(theme)
            
            ax = axes[i]
            
            # Plot data
            ax.plot(self.demo_data['sine_wave'], 
                   color=self.plot_config.config.primary_color,
                   linewidth=self.plot_config.config.line_width,
                   alpha=self.plot_config.config.line_alpha)
            
            # Style axes
            self.plot_config.style_axes(ax, 
                                       title=f"{theme_name} Theme",
                                       xlabel="Time",
                                       ylabel="Value")
        
        plt.tight_layout()
        plt.show()
        
        # Reset to default theme
        self.plot_config.apply_theme(PlotTheme.DEFAULT)
        
        # Save the plot
        self.plot_config.save_plot("theme_comparison_demo.png", fig)
    
    def demo_subplot_layout(self) -> None:
        """Demonstrate subplot layout with consistent styling."""
        print("\n" + "="*60)
        print("SUBPLOT LAYOUT DEMO")
        print("="*60)
        
        # Create subplot layout
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot different data types in each subplot
        data_items = list(self.demo_data.items())
        
        for i, (name, data) in enumerate(data_items):
            row, col = i // 2, i % 2
            ax = axes[row, col]
            
            # Plot data
            ax.plot(data, color=self.plot_config.config.primary_color,
                   linewidth=self.plot_config.config.line_width,
                   alpha=self.plot_config.config.line_alpha)
            
            # Style axes
            self.plot_config.style_axes(ax, 
                                       title=f"{name.replace('_', ' ').title()}",
                                       xlabel="Time",
                                       ylabel="Value")
        
        plt.tight_layout()
        plt.show()
        
        # Save the plot
        self.plot_config.save_plot("subplot_layout_demo.png", fig)
    
    def demo_statistical_plots(self) -> None:
        """Demonstrate statistical plots with consistent styling."""
        print("\n" + "="*60)
        print("STATISTICAL PLOTS DEMO")
        print("="*60)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Histogram
        ax1 = axes[0, 0]
        ax1.hist(self.demo_data['random_walk'], bins=30, alpha=0.7,
                color=self.plot_config.config.primary_color)
        self.plot_config.style_axes(ax1, 
                                   title="Histogram",
                                   xlabel="Value",
                                   ylabel="Frequency")
        
        # Box plot
        ax2 = axes[0, 1]
        data_for_box = [self.demo_data['sine_wave'], 
                       self.demo_data['random_walk'],
                       self.demo_data['exponential']]
        ax2.boxplot(data_for_box, labels=['Sine', 'Random Walk', 'Exponential'])
        self.plot_config.style_axes(ax2, 
                                   title="Box Plot",
                                   xlabel="Data Type",
                                   ylabel="Value")
        
        # Scatter plot
        ax3 = axes[1, 0]
        ax3.scatter(self.demo_data['sine_wave'][::10], 
                   self.demo_data['random_walk'][::10],
                   alpha=0.6, color=self.plot_config.config.secondary_color)
        self.plot_config.style_axes(ax3, 
                                   title="Scatter Plot",
                                   xlabel="Sine Wave",
                                   ylabel="Random Walk")
        
        # Correlation matrix
        ax4 = axes[1, 1]
        data_matrix = np.column_stack(list(self.demo_data.values()))
        corr_matrix = np.corrcoef(data_matrix.T)
        im = ax4.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
        ax4.set_xticks(range(len(self.demo_data)))
        ax4.set_yticks(range(len(self.demo_data)))
        ax4.set_xticklabels(list(self.demo_data.keys()), rotation=45)
        ax4.set_yticklabels(list(self.demo_data.keys()))
        plt.colorbar(im, ax=ax4)
        self.plot_config.style_axes(ax4, 
                                   title="Correlation Matrix")
        
        plt.tight_layout()
        plt.show()
        
        # Save the plot
        self.plot_config.save_plot("statistical_plots_demo.png", fig)
    
    def demo_export_formats(self) -> None:
        """Demonstrate different export formats."""
        print("\n" + "="*60)
        print("EXPORT FORMATS DEMO")
        print("="*60)
        
        # Create a simple plot
        fig, ax = self.plot_config.create_figure()
        ax.plot(self.demo_data['sine_wave'], 
               color=self.plot_config.config.primary_color,
               linewidth=self.plot_config.config.line_width)
        self.plot_config.style_axes(ax, 
                                   title="Export Demo",
                                   xlabel="Time",
                                   ylabel="Value")
        
        # Save in different formats
        formats = ['png', 'pdf', 'svg', 'jpg']
        
        for fmt in formats:
            # Temporarily change save format
            original_format = self.plot_config.config.save_format
            self.plot_config.config.save_format = fmt
            
            filename = f"export_demo.{fmt}"
            self.plot_config.save_plot(filename, fig)
            
            # Restore original format
            self.plot_config.config.save_format = original_format
        
        plt.show()
    
    def run_full_demo(self) -> None:
        """Run the complete plotting configuration demonstration."""
        print("="*60)
        print("GLOBAL PLOTTING CONFIGURATION DEMO")
        print("="*60)
        
        # Run all demos
        self.demo_basic_plotting()
        self.demo_theme_comparison()
        self.demo_subplot_layout()
        self.demo_statistical_plots()
        self.demo_export_formats()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nAll plots have been saved to the 'results/plots' directory.")


def main():
    """Main function to run the plotting configuration demo."""
    # Create demo instance
    demo = PlottingConfigurationDemo()
    
    # Run the full demonstration
    demo.run_full_demo()


if __name__ == "__main__":
    main()
