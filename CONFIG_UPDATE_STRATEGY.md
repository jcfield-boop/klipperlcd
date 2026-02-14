# Config Update Strategy for KlipperLCD

## Problem
When KlipperLCD is updated via `git pull`, we want to:
- Add new configuration options (like the new `[features]` section)
- Preserve existing user customizations
- NOT overwrite the user's config file

## Linux Standard Approaches

### 1. Package Manager Approach (.dpkg-dist)
**How it works:**
- Package update creates `config.conf.dpkg-dist` with new version
- User manually diffs and merges: `diff config.conf config.conf.dpkg-dist`

**Pros:** User has full control, no data loss
**Cons:** Requires manual intervention, technical knowledge

### 2. Drop-in Directory Pattern
**How it works:**
```
KlipperLCD.cfg              # User edits this
KlipperLCD.defaults.cfg     # Package-provided (updated automatically)
```

**Pros:** Clean separation, automatic updates
**Cons:** Requires code changes to load multiple files

### 3. In-Place Migration
**How it works:**
- On startup, check config version
- If old version, add new sections programmatically
- Write back updated config

**Pros:** Automatic, seamless for users
**Cons:** Modifies user file (scary), can mess up comments/formatting

### 4. Runtime Merging (RECOMMENDED)
**How it works:**
- Load defaults from code or defaults file
- Overlay user config on top
- Missing sections use defaults (in-memory only)
- Never write back unless user explicitly regenerates

**Pros:** No file modification, safe, automatic
**Cons:** Slightly more complex code

## Recommended Implementation

### Strategy: Runtime Merging + Optional Migration

#### Step 1: Default Values in Code
```python
# config.py - FeaturesConfig class
class FeaturesConfig:
    def __init__(self, config_parser=None):
        # Define all defaults in code
        defaults = {
            'default_pa': 0.0,
            'enable_console_shortcuts': True
        }

        if config_parser and config_parser.has_section('features'):
            # User config overrides defaults
            self.default_pa = config_parser.getfloat('features', 'default_pa',
                                                     fallback=defaults['default_pa'])
            self.enable_console_shortcuts = config_parser.getboolean(
                'features', 'enable_console_shortcuts',
                fallback=defaults['enable_console_shortcuts']
            )
        else:
            # Section missing? Use defaults (no error)
            self.default_pa = defaults['default_pa']
            self.enable_console_shortcuts = defaults['enable_console_shortcuts']
            logger.info("[features] section not in config, using defaults")
```

**Result:** Missing sections work automatically with defaults!

#### Step 2: Offer Config Update Command
```bash
# User runs this OPTIONALLY to update config
python3 main.py --update-config
```

This command:
1. Reads current config
2. Preserves all user values
3. Adds missing sections with defaults
4. Writes back with updated comments

#### Step 3: Config Version Tracking
```ini
# KlipperLCD.cfg
[meta]
# Config file version (do not edit manually)
version = 2.0
```

```python
# config.py
def needs_update(config_path):
    parser = ConfigParser()
    parser.read(config_path)
    version = parser.get('meta', 'version', fallback='1.0')
    return version < CURRENT_VERSION

def update_config(config_path):
    """Non-destructive config update"""
    parser = ConfigParser()
    parser.read(config_path)

    # Preserve all existing values
    existing_values = {}
    for section in parser.sections():
        existing_values[section] = dict(parser.items(section))

    # Generate new config with current defaults
    generate_default_config(config_path + '.new')

    # Merge: user values override defaults
    new_parser = ConfigParser()
    new_parser.read(config_path + '.new')

    for section, values in existing_values.items():
        if new_parser.has_section(section):
            for key, value in values.items():
                new_parser.set(section, key, value)

    # Write merged config
    with open(config_path, 'w') as f:
        new_parser.write(f)

    # Clean up
    os.remove(config_path + '.new')
```

