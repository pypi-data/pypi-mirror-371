# ⚙️ **Configuration & Registry**

This folder contains configuration files, component registry, and discovery metadata for the DataExploratoryProject.

## 📁 **Contents**

### **Component Registry**
- `component_registry.json` - **Main component registry** with all discovered estimators and data generators
- `.last_discovery` - Timestamp of last component discovery run

### **Git Configuration**
- `.gitconfig` - Git configuration settings for the project

## 🔍 **Component Registry**

### **Purpose**
The `component_registry.json` file serves as the central registry for all discovered components in the project, including:
- **Data Generators**: ARFIMA, fBm, fGn, MRW, Neural fSDE
- **Estimators**: 13 estimators across temporal, spectral, wavelet, and multifractal categories
- **Component Metadata**: Version information, dependencies, and capabilities

### **Auto-Discovery**
The registry is automatically populated by the `auto_discovery_system.py` script, which:
- Scans the project structure for available components
- Detects new estimators and data generators
- Updates metadata and capability information
- Maintains consistency across the framework

### **Usage**
```python
import json

# Load component registry
with open('config/component_registry.json', 'r') as f:
    registry = json.load(f)

# Access available estimators
estimators = registry['estimators']
print(f"Available estimators: {len(estimators)}")

# Access available data generators
generators = registry['data_generators']
print(f"Available generators: {len(generators)}")
```

## 🔧 **Git Configuration**

### **Purpose**
The `.gitconfig` file contains project-specific Git settings, including:
- **Editor Configuration**: VS Code as default editor
- **Line Ending Settings**: Consistent line ending handling
- **Shell Configuration**: Git Bash integration
- **Aliases**: Useful Git command shortcuts

### **Features**
- **Cross-Platform Compatibility**: Consistent behavior across Windows, macOS, and Linux
- **Editor Integration**: Seamless integration with VS Code
- **Line Ending Management**: Prevents cross-platform line ending issues
- **Git Bash Integration**: Optimized for Git Bash usage

## 📊 **Discovery Metadata**

### **Last Discovery Timestamp**
The `.last_discovery` file tracks when the component registry was last updated, enabling:
- **Change Detection**: Identify when new components are added
- **Cache Management**: Determine if registry needs refresh
- **Build Optimization**: Skip discovery if no changes detected

### **Discovery Process**
1. **Scan Project Structure**: Recursively search for component files
2. **Validate Components**: Check imports and dependencies
3. **Extract Metadata**: Gather version and capability information
4. **Update Registry**: Write updated registry to JSON file
5. **Update Timestamp**: Record discovery completion time

## 🚀 **Configuration Management**

### **Adding New Components**
1. **Implement Component**: Create new estimator or data generator
2. **Follow Naming Convention**: Use consistent naming patterns
3. **Add Documentation**: Include docstrings and type hints
4. **Run Discovery**: Execute auto-discovery to update registry

### **Modifying Configuration**
1. **Edit Files**: Modify configuration files as needed
2. **Test Changes**: Verify configuration works correctly
3. **Commit Changes**: Use Git to track configuration updates
4. **Document Changes**: Update relevant documentation

## 📖 **File Descriptions**

### **component_registry.json**
- **Format**: JSON with nested component structure
- **Size**: ~38KB with comprehensive component information
- **Update Frequency**: Automatically updated by discovery system
- **Backup**: Version controlled through Git

### **.last_discovery**
- **Format**: Single line timestamp
- **Purpose**: Track discovery system execution
- **Usage**: Build system optimization
- **Maintenance**: Automatically managed

### **.gitconfig**
- **Format**: Git configuration file
- **Scope**: Project-specific Git settings
- **Integration**: Works with global Git configuration
- **Customization**: Modify for project-specific needs

---

**This folder provides the configuration foundation for the DataExploratoryProject, ensuring consistent component discovery, Git integration, and project management across all development environments.**
