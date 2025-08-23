from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from vschart.constants import Color
from vschart.series_primitive import SeriesPrimitive

if TYPE_CHECKING:
    from vschart.series_base import SeriesBase

class TrendLine(SeriesPrimitive):
    def __init__(self, series: 'SeriesBase', id: str):
        super().__init__(series, id)
        
    def set_line_style(self, line_style: int = 0):
        """Set line style (0: solid, 1: dotted, 2: dashed, 3: large dashed, 4: sparse dotted)"""
        result = self.send_request('applyOptions', [self.id, {'lineStyle': line_style}])
        if result['success']:
            self.logger.debug(f"Line style set to {line_style}")
        else:
            self.logger.error(f"Failed to set line style to {line_style}")
        
    def set_line_color(self, line_color: str = Color.BLUE):
        """Set line color"""
        result = self.send_request('applyOptions', [self.id, {'lineColor': line_color}])
        if result['success']:
            self.logger.debug(f"Line color set to {line_color}")
        else:
            self.logger.error(f"Failed to set line color to {line_color}")
        
    def set_width(self, width: int = 2):
        """Set line width"""
        result = self.send_request('applyOptions', [self.id, {'width': width}])
        if result['success']:
            self.logger.debug(f"Line width set to {width}")
        else:
            self.logger.error(f"Failed to set line width to {width}")
        
    def set_show_labels(self, show_labels: bool = True):
        """Set show labels"""
        result = self.send_request('applyOptions', [self.id, {'showLabels': show_labels}])
        if result['success']:
            self.logger.debug(f"Show labels set to {show_labels}")
        else:
            self.logger.error(f"Failed to set show labels to {show_labels}")
        
    def set_label_background_color(self, label_background_color: str = Color.TRANS_WHITE):
        """Set label background color"""
        result = self.send_request('applyOptions', [self.id, {'labelBackgroundColor': label_background_color}])
        if result['success']:
            self.logger.debug(f"Label background color set to {label_background_color}")
        else:
            self.logger.error(f"Failed to set label background color to {label_background_color}")
        
    def set_label_text_color(self, label_text_color: str = Color.BLACK):
        """Set label text color"""
        result = self.send_request('applyOptions', [self.id, {'labelTextColor': label_text_color}])
        if result['success']:
            self.logger.debug(f"Label text color set to {label_text_color}")
        else:
            self.logger.error(f"Failed to set label text color to {label_text_color}")
    
    def set_show_fibonacci(self, show_fibonacci: bool = True):
        """Enable or disable Fibonacci lines display"""
        result = self.send_request('applyOptions', [self.id, {'showFibonacci': show_fibonacci}])
        if result['success']:
            self.logger.debug(f"Show Fibonacci set to {show_fibonacci}")
        else:
            self.logger.error(f"Failed to set show Fibonacci to {show_fibonacci}")
    
    def set_fibonacci_line_color(self, fibonacci_line_color: str = '#FFA500'):
        """Set Fibonacci lines color"""
        result = self.send_request('applyOptions', [self.id, {'fibonacciLineColor': fibonacci_line_color}])
        if result['success']:
            self.logger.debug(f"Fibonacci line color set to {fibonacci_line_color}")
        else:
            self.logger.error(f"Failed to set Fibonacci line color to {fibonacci_line_color}")
    
    def set_fibonacci_line_width(self, fibonacci_line_width: int = 1):
        """Set Fibonacci lines width"""
        result = self.send_request('applyOptions', [self.id, {'fibonacciLineWidth': fibonacci_line_width}])
        if result['success']:
            self.logger.debug(f"Fibonacci line width set to {fibonacci_line_width}")
        else:
            self.logger.error(f"Failed to set Fibonacci line width to {fibonacci_line_width}")
    
    def set_fibonacci_line_style(self, fibonacci_line_style: int = 2):
        """Set Fibonacci lines style (0: solid, 1: dotted, 2: dashed, 3: large dashed, 4: sparse dotted)"""
        result = self.send_request('applyOptions', [self.id, {'fibonacciLineStyle': fibonacci_line_style}])
        if result['success']:
            self.logger.debug(f"Fibonacci line style set to {fibonacci_line_style}")
        else:
            self.logger.error(f"Failed to set Fibonacci line style to {fibonacci_line_style}")
