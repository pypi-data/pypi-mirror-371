import json
import logging
import os
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import io

from fairlib.core.interfaces.tools import AbstractTool
from fairlib.core.interfaces.security import AbstractSecurityManager
from fairlib.core.interfaces.llm import AbstractChatModel

logger = logging.getLogger(__name__)


class GraphingTool(AbstractTool):
    """
    A comprehensive graphing tool that:
    1. Accepts structured data from the DataExtractor
    2. Generates appropriate Python plotting code
    3. Executes the code safely to create visualizations
    4. Saves the plots and returns metadata for the summarizer
    """
    
    name = "graphing_tool"
    description = (
        "Creates data visualizations from structured data. Accepts extracted data "
        "in JSON format, generates appropriate plotting code, executes it safely, "
        "and saves the resulting graphs. Returns plot metadata and file paths."
    )
    
    def __init__(self, 
                 security_manager: AbstractSecurityManager,
                 llm: Optional[AbstractChatModel] = None,
                 output_dir: str = "./outputs",
                 allowed_libraries: List[str] = None):
        """
        Initialize the graphing tool.
        
        Args:
            security_manager: Security manager for safe code execution
            llm: Optional LLM for intelligent code generation
            output_dir: Directory to save generated plots
            allowed_libraries: List of allowed Python libraries for plotting
        """
        self.security_manager = security_manager
        self.llm = llm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Default allowed libraries for safety
        self.allowed_libraries = allowed_libraries or [
            'matplotlib', 'numpy', 'pandas', 'seaborn', 'datetime'
        ]
        
        # Plot style configurations
        self.plot_styles = {
            'default': {
                'figure.figsize': (12, 8),
                'font.size': 12,
                'axes.labelsize': 14,
                'axes.titlesize': 16,
                'xtick.labelsize': 12,
                'ytick.labelsize': 12,
                'legend.fontsize': 12,
                'figure.dpi': 100
            }
        }
        
        logger.info(f"GraphingTool initialized with output directory: {self.output_dir}")
    
    def use(self, tool_input: str) -> str:
        """
        Main entry point for the graphing tool.
        
        Args:
            tool_input: JSON string containing:
                - data: The structured data to plot
                - plot_type: Optional plot type hint
                - title: Optional plot title
                - instructions: Optional specific plotting instructions
        
        Returns:
            JSON string with plot metadata and file path
        """
        try:
            # Parse input
            input_data = self._parse_input(tool_input)
            
            # Analyze data to determine best plot type
            data_analysis = self._analyze_data(input_data['data'])
            
            # Generate plotting code
            plot_code = self._generate_plot_code(
                input_data['data'],
                data_analysis,
                input_data.get('instructions', ''),
                input_data.get('title', 'Data Visualization')
            )
            
            # Execute code safely
            execution_result = self._execute_plot_code(plot_code)
            
            if execution_result['success']:
                # Save plot and get metadata
                plot_metadata = self._save_plot(
                    execution_result['plot_path'],
                    input_data,
                    data_analysis
                )
                
                return json.dumps({
                    'status': 'success',
                    'plot_metadata': plot_metadata,
                    'code_executed': plot_code,
                    'data_analysis': data_analysis
                }, indent=2)
            else:
                return json.dumps({
                    'status': 'error',
                    'error': execution_result['error'],
                    'code_attempted': plot_code
                }, indent=2)
                
        except Exception as e:
            logger.error(f"GraphingTool error: {e}", exc_info=True)
            return json.dumps({
                'status': 'error',
                'error': str(e)
            }, indent=2)
    
    def _parse_input(self, tool_input: str) -> Dict[str, Any]:
        """Parse and validate input data"""
        try:
            data = json.loads(tool_input)
        except json.JSONDecodeError:
            # Try to parse as simple string instruction
            data = {'instructions': tool_input}
        
        # Convert various input formats to standard columns/rows format
        if 'data' not in data:
            # Check if it's from WebDataExtractor format
            if 'extracted_data' in data and data['extracted_data']:
                # Use the first dataset
                extracted = data['extracted_data'][0]
                data['data'] = {
                    'columns': extracted['columns'],
                    'rows': extracted['rows']
                }
            else:
                raise ValueError("No data provided for plotting")
        else:
            # Check if data is in a non-standard format and convert it
            data_content = data['data']
            
            # Handle different data formats
            if isinstance(data_content, dict):
                # Check for various common formats
                if 'columns' not in data_content or 'rows' not in data_content:
                    # Try to convert from other formats
                    converted_data = self._convert_to_standard_format(data_content)
                    data['data'] = converted_data
        
        return data
    
    def _convert_to_standard_format(self, data_content: Dict[str, Any]) -> Dict[str, Any]:
        """Convert various data formats to standard columns/rows format"""

        # Format 1: Separate arrays for each dimension (e.g., months and anomalies)
        if isinstance(data_content, dict) and all(isinstance(v, list) for v in data_content.values()):
            keys = list(data_content.keys())
            if len(keys) >= 2:
                x_key = keys[0]
                y_key = keys[1]
                x_values = data_content[x_key]
                y_values = data_content[y_key]
                min_len = min(len(x_values), len(y_values))
                return {
                    'columns': [x_key, y_key],
                    'rows': [[x_values[i], y_values[i]] for i in range(min_len)]
                }

        # Format 2: List of dictionaries
        elif isinstance(data_content, list) and data_content and isinstance(data_content[0], dict):
            columns = list(data_content[0].keys())
            rows = [[item.get(col) for col in columns] for item in data_content]
            return {'columns': columns, 'rows': rows}

        # Format 3: Single dictionary with nested structure (x/y keys)
        elif isinstance(data_content, dict) and 'x' in data_content and 'y' in data_content:
            return {
                'columns': ['x', 'y'],
                'rows': [[x, y] for x, y in zip(data_content['x'], data_content['y'])]
            }

        raise ValueError(
            f"Unable to convert data format. Expected format: "
            f"{{'columns': ['col1', 'col2'], 'rows': [[val1, val2], ...]}}. "
            f"Got type={type(data_content).__name__}, keys={getattr(data_content, 'keys', lambda: [])()}"
        )

    
    def _analyze_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data to determine characteristics and best plot type"""
        columns = data.get('columns', [])
        rows = data.get('rows', [])
        
        if not columns or not rows:
            raise ValueError("Empty data provided")
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(rows, columns=columns)
        
        analysis = {
            'num_columns': len(columns),
            'num_rows': len(rows),
            'column_types': {},
            'suggested_plot_type': 'line',
            'has_time_series': False,
            'has_categories': False,
            'numeric_columns': [],
            'date_columns': [],
            'text_columns': []
        }
        
        # Analyze each column
        for col in columns:
            # Try to infer data type
            sample_values = df[col].dropna().head(10)
            
            # Check for dates/time data
            if self._is_date_column(col, sample_values):
                analysis['date_columns'].append(col)
                analysis['has_time_series'] = True
                analysis['column_types'][col] = 'date'
            # Check for months (special case for text that represents time)
            elif self._is_month_column(col, sample_values):
                analysis['date_columns'].append(col)
                analysis['has_time_series'] = True
                analysis['column_types'][col] = 'month'
            # Check for numeric
            elif pd.api.types.is_numeric_dtype(df[col]):
                analysis['numeric_columns'].append(col)
                analysis['column_types'][col] = 'numeric'
            else:
                analysis['text_columns'].append(col)
                analysis['column_types'][col] = 'text'
                if df[col].nunique() < len(df) * 0.5:  # Likely categorical
                    analysis['has_categories'] = True
        
        # Suggest plot type based on data characteristics
        analysis['suggested_plot_type'] = self._suggest_plot_type(analysis, df)
        
        return analysis
    
    def _is_month_column(self, col_name: str, values: pd.Series) -> bool:
        """Check if a column contains month names"""
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        
        # Check column name
        if 'month' in col_name.lower():
            return True
        
        # Check if values are month names
        try:
            values_lower = values.astype(str).str.lower()
            if all(v in months for v in values_lower):
                return True
        except:
            pass
        
        return False
    
    def _is_date_column(self, col_name: str, values: pd.Series) -> bool:
        date_keywords = ['date', 'time', 'year', 'month', 'day', 'timestamp']
        if any(keyword in col_name.lower() for keyword in date_keywords):
            return True

        s = values.astype(str).dropna()

        if not s.empty and s.str.fullmatch(r"\d{4}").all():
            year = pd.to_numeric(s, errors="coerce")
            return year.between(1900, 2100).all()

        try:
            parsed = pd.to_datetime(s, format="mixed", errors="coerce")
        except TypeError:
            parsed = pd.to_datetime(s, errors="coerce")

        return parsed.notna().mean() >= 0.8

    
    def _suggest_plot_type(self, analysis: Dict[str, Any], df: pd.DataFrame) -> str:
        """Suggest the best plot type based on data characteristics"""
        num_numeric = len(analysis['numeric_columns'])
        num_date = len(analysis['date_columns'])
        num_text = len(analysis['text_columns'])
        num_rows = analysis['num_rows']
        
        # Time series data
        if analysis['has_time_series'] and num_numeric >= 1:
            return 'line'
        
        # Categorical comparisons
        elif analysis['has_categories'] and num_numeric >= 1:
            if num_rows < 20:
                return 'bar'
            else:
                return 'box'  # For many categories, box plot is clearer
        
        # Two numeric variables
        elif num_numeric == 2 and not analysis['has_time_series']:
            return 'scatter'
        
        # Single numeric variable
        elif num_numeric == 1 and num_text == 0:
            return 'histogram'
        
        # Multiple numeric variables
        elif num_numeric > 2:
            return 'heatmap'
        
        # Default to bar chart
        else:
            return 'bar'
    
    def _generate_plot_code(self, data: Dict[str, Any], 
                           analysis: Dict[str, Any],
                           instructions: str,
                           title: str) -> str:
        """Generate Python plotting code based on data and analysis"""
        
        if self.llm and instructions:
            # Use LLM for custom plotting based on instructions
            return self._generate_plot_code_with_llm(data, analysis, instructions, title)
        else:
            # Use template-based code generation
            return self._generate_plot_code_template(data, analysis, title)
    
    def _generate_plot_code_template(self, data: Dict[str, Any],
                                    analysis: Dict[str, Any],
                                    title: str) -> str:
        """Generate plotting code using templates"""
        
        plot_type = analysis['suggested_plot_type']
        
        # Common imports and setup
        code = """
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Create DataFrame
data = {data_json}
df = pd.DataFrame(data['rows'], columns=data['columns'])

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

