"""
PyLua VM Curator CLI
Provides interactive and command-line tools for environment setup, package management, and diagnostics.
Embodies the curator philosophy of intelligent, discerning package management.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import subprocess

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from pylua_vm.env import EnvironmentManager
from pylua_vm.utils.curator import Curator, get_curator, bootstrap_lua_environment
from pylua_vm.lua_process import LuaProcess
from pylua_vm.networking import NetworkedLuaVM


class CuratorCLI:
    """Enhanced CLI with intelligent user experience"""
    
    def __init__(self):
        self.env = None
        self.curator = None
    
    def _print_header(self, text: str, color=None):
        """Print styled header"""
        if COLORS_AVAILABLE and color:
            print(f"\n{color}{'='*60}")
            print(f"{text.center(60)}")
            print(f"{'='*60}{Style.RESET_ALL}\n")
        else:
            print(f"\n{'='*60}")
            print(f"{text.center(60)}")
            print(f"{'='*60}\n")
    
    def _print_success(self, text: str):
        """Print success message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
        else:
            print(f"✓ {text}")
    
    def _print_error(self, text: str):
        """Print error message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
        else:
            print(f"✗ {text}")
    
    def _print_warning(self, text: str):
        """Print warning message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
        else:
            print(f"⚠ {text}")
    
    def _print_info(self, text: str):
        """Print info message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")
        else:
            print(f"ℹ {text}")
    
    def initialize_environment(self, profile: str = 'standard', debug: bool = False):
        """Initialize environment and curator"""
        try:
            self.env = EnvironmentManager(profile=profile, debug_mode=debug)
            self.curator = get_curator()
            return True
        except Exception as e:
            self._print_error(f"Failed to initialize environment: {e}")
            return False
    
    def setup_environment(self, profile: str):
        """Setup complete environment with validation"""
        self._print_header(f"Setting up {profile.title()} Environment", Fore.BLUE if COLORS_AVAILABLE else None)
        
        if not self.initialize_environment(profile):
            return False
        
        # Validate environment first
        self._print_info("Validating environment prerequisites...")
        errors = self.env.validate_environment()
        
        if errors:
            self._print_warning("Environment validation issues found:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more issues")
            
            response = input("\nContinue despite issues? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                self._print_info("Setup cancelled by user")
                return False
        else:
            self._print_success("Environment validation passed")
        
        # Setup packages using curator
        self._print_info(f"Installing packages for '{profile}' profile...")
        success = self.curator.curate_environment(profile)
        
        if success:
            self._print_success(f"Environment setup complete for profile '{profile}'")
            
            # Show recommendations
            recommendations = self.curator.get_recommendations()
            if recommendations:
                self._print_info("Additional package recommendations:")
                for pkg in recommendations[:3]:
                    print(f"  - {pkg.name}: {pkg.description}")
        else:
            self._print_error("Environment setup encountered errors")
            return False
        
        return True
    
    def install_package(self, package_name: str, version: str = "latest", force: bool = False):
        """Install a specific package"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_info(f"Installing {package_name} v{version}...")
        
        success = self.curator.install_package(package_name, version, force)
        
        if success:
            self._print_success(f"Successfully installed {package_name}")
        else:
            self._print_error(f"Failed to install {package_name}")
        
        return success
    
    def remove_package(self, package_name: str):
        """Remove a package"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_info(f"Removing {package_name}...")
        
        success = self.curator.remove_package(package_name)
        
        if success:
            self._print_success(f"Successfully removed {package_name}")
        else:
            self._print_error(f"Failed to remove {package_name}")
        
        return success
    
    def show_recommendations(self, category: str = None):
        """Show intelligent package recommendations"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_header("Package Recommendations", Fore.MAGENTA if COLORS_AVAILABLE else None)
        
        recommendations = self.curator.get_recommendations()
        
        if not recommendations:
            self._print_info("No recommendations at this time - your environment looks complete!")
            return
        
        print("Based on your current setup, we recommend:\n")
        
        for i, pkg in enumerate(recommendations, 1):
            if COLORS_AVAILABLE:
                print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.YELLOW}{pkg.name}{Style.RESET_ALL}")
            else:
                print(f"{i}. {pkg.name}")
            
            print(f"   Category: {pkg.category}")
            print(f"   Priority: {pkg.priority}/10")
            print(f"   Description: {pkg.description}")
            print()
        
        # Interactive installation
        response = input("Install any of these packages? Enter numbers (e.g., 1,3) or 'all': ").strip()
        
        if response.lower() == 'all':
            for pkg in recommendations:
                self.install_package(pkg.name)
        elif response:
            try:
                indices = [int(x.strip()) for x in response.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(recommendations):
                        pkg = recommendations[idx - 1]
                        self.install_package(pkg.name)
            except ValueError:
                self._print_error("Invalid input format")
    
    def run_health_check(self, detailed: bool = False):
        """Run comprehensive health check"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_header("Environment Health Check", Fore.GREEN if COLORS_AVAILABLE else None)
        
        # Basic health check
        health = self.curator.health_check()
        
        # Environment health if available
        if self.env:
            env_errors = self.env.validate_environment()
            health['environment_errors'] = len(env_errors)
            health['lua_executable'] = self.env.lua_executable
            health['profile'] = self.env.profile
        
        # Display results
        for key, value in health.items():
            key_display = key.replace('_', ' ').title()
            
            if isinstance(value, bool):
                if value:
                    self._print_success(f"{key_display}: OK")
                else:
                    self._print_error(f"{key_display}: FAILED")
            else:
                print(f"{key_display}: {value}")
        
        # Detailed diagnostics
        if detailed:
            print("\n" + "="*40)
            print("DETAILED DIAGNOSTICS")
            print("="*40)
            
            # Check specific tools
            tools = ['lua', 'luarocks', 'git']
            for tool in tools:
                try:
                    result = subprocess.run([tool, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.split('\n')[0]
                        self._print_success(f"{tool}: {version}")
                    else:
                        self._print_error(f"{tool}: Not working properly")
                except Exception:
                    self._print_error(f"{tool}: Not found")
            
            # Show installed packages count by category
            installed = self.curator.list_installed_packages()
            categories = {}
            for pkg in installed:
                cat = pkg.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            if categories:
                print(f"\nPackages by category:")
                for cat, count in sorted(categories.items()):
                    print(f"  {cat}: {count} packages")
    
    def list_packages(self, filter_category: str = None, show_details: bool = False):
        """List installed packages"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_header("Installed Packages", Fore.BLUE if COLORS_AVAILABLE else None)
        
        packages = self.curator.list_installed_packages()
        
        if filter_category:
            packages = [p for p in packages if p.get('category') == filter_category]
            print(f"Showing packages in category: {filter_category}\n")
        
        if not packages:
            self._print_info("No packages installed" + (f" in category '{filter_category}'" if filter_category else ""))
            return
        
        # Group by category
        by_category = {}
        for pkg in packages:
            cat = pkg.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(pkg)
        
        total_packages = 0
        for category, pkgs in sorted(by_category.items()):
            if COLORS_AVAILABLE:
                print(f"{Fore.YELLOW}{category.upper()}:{Style.RESET_ALL}")
            else:
                print(f"{category.upper()}:")
            
            for pkg in sorted(pkgs, key=lambda x: x['name']):
                total_packages += 1
                name = pkg['name']
                version = pkg.get('version', 'unknown')
                
                if show_details:
                    desc = pkg.get('description', 'No description')
                    priority = pkg.get('priority', 'Unknown')
                    print(f"  ✓ {name} v{version}")
                    print(f"    Description: {desc}")
                    print(f"    Priority: {priority}")
                    print()
                else:
                    print(f"  ✓ {name} v{version}")
            print()
        
        self._print_info(f"Total: {total_packages} packages installed")
    
    def show_manifest(self, export_file: str = None):
        """Show or export current manifest"""
        if not self.curator:
            self.curator = get_curator()
        
        manifest = self.curator.manifest
        
        if export_file:
            try:
                with open(export_file, 'w') as f:
                    json.dump(manifest, f, indent=2, default=str)
                self._print_success(f"Manifest exported to {export_file}")
            except Exception as e:
                self._print_error(f"Failed to export manifest: {e}")
        else:
            self._print_header("Current Manifest", Fore.CYAN if COLORS_AVAILABLE else None)
            print(json.dumps(manifest, indent=2, default=str))
    
    def manage_profiles(self, list_profiles: bool = False, create_profile: str = None, 
                       packages: List[str] = None):
        """Manage environment profiles"""
        if not self.curator:
            self.curator = get_curator()
        
        if list_profiles:
            self._print_header("Available Profiles", Fore.MAGENTA if COLORS_AVAILABLE else None)
            
            profiles = self.curator.manifest.get('profiles', {})
            for name, pkgs in profiles.items():
                if COLORS_AVAILABLE:
                    print(f"{Fore.YELLOW}{name}:{Style.RESET_ALL} {len(pkgs)} packages")
                else:
                    print(f"{name}: {len(pkgs)} packages")
                
                for pkg in pkgs[:5]:  # Show first 5 packages
                    print(f"  - {pkg}")
                if len(pkgs) > 5:
                    print(f"  ... and {len(pkgs) - 5} more")
                print()
        
        if create_profile and packages:
            self._print_info(f"Creating profile '{create_profile}' with {len(packages)} packages")
            
            # Validate packages exist in catalog
            invalid_packages = []
            for pkg in packages:
                if pkg not in self.curator.catalog:
                    invalid_packages.append(pkg)
            
            if invalid_packages:
                self._print_warning(f"Unknown packages: {invalid_packages}")
                response = input("Continue anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    return
            
            # Add to manifest
            if 'profiles' not in self.curator.manifest:
                self.curator.manifest['profiles'] = {}
            
            self.curator.manifest['profiles'][create_profile] = packages
            self.curator._save_manifest()
            
            self._print_success(f"Profile '{create_profile}' created successfully")
    
    def cleanup_orphans(self, dry_run: bool = True):
        """Clean up orphaned packages"""
        if not self.curator:
            self.curator = get_curator()
        
        self._print_header("Orphaned Package Cleanup", Fore.YELLOW if COLORS_AVAILABLE else None)
        
        orphans = self.curator.cleanup_orphaned_packages()
        
        if not orphans:
            self._print_success("No orphaned packages found")
            return
        
        print(f"Found {len(orphans)} orphaned packages:")
        for pkg in orphans:
            print(f"  - {pkg}")
        
        if dry_run:
            self._print_info("This was a dry run. Use --cleanup-orphans --no-dry-run to actually remove them")
        else:
            response = input(f"\nRemove {len(orphans)} orphaned packages? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                removed = 0
                for pkg in orphans:
                    if self.curator.remove_package(pkg):
                        removed += 1
                
                self._print_success(f"Removed {removed}/{len(orphans)} orphaned packages")
    
    def interactive_setup(self):
        """Interactive environment setup wizard"""
        self._print_header("PyLua VM Environment Setup Wizard", Fore.BLUE if COLORS_AVAILABLE else None)
        
        print("Welcome to the PyLua VM Curator!")
        print("This wizard will help you set up your Lua environment.\n")
        
        # Profile selection
        profiles = ['minimal', 'standard', 'full', 'development', 'production', 'networking']
        
        print("Available profiles:")
        for i, profile in enumerate(profiles, 1):
            print(f"  {i}. {profile}")
        
        while True:
            try:
                choice = input(f"\nSelect profile (1-{len(profiles)}) or enter custom name: ").strip()
                
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(profiles):
                        selected_profile = profiles[idx]
                        break
                else:
                    selected_profile = choice
                    if selected_profile in profiles:
                        break
                    else:
                        # Custom profile - ask for confirmation
                        response = input(f"Create new profile '{selected_profile}'? (y/N): ").strip().lower()
                        if response in ['y', 'yes']:
                            break
                
                print("Invalid selection. Please try again.")
                
            except (ValueError, KeyboardInterrupt):
                print("\nSetup cancelled.")
                return False
        
        # Run setup
        return self.setup_environment(selected_profile)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PyLua VM Curator - Intelligent Lua Environment Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --setup --profile standard          # Setup standard environment
  %(prog)s --install lua-cjson                 # Install specific package
  %(prog)s --recommend                         # Show package recommendations
  %(prog)s --health --detailed                 # Detailed health check
  %(prog)s --list --category network           # List networking packages
  %(prog)s --interactive                       # Interactive setup wizard
  %(prog)s --cleanup-orphans --no-dry-run      # Remove orphaned packages
        """)
    
    # Environment options
    env_group = parser.add_argument_group('Environment Management')
    env_group.add_argument('--profile', type=str, default='standard',
                          choices=['minimal', 'standard', 'full', 'development', 'production', 'networking'],
                          help='Environment profile')
    env_group.add_argument('--setup', action='store_true', 
                          help='Setup environment and install recommended packages')
    env_group.add_argument('--interactive', action='store_true',
                          help='Interactive setup wizard')
    env_group.add_argument('--validate', action='store_true',
                          help='Validate environment without installing packages')
    
    # Package management
    pkg_group = parser.add_argument_group('Package Management')
    pkg_group.add_argument('--install', type=str, 
                          help='Install a specific LuaRocks package')
    pkg_group.add_argument('--version', type=str, default='latest',
                          help='Package version to install (default: latest)')
    pkg_group.add_argument('--force', action='store_true',
                          help='Force reinstallation of packages')
    pkg_group.add_argument('--remove', type=str,
                          help='Remove a specific package')
    pkg_group.add_argument('--recommend', action='store_true',
                          help='Show intelligent package recommendations')
    
    # Information and diagnostics
    info_group = parser.add_argument_group('Information & Diagnostics')
    info_group.add_argument('--health', action='store_true',
                           help='Run environment health check')
    info_group.add_argument('--detailed', action='store_true',
                           help='Show detailed information (use with --health or --list)')
    info_group.add_argument('--list', action='store_true',
                           help='List installed packages')
    info_group.add_argument('--category', type=str,
                           help='Filter by package category (use with --list)')
    info_group.add_argument('--manifest', action='store_true',
                           help='Show current manifest')
    info_group.add_argument('--export', type=str,
                           help='Export manifest to file')
    
    # Profile management
    profile_group = parser.add_argument_group('Profile Management')
    profile_group.add_argument('--list-profiles', action='store_true',
                              help='List available profiles')
    profile_group.add_argument('--create-profile', type=str,
                              help='Create new profile with specified packages')
    profile_group.add_argument('--packages', nargs='+',
                              help='Package list for profile creation')
    
    # Maintenance
    maint_group = parser.add_argument_group('Maintenance')
    maint_group.add_argument('--cleanup-orphans', action='store_true',
                            help='Clean up orphaned packages')
    maint_group.add_argument('--no-dry-run', action='store_true',
                            help='Actually perform cleanup (default is dry run)')
    maint_group.add_argument('--debug', action='store_true',
                            help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = CuratorCLI()
    
    # Handle no arguments - show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    # Interactive mode
    if args.interactive:
        return 0 if cli.interactive_setup() else 1
    
    # Initialize environment for most operations
    if any([args.setup, args.install, args.remove, args.recommend, 
            args.health, args.list, args.manifest]):
        if not cli.initialize_environment(args.profile, args.debug):
            return 1
    
    # Execute commands
    try:
        if args.validate:
            if not cli.initialize_environment(args.profile, args.debug):
                return 1
            errors = cli.env.validate_environment()
            if errors:
                cli._print_error(f"Validation failed with {len(errors)} errors:")
                for error in errors[:10]:  # Show first 10
                    print(f"  - {error}")
                return 1
            else:
                cli._print_success("Environment validation passed")
        
        if args.setup:
            success = cli.setup_environment(args.profile)
            if not success:
                return 1
        
        if args.install:
            success = cli.install_package(args.install, args.version, args.force)
            if not success:
                return 1
        
        if args.remove:
            success = cli.remove_package(args.remove)
            if not success:
                return 1
        
        if args.recommend:
            cli.show_recommendations()
        
        if args.health:
            cli.run_health_check(args.detailed)
        
        if args.list:
            cli.list_packages(args.category, args.detailed)
        
        if args.manifest:
            cli.show_manifest(args.export)
        
        if args.list_profiles:
            cli.manage_profiles(list_profiles=True)
        
        if args.create_profile:
            if not args.packages:
                cli._print_error("--packages required when creating profile")
                return 1
            cli.manage_profiles(create_profile=args.create_profile, packages=args.packages)
        
        if args.cleanup_orphans:
            cli.cleanup_orphans(dry_run=not args.no_dry_run)
    
    except KeyboardInterrupt:
        cli._print_info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        cli._print_error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())