#### Step 4: Startup Notification
```python
# main.py
if __name__ == "__main__":
    config = KlipperLCDConfig(args.config)

    # Check if config needs update
    if config.needs_update():
        logger.warning("=" * 60)
        logger.warning("CONFIG UPDATE AVAILABLE")
        logger.warning("New configuration options are available!")
        logger.warning("Run: python3 main.py --update-config")
        logger.warning("This will preserve your settings and add new options.")
        logger.warning("=" * 60)

    # Continue normally (using defaults for missing sections)
    x = KlipperLCD(config)
    x.start()
```

## Implementation Example

### File: `config.py`

```python
CURRENT_CONFIG_VERSION = '2.0'

class KlipperLCDConfig:
    def __init__(self, config_path=None):
        # ... existing code ...

        # Check if update needed (but don't force it)
        self._check_for_updates()

    def needs_update(self):
        """Check if config file is old version"""
        if not self.config_path or not os.path.exists(self.config_path):
            return False

        parser = ConfigParser()
        parser.read(self.config_path)
        version = parser.get('meta', 'version', fallback='1.0')
        return version < CURRENT_CONFIG_VERSION

    def _check_for_updates(self):
        """Warn user if config is outdated"""
        if self.needs_update():
            logger.warning("")
            logger.warning("=" * 70)
            logger.warning("  CONFIG UPDATE AVAILABLE")
            logger.warning("")
            logger.warning("  Your configuration file is from an older version.")
            logger.warning("  New options are available with improved defaults!")
            logger.warning("")
            logger.warning("  To update (preserves your settings):")
            logger.warning("    python3 main.py --update-config")
            logger.warning("")
            logger.warning("  Or regenerate from scratch:")
            logger.warning("    python3 main.py --generate-config ~/printer_data/config/KlipperLCD.cfg")
            logger.warning("")
            logger.warning("  KlipperLCD will continue using defaults for new options.")
            logger.warning("=" * 70)
            logger.warning("")

    def update_config_preserving_values(self):
        """Update config file while preserving user values"""
        if not self.config_path:
            logger.error("No config path specified")
            return False

        if not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            return False

        # Backup original
        backup_path = self.config_path + '.backup'
        shutil.copy2(self.config_path, backup_path)
        logger.info(f"Created backup: {backup_path}")

        # Read current config
        old_parser = ConfigParser()
        old_parser.read(self.config_path)

        # Read all existing user values
        user_values = {}
        for section in old_parser.sections():
            user_values[section] = dict(old_parser.items(section))

        # Generate new config with current template
        temp_path = self.config_path + '.new'
        self.config_path = temp_path
        self._generate_default_config()

        # Load new template
        new_parser = ConfigParser()
        new_parser.read(temp_path)

        # Merge: user values override template defaults
        for section, values in user_values.items():
            # Ensure section exists
            if not new_parser.has_section(section):
                new_parser.add_section(section)

            # Set user values
            for key, value in values.items():
                new_parser.set(section, key, value)

        # Update version
        if not new_parser.has_section('meta'):
            new_parser.add_section('meta')
        new_parser.set('meta', 'version', CURRENT_CONFIG_VERSION)

        # Write merged config (THIS LOSES COMMENTS - see note below)
        original_path = self.config_path.replace('.new', '')
        with open(original_path, 'w') as f:
            new_parser.write(f)

        # Clean up
        os.remove(temp_path)

        logger.info(f"Config updated to version {CURRENT_CONFIG_VERSION}")
        logger.info(f"Original backed up to: {backup_path}")

        return True
```