"""
        
        # Add plot-specific code
        if plot_type == 'line':
            code += self._generate_line_plot_code(analysis)
        elif plot_type == 'bar':
            code += self._generate_bar_plot_code(analysis)
        elif plot_type == 'scatter':
            code += self._generate_scatter_plot_code(analysis)
        elif plot_type == 'histogram':
            code += self._generate_histogram_code(analysis)
        elif plot_type == 'box':
            code += self._generate_box_plot_code(analysis)
        else:
            code += self._generate_default_plot_code(analysis)
        
        # Common ending
        code += f"""
# Set title and labels
plt.title('{title}', fontsize=16, fontweight='bold', pad=20)
plt.xlabel(ax.get_xlabel() or 'X-axis', fontsize=14)
plt.ylabel(ax.get_ylabel() or 'Y-axis', fontsize=14)

# Improve layout
plt.tight_layout()

# Save the plot
plt.savefig('__PLOT_PATH__', dpi=300, bbox_inches='tight')
plt.close()

# Store result
result = 'Plot saved successfully'
"""
        
        # Replace data placeholder
        code = code.replace('{data_json}', json.dumps(data))
        
        return code
    
    def _generate_line_plot_code(self, analysis: Dict[str, Any]) -> str:
        """Generate code for line plots"""
        date_col = analysis['date_columns'][0] if analysis['date_columns'] else None
        numeric_cols = analysis['numeric_columns']
        
        code = ""
        
        # Handle date/time conversion if needed
        if date_col:
            col_type = analysis['column_types'].get(date_col, 'date')
            
            if col_type == 'month':
                # Handle month names
                code += f"""
