# Git Bash Setup Guide

This guide will help you configure your system to always use Git Bash instead of PowerShell.

## Files Created

1. **`.gitconfig`** - Git configuration file that forces Git to use Git Bash
2. **`setup_git_bash_default.ps1`** - PowerShell script to configure your system
3. **`windows_terminal_settings.json`** - Windows Terminal configuration
4. **`git_bash.bat`** - Simple batch file to launch Git Bash
5. **`GIT_BASH_SETUP_README.md`** - This file

## Quick Setup

### Option 1: Run the PowerShell Script (Recommended)

1. **Right-click on `setup_git_bash_default.ps1`** and select "Run with PowerShell"
2. **Or open PowerShell as Administrator** and run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\setup_git_bash_default.ps1
   ```

### Option 2: Manual Configuration

#### Step 1: Configure Git
Copy the `.gitconfig` file to your home directory:
```bash
copy .gitconfig %USERPROFILE%\.gitconfig
```

#### Step 2: Set Git Bash as Default Shell
```bash
git config --global core.shell "C:/Program Files/Git/bin/bash.exe"
git config --global core.terminal "C:/Program Files/Git/bin/bash.exe"
```

#### Step 3: Configure Windows Terminal (Optional)
1. Open Windows Terminal
2. Press `Ctrl+,` to open settings
3. Replace the contents with `windows_terminal_settings.json`
4. Save and restart Windows Terminal

## What This Configuration Does

### Git Configuration
- Forces Git to use Git Bash for all operations
- Sets VS Code as the default editor
- Configures proper line endings for cross-platform compatibility
- Adds useful Git aliases

### PowerShell Profile
- Automatically launches Git Bash when PowerShell is opened in a Git repository
- Provides `Start-GitBash` function for manual launching
- Sets environment variables for Git operations

### Windows Terminal
- Sets Git Bash as the default profile
- Configures proper icons and colors
- Maintains PowerShell as a secondary option

## Usage

### Launch Git Bash
- **Double-click** `git_bash.bat`
- **Use the desktop shortcut** (created by the setup script)
- **Run** `Start-GitBash` in PowerShell
- **Open Windows Terminal** (will default to Git Bash)

### Git Operations
All Git operations will now use Git Bash automatically:
```bash
git status
git add .
git commit -m "Your message"
git push
```

## Troubleshooting

### Git Not Found
If you get "Git not found" errors:
1. Install Git for Windows: https://git-scm.com/download/win
2. Ensure Git is installed to `C:\Program Files\Git\`
3. Restart your terminal after installation

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path Issues
If Git commands aren't found:
1. Add `C:\Program Files\Git\bin` to your PATH
2. Restart your terminal

### Windows Terminal Issues
If Windows Terminal doesn't recognize the settings:
1. Copy `windows_terminal_settings.json` to:
   `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`
2. Restart Windows Terminal

## Verification

To verify Git Bash is working:
```bash
# Check Git shell
git config --get core.shell

# Check current shell
echo $SHELL

# Check Git version
git --version
```

## Benefits of Using Git Bash

1. **Unix-like environment** - Familiar commands and syntax
2. **Better Git integration** - Native Git commands work seamlessly
3. **Cross-platform compatibility** - Same commands work on Linux/Mac
4. **Rich ecosystem** - Access to Unix tools and utilities
5. **Better scripting** - Bash scripting capabilities
6. **Consistent behavior** - Same experience across different systems

## Customization

### Add More Aliases
Edit your `.gitconfig` file to add more Git aliases:
```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    # Add your own aliases here
```

### Change Default Editor
Modify the editor setting in `.gitconfig`:
```ini
[core]
    editor = notepad++ -multiInst -nosession
```

### Custom Bash Profile
Create `~/.bashrc` or `~/.bash_profile` for custom Bash configurations.

## Support

If you encounter issues:
1. Check that Git for Windows is properly installed
2. Verify the paths in the configuration files match your Git installation
3. Restart your terminal after making changes
4. Check Windows Terminal settings if using that application

## Notes

- This configuration assumes Git is installed to `C:\Program Files\Git\`
- If Git is installed elsewhere, update the paths in the configuration files
- The setup script requires PowerShell execution policy to allow running scripts
- Some features may require Windows 10 or later
