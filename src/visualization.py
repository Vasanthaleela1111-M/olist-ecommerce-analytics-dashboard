"""
Olist Hackathon Visualization Helper Library
Provides standardized, high-quality, publication-ready plotting utilities with rich aesthetics,
clear titles, annotated values, legible fonts, and zero chart clutter.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set global matplotlib styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# Color palette
PALETTE = {
    'primary': '#1E3A8A',       # Dark Navy / Blue
    'secondary': '#0D9488',     # Teal
    'accent': '#F59E0B',        # Amber / Gold
    'danger': '#DC2626',        # Crimson Red
    'success': '#16A34A',       # Emerald Green
    'purple': '#7C3AED',        # Indigo / Violet
    'gray': '#64748B',          # Slate Gray
    'light_bg': '#F8FAFC',
    'dark_navy': '#0F172A'
}

CHART_COLORS = [PALETTE['primary'], PALETTE['secondary'], PALETTE['accent'], 
                PALETTE['purple'], PALETTE['danger'], PALETTE['success'], PALETTE['gray']]

def set_chart_style(ax, title=None, xlabel=None, ylabel=None, grid=True):
    """Applies standardized formatting to a matplotlib axis."""
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color=PALETTE['dark_navy'])
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, fontweight='semibold', labelpad=10, color='#334155')
    
    ax.tick_params(axis='both', which='major', labelsize=10, colors='#334155')
    if grid:
        ax.grid(True, linestyle='--', alpha=0.5)
    else:
        ax.grid(False)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def annotate_bars(ax, format_str='{:.1f}', is_horizontal=False, fontsize=9, padding=3):
    """Adds value labels to bar charts."""
    for p in ax.patches:
        val = p.get_height() if not is_horizontal else p.get_width()
        if not val or val != val: continue # skip nan or zero
        
        text = format_str.format(val)
        if is_horizontal:
            ax.annotate(text, (p.get_width() + padding, p.get_y() + p.get_height() / 2.),
                        ha='left', va='center', fontsize=fontsize, fontweight='semibold', color='#334155')
        else:
            ax.annotate(text, (p.get_x() + p.get_width() / 2., p.get_height() + padding),
                        ha='center', va='bottom', fontsize=fontsize, fontweight='semibold', color='#334155')

def save_chart(fig, filename, output_dir=None):
    """Saves figure to output directory with high resolution."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'charts')
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved chart to {filepath}")
    return filepath
