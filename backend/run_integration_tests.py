#!/usr/bin/env python3
"""
Integration and E2E Test Runner
Runs all integration and end-to-end tests for the Zero Trust Security Framework
"""
import sys
import subprocess


def run_tests():
    """Run all integration and E2E tests"""
    print("=" * 70)
    print("Zero Trust Security Framework - Integration & E2E Test Suite")
    print("=" * 70)
    print()
    
    # Run pytest with specific markers
    test_commands = [
        ("All Tests", ["pytest", "tests/", "-v"]),
        ("Integration Tests Only", ["pytest", "tests/", "-v", "-m", "integration"]),
        ("E2E Tests Only", ["pytest", "tests/", "-v", "-m", "e2e"]),
    ]
    
    print("Select test suite to run:")
    for i, (name, _) in enumerate(test_commands, 1):
        print(f"{i}. {name}")
    print()
    
    try:
        choice = input("Enter choice (1-3) or press Enter for all tests: ").strip()
        
        if not choice:
            choice = "1"
        
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(test_commands):
            name, command = test_commands[choice_idx]
            print()
            print(f"Running: {name}")
            print("-" * 70)
            
            result = subprocess.run(command)
            
            print()
            print("-" * 70)
            if result.returncode == 0:
                print(f"✓ {name} completed successfully")
            else:
                print(f"✗ {name} failed with exit code {result.returncode}")
            
            return result.returncode
        else:
            print("Invalid choice")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nTest run cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