# Handle month names
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Check if months are in the data
if df['{date_col}'].iloc[0] in month_order:
    # Create numeric mapping for proper ordering
    month_to_num = {{month: i for i, month in enumerate(month_order)}}
    df['_month_order'] = df['{date_col}'].map(month_to_num)
    df = df.sort_values('_month_order')
    x_data = range(len(df))
    x_labels = df['{date_col}']
else:
    x_data = range(len(df))
    x_labels = df['{date_col}']

"""
            else:
                # Regular date handling
                code += f"""
# Convert date column
try:
    df['{date_col}'] = pd.to_datetime(df['{date_col}'])
    df = df.sort_values('{date_col}')
    x_data = df['{date_col}']
    x_labels = None
except:
    # If date parsing fails, try numeric conversion
    df['{date_col}'] = pd.to_numeric(df['{date_col}'], errors='coerce')
    df = df.sort_values('{date_col}')
    x_data = df['{date_col}']
    x_labels = None

"""
        else:
            # No date column, use index
            code += """
x_data = range(len(df))
x_labels = None

"""
        
        # Plot lines
        if len(numeric_cols) == 1:
            y_col = numeric_cols[0]
            if date_col and analysis['column_types'].get(date_col) == 'month':
                code += f"""
# Single line plot with months
ax.plot(x_data, df['{y_col}'], marker='o', linewidth=2, markersize=8)
ax.set_xticks(x_data)
ax.set_xticklabels(x_labels, rotation=45, ha='right')
ax.set_xlabel('{date_col}')
ax.set_ylabel('{y_col}')