### File: `main.py`

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KlipperLCD Service')
    parser.add_argument('--config', '-c', type=str, help='Path to config file')
    parser.add_argument('--generate-config', type=str, metavar='PATH',
                       help='Generate sample config')
    parser.add_argument('--update-config', action='store_true',
                       help='Update config file with new options (preserves values)')
    args = parser.parse_args()

    if args.generate_config:
        config = KlipperLCDConfig()
        config.generate_sample_config(args.generate_config)
        print(f"Sample configuration generated at: {args.generate_config}")
        sys.exit(0)

    # Load configuration
    config = KlipperLCDConfig(args.config)

    if args.update_config:
        print("Updating configuration file...")
        if config.update_config_preserving_values():
            print("Config updated successfully!")
            print(f"Backup saved to: {config.config_path}.backup")
            print("Please review the changes and restart the service.")
        else:
            print("Config update failed. See logs for details.")
        sys.exit(0)

    # Start KlipperLCD
    x = KlipperLCD(config)
    x.start()
```

## Important Note: ConfigParser Loses Comments!

**Problem:** Python's `ConfigParser.write()` strips all comments!

**Solutions:**

### Option A: Don't Update Config File (RECOMMENDED)
- Use runtime merging (defaults in code)
- User config only contains their changes
- Updates add new features automatically via defaults
- User runs `--generate-config` manually if they want new comments

### Option B: Template-Based Update
Use a template file with placeholders:

```python
def update_config_with_template(config_path):
    """Update using template while preserving user values"""
    # Read user values
    user_parser = ConfigParser()
    user_parser.read(config_path)

    # Read template (with all comments)
    with open('KlipperLCD.cfg.template', 'r') as f:
        template = f.read()

    # Replace {{placeholders}} with user values
    for section in user_parser.sections():
        for key, value in user_parser.items(section):
            placeholder = f"{{{{{section}.{key}}}}}"
            template = template.replace(placeholder, value)

    # Write updated config
    with open(config_path, 'w') as f:
        f.write(template)
```

### Option C: Comment-Preserving Parser
Use `configobj` library instead of `ConfigParser`:

```python
from configobj import ConfigObj

def update_with_comments(config_path):
    config = ConfigObj(config_path, indent_type='    ')

    # Add new section while preserving comments
    if 'features' not in config:
        config['features'] = {}
        config.comments['features'] = ['Enhanced features configuration']
        config['features']['default_pa'] = 0.0
        config['features'].comments['default_pa'] = [
            'Default Pressure Advance value'
        ]

    config.write()
```

## Final Recommendation for KlipperLCD

**Best Approach:**

1. **Runtime Merging (Already Implemented)** ✅
   - All config classes use `fallback=` parameters
   - Missing sections work with defaults
   - Zero user intervention needed

2. **Add `--update-config` Command** (Simple to add)
   - Backs up original
   - Regenerates config with current template
   - User manually merges using diff tool
   - Show helpful message with diff command

3. **Version Check Warning** (Add this)
   - On startup, check `[meta] version`
   - Print warning if outdated
   - Explain how to update
   - Continue normally with defaults

## User Experience

### Scenario 1: User Does Nothing
```
git pull
sudo systemctl restart KlipperLCD.service
```
**Result:** New features work automatically with defaults. ✅

### Scenario 2: User Wants New Config Comments
```
python3 main.py --generate-config ~/printer_data/config/KlipperLCD.cfg.new
diff ~/printer_data/config/KlipperLCD.cfg{,.new}
# Manually merge desired changes
```

### Scenario 3: User Runs Update Command
```
python3 main.py --update-config
# Shows: "Backup created at KlipperLCD.cfg.backup"
# Shows: "New sections added, please review"
```

## Summary

**Current Implementation:** Already does runtime merging! ✅

**Suggested Additions:**
1. Add `[meta] version = 2.0` to generated configs
2. Add `--update-config` that regenerates and shows diff
3. Add startup warning if config version is old
4. Document update process in README

**User Impact:**
- **Zero**: Updates work automatically
- **Optional**: Users can update config for new comments
- **Safe**: Never overwrites without backup

This matches the Linux philosophy: "preserve user data, make updates easy, require explicit action for destructive changes."
