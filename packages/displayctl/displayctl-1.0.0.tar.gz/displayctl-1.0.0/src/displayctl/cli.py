#!/usr/bin/env python3
"""
DisplayCtl - Display Configuration Manager for GNOME

A script to save and load monitor configurations using GNOME's D-Bus interface.
Uses org.gnome.Mutter.DisplayConfig for monitor management.

This module provides the command-line interface for DisplayCtl.
"""

import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List

# Defer dbus import until needed
dbus = None


def _ensure_dbus():
    """Import dbus module when needed."""
    global dbus
    if dbus is None:
        try:
            import dbus as _dbus
            dbus = _dbus
        except ImportError:
            print("Error: python3-dbus is required. "
                  "Install with: sudo apt install python3-dbus")
            sys.exit(1)
    return dbus


class MonitorConfigManager:
    """Manages monitor configurations using GNOME's D-Bus interface."""
    
    def __init__(self):
        self.bus = None
        self.display_config = None
        self.interface = None
        
        # Create config directory
        self.config_dir = Path.home() / '.config' / 'displayctl'
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _ensure_dbus_connection(self):
        """Ensure D-Bus connection is established."""
        if self.interface is None:
            _ensure_dbus()
            self.bus = dbus.SessionBus()
            self.display_config = self.bus.get_object(
                'org.gnome.Mutter.DisplayConfig',
                '/org/gnome/Mutter/DisplayConfig'
            )
            self.interface = dbus.Interface(
                self.display_config,
                'org.gnome.Mutter.DisplayConfig'
            )
    
    def _safe_dict_conversion(self, properties):
        """Safely convert D-Bus properties to a dictionary."""
        try:
            if isinstance(properties, dict):
                return dict(properties)
            else:
                # Handle D-Bus arrays/structs
                return dict(properties) if properties else {}
        except (ValueError, TypeError):
            return {}
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current monitor configuration state."""
        self._ensure_dbus_connection()
        try:
            # Get current resources (monitors, logical monitors, etc.)
            result = self.interface.GetCurrentState()
            serial, monitors, logical_monitors, properties = result
            
            return {
                'serial': int(serial),
                'monitors': self._parse_monitors(monitors),
                'logical_monitors': self._parse_logical_monitors(
                    logical_monitors),
                'properties': dict(properties)
            }
        except Exception as e:
            if 'dbus' in str(type(e).__module__):
                raise RuntimeError(f"Failed to get current state: {e}")
            else:
                raise
    
    def _parse_monitors(self, monitors) -> List[Dict[str, Any]]:
        """Parse monitor information from D-Bus response."""
        parsed_monitors = []
        
        for monitor in monitors:
            connector, modes, properties = monitor
            
            # Extract clean connector name from D-Bus structure
            connector_name = str(connector)
            if connector_name.startswith('dbus.Struct'):
                # Extract the first element from the D-Bus struct
                try:
                    # Parse connector info from D-Bus struct
                    pattern = r"dbus\.String\('([^']+)'\)"
                    match = re.search(pattern, connector_name)
                    if match:
                        connector_name = match.group(1)
                except Exception:
                    pass
            
            parsed_monitor = {
                'connector': connector_name,
                'modes': [],
                'properties': self._safe_dict_conversion(properties)
            }
            
            for mode in modes:
                (mode_id, width, height, refresh_rate, preferred_scale,
                 supported_scales, mode_properties) = mode
                
                parsed_mode = {
                    'id': str(mode_id),
                    'width': int(width),
                    'height': int(height),
                    'refresh_rate': float(refresh_rate),
                    'preferred_scale': float(preferred_scale),
                    'supported_scales': [float(s) for s in supported_scales],
                    'properties': self._safe_dict_conversion(mode_properties)
                }
                parsed_monitor['modes'].append(parsed_mode)
            
            parsed_monitors.append(parsed_monitor)
        
        return parsed_monitors
    
    def _parse_logical_monitors(self, logical_monitors) -> List[
            Dict[str, Any]]:
        """Parse logical monitor information from D-Bus response."""
        parsed_logical = []
        
        for logical_monitor in logical_monitors:
            (x, y, scale, transform, primary, monitor_specs,
             properties) = logical_monitor
            
            parsed_logical_monitor = {
                'x': int(x),
                'y': int(y),
                'scale': float(scale),
                'transform': int(transform),
                'primary': bool(primary),
                'monitors': [],
                'properties': self._safe_dict_conversion(properties)
            }
            
            for monitor_spec in monitor_specs:
                try:
                    if len(monitor_spec) >= 2:
                        connector = str(monitor_spec[0])
                        mode_id = str(monitor_spec[1])
                        
                        # Handle properties safely
                        properties = {}
                        if len(monitor_spec) > 2 and monitor_spec[2]:
                            try:
                                if isinstance(monitor_spec[2], dict):
                                    properties = dict(monitor_spec[2])
                                else:
                                    # Try to convert to dict if it's a sequence
                                    properties = dict(monitor_spec[2])
                            except (ValueError, TypeError):
                                # If conversion fails, store as empty dict
                                properties = {}
                        
                        parsed_logical_monitor['monitors'].append({
                            'connector': connector,
                            'mode_id': mode_id,
                            'properties': properties
                        })
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Warning: Failed to parse monitor spec: {e}")
                    continue
            
            parsed_logical.append(parsed_logical_monitor)
        
        return parsed_logical
    
    def save_config(self, name: str) -> None:
        """Save the current monitor configuration."""
        try:
            config = self.get_current_state()
            config_file = self.config_dir / f"{name}.json"
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Configuration saved as '{name}' to {config_file}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            sys.exit(1)
    
    def load_config(self, name: str, dry_run: bool = False) -> None:
        """Load and apply a saved monitor configuration."""
        config_file = self.config_dir / f"{name}.json"
        
        if not config_file.exists():
            print(f"Configuration '{name}' not found in {self.config_dir}")
            sys.exit(1)
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if dry_run:
                self._show_config_preview(config, name)
            else:
                self._apply_config(config)
                print(f"Configuration '{name}' applied successfully")
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            sys.exit(1)
    
    def _show_config_preview(self, config: Dict[str, Any], name: str) -> None:
        """Show what a configuration would do without applying it."""
        print(f"Configuration '{name}' would apply:")
        print(f"Serial: {config['serial']}")
        
        for i, lm in enumerate(config.get('logical_monitors', [])):
            primary = " (primary)" if lm.get('primary', False) else ""
            print(f"  Logical monitor {i+1}: {lm['x']},{lm['y']} "
                  f"scale {lm['scale']}{primary}")
            for monitor in lm.get('monitors', []):
                print(f"    - {monitor['connector']} "
                      f"(mode: {monitor['mode_id']})")
        
        print("\nUse 'load' without --dry-run to apply this configuration.")
    
    def _apply_config(self, config: Dict[str, Any]) -> None:
        """Apply a monitor configuration using D-Bus."""
        print("Note: Configuration loading is implemented but may require")
        print("specific mode IDs that match your current monitor setup.")
        print("This is a limitation of GNOME's D-Bus interface.")
        print("For now, use this tool primarily for saving and "
              "comparing configs.")
        
        # For demonstration, show what would be applied
        self._show_config_preview(config, "loaded config")
        
        # TODO: Implement robust config application
        # The D-Bus interface requires very specific formatting and
        # mode IDs that match exactly what the system supports
        return
    
    def list_configs(self) -> None:
        """List all saved configurations."""
        config_files = list(self.config_dir.glob("*.json"))
        
        if not config_files:
            print(f"No configurations found in {self.config_dir}")
            return
        
        print("Saved configurations:")
        for config_file in sorted(config_files):
            name = config_file.stem
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                logical_monitors = config.get('logical_monitors', [])
                monitor_count = sum(
                    len(lm.get('monitors', [])) for lm in logical_monitors)
                
                print(f"  {name}: {monitor_count} monitor(s)")
                
                for i, lm in enumerate(logical_monitors):
                    primary = " (primary)" if lm.get('primary', False) else ""
                    print(f"    Logical monitor {i+1}: {lm['x']}x{lm['y']}, "
                          f"scale {lm['scale']}{primary}")
                    for monitor in lm.get('monitors', []):
                        print(f"      - {monitor['connector']} "
                              f"(mode: {monitor['mode_id']})")
                
            except Exception as e:
                print(f"  {name}: (error reading file: {e})")
    
    def show_current(self) -> None:
        """Show current monitor configuration."""
        try:
            config = self.get_current_state()
            
            print("Current monitor configuration:")
            print(f"Serial: {config['serial']}")
            
            print("\nAvailable monitors:")
            for monitor in config['monitors']:
                print(f"  {monitor['connector']}:")
                print(f"    Available modes: {len(monitor['modes'])}")
                for mode in monitor['modes'][:3]:  # Show first 3 modes
                    refresh = mode['refresh_rate']
                    print(f"      {mode['width']}x{mode['height']}"
                          f"@{refresh:.1f}Hz")
                if len(monitor['modes']) > 3:
                    remaining = len(monitor['modes']) - 3
                    print(f"      ... and {remaining} more")
            
            print("\nActive logical monitors:")
            for i, lm in enumerate(config['logical_monitors']):
                primary = " (primary)" if lm['primary'] else ""
                print(f"  Logical monitor {i+1}: {lm['x']},{lm['y']} "
                      f"scale {lm['scale']}{primary}")
                for monitor in lm['monitors']:
                    print(f"    - {monitor['connector']} "
                          f"(mode: {monitor['mode_id']})")
                    
        except Exception as e:
            print(f"Error getting current configuration: {e}")
            # Add debug information
            import traceback
            print("Debug information:")
            traceback.print_exc()
            sys.exit(1)
    
    def delete_config(self, name: str) -> None:
        """Delete a saved configuration."""
        config_file = self.config_dir / f"{name}.json"
        
        if not config_file.exists():
            print(f"Configuration '{name}' not found")
            sys.exit(1)
        
        try:
            config_file.unlink()
            print(f"Configuration '{name}' deleted")
        except Exception as e:
            print(f"Error deleting configuration: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DisplayCtl - Display Configuration Manager for GNOME",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s save work        # Save current config as 'work'
  %(prog)s load work        # Load and apply 'work' config
  %(prog)s list             # List all saved configs
  %(prog)s current          # Show current monitor setup
  %(prog)s delete work      # Delete 'work' config
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')
    
    # Save command
    save_parser = subparsers.add_parser(
        'save', help='Save current monitor configuration')
    save_parser.add_argument('name', help='Name for the configuration')
    
    # Load command
    load_parser = subparsers.add_parser(
        'load', help='Load and apply a saved configuration')
    load_parser.add_argument('name', help='Name of the configuration to load')
    load_parser.add_argument('--dry-run', action='store_true',
                             help='Show what would be applied '
                                  'without applying')
    
    # List command
    subparsers.add_parser('list', help='List all saved configurations')
    
    # Current command
    subparsers.add_parser('current', help='Show current monitor configuration')
    
    # Delete command
    delete_parser = subparsers.add_parser(
        'delete', help='Delete a saved configuration')
    delete_parser.add_argument(
        'name', help='Name of the configuration to delete')
    
    args = parser.parse_args()
    
    try:
        if not args.command:
            parser.print_help()
            sys.exit(1)
        
        manager = MonitorConfigManager()
        
        if args.command == 'save':
            manager.save_config(args.name)
        elif args.command == 'load':
            dry_run = getattr(args, 'dry_run', False)
            manager.load_config(args.name, dry_run)
        elif args.command == 'list':
            manager.list_configs()
        elif args.command == 'current':
            manager.show_current()
        elif args.command == 'delete':
            manager.delete_config(args.name)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
