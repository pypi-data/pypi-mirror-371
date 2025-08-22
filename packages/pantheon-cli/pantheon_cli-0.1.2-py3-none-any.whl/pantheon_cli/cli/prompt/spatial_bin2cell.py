


from pathlib import Path
from typing import Optional

def generate_spatial_workflow_message(workflow_type: str) -> str:
    """Generate spatial workflow message using spatial toolset with omicverse"""
    bin2cell_message = f"""
🧬 Spatial Analysis Pipeline with omicverse Integration 

🔧 AVAILABLE WORKFLOW TOOLS:
You have access to the Spatial_Bin2Cell_Analysis tool for getting official templates.
💡 Use the tool when you need guidance, official examples, or best practices for a specific workflow step.
You need to ask the user for the path of the data, and then use ls command to check the folder contents,and then proceed with file loading.


⚠️ CRITICAL PYTHON ENVIRONMENT RULES:
- **PERSISTENT STATE**: Python interpreter maintains ALL variables across calls! 
- **MEMORY OPTIMIZATION**: Variables persist! NEVER re-read or re-import data that already exists in memory!
- **SMART VARIABLE CHECKING**: Use `try/except` or `'var' in globals()` to check existence - NO redundant file I/O!
- **EFFICIENCY FIRST**: 
  - Check if adata exists before loading: `if 'adata' not in globals()`
  - Use existing results: `if 'pca_result' in adata.obsm`
  - Reuse computed values: `if 'marker_genes' in locals()`
- **ERROR RECOVERY**: If code fails, analyze error and fix - don't reload everything!
- **NO REPETITION**: Each import/load/compute happens ONCE per session unless explicitly needed
- **After each step**: mark_task_done("description"), then show_todos()
- **AUTOMATIC EXECUTION**: Proceed automatically without confirmations; log warnings when needed.

PHASE 0 — SETUP & VALIDATION
1) Data discovery: Use ls command to check folder contents, then proceed with file loading
2) Environment check will be done automatically within data loading step

PHASE 1 - TODO CREATION (ONCE ONLY)
Execute: current = show_todos()
IF current is EMPTY, create these todos ONCE:
1. "Check Python environment and load initial data"
2. "Run read_visium workflow"
3. "Run cellpose_he workflow"
4. "Run expand_labels workflow"
5. "Run cellpose_gex workflow"
6. "Run salvage_secondary_labels workflow"
7. "Run bin2cell workflow"

⚡ AUTOMATIC WORKFLOW MODE:
- Execute each todo task automatically without asking for confirmation
- After successful completion of any step, immediately call mark_task_done("description") and proceed to next
- Continue the workflow seamlessly until all tasks complete or user intervenes


PHASE 2 — INTELLIGENT EXECUTION STRATEGY
🧠 SMART DECISION MAKING:

**ASSESS CURRENT SITUATION FIRST:**
- What data do you have loaded?
- What analysis steps are completed?
- What specific guidance do you need?

**CHOOSE YOUR APPROACH:**

**Option A - Use Template Tool (Recommended for new users or complex steps):**
- Call Spatial_Bin2Cell_Analysis(workflow_type="<type>") to get official template
- Study the returned guidance and code patterns
- Adapt the template to your specific data
- Execute the adapted code

**Option B - Direct Implementation (For experienced users with clear requirements):**
- Directly write and execute code based on omicverse documentation
- Use help() functions to check parameters
- Follow established best practices

**WHEN TO USE TEMPLATE TOOL:**
✅ When you need official guidance for a workflow step
✅ When you want to see best practices and parameter examples  
✅ When you're unsure about the correct approach
✅ When you want standardized, tested code patterns

**WHEN DIRECT IMPLEMENTATION IS OK:**
✅ When you have clear requirements and know the approach
✅ When adapting previous successful code
✅ When making minor parameter adjustments

🧠 **RESULT ANALYSIS REQUIREMENT:**
After executing any code:
1. **Analyze the output** - Don't just print and move on!
2. **Interpret the results** - What do the numbers, plots, and warnings mean?
3. **Check for issues** - Are there data quality problems or unexpected patterns?
4. **Make decisions** - Should parameters be adjusted based on what you observed?
5. **Document findings** - Save key insights to results directory
6. **Proceed intelligently** - Use results to inform next steps

The returned content serves as GUIDANCE and TEMPLATES, not direct execution scripts.
📊 STEP 1 - DATA LOADING, INSPECTION & PROJECT SETUP:
The path is the path of the data,you can use ls command to check the folder contents,then proceed with file loading.
if you don't know the path, you need to ask the user for the path and use ls command to explore the folder contents and structure.
after you have the path, you need to find some look like `"binned_outputs/square_002um/"` in the path,and then load the data.
the img should be stored in any location in the path, you need to find the correct img and ask the user to confirm the img path.
the img should end with btf or tiff, you need to find the correct img and ask the user to confirm the img path.


```python
# EFFICIENT DATA LOADING - Check memory first!
try:
    # Check if adata exists and is valid
    print(f"Using existing adata: {{adata.shape}} (n_obs, n_var)")
    data_already_loaded = True
except NameError:
    # Only load if not in memory
    print("Loading data for the first time...")
    
    # Check and install required packages
    import subprocess
    import sys
    print("Checking required packages...")
    required = ['scanpy', 'omicverse', 'pandas', 'numpy']
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"Installing {{pkg}}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', pkg])
    
    import scanpy as sc
    import omicverse as ov
    import pandas as pd
    import numpy as np
    
    # Load data based on detected format
    adata = ov.space.read_visium_10x("path")  # .h5ad, .h5, .mtx, etc.
    print(f"Loaded adata: {{adata.shape}} (n_obs, n_var)")

# Only import libraries once
if 'sc' not in globals():
    import scanpy as sc
    import omicverse as ov
    import pandas as pd
    import numpy as np
    print("Libraries imported")

# Create structured output directory (only if not exists)
print("\\n📁 Setting up project structure...")
try:
    # Check if we already have a results directory
    if 'results_dir' not in globals():
        import os
        from datetime import datetime
        
        # Create main results directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f"spatial_analysis_results_{{timestamp}}"
        os.makedirs(results_dir, exist_ok=True)
    else:
        print(f"Using existing results directory: {{results_dir}}")
    
    # Create subdirectories for different analysis components
    subdirs = [
        "01_data_loading",
        "02_stardist",
        "03_bin2cell", 
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(results_dir, subdir), exist_ok=True)
    print(f"📂 Project structure created in: {{results_dir}}")
except Exception as e:
    print(f"❌ Error creating project structure: {{e}}")

```

🏷️ STEP 2 - cellpose_he:
🤔 **ASSESS YOUR NEEDS:**
- Do you need guidance on cellpose_he workflow?
- Are you familiar with omicverse cellpose functions?
- Do you have the required parameters (mpp, thresholds, etc.)?

🛠️ **CHOOSE YOUR PATH:**

**Path A - Get Official Template:**
```
Spatial_Bin2Cell_Analysis(workflow_type="cellpose_he")
```
Then adapt the returned template to your data.

**Path B - Direct Implementation:**
Direct implementation using omicverse if you know the approach:
```python
import omicverse as ov
help(ov.space.visium_10x_hd_cellpose_he)  # Check parameters first
# Then implement based on your data
```

🎯 **GOAL:** Generate H&E-based cell segmentation labels

🏷️ STEP 3 - expand_labels:
🤔 **ASSESS YOUR NEEDS:**
- Do you need guidance on label expansion?
- Do you know the optimal max_bin_distance for your data?
- Are you familiar with the expansion algorithm?

🛠️ **CHOOSE YOUR PATH:**

**Path A - Get Official Template:**
```
Spatial_Bin2Cell_Analysis(workflow_type="expand_labels")
```
Then adapt the template with your specific parameters.

**Path B - Direct Implementation:**
Direct implementation if you know the approach:
```python
help(ov.space.visium_10x_hd_cellpose_expand)  # Check parameters
# Implement with appropriate max_bin_distance
```

🎯 **GOAL:** Expand cell labels to cover more spatial bins

🏷️ STEP 4 - cellpose_gex:
🤔 **ASSESS YOUR NEEDS:**
- Do you need guidance on GEX-based segmentation?
- Do you know the optimal obs_key for gene expression?
- Are you familiar with GEX segmentation parameters?

🛠️ **CHOOSE YOUR PATH:**

**Path A - Get Official Template:**
```
Spatial_Bin2Cell_Analysis(workflow_type="cellpose_gex")
```
Then adapt with your GEX-specific settings.

**Path B - Direct Implementation:**
Direct implementation if you understand the approach:
```python
help(ov.space.visium_10x_hd_cellpose_gex)  # Check parameters
# Implement with appropriate obs_key and thresholds
```

🎯 **GOAL:** Generate gene expression-based cell segmentation

🏷️ STEP 5 - salvage_secondary_labels:
🤔 **ASSESS YOUR NEEDS:**
- Do you need guidance on combining HE and GEX labels?
- Do you know which labels to use as primary/secondary?
- Are you familiar with the salvage algorithm?

🛠️ **CHOOSE YOUR PATH:**

**Path A - Get Official Template:**
```
Spatial_Bin2Cell_Analysis(workflow_type="salvage_secondary_labels")
```
Then adapt with your specific label keys.

**Path B - Direct Implementation:**
Direct implementation if you understand the process:
```python
help(ov.space.salvage_secondary_labels)  # Check parameters
# Combine HE and GEX labels appropriately
```

🎯 **GOAL:** Combine primary and secondary labels optimally

🏷️ STEP 6 - bin2cell:
🤔 **ASSESS YOUR NEEDS:**
- Do you need guidance on bin-to-cell conversion?
- Do you know the correct labels_key and spatial_keys?
- Are you familiar with the aggregation process?

🛠️ **CHOOSE YOUR PATH:**

**Path A - Get Official Template:**
```
Spatial_Bin2Cell_Analysis(workflow_type="bin2cell")
```
Then adapt with your verified keys and parameters.

**Path B - Direct Implementation:**
Direct implementation if you know the requirements:
```python
help(ov.space.bin2cell)  # Check parameters
# Convert bins to cells using final labels
```

🎯 **GOAL:** Convert spatial bins to cell-level data (cdata)

🔧 **AVAILABLE GUIDANCE TOOLS:**

**SPATIAL TEMPLATE ENGINE (Optional):**
- `Spatial_Bin2Cell_Analysis(workflow_type="cellpose_he")` - Get H&E segmentation template
- `Spatial_Bin2Cell_Analysis(workflow_type="expand_labels")` - Get label expansion template
- `Spatial_Bin2Cell_Analysis(workflow_type="cellpose_gex")` - Get GEX segmentation template
- `Spatial_Bin2Cell_Analysis(workflow_type="salvage_secondary_labels")` - Get label combination template
- `Spatial_Bin2Cell_Analysis(workflow_type="bin2cell")` - Get bin-to-cell conversion template

**FLEXIBLE EXECUTION STRATEGY:**
1. **ASSESS**: Evaluate your current needs and knowledge level
2. **CHOOSE**: Use templates for guidance OR implement directly
3. **ADAPT**: Modify any template code to fit your specific data
4. **EXECUTE**: Run your adapted code with run_python_code
5. **PROGRESS**: Mark tasks complete and continue workflow

**EFFICIENCY PRINCIPLES:**
1. **CHECK BEFORE COMPUTE**: Always check if variables/results exist before recomputing
2. **USE TRY/EXCEPT**: Gracefully handle missing variables without re-reading files
3. **MEMORY-FIRST**: Trust the persistent Python interpreter - no redundant I/O
4. **SMART RECOVERY**: Fix errors in-place, don't restart entire analysis
5. **INCREMENTAL PROGRESS**: Each step builds on previous results

Example patterns:
```python
# Good - Check memory first
try:
    print(f"Using existing adata: {{adata.shape}}")
except NameError:
    adata = sc.read_h5ad(path)

# Good - Check computed results
if 'X_pca' not in adata.obsm:
    sc.tl.pca(adata)
else:
    print("PCA already computed")

# Bad - Redundant file I/O
adata = sc.read_h5ad(path)  # Don't do this if adata exists!
```

**Remember:** Maintain persistent state, avoid redundant operations, and mark tasks complete with mark_task_done()!

"""
    if workflow_type == "bin2cell":
        return bin2cell_message
    else:
        return None