# Add value labels on points
for i, (x, y) in enumerate(zip(x_data, df['{y_col}'])):
    ax.annotate(f'{{y:.2f}}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
"""
            else:
                code += f"""
# Single line plot
ax.plot(x_data, df['{y_col}'], marker='o', linewidth=2, markersize=6)
ax.set_xlabel('{date_col if date_col else "Index"}')
ax.set_ylabel('{y_col}')
"""
        else:
            # Multiple lines
            x_col = date_col if date_col else 'Index'
            code += f"""
# Multiple line plot
for col in {numeric_cols}:
    ax.plot(x_data, df[col], marker='o', linewidth=2, markersize=6, label=col)

ax.set_xlabel('{x_col}')
ax.legend(loc='best')
"""
        
        # Format x-axis for dates
        if date_col and analysis['column_types'].get(date_col) != 'month':
            code += """
# Format date axis
if x_labels is None:
    fig.autofmt_xdate()
"""
        
        # Add grid
        code += """
# Add grid for better readability
ax.grid(True, alpha=0.3, linestyle='--')
"""
        
        return code
    
    def _generate_bar_plot_code(self, analysis: Dict[str, Any]) -> str:
        """Generate code for bar plots"""
        # Find categorical and numeric columns
        cat_col = analysis['text_columns'][0] if analysis['text_columns'] else df.columns[0]
        num_col = analysis['numeric_columns'][0] if analysis['numeric_columns'] else df.columns[1]
        
        return f"""
# Bar plot
df_grouped = df.groupby('{cat_col}')['{num_col}'].sum().sort_values(ascending=False)
df_grouped.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('{cat_col}')
ax.set_ylabel('{num_col}')

# Rotate x labels if needed
if len(df_grouped) > 10:
    plt.xticks(rotation=45, ha='right')
"""
    
    def _generate_scatter_plot_code(self, analysis: Dict[str, Any]) -> str:
        """Generate code for scatter plots"""
        if len(analysis['numeric_columns']) >= 2:
            x_col = analysis['numeric_columns'][0]
            y_col = analysis['numeric_columns'][1]
            
            return f"""
# Scatter plot
ax.scatter(df['{x_col}'], df['{y_col}'], alpha=0.6, s=50, edgecolor='black', linewidth=0.5)
ax.set_xlabel('{x_col}')
ax.set_ylabel('{y_col}')

# Add trend line
z = np.polyfit(df['{x_col}'].dropna(), df['{y_col}'].dropna(), 1)
p = np.poly1d(z)
ax.plot(df['{x_col}'].sort_values(), p(df['{x_col}'].sort_values()), "r--", alpha=0.8, label='Trend line')
ax.legend()
"""
        else:
            return self._generate_default_plot_code(analysis)
    
    def _generate_histogram_code(self, analysis: Dict[str, Any]) -> str:
        """Generate code for histograms"""
        num_col = analysis['numeric_columns'][0] if analysis['numeric_columns'] else df.columns[0]
        
        return f"""
# Histogram
df['{num_col}'].hist(ax=ax, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
ax.set_xlabel('{num_col}')
ax.set_ylabel('Frequency')

# Add statistics
mean_val = df['{num_col}'].mean()
median_val = df['{num_col}'].median()
ax.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {{mean_val:.2f}}')
ax.axvline(median_val, color='green', linestyle='dashed', linewidth=2, label=f'Median: {{median_val:.2f}}')
ax.legend()
"""
    
    def _generate_box_plot_code(self, analysis: Dict[str, Any]) -> str:
        """Generate code for box plots"""
        cat_col = analysis['text_columns'][0] if analysis['text_columns'] else None
        num_cols = analysis['numeric_columns']
        
        if cat_col and num_cols:
            return f"""
# Box plot grouped by category
df.boxplot(column={num_cols}, by='{cat_col}', ax=ax)
ax.set_xlabel('{cat_col}')
plt.suptitle('')  # Remove default title
"""
        else:
            return f"""
# Box plot of numeric columns
df[{num_cols}].boxplot(ax=ax)
"""
    
    def _generate_default_plot_code(self, analysis: Dict[str, Any]) -> str:
        """Generate default plot when type can't be determined"""
        return """
# Default plot - first numeric column
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    df[numeric_cols[0]].plot(ax=ax, kind='line', marker='o')
else:
    # Fallback to value counts
    df.iloc[:, 0].value_counts().plot(kind='bar', ax=ax)
"""
    
    def _generate_plot_code_with_llm(self, data: Dict[str, Any],
                                    analysis: Dict[str, Any],
                                    instructions: str,
                                    title: str) -> str:
        """Use LLM to generate custom plotting code"""
        
        from fairlib import Message
        
        prompt = f"""
Generate Python code to create a data visualization based on the following:

Data structure:
- Columns: {data['columns']}
- Number of rows: {len(data['rows'])}
- Sample rows: {data['rows'][:3]}

Data analysis:
{json.dumps(analysis, indent=2)}

User instructions: {instructions}
Plot title: {title}

Requirements:
1. Use only these libraries: {self.allowed_libraries}
2. Create a high-quality, publication-ready plot
3. Include proper labels, title, and legend
4. Use appropriate plot type for the data
5. Save the plot to '__PLOT_PATH__' with 300 DPI
6. Set result = 'Plot saved successfully' at the end

Generate only the Python code, no explanations:
"""
        
        response = self.llm.chat([Message(role="system", content=prompt)])
        
        # Clean the response
        code = response.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        # Ensure data is included
        if "data = " not in code:
            code = f"data = {json.dumps(data)}\n" + code
        
        return code
    
    def _execute_plot_code(self, code: str) -> Dict[str, Any]:
        """Execute plotting code safely"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_filename = f"plot_{timestamp}.png"
            plot_path = self.output_dir / plot_filename
            
            # Replace placeholder with actual path
            code = code.replace('__PLOT_PATH__', str(plot_path))
            
            # Execute code
            result = self.security_manager.sandbox_code_execution(code, language='python')
            
            # Check if plot was created
            if plot_path.exists():
                return {
                    'success': True,
                    'plot_path': str(plot_path),
                    'execution_result': result
                }
            else:
                return {
                    'success': False,
                    'error': f"Plot file not created. Execution result: {result}"
                }
                
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_plot(self, plot_path: str, input_data: Dict[str, Any], 
                   analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Save plot and generate metadata"""
        
        # Get plot file info
        plot_file = Path(plot_path)
        file_size = plot_file.stat().st_size
        
        # Load image to get dimensions
        with Image.open(plot_path) as img:
            width, height = img.size
        
        metadata = {
            'file_path': str(plot_path),
            'file_name': plot_file.name,
            'file_size_bytes': file_size,
            'dimensions': {'width': width, 'height': height},
            'plot_type': analysis['suggested_plot_type'],
            'data_shape': {
                'columns': len(input_data['data']['columns']),
                'rows': len(input_data['data']['rows'])
            },
            'creation_time': datetime.now().isoformat(),
            'title': input_data.get('title', 'Data Visualization')
        }
        
        # Generate preview (base64 encoded thumbnail)
        metadata['preview'] = self._generate_preview(plot_path)
        
        logger.info(f"Plot saved successfully: {plot_path}")
        
        return metadata
    
    def _generate_preview(self, plot_path: str, max_size: Tuple[int, int] = (200, 200)) -> str:
        """Generate a base64 encoded thumbnail preview"""
        try:
            with Image.open(plot_path) as img:
                # Create thumbnail
                img.thumbnail(max_size)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            return